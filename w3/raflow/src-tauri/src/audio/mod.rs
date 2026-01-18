mod capture;
mod denoise;

pub use capture::AudioCapture;
pub use denoise::{AudioDenoiser, DENOISE_FRAME_SIZE, DENOISE_SAMPLE_RATE, resample};
