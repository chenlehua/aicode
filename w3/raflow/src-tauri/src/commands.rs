use serde::Serialize;
use tauri::{AppHandle, Emitter, State};
use tokio::sync::mpsc;
use tokio::task::JoinHandle;

use crate::audio::AudioCapture;
use crate::error::{AppError, Result};
use crate::hotkey;
use crate::input::{
    check_accessibility_permission, get_frontmost_app, request_accessibility_permission,
    TextInserter,
};
use crate::settings_store;
use crate::state::{AppSettings, AppStateHandle, ConnectionStatus, RecordingState};
use crate::transcriber::{TranscriberClient, TranscriptEvent};

#[derive(Serialize, Clone)]
pub struct RecordingStatus {
    pub is_recording: bool,
    pub duration_ms: Option<u64>,
}

#[derive(Serialize, Clone)]
pub struct AppStatus {
    pub recording_state: RecordingState,
    pub connection_status: ConnectionStatus,
    pub transcript: String,
    pub duration_ms: Option<u64>,
}

// Global state for audio and transcription tasks
struct RecordingSession {
    audio_tx: mpsc::Sender<Vec<i16>>,
    shutdown_tx: mpsc::Sender<()>,
    transcriber_handle: JoinHandle<()>,
    transcript_handler: JoinHandle<()>,
}

static RECORDING_SESSION: std::sync::OnceLock<tokio::sync::Mutex<Option<RecordingSession>>> =
    std::sync::OnceLock::new();

fn get_recording_session() -> &'static tokio::sync::Mutex<Option<RecordingSession>> {
    RECORDING_SESSION.get_or_init(|| tokio::sync::Mutex::new(None))
}

#[tauri::command]
pub async fn toggle_recording(
    state: State<'_, AppStateHandle>,
    app: AppHandle,
) -> Result<RecordingStatus> {
    let is_currently_recording = state.is_recording();
    log::info!("toggle_recording called, is_currently_recording: {}", is_currently_recording);

    if is_currently_recording {
        // Stop recording
        stop_recording_internal(&state, &app).await?;
    } else {
        // Start recording
        start_recording_internal(&state, &app).await?;
    }

    Ok(RecordingStatus {
        is_recording: state.is_recording(),
        duration_ms: state.get_recording_duration_ms(),
    })
}

