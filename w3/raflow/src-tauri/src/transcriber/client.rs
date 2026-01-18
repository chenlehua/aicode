use futures_util::{SinkExt, StreamExt};
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::Arc;
use tokio::sync::{mpsc, oneshot};
use tokio_tungstenite::{connect_async, tungstenite::Message};

use super::message::*;
use crate::error::{AppError, Result};

const API_BASE_URL: &str = "wss://api.elevenlabs.io/v1/speech-to-text/realtime";

/// Audio buffer chunk duration in milliseconds
const AUDIO_CHUNK_MS: u32 = 250;

/// How long to wait for final transcripts after stopping (ms)
const DRAIN_TIMEOUT_MS: u64 = 500;

/// Message type for transcript updates
#[derive(Debug, Clone)]
pub enum TranscriptEvent {
    Partial(String),
    Committed(String),
}

pub struct TranscriberClient {
    api_key: String,
    language_code: String,
    vad_enabled: bool,
    vad_threshold: f32,
}

impl TranscriberClient {
    pub fn new(
        api_key: String,
        language_code: String,
        vad_enabled: bool,
        vad_threshold: f32,
    ) -> Self {
        Self {
            api_key,
            language_code,
            vad_enabled,
            vad_threshold,
        }
    }

    fn build_url(&self) -> String {
        let mut url = format!(
            "{}?model_id=scribe_v2_realtime&sample_rate=16000&language_code={}",
            API_BASE_URL, self.language_code
        );

        // Always enable VAD for real-time transcription
        url.push_str("&vad_commit_strategy=true");
        url.push_str(&format!(
            "&vad_silence_threshold_secs={}",
            self.vad_threshold.min(0.8) // Cap at 0.8s for faster response
        ));

        url
    }

