use arboard::Clipboard;

use crate::error::{AppError, Result};

pub struct ClipboardManager {
    clipboard: Clipboard,
}

impl ClipboardManager {
    pub fn new() -> Result<Self> {
        let clipboard =
            Clipboard::new().map_err(|e| AppError::Input(format!("Clipboard init failed: {}", e)))?;
        Ok(Self { clipboard })
    }

    pub fn get_text(&mut self) -> Result<String> {
        self.clipboard
            .get_text()
            .map_err(|e| AppError::Input(format!("Failed to get clipboard text: {}", e)))
    }

    pub fn set_text(&mut self, text: &str) -> Result<()> {
        self.clipboard
            .set_text(text)
            .map_err(|e| AppError::Input(format!("Failed to set clipboard text: {}", e)))
    }

    #[allow(dead_code)]
    pub fn clear(&mut self) -> Result<()> {
        self.clipboard
            .clear()
            .map_err(|e| AppError::Input(format!("Failed to clear clipboard: {}", e)))
    }
}