async fn start_recording_internal(state: &AppStateHandle, app: &AppHandle) -> Result<()> {
    let settings = state.get_settings();

    if settings.api_key.is_empty() {
        return Err(AppError::Config(
            "API key not configured. Please set your ElevenLabs API key in settings.".to_string(),
        ));
    }

    // Check if target app was already captured by hotkey handler
    // If not (e.g., user clicked the button), try to capture it now
    let target_app = state.get_target_app().await;
    if target_app.is_none() {
        let captured = get_frontmost_app();
        log::info!("Target app captured on button click: {:?}", captured);
        state.set_target_app(captured).await;
    } else {
        log::info!("Using target app from hotkey: {:?}", target_app);
    }

    // Clear previous transcript
    state.clear_transcript().await;

    // Create channels for audio and transcription
    // Use larger buffer to prevent blocking during WebSocket connection
    let (audio_tx, audio_rx) = mpsc::channel::<Vec<i16>>(500);
    let (transcript_tx, mut transcript_rx) = mpsc::channel::<TranscriptEvent>(100);
    let (shutdown_tx, shutdown_rx) = mpsc::channel::<()>(1);

    // Start audio capture in a separate thread (cpal requires this)
    let audio_tx_clone = audio_tx.clone();
    let sample_rate = settings.sample_rate;
    std::thread::spawn(move || {
        let mut capture = AudioCapture::new();
        if let Err(e) = capture.start(sample_rate, audio_tx_clone) {
            log::error!("Failed to start audio capture: {}", e);
        }
        // Keep the thread alive until the stream is stopped
        // The stream will be stopped when audio_tx is dropped
        loop {
            std::thread::sleep(std::time::Duration::from_millis(100));
            if !capture.is_recording() {
                break;
            }
        }
    });

    // Start transcription client
    let api_key = settings.api_key.clone();
    let language_code = settings.language_code.clone();
    let vad_enabled = settings.vad_enabled;
    let vad_threshold = settings.vad_silence_threshold;

    let transcriber_handle = tokio::spawn(async move {
        let client = TranscriberClient::new(api_key, language_code, vad_enabled, vad_threshold);
        if let Err(e) = client.run(audio_rx, transcript_tx, shutdown_rx).await {
            log::error!("Transcription error: {}", e);
        }
    });

    // Handle incoming transcripts - insert in real-time
    let state_clone = state.clone();
    let app_clone = app.clone();
    let transcript_handler = tokio::spawn(async move {
        // Track the last partial text for real-time replacement
        let mut last_partial_text: String = String::new();

        while let Some(event) = transcript_rx.recv().await {
            match event {
                TranscriptEvent::Partial(text) => {
                    // Emit partial for UI preview
                    if let Err(e) = app_clone.emit("partial-transcript", &text) {
                        log::error!("Failed to emit partial transcript: {}", e);
                    }

                    // Skip if text hasn't changed
                    if text == last_partial_text {
                        continue;
                    }

                    // Real-time text insertion: replace previous partial with new one
                    let target = state_clone.get_target_app().await;
                    let old_len = last_partial_text.chars().count();
                    let new_text = text.clone();
                    last_partial_text = text;

                    log::info!(
                        "Partial update: replacing {} chars with '{}' ({} chars)",
                        old_len,
                        new_text,
                        new_text.chars().count()
                    );

                    std::thread::spawn(move || {
                        match TextInserter::new() {
                            Ok(mut inserter) => {
                                if let Err(e) = inserter.replace_partial_text(
                                    old_len,
                                    &new_text,
                                    target.as_deref(),
                                ) {
                                    log::error!("Failed to replace partial text: {}", e);
                                }
                            }
                            Err(e) => {
                                log::error!("Failed to create text inserter: {}", e);
                            }
                        }
                    });
                }
                TranscriptEvent::Committed(text) => {
                    log::info!("Committed text: '{}'", text);

                    // Add to transcript buffer
                    state_clone.append_transcript(&text).await;
                    state_clone.append_transcript(" ").await;

                    // Emit for UI
                    if let Err(e) = app_clone.emit("transcript-update", &text) {
                        log::error!("Failed to emit transcript update: {}", e);
                    }

                    // The committed text should already be displayed from partials
                    // Just add a space after the committed segment
                    let target = state_clone.get_target_app().await;
                    let old_len = last_partial_text.chars().count();
                    let committed_text = format!("{} ", text);
                    last_partial_text.clear(); // Reset for next segment

                    std::thread::spawn(move || {
                        match TextInserter::new() {
                            Ok(mut inserter) => {
                                // Replace partial with final committed text + space
                                if let Err(e) = inserter.replace_partial_text(
                                    old_len,
                                    &committed_text,
                                    target.as_deref(),
                                ) {
                                    log::error!("Failed to insert committed text: {}", e);
                                }
                            }
                            Err(e) => {
                                log::error!("Failed to create text inserter: {}", e);
                            }
                        }
                    });
                }
            }
        }
        log::info!("Transcript receiver task finished");
    });

    // Store session
    let mut session = get_recording_session().lock().await;
    *session = Some(RecordingSession {
        audio_tx,
        shutdown_tx,
        transcriber_handle,
        transcript_handler,
    });

    // Update state
    state.set_recording(true).await;
    state.set_connection_status(ConnectionStatus::Connected).await;

    // Emit event
    if let Err(e) = app.emit("recording-started", ()) {
        log::error!("Failed to emit recording-started event: {}", e);
    }

    log::info!("Recording started");
    Ok(())
}

