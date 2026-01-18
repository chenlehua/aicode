use serde::Serialize;
use thiserror::Error;

#[derive(Error, Debug)]
pub enum AppError {
    #[error("Audio error: {0}")]
    Audio(String),

    #[error("WebSocket error: {0}")]
    WebSocket(String),

    #[error("API error: {0}")]
    Api(String),

    #[error("Input error: {0}")]
    Input(String),

    #[error("Permission error: {0}")]
    Permission(String),

    #[error("Configuration error: {0}")]
    Config(String),

    #[error("State error: {0}")]
    State(String),

    #[error("IO error: {0}")]
    Io(String),

    #[error("Serialization error: {0}")]
    Serialization(String),
}

impl Serialize for AppError {
    fn serialize<S>(&self, serializer: S) -> std::result::Result<S::Ok, S::Error>
    where
        S: serde::Serializer,
    {
        serializer.serialize_str(&self.to_string())
    }
}

impl From<std::io::Error> for AppError {
    fn from(err: std::io::Error) -> Self {
        AppError::Io(err.to_string())
    }
}

impl From<serde_json::Error> for AppError {
    fn from(err: serde_json::Error) -> Self {
        AppError::Serialization(err.to_string())
    }
}

impl From<cpal::BuildStreamError> for AppError {
    fn from(err: cpal::BuildStreamError) -> Self {
        AppError::Audio(err.to_string())
    }
}

impl From<cpal::PlayStreamError> for AppError {
    fn from(err: cpal::PlayStreamError) -> Self {
        AppError::Audio(err.to_string())
    }
}

impl From<cpal::DevicesError> for AppError {
    fn from(err: cpal::DevicesError) -> Self {
        AppError::Audio(err.to_string())
    }
}

impl From<cpal::SupportedStreamConfigsError> for AppError {
    fn from(err: cpal::SupportedStreamConfigsError) -> Self {
        AppError::Audio(err.to_string())
    }
}

impl From<tokio_tungstenite::tungstenite::Error> for AppError {
    fn from(err: tokio_tungstenite::tungstenite::Error) -> Self {
        AppError::WebSocket(err.to_string())
    }
}

impl From<arboard::Error> for AppError {
    fn from(err: arboard::Error) -> Self {
        AppError::Input(format!("Clipboard error: {}", err))
    }
}

impl From<tauri::Error> for AppError {
    fn from(err: tauri::Error) -> Self {
        AppError::Config(err.to_string())
    }
}

pub type Result<T> = std::result::Result<T, AppError>;
