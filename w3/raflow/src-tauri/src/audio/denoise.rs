//! Audio denoising using nnnoiseless (RNNoise-based)
//!
//! nnnoiseless requires:
//! - 48kHz sample rate
//! - Frame size of 480 samples
//! - Mono audio (f32)

use nnnoiseless::DenoiseState;

/// Frame size required by RNNoise (10ms at 48kHz)
pub const DENOISE_FRAME_SIZE: usize = 480;

/// Sample rate required by RNNoise
pub const DENOISE_SAMPLE_RATE: u32 = 48000;

/// Audio denoiser that processes audio in frames
pub struct AudioDenoiser {
    state: Box<DenoiseState<'static>>,
    buffer: Vec<f32>,
}

impl AudioDenoiser {
    pub fn new() -> Self {
        Self {
            state: DenoiseState::new(),
            buffer: Vec::with_capacity(DENOISE_FRAME_SIZE * 4),
        }
    }

    /// Process audio samples through the denoiser
    /// Input should be mono f32 samples at 48kHz
    /// Returns denoised samples
    pub fn process(&mut self, input: &[f32]) -> Vec<f32> {
        // Add input to buffer
        self.buffer.extend_from_slice(input);

        let mut output = Vec::with_capacity(input.len());

        // Process complete frames
        while self.buffer.len() >= DENOISE_FRAME_SIZE {
            let mut out_frame = [0.0f32; DENOISE_FRAME_SIZE];
            
            // Process the frame (in-place style: output, input)
            self.state.process_frame(&mut out_frame, &self.buffer[..DENOISE_FRAME_SIZE]);
            output.extend_from_slice(&out_frame);

            // Remove processed samples from buffer
            self.buffer.drain(..DENOISE_FRAME_SIZE);
        }

        output
    }

    /// Flush any remaining samples in the buffer
    pub fn flush(&mut self) -> Vec<f32> {
        if self.buffer.is_empty() {
            return Vec::new();
        }

        // Pad the remaining samples to a full frame
        let remaining = self.buffer.len();
        let mut in_frame = [0.0f32; DENOISE_FRAME_SIZE];
        let mut out_frame = [0.0f32; DENOISE_FRAME_SIZE];
        in_frame[..remaining].copy_from_slice(&self.buffer);

        self.state.process_frame(&mut out_frame, &in_frame);

        self.buffer.clear();

        // Only return the non-padded portion
        out_frame[..remaining].to_vec()
    }

    /// Reset the denoiser state
    pub fn reset(&mut self) {
        self.state = DenoiseState::new();
        self.buffer.clear();
    }
}

impl Default for AudioDenoiser {
    fn default() -> Self {
        Self::new()
    }
}

/// Resample audio from source rate to target rate using linear interpolation
pub fn resample(input: &[f32], source_rate: u32, target_rate: u32) -> Vec<f32> {
    if source_rate == target_rate {
        return input.to_vec();
    }

    let ratio = target_rate as f64 / source_rate as f64;
    let output_len = (input.len() as f64 * ratio).ceil() as usize;
    let mut output = Vec::with_capacity(output_len);

    for i in 0..output_len {
        let src_idx = i as f64 / ratio;
        let src_floor = src_idx.floor() as usize;
        let frac = src_idx - src_floor as f64;

        let sample = if src_floor + 1 < input.len() {
            // Linear interpolation
            input[src_floor] * (1.0 - frac as f32) + input[src_floor + 1] * frac as f32
        } else if src_floor < input.len() {
            input[src_floor]
        } else {
            0.0
        };

        output.push(sample);
    }

    output
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_denoiser_creation() {
        let _denoiser = AudioDenoiser::new();
    }

    #[test]
    fn test_denoiser_process() {
        let mut denoiser = AudioDenoiser::new();

        // Create a test signal (silence)
        let input = vec![0.0f32; DENOISE_FRAME_SIZE * 2];
        let output = denoiser.process(&input);

        // Should get back roughly the same number of samples
        assert!(output.len() >= DENOISE_FRAME_SIZE);
    }

    #[test]
    fn test_resample() {
        let input = vec![0.0f32; 480];
        
        // Upsample
        let upsampled = resample(&input, 16000, 48000);
        assert!(upsampled.len() > input.len());

        // Downsample
        let downsampled = resample(&input, 48000, 16000);
        assert!(downsampled.len() < input.len());
    }
}
