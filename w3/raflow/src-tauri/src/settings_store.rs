use std::fs;
use std::path::PathBuf;

use crate::error::{AppError, Result};
use crate::state::AppSettings;

const SETTINGS_FILE: &str = "settings.json";

/// Get the settings file path
pub fn get_settings_path() -> Result<PathBuf> {
    let config_dir = dirs::config_dir()
        .ok_or_else(|| AppError::Config("Could not find config directory".to_string()))?;

    let app_dir = config_dir.join("raflow");

    // Create directory if it doesn't exist
    if !app_dir.exists() {
        fs::create_dir_all(&app_dir)?;
    }

    Ok(app_dir.join(SETTINGS_FILE))
}

/// Load settings from file
pub fn load_settings() -> Result<AppSettings> {
    let path = get_settings_path()?;

    if !path.exists() {
        log::info!("Settings file not found, using defaults");
        return Ok(AppSettings::default());
    }

    let content = fs::read_to_string(&path)?;
    let settings: AppSettings =
        serde_json::from_str(&content).map_err(|e| AppError::Serialization(e.to_string()))?;

    log::info!("Settings loaded from {:?}", path);
    Ok(settings)
}

/// Save settings to file
pub fn save_settings(settings: &AppSettings) -> Result<()> {
    let path = get_settings_path()?;

    let content =
        serde_json::to_string_pretty(settings).map_err(|e| AppError::Serialization(e.to_string()))?;

    fs::write(&path, content)?;

    log::info!("Settings saved to {:?}", path);
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_default_settings() {
        let settings = AppSettings::default();
        assert_eq!(settings.language_code, "zho");
        assert_eq!(settings.sample_rate, 16000);
        assert!(settings.vad_enabled);
    }
}