    pub async fn run(
        &self,
        mut audio_rx: mpsc::Receiver<Vec<i16>>,
        transcript_tx: mpsc::Sender<TranscriptEvent>,
        mut shutdown_rx: mpsc::Receiver<()>,
    ) -> Result<()> {
        let url = self.build_url();

        // Build WebSocket request with auth header
        let request = http::Request::builder()
            .uri(&url)
            .header("xi-api-key", &self.api_key)
            .header("Host", "api.elevenlabs.io")
            .header("Connection", "Upgrade")
            .header("Upgrade", "websocket")
            .header("Sec-WebSocket-Version", "13")
            .header(
                "Sec-WebSocket-Key",
                tokio_tungstenite::tungstenite::handshake::client::generate_key(),
            )
            .body(())
            .map_err(|e| AppError::WebSocket(e.to_string()))?;

        log::info!("Connecting to ElevenLabs API...");
        log::debug!("URL: {}", url);

        let (ws_stream, _) = connect_async(request).await?;
        let (mut write, mut read) = ws_stream.split();

        log::info!("Connected, waiting for session start...");

        // Flag to signal shutdown to tasks
        let stop_sending = Arc::new(AtomicBool::new(false));
        let stop_sending_clone = stop_sending.clone();

        // Channel to signal when Committed message is received (for early drain exit)
        let (committed_tx, committed_rx) = oneshot::channel::<()>();
        let committed_tx = Arc::new(std::sync::Mutex::new(Some(committed_tx)));

        // Task to handle incoming messages
        let tx = transcript_tx.clone();
        let committed_signal = committed_tx.clone();
        let read_task = tokio::spawn(async move {
            while let Some(msg_result) = read.next().await {
                match msg_result {
                    Ok(Message::Text(text)) => match serde_json::from_str::<ServerMessage>(&text) {
                        Ok(ServerMessage::SessionStarted(session)) => {
                            log::info!("Session started: {}", session.session_id);
                            if let Some(cfg) = &session.config {
                                log::info!("Model: {}", cfg.model_id);
                            }
                        }
                        Ok(ServerMessage::PartialTranscript(transcript)) => {
                            log::info!("Partial transcript: '{}'", transcript.text);
                            if !transcript.text.is_empty() {
                                if let Err(e) = tx.send(TranscriptEvent::Partial(transcript.text)).await {
                                    log::error!("Failed to send partial transcript: {}", e);
                                    break;
                                }
                            }
                        }
                        Ok(ServerMessage::CommittedTranscript(transcript)) => {
                            log::info!("Committed: {}", transcript.text);
                            // Signal that we received the final transcript
                            if let Ok(mut guard) = committed_signal.lock() {
                                if let Some(tx) = guard.take() {
                                    let _ = tx.send(());
                                }
                            }
                            if !transcript.text.is_empty() {
                                if let Err(e) = tx.send(TranscriptEvent::Committed(transcript.text)).await {
                                    log::error!("Failed to send committed transcript: {}", e);
                                    break;
                                }
                            }
                        }
                        Ok(ServerMessage::Error(err)) => {
                            log::error!("API error: {} ({:?})", err.error, err.code);
                        }
                        Ok(ServerMessage::Unknown) => {
                            log::info!("Unknown message type: {}", text);
                        }
                        Err(e) => {
                            log::error!("Failed to parse message: {} - {}", e, text);
                        }
                    },
                    Ok(Message::Close(_)) => {
                        log::info!("WebSocket closed by server");
                        break;
                    }
                    Ok(Message::Ping(_)) => {
                        log::debug!("Received ping");
                    }
                    Err(e) => {
                        log::error!("WebSocket error: {}", e);
                        break;
                    }
                    _ => {}
                }
            }
            log::info!("Read task finished");
        });

        // Task to send audio chunks with buffering
        let samples_per_chunk = (16000 * AUDIO_CHUNK_MS / 1000) as usize;
        log::info!("Audio buffering: {}ms chunks ({} samples)", AUDIO_CHUNK_MS, samples_per_chunk);

        // Track chunks sent for logging
        let mut chunks_sent = 0u32;

        let write_task = tokio::spawn(async move {
            let mut audio_buffer: Vec<i16> = Vec::with_capacity(samples_per_chunk * 2);

            loop {
                // Check if we should stop
                if stop_sending_clone.load(Ordering::SeqCst) {
                    log::info!("Stop signal received, finishing audio send... (sent {} chunks)", chunks_sent);
                    break;
                }

                // Try to receive audio with a small timeout
                match tokio::time::timeout(
                    tokio::time::Duration::from_millis(50),
                    audio_rx.recv()
                ).await {
                    Ok(Some(pcm_data)) => {
                        audio_buffer.extend(pcm_data);

                        // Send when buffer reaches threshold
                        while audio_buffer.len() >= samples_per_chunk {
                            let chunk: Vec<i16> = audio_buffer.drain(..samples_per_chunk).collect();
                            let bytes: Vec<u8> = chunk.iter().flat_map(|&s| s.to_le_bytes()).collect();

                            let msg = AudioChunkMessage::new(&bytes, false);
                            let json = match serde_json::to_string(&msg) {
                                Ok(j) => j,
                                Err(e) => {
                                    log::error!("Failed to serialize audio chunk: {}", e);
                                    continue;
                                }
                            };

                            if let Err(e) = write.send(Message::Text(json.into())).await {
                                log::error!("Failed to send audio chunk: {}", e);
                                return;
                            }
                            chunks_sent += 1;
                            if chunks_sent % 4 == 0 {
                                log::info!("Sent {} audio chunks ({}ms of audio)", chunks_sent, chunks_sent * AUDIO_CHUNK_MS);
                            }
                        }
                    }
                    Ok(None) => {
                        log::info!("Audio channel closed (sent {} chunks total)", chunks_sent);
                        break;
                    }
                    Err(_) => {
                        // Timeout, continue loop to check stop flag
                        continue;
                    }
                }
            }

            // Send remaining audio in buffer (if any) with commit flag
            if !audio_buffer.is_empty() {
                log::info!("Sending remaining {} samples with commit flag", audio_buffer.len());
                let bytes: Vec<u8> = audio_buffer.iter().flat_map(|&s| s.to_le_bytes()).collect();
                let msg = AudioChunkMessage::new(&bytes, true); // commit = true
                if let Ok(json) = serde_json::to_string(&msg) {
                    let _ = write.send(Message::Text(json.into())).await;
                }
            } else {
                // Send empty audio chunk with commit flag to force transcript finalization
                log::info!("Sending empty commit signal to finalize transcript");
                let msg = AudioChunkMessage::new(&[], true);
                if let Ok(json) = serde_json::to_string(&msg) {
                    let _ = write.send(Message::Text(json.into())).await;
                }
            }

            // Small delay to allow the server to process the commit
            tokio::time::sleep(tokio::time::Duration::from_millis(100)).await;

            log::info!("Write task finished");
        });

        // Wait for shutdown signal
        shutdown_rx.recv().await;
        log::info!("Shutdown signal received, stopping audio capture...");

        // Signal the write task to stop
        stop_sending.store(true, Ordering::SeqCst);

        // Wait for write task to finish
        let _ = write_task.await;

        // Wait for read task to receive final transcripts (with timeout or early exit on Committed)
        log::info!("Waiting up to {}ms for final transcripts...", DRAIN_TIMEOUT_MS);

        tokio::select! {
            _ = committed_rx => {
                log::info!("Committed received, exiting drain early");
                // Give a tiny bit of time for the transcript to be processed
                tokio::time::sleep(tokio::time::Duration::from_millis(50)).await;
            }
            _ = tokio::time::sleep(tokio::time::Duration::from_millis(DRAIN_TIMEOUT_MS)) => {
                log::info!("Drain timeout reached");
            }
        }

        // Abort the read task - we're done waiting
        read_task.abort();

        Ok(())
    }
}
