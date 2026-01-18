use cpal::traits::{DeviceTrait, HostTrait, StreamTrait};
use cpal::{SampleRate, StreamConfig};
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::Arc;
use std::sync::Mutex;
use tokio::sync::mpsc;

use super::denoise::{AudioDenoiser, DENOISE_SAMPLE_RATE, resample};
use crate::error::{AppError, Result};

pub struct AudioCapture {
    stream: Option<cpal::Stream>,
    is_recording: Arc<AtomicBool>,
}

impl AudioCapture {
    pub fn new() -> Self {
        Self {
            stream: None,
            is_recording: Arc::new(AtomicBool::new(false)),
        }
    }

    pub fn start(&mut self, target_sample_rate: u32, audio_tx: mpsc::Sender<Vec<i16>>) -> Result<()> {
        let host = cpal::default_host();
        let device = host
            .default_input_device()
            .ok_or_else(|| AppError::Audio("No input device available".to_string()))?;

        let device_name = device.name().unwrap_or_else(|_| "Unknown".to_string());
        log::info!("Using audio device: {}", device_name);

        // Get supported configs
        let supported_configs: Vec<_> = device.supported_input_configs()?.collect();

        // Log available configs for debugging
        for cfg in &supported_configs {
            log::debug!(
                "Supported config: {} channels, {:?} format, {}Hz - {}Hz",
                cfg.channels(),
                cfg.sample_format(),
                cfg.min_sample_rate().0,
                cfg.max_sample_rate().0
            );
        }

        // Try to find a config that supports the target sample rate
        let (supported_config, actual_sample_rate) = supported_configs
            .iter()
            .find(|c| {
                c.channels() <= 2
                    && c.min_sample_rate().0 <= target_sample_rate
                    && c.max_sample_rate().0 >= target_sample_rate
            })
            .map(|c| (c, target_sample_rate))
            .or_else(|| {
                // Fallback: use the device's default/preferred sample rate
                // Try common sample rates that macOS supports: 48000, 44100
                for &rate in &[48000u32, 44100, 24000, 22050] {
                    if let Some(cfg) = supported_configs.iter().find(|c| {
                        c.channels() <= 2
                            && c.min_sample_rate().0 <= rate
                            && c.max_sample_rate().0 >= rate
                    }) {
                        log::info!(
                            "Using fallback sample rate {}Hz (device doesn't support {}Hz)",
                            rate,
                            target_sample_rate
                        );
                        return Some((cfg, rate));
                    }
                }
                None
            })
            .ok_or_else(|| {
                AppError::Audio("No suitable audio configuration found".to_string())
            })?;

        let channels = supported_config.channels();
        let sample_format = supported_config.sample_format();

        log::info!(
            "Audio config: {} channels, {:?} format, {}Hz (target: {}Hz)",
            channels,
            sample_format,
            actual_sample_rate,
            target_sample_rate
        );

        let config = StreamConfig {
            channels,
            sample_rate: SampleRate(actual_sample_rate),
            buffer_size: cpal::BufferSize::Default,
        };

        let is_recording = self.is_recording.clone();
        is_recording.store(true, Ordering::SeqCst);

        let err_fn = |err| log::error!("Audio stream error: {}", err);

        log::info!("Audio pipeline: {}Hz -> 48kHz (denoise) -> {}Hz",
            actual_sample_rate, target_sample_rate);

        // Create shared denoiser
        let denoiser = Arc::new(Mutex::new(AudioDenoiser::new()));
        log::info!("Audio denoiser initialized (nnnoiseless @ 48kHz)");

        let stream = match sample_format {
            cpal::SampleFormat::F32 => {
                let tx = audio_tx.clone();
                let recording = is_recording.clone();
                let ch = channels as usize;
                let mut callback_count = 0u32;
                let denoiser_clone = denoiser.clone();
                let source_rate = actual_sample_rate;
                device.build_input_stream(
                    &config,
                    move |data: &[f32], _| {
                        if recording.load(Ordering::SeqCst) {
                            callback_count += 1;
                            if callback_count == 1 || callback_count % 100 == 0 {
                                log::info!("Audio callback #{}, {} samples", callback_count, data.len());
                            }
                            // Convert to mono if stereo
                            let mono_f32: Vec<f32> = if ch == 2 {
                                data.chunks(2)
                                    .map(|chunk| {
                                        (chunk[0] + chunk.get(1).copied().unwrap_or(0.0)) / 2.0
                                    })
                                    .collect()
                            } else {
                                data.to_vec()
                            };

                            // Step 1: Upsample to 48kHz for denoising (if needed)
                            let audio_48k = if source_rate != DENOISE_SAMPLE_RATE {
                                resample(&mono_f32, source_rate, DENOISE_SAMPLE_RATE)
                            } else {
                                mono_f32
                            };

                            // Step 2: Apply noise reduction
                            let denoised = if let Ok(mut dn) = denoiser_clone.lock() {
                                dn.process(&audio_48k)
                            } else {
                                audio_48k
                            };

                            // Step 3: Downsample to target rate
                            let final_audio = if DENOISE_SAMPLE_RATE != target_sample_rate {
                                resample(&denoised, DENOISE_SAMPLE_RATE, target_sample_rate)
                            } else {
                                denoised
                            };

                            // Convert to i16
                            let pcm16: Vec<i16> = final_audio
                                .iter()
                                .map(|&s| {
                                    let clamped = s.clamp(-1.0, 1.0);
                                    (clamped * 32767.0) as i16
                                })
                                .collect();

                            if let Err(_) = tx.blocking_send(pcm16) {
                                // Channel closed - stop recording silently
                                recording.store(false, Ordering::SeqCst);
                            }
                        }
                    },
                    err_fn,
                    None,
                )?
            }
            cpal::SampleFormat::I16 => {
                let tx = audio_tx.clone();
                let recording = is_recording.clone();
                let ch = channels as usize;
                let denoiser_clone = denoiser.clone();
                let source_rate = actual_sample_rate;
                device.build_input_stream(
                    &config,
                    move |data: &[i16], _| {
                        if recording.load(Ordering::SeqCst) {
                            // Convert to mono f32
                            let mono_f32: Vec<f32> = if ch == 2 {
                                data.chunks(2)
                                    .map(|chunk| {
                                        let mono = (chunk[0] as i32
                                            + chunk.get(1).copied().unwrap_or(0) as i32)
                                            / 2;
                                        mono as f32 / 32768.0
                                    })
                                    .collect()
                            } else {
                                data.iter().map(|&s| s as f32 / 32768.0).collect()
                            };

                            // Step 1: Upsample to 48kHz for denoising
                            let audio_48k = if source_rate != DENOISE_SAMPLE_RATE {
                                resample(&mono_f32, source_rate, DENOISE_SAMPLE_RATE)
                            } else {
                                mono_f32
                            };

                            // Step 2: Apply noise reduction
                            let denoised = if let Ok(mut dn) = denoiser_clone.lock() {
                                dn.process(&audio_48k)
                            } else {
                                audio_48k
                            };

                            // Step 3: Downsample to target rate
                            let final_audio = if DENOISE_SAMPLE_RATE != target_sample_rate {
                                resample(&denoised, DENOISE_SAMPLE_RATE, target_sample_rate)
                            } else {
                                denoised
                            };

                            // Convert back to i16
                            let pcm16: Vec<i16> = final_audio
                                .iter()
                                .map(|&s| {
                                    let clamped = s.clamp(-1.0, 1.0);
                                    (clamped * 32767.0) as i16
                                })
                                .collect();

                            if let Err(_) = tx.blocking_send(pcm16) {
                                recording.store(false, Ordering::SeqCst);
                            }
                        }
                    },
                    err_fn,
                    None,
                )?
            }
            cpal::SampleFormat::I32 => {
                let tx = audio_tx.clone();
                let recording = is_recording.clone();
                let ch = channels as usize;
                let denoiser_clone = denoiser.clone();
                let source_rate = actual_sample_rate;
                device.build_input_stream(
                    &config,
                    move |data: &[i32], _| {
                        if recording.load(Ordering::SeqCst) {
                            // Convert to mono f32
                            let mono_f32: Vec<f32> = if ch == 2 {
                                data.chunks(2)
                                    .map(|chunk| {
                                        let mono = ((chunk[0] as i64
                                            + chunk.get(1).copied().unwrap_or(0) as i64)
                                            / 2) as i32;
                                        mono as f32 / 2147483648.0
                                    })
                                    .collect()
                            } else {
                                data.iter().map(|&s| s as f32 / 2147483648.0).collect()
                            };

                            // Step 1: Upsample to 48kHz for denoising
                            let audio_48k = if source_rate != DENOISE_SAMPLE_RATE {
                                resample(&mono_f32, source_rate, DENOISE_SAMPLE_RATE)
                            } else {
                                mono_f32
                            };

                            // Step 2: Apply noise reduction
                            let denoised = if let Ok(mut dn) = denoiser_clone.lock() {
                                dn.process(&audio_48k)
                            } else {
                                audio_48k
                            };

                            // Step 3: Downsample to target rate
                            let final_audio = if DENOISE_SAMPLE_RATE != target_sample_rate {
                                resample(&denoised, DENOISE_SAMPLE_RATE, target_sample_rate)
                            } else {
                                denoised
                            };

                            // Convert to i16
                            let pcm16: Vec<i16> = final_audio
                                .iter()
                                .map(|&s| {
                                    let clamped = s.clamp(-1.0, 1.0);
                                    (clamped * 32767.0) as i16
                                })
                                .collect();

                            if let Err(_) = tx.blocking_send(pcm16) {
                                recording.store(false, Ordering::SeqCst);
                            }
                        }
                    },
                    err_fn,
                    None,
                )?
            }
            _ => {
                return Err(AppError::Audio(format!(
                    "Unsupported sample format: {:?}",
                    sample_format
                )));
            }
        };

        stream.play()?;
        self.stream = Some(stream);

        log::info!("Audio capture started at {}Hz (output: {}Hz)", actual_sample_rate, target_sample_rate);
        Ok(())
    }

    pub fn stop(&mut self) {
        self.is_recording.store(false, Ordering::SeqCst);
        if let Some(stream) = self.stream.take() {
            drop(stream);
        }
        log::info!("Audio capture stopped");
    }

    pub fn is_recording(&self) -> bool {
        self.is_recording.load(Ordering::SeqCst)
    }
}

impl Default for AudioCapture {
    fn default() -> Self {
        Self::new()
    }
}

impl Drop for AudioCapture {
    fn drop(&mut self) {
        self.stop();
    }
}