async fn stop_recording_internal(state: &AppStateHandle, app: &AppHandle) -> Result<()> {
    log::info!("stop_recording_internal called");

    // Get the session and send shutdown signal
    let session = {
        log::info!("Acquiring session lock...");
        let mut session_lock = get_recording_session().lock().await;
        log::info!("Session lock acquired, taking session...");
        session_lock.take()
    };

    if let Some(s) = session {
        log::info!("Sending shutdown signal...");

        // Send shutdown signal
        let _ = s.shutdown_tx.send(()).await;

        // Drop the audio sender to stop the audio capture
        drop(s.audio_tx);

        // Wait for the transcriber to finish (with timeout)
        log::info!("Waiting for transcriber to finish...");
        let transcriber_result = tokio::time::timeout(
            tokio::time::Duration::from_millis(3000),
            s.transcriber_handle
        ).await;

        match transcriber_result {
            Ok(_) => log::info!("Transcriber finished"),
            Err(_) => log::warn!("Transcriber timeout - continuing anyway"),
        }

        // Don't wait for transcript handler - let it finish in the background
        // The text insertion threads are already spawned and will complete on their own
        log::info!("Detaching transcript handler (will finish in background)");
        // Just abort it - the spawned threads will continue
        s.transcript_handler.abort();

        log::info!("All critical tasks finished");
    } else {
        log::warn!("No session found - already stopped?");
    }

    // Update state immediately so UI can respond
    log::info!("Updating state to not recording...");
    state.set_recording(false).await;
    state.set_connection_status(ConnectionStatus::Disconnected).await;

    // Clear target app for next session
    state.set_target_app(None).await;

    // Clear transcript buffer (text was already inserted in real-time)
    let transcript = state.take_transcript().await;
    log::info!("Session transcript: '{}' ({} chars)", transcript.trim(), transcript.len());

    // Emit event
    if let Err(e) = app.emit("recording-stopped", ()) {
        log::error!("Failed to emit recording-stopped event: {}", e);
    }

    log::info!("Recording stopped");
    Ok(())
}

#[tauri::command]
pub async fn get_status(state: State<'_, AppStateHandle>) -> Result<AppStatus> {
    let transcript = state.get_transcript().await;

    Ok(AppStatus {
        recording_state: state.get_recording_state().await,
        connection_status: state.get_connection_status().await,
        transcript,
        duration_ms: state.get_recording_duration_ms(),
    })
}

#[tauri::command]
pub async fn get_transcript(state: State<'_, AppStateHandle>) -> Result<String> {
    Ok(state.get_transcript().await)
}

#[tauri::command]
pub async fn clear_transcript(state: State<'_, AppStateHandle>) -> Result<()> {
    state.clear_transcript().await;
    Ok(())
}

#[tauri::command]
pub async fn update_settings(
    state: State<'_, AppStateHandle>,
    app: AppHandle,
    settings: AppSettings,
) -> Result<()> {
    let old_settings = state.get_settings();
    let hotkey_changed = old_settings.hotkey != settings.hotkey;

    // Update state
    state.update_settings(settings.clone());

    // Save to file
    if let Err(e) = settings_store::save_settings(&settings) {
        log::error!("Failed to save settings: {}", e);
    }

    // Update hotkey if changed
    if hotkey_changed {
        if let Err(e) = hotkey::update_shortcut(&app, &settings.hotkey) {
            log::error!("Failed to update hotkey: {}", e);
            return Err(e);
        }
    }

    log::info!("Settings updated");
    Ok(())
}

#[tauri::command]
pub async fn get_settings(state: State<'_, AppStateHandle>) -> Result<AppSettings> {
    Ok((*state.get_settings()).clone())
}

#[tauri::command]
pub async fn load_settings(state: State<'_, AppStateHandle>) -> Result<AppSettings> {
    // Try to load from file
    match settings_store::load_settings() {
        Ok(settings) => {
            state.update_settings(settings.clone());
            Ok(settings)
        }
        Err(e) => {
            log::warn!("Failed to load settings from file: {}, using defaults", e);
            Ok((*state.get_settings()).clone())
        }
    }
}

#[tauri::command]
pub async fn update_hotkey(
    state: State<'_, AppStateHandle>,
    app: AppHandle,
    hotkey: String,
) -> Result<()> {
    // Validate the hotkey first
    hotkey::parse_hotkey(&hotkey)?;

    // Update settings
    let mut settings = (*state.get_settings()).clone();
    settings.hotkey = hotkey.clone();
    state.update_settings(settings.clone());

    // Save to file
    if let Err(e) = settings_store::save_settings(&settings) {
        log::error!("Failed to save settings: {}", e);
    }

    // Update the registered shortcut
    hotkey::update_shortcut(&app, &hotkey)?;

    log::info!("Hotkey updated to: {}", hotkey);
    Ok(())
}

#[tauri::command]
pub async fn check_accessibility() -> bool {
    let has_permission = check_accessibility_permission();
    log::info!("Accessibility permission check: {}", has_permission);
    has_permission
}

#[tauri::command]
pub async fn request_accessibility() {
    log::info!("Opening accessibility preferences...");
    request_accessibility_permission();
}
