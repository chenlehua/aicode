use base64::{engine::general_purpose::STANDARD, Engine};
use serde::{Deserialize, Deserializer, Serialize};

/// Deserialize a string that might be null as an empty string
fn deserialize_nullable_string<'de, D>(deserializer: D) -> Result<String, D::Error>
where
    D: Deserializer<'de>,
{
    Option::<String>::deserialize(deserializer).map(|opt| opt.unwrap_or_default())
}

// ============ Outgoing Messages ============

#[derive(Debug, Serialize)]
pub struct SessionConfigMessage {
    pub message_type: &'static str,
    pub sample_rate: u32,
    pub language_code: String,
    pub vad_commit_strategy: bool,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub vad_silence_threshold_secs: Option<f32>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub include_timestamps: Option<bool>,
}

impl SessionConfigMessage {
    pub fn new(language_code: String, vad_enabled: bool, vad_threshold: f32) -> Self {
        Self {
            message_type: "session_config",
            sample_rate: 16000,
            language_code,
            vad_commit_strategy: vad_enabled,
            vad_silence_threshold_secs: if vad_enabled {
                Some(vad_threshold)
            } else {
                None
            },
            include_timestamps: Some(true),
        }
    }
}

#[derive(Debug, Serialize)]
pub struct AudioChunkMessage {
    pub message_type: &'static str,
    pub audio_base_64: String,
    pub commit: bool,
    pub sample_rate: u32,
}

impl AudioChunkMessage {
    pub fn new(audio_data: &[u8], commit: bool) -> Self {
        Self {
            message_type: "input_audio_chunk",
            audio_base_64: STANDARD.encode(audio_data),
            commit,
            sample_rate: 16000,
        }
    }
}

#[derive(Debug, Serialize)]
pub struct CommitMessage {
    pub message_type: &'static str,
}

impl CommitMessage {
    pub fn new() -> Self {
        Self {
            message_type: "commit",
        }
    }
}

impl Default for CommitMessage {
    fn default() -> Self {
        Self::new()
    }
}

// ============ Incoming Messages ============

#[derive(Debug, Deserialize)]
#[serde(tag = "message_type")]
pub enum ServerMessage {
    #[serde(rename = "session_started")]
    SessionStarted(SessionStartedMessage),

    #[serde(rename = "partial_transcript")]
    PartialTranscript(TranscriptMessage),

    #[serde(rename = "committed_transcript")]
    CommittedTranscript(TranscriptMessage),

    #[serde(rename = "error")]
    Error(ErrorMessage),

    #[serde(other)]
    Unknown,
}

#[derive(Debug, Deserialize)]
pub struct SessionStartedMessage {
    pub session_id: String,
    #[serde(default)]
    pub config: Option<SessionConfig>,
}

#[derive(Debug, Deserialize)]
pub struct SessionConfig {
    #[serde(default)]
    pub sample_rate: u32,
    #[serde(default, deserialize_with = "deserialize_nullable_string")]
    pub audio_format: String,
    #[serde(default, deserialize_with = "deserialize_nullable_string")]
    pub language_code: String,
    #[serde(default, deserialize_with = "deserialize_nullable_string")]
    pub model_id: String,
    #[serde(default)]
    pub vad_commit_strategy: bool,
    #[serde(default)]
    pub vad_silence_threshold_secs: f32,
    #[serde(default)]
    pub include_timestamps: bool,
}

impl Default for SessionConfig {
    fn default() -> Self {
        Self {
            sample_rate: 16000,
            audio_format: String::new(),
            language_code: String::new(),
            model_id: String::new(),
            vad_commit_strategy: false,
            vad_silence_threshold_secs: 1.5,
            include_timestamps: false,
        }
    }
}

#[derive(Debug, Deserialize, Clone)]
pub struct TranscriptMessage {
    #[serde(default)]
    pub text: String,
    #[serde(default)]
    pub timestamp: Option<f64>,
}

#[derive(Debug, Deserialize)]
pub struct ErrorMessage {
    #[serde(default)]
    pub error: String,
    #[serde(default)]
    pub code: Option<String>,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_session_config_serialization() {
        let config = SessionConfigMessage::new("zh".to_string(), true, 1.5);
        let json = serde_json::to_string(&config).expect("Failed to serialize");
        assert!(json.contains("session_config"));
        assert!(json.contains("16000"));
        assert!(json.contains("zh"));
    }

    #[test]
    fn test_audio_chunk_serialization() {
        let data = vec![0u8, 1, 2, 3];
        let msg = AudioChunkMessage::new(&data, false);
        let json = serde_json::to_string(&msg).expect("Failed to serialize");
        assert!(json.contains("input_audio_chunk"));
        assert!(json.contains("audio_base_64"));
    }

    #[test]
    fn test_server_message_deserialization() {
        let json = r#"{"message_type":"partial_transcript","text":"Hello"}"#;
        let msg: ServerMessage = serde_json::from_str(json).expect("Failed to deserialize");
        match msg {
            ServerMessage::PartialTranscript(t) => assert_eq!(t.text, "Hello"),
            _ => panic!("Wrong message type"),
        }
    }

    #[test]
    fn test_session_started_with_null_language_code() {
        let json = r#"{"message_type":"session_started","session_id":"test-123","config":{"sample_rate":16000,"language_code":null,"model_id":null}}"#;
        let msg: ServerMessage = serde_json::from_str(json).expect("Failed to deserialize");
        match msg {
            ServerMessage::SessionStarted(s) => {
                assert_eq!(s.session_id, "test-123");
                assert!(s.config.is_some());
                let config = s.config.unwrap();
                assert_eq!(config.language_code, "");
            }
            _ => panic!("Wrong message type"),
        }
    }
}
