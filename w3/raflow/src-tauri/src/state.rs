use arc_swap::ArcSwap;
use serde::{Deserialize, Serialize};
use std::sync::atomic::{AtomicBool, AtomicU64, Ordering};
use std::sync::Arc;
use tokio::sync::RwLock;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AppSettings {
    pub api_key: String,
    pub language_code: String,
    pub sample_rate: u32,
    pub vad_enabled: bool,
    pub vad_silence_threshold: f32,
    pub hotkey: String,
}

impl Default for AppSettings {
    fn default() -> Self {
        Self {
            api_key: String::new(),
            language_code: "zho".to_string(), // Chinese (中文)
            sample_rate: 16000,
            vad_enabled: true,
            vad_silence_threshold: 0.5, // Low threshold for faster real-time response
            hotkey: "CommandOrControl+Shift+\\".to_string(),
        }
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum RecordingState {
    Idle,
    Recording,
    Processing,
}

impl Default for RecordingState {
    fn default() -> Self {
        Self::Idle
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum ConnectionStatus {
    Disconnected,
    Connecting,
    Connected,
    Error,
}

impl Default for ConnectionStatus {
    fn default() -> Self {
        Self::Disconnected
    }
}

pub struct AppState {
    recording_state: RwLock<RecordingState>,
    connection_status: RwLock<ConnectionStatus>,
    transcript_buffer: RwLock<String>,
    recording_start_ms: AtomicU64,
    is_recording: AtomicBool,
    settings: ArcSwap<AppSettings>,
    target_app: RwLock<Option<String>>,
}

impl AppState {
    pub fn new() -> Self {
        Self {
            recording_state: RwLock::new(RecordingState::Idle),
            connection_status: RwLock::new(ConnectionStatus::Disconnected),
            transcript_buffer: RwLock::new(String::new()),
            recording_start_ms: AtomicU64::new(0),
            is_recording: AtomicBool::new(false),
            settings: ArcSwap::from_pointee(AppSettings::default()),
            target_app: RwLock::new(None),
        }
    }

    pub fn is_recording(&self) -> bool {
        self.is_recording.load(Ordering::SeqCst)
    }

    pub async fn set_recording(&self, recording: bool) {
        self.is_recording.store(recording, Ordering::SeqCst);

        let mut state = self.recording_state.write().await;
        *state = if recording {
            self.recording_start_ms.store(
                std::time::SystemTime::now()
                    .duration_since(std::time::UNIX_EPOCH)
                    .map(|d| d.as_millis() as u64)
                    .unwrap_or(0),
                Ordering::SeqCst,
            );
            RecordingState::Recording
        } else {
            RecordingState::Idle
        };
    }

    pub async fn get_recording_state(&self) -> RecordingState {
        *self.recording_state.read().await
    }

    pub async fn set_connection_status(&self, status: ConnectionStatus) {
        let mut conn_status = self.connection_status.write().await;
        *conn_status = status;
    }

    pub async fn get_connection_status(&self) -> ConnectionStatus {
        *self.connection_status.read().await
    }

    pub async fn append_transcript(&self, text: &str) {
        let mut buffer = self.transcript_buffer.write().await;
        buffer.push_str(text);
    }

    pub async fn get_transcript(&self) -> String {
        self.transcript_buffer.read().await.clone()
    }

    pub async fn take_transcript(&self) -> String {
        let mut buffer = self.transcript_buffer.write().await;
        std::mem::take(&mut *buffer)
    }

    pub async fn clear_transcript(&self) {
        let mut buffer = self.transcript_buffer.write().await;
        buffer.clear();
    }

    pub fn get_recording_duration_ms(&self) -> Option<u64> {
        if self.is_recording() {
            let start = self.recording_start_ms.load(Ordering::SeqCst);
            if start > 0 {
                let now = std::time::SystemTime::now()
                    .duration_since(std::time::UNIX_EPOCH)
                    .map(|d| d.as_millis() as u64)
                    .unwrap_or(0);
                Some(now.saturating_sub(start))
            } else {
                None
            }
        } else {
            None
        }
    }

    pub fn get_settings(&self) -> Arc<AppSettings> {
        self.settings.load_full()
    }

    pub fn update_settings(&self, new_settings: AppSettings) {
        self.settings.store(Arc::new(new_settings));
    }

    pub async fn set_target_app(&self, app_name: Option<String>) {
        let mut target = self.target_app.write().await;
        *target = app_name;
    }

    pub async fn get_target_app(&self) -> Option<String> {
        self.target_app.read().await.clone()
    }
}

impl Default for AppState {
    fn default() -> Self {
        Self::new()
    }
}

pub type AppStateHandle = Arc<AppState>;

pub fn create_app_state() -> AppStateHandle {
    Arc::new(AppState::new())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_recording_state() {
        let state = create_app_state();
        assert!(!state.is_recording());

        state.set_recording(true).await;
        assert!(state.is_recording());
        assert_eq!(state.get_recording_state().await, RecordingState::Recording);

        state.set_recording(false).await;
        assert!(!state.is_recording());
        assert_eq!(state.get_recording_state().await, RecordingState::Idle);
    }

    #[tokio::test]
    async fn test_transcript_buffer() {
        let state = create_app_state();

        state.append_transcript("Hello ").await;
        state.append_transcript("World").await;

        let transcript = state.get_transcript().await;
        assert_eq!(transcript, "Hello World");

        let taken = state.take_transcript().await;
        assert_eq!(taken, "Hello World");

        let empty = state.get_transcript().await;
        assert!(empty.is_empty());
    }

    #[test]
    fn test_settings() {
        let state = create_app_state();

        let settings = state.get_settings();
        assert_eq!(settings.language_code, "zho");

        let mut new_settings = (*settings).clone();
        new_settings.language_code = "en".to_string();
        state.update_settings(new_settings);

        let updated = state.get_settings();
        assert_eq!(updated.language_code, "en");
    }
}
