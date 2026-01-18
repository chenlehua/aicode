use cpal::traits::{DeviceTrait, HostTrait, StreamTrait};
use cpal::{SampleRate, StreamConfig};
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::Arc;
use tokio::sync::mpsc;

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

        // Calculate resampling ratio
        let resample_ratio = target_sample_rate as f64 / actual_sample_rate as f64;
        let need_resample = (resample_ratio - 1.0).abs() > 0.001;

        if need_resample {
            log::info!("Will resample from {}Hz to {}Hz (ratio: {:.4})",
                actual_sample_rate, target_sample_rate, resample_ratio);
        }

        let stream = match sample_format {
            cpal::SampleFormat::F32 => {
                let tx = audio_tx.clone();
                let recording = is_recording.clone();
                let ch = channels as usize;
                let mut callback_count = 0u32;
                device.build_input_stream(
                    &config,
                    move |data: &[f32], _| {
                        if recording.load(Ordering::SeqCst) {
                            callback_count += 1;
                            if callback_count == 1 || callback_count % 100 == 0 {
                                log::info!("Audio callback #{}, {} samples", callback_count, data.len());
                            }
                            // Convert to mono if stereo, then to i16
                            let mono_f32: Vec<f32> = if ch == 2 {
                                data.chunks(2)
                                    .map(|chunk| {
                                        (chunk[0] + chunk.get(1).copied().unwrap_or(0.0)) / 2.0
                                    })
                                    .collect()
                            } else {
                                data.to_vec()
                            };

                            // Resample if needed
                            let resampled = if need_resample {
                                simple_resample(&mono_f32, resample_ratio)
                            } else {
                                mono_f32
                            };

                            // Convert to i16
                            let pcm16: Vec<i16> = resampled
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

                            // Resample if needed
                            let resampled = if need_resample {
                                simple_resample(&mono_f32, resample_ratio)
                            } else {
                                mono_f32
                            };

                            // Convert back to i16
                            let pcm16: Vec<i16> = resampled
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

                            // Resample if needed
                            let resampled = if need_resample {
                                simple_resample(&mono_f32, resample_ratio)
                            } else {
                                mono_f32
                            };

                            // Convert to i16
                            let pcm16: Vec<i16> = resampled
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

/// Simple linear interpolation resampling
fn simple_resample(input: &[f32], ratio: f64) -> Vec<f32> {
    if input.is_empty() {
        return Vec::new();
    }

    let output_len = ((input.len() as f64) * ratio).ceil() as usize;
    let mut output = Vec::with_capacity(output_len);

    for i in 0..output_len {
        let src_pos = i as f64 / ratio;
        let src_idx = src_pos.floor() as usize;
        let frac = src_pos - src_idx as f64;

        if src_idx + 1 < input.len() {
            // Linear interpolation
            let sample = input[src_idx] * (1.0 - frac as f32) + input[src_idx + 1] * frac as f32;
            output.push(sample);
        } else if src_idx < input.len() {
            output.push(input[src_idx]);
        }
    }

    output
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
