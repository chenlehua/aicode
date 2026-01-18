use std::process::Command;
use std::thread;
use std::time::Duration;

use super::ClipboardManager;
use crate::error::{AppError, Result};

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum InsertResult {
    Inserted,
    CopiedToClipboard,
}

pub struct TextInserter {
    clipboard: ClipboardManager,
}

impl TextInserter {
    pub fn new() -> Result<Self> {
        let clipboard = ClipboardManager::new()?;
        Ok(Self { clipboard })
    }

    /// Insert text via clipboard paste to a specific target app
    pub fn insert_text_to_app(&mut self, text: &str, target_app: Option<&str>) -> Result<InsertResult> {
        if text.is_empty() {
            return Ok(InsertResult::Inserted);
        }

        // Step 1: Copy text to clipboard
        self.clipboard.set_text(text)?;
        log::info!("Text copied to clipboard ({} chars)", text.len());

        // Wait for clipboard to be ready
        thread::sleep(Duration::from_millis(50));

        // Step 2: Activate target app and paste in one AppleScript
        #[cfg(target_os = "macos")]
        {
            if let Some(app) = target_app {
                log::info!("Pasting to target app: {}", app);
                let result = activate_and_paste(app);
                if result.is_ok() {
                    log::info!("Paste to {} successful", app);
                    return Ok(InsertResult::Inserted);
                }
                log::warn!("Failed to paste to {}: {:?}", app, result);
            }

            // Fallback: just paste to current frontmost
            let result = paste_with_applescript();
            if result.is_ok() {
                log::info!("Paste command sent via AppleScript");
                return Ok(InsertResult::Inserted);
            }
            log::warn!("AppleScript paste failed: {:?}", result);
        }

        // Note: enigo must be called from main thread on macOS
        // Since we're often in a background thread, just report clipboard fallback
        log::warn!("AppleScript paste failed, text is in clipboard");
        Ok(InsertResult::CopiedToClipboard)
    }

    /// Insert text via clipboard paste (legacy, uses current frontmost app)
    pub fn insert_text(&mut self, text: &str) -> Result<InsertResult> {
        self.insert_text_to_app(text, None)
    }

    fn paste_with_enigo(&self) -> Result<InsertResult> {
        use enigo::{Direction, Enigo, Key, Keyboard, Settings};

        let mut enigo = Enigo::new(&Settings::default())
            .map_err(|e| AppError::Input(format!("Failed to create Enigo: {}", e)))?;

        #[cfg(target_os = "macos")]
        let modifier = Key::Meta;
        #[cfg(not(target_os = "macos"))]
        let modifier = Key::Control;

        // Small delay before key simulation
        thread::sleep(Duration::from_millis(50));

        // Press modifier key
        if let Err(e) = enigo.key(modifier, Direction::Press) {
            log::warn!("Failed to press modifier key: {}", e);
            return Ok(InsertResult::CopiedToClipboard);
        }

        thread::sleep(Duration::from_millis(20));

        // Press V key
        if let Err(e) = enigo.key(Key::Unicode('v'), Direction::Click) {
            log::warn!("Failed to press V key: {}", e);
            let _ = enigo.key(modifier, Direction::Release);
            return Ok(InsertResult::CopiedToClipboard);
        }

        thread::sleep(Duration::from_millis(20));

        // Release modifier key
        if let Err(e) = enigo.key(modifier, Direction::Release) {
            log::warn!("Failed to release modifier key: {}", e);
        }

        // Wait for paste to complete
        thread::sleep(Duration::from_millis(50));

        log::info!("Paste command sent via Enigo (Cmd+V)");
        Ok(InsertResult::Inserted)
    }

    /// Just copy to clipboard (fallback)
    pub fn copy_to_clipboard(&mut self, text: &str) -> Result<InsertResult> {
        self.clipboard.set_text(text)?;
        log::info!("Text copied to clipboard ({} chars)", text.len());
        Ok(InsertResult::CopiedToClipboard)
    }

    /// Send Cmd+V keystroke using enigo (MUST be called from main thread on macOS!)
    pub fn send_paste_keystroke() -> Result<()> {
        use enigo::{Direction, Enigo, Key, Keyboard, Settings};

        log::info!("Sending Cmd+V from main thread...");

        let mut enigo = Enigo::new(&Settings::default())
            .map_err(|e| AppError::Input(format!("Failed to create Enigo: {}", e)))?;

        #[cfg(target_os = "macos")]
        let modifier = Key::Meta;
        #[cfg(not(target_os = "macos"))]
        let modifier = Key::Control;

        // Press modifier key
        enigo.key(modifier, Direction::Press)
            .map_err(|e| AppError::Input(format!("Failed to press modifier: {}", e)))?;

        thread::sleep(Duration::from_millis(20));

        // Press V key
        enigo.key(Key::Unicode('v'), Direction::Click)
            .map_err(|e| AppError::Input(format!("Failed to press V: {}", e)))?;

        thread::sleep(Duration::from_millis(20));

        // Release modifier key
        enigo.key(modifier, Direction::Release)
            .map_err(|e| AppError::Input(format!("Failed to release modifier: {}", e)))?;

        thread::sleep(Duration::from_millis(50));
        log::info!("Cmd+V sent successfully from main thread");
        Ok(())
    }

    /// Send backspace keystrokes using enigo (MUST be called from main thread on macOS!)
    pub fn send_backspace_keystrokes(count: usize) -> Result<()> {
        use enigo::{Direction, Enigo, Key, Keyboard, Settings};

        if count == 0 {
            return Ok(());
        }

        log::info!("Sending {} backspaces from main thread...", count);

        let mut enigo = Enigo::new(&Settings::default())
            .map_err(|e| AppError::Input(format!("Failed to create Enigo: {}", e)))?;

        for _ in 0..count {
            enigo.key(Key::Backspace, Direction::Click)
                .map_err(|e| AppError::Input(format!("Failed to press backspace: {}", e)))?;
            thread::sleep(Duration::from_millis(5));
        }

        thread::sleep(Duration::from_millis(30));
        log::info!("Backspaces sent successfully");
        Ok(())
    }

    /// Replace previously inserted partial text with new text
    /// This is used for real-time text updates during speech recognition
    pub fn replace_partial_text(
        &mut self,
        old_char_count: usize,
        new_text: &str,
        target_app: Option<&str>,
    ) -> Result<InsertResult> {
        if old_char_count == 0 {
            // No previous text, just insert
            return self.insert_text_to_app(new_text, target_app);
        }

        // Copy new text to clipboard first
        self.clipboard.set_text(new_text)?;
        thread::sleep(Duration::from_millis(30));

        #[cfg(target_os = "macos")]
        {
            if let Some(app) = target_app {
                log::info!(
                    "Replacing {} chars with '{}' in {}",
                    old_char_count,
                    new_text,
                    app
                );
                let result = select_delete_and_paste(app, old_char_count);
                if result.is_ok() {
                    return Ok(InsertResult::Inserted);
                }
                log::warn!("Failed to replace text in {}: {:?}", app, result);
            }
        }

        // Fallback: just insert via AppleScript (avoid enigo on non-main thread)
        #[cfg(target_os = "macos")]
        {
            if let Some(app) = target_app {
                let result = activate_and_paste(app);
                if result.is_ok() {
                    return Ok(InsertResult::Inserted);
                }
            }
            // Last resort: just copy to clipboard
            log::warn!("Could not insert text automatically, text is in clipboard");
            return Ok(InsertResult::CopiedToClipboard);
        }
        
        #[cfg(not(target_os = "macos"))]
        self.insert_text_to_app(new_text, target_app)
    }
}

/// Get the frontmost application name (excluding Raflow)
/// If Raflow is frontmost, get the previously active app
#[cfg(target_os = "macos")]
pub fn get_frontmost_app() -> Option<String> {
    // First, try to get the frontmost app
    let script = r#"
        tell application "System Events"
            set appList to every application process whose visible is true
            set targetApp to ""

            -- First check frontmost app
            set frontApp to name of first application process whose frontmost is true
            if frontApp is not "raflow" and frontApp is not "Raflow" then
                return frontApp
            end if

            -- If frontmost is Raflow, find the most recent non-Raflow app
            -- by checking window order
            repeat with proc in appList
                set appName to name of proc
                if appName is not "raflow" and appName is not "Raflow" and appName is not "Finder" then
                    return appName
                end if
            end repeat

            -- Fallback to Finder if nothing else
            return ""
        end tell
    "#;

    match Command::new("osascript").arg("-e").arg(script).output() {
        Ok(output) => {
            if output.status.success() {
                let app_name = String::from_utf8_lossy(&output.stdout).trim().to_string();
                log::info!("Target app (excluding Raflow): {}", app_name);
                if app_name.is_empty() {
                    None
                } else {
                    Some(app_name)
                }
            } else {
                log::warn!("Failed to get frontmost app: {}", String::from_utf8_lossy(&output.stderr));
                None
            }
        }
        Err(e) => {
            log::warn!("Failed to run AppleScript: {}", e);
            None
        }
    }
}

#[cfg(not(target_os = "macos"))]
pub fn get_frontmost_app() -> Option<String> {
    None
}

/// Activate a specific application and paste
#[cfg(target_os = "macos")]
fn activate_and_paste(app_name: &str) -> Result<()> {
    let script = format!(
        r#"
        tell application "{}"
            activate
        end tell
        delay 0.15
        tell application "System Events"
            keystroke "v" using command down
        end tell
        "#,
        app_name.replace("\"", "\\\"")
    );

    let output = Command::new("osascript")
        .arg("-e")
        .arg(&script)
        .output()
        .map_err(|e| AppError::Input(format!("Failed to run AppleScript: {}", e)))?;

    if output.status.success() {
        Ok(())
    } else {
        let stderr = String::from_utf8_lossy(&output.stderr);
        Err(AppError::Input(format!("Failed to activate and paste: {}", stderr)))
    }
}

/// Select and delete old text, then paste new text
#[cfg(target_os = "macos")]
fn select_delete_and_paste(app_name: &str, char_count: usize) -> Result<()> {
    // Use AppleScript to:
    // 1. Activate the target app
    // 2. Select previous text using shift+left arrow
    // 3. Delete selection
    // 4. Paste new text
    let script = format!(
        r#"
        tell application "{}"
            activate
        end tell
        delay 0.1
        tell application "System Events"
            -- Delete previous partial text using backspace
            repeat {} times
                key code 51 -- backspace
            end repeat
            delay 0.05
            -- Paste new text
            keystroke "v" using command down
        end tell
        "#,
        app_name.replace("\"", "\\\""),
        char_count
    );

    let output = Command::new("osascript")
        .arg("-e")
        .arg(&script)
        .output()
        .map_err(|e| AppError::Input(format!("Failed to run AppleScript: {}", e)))?;

    if output.status.success() {
        Ok(())
    } else {
        let stderr = String::from_utf8_lossy(&output.stderr);
        Err(AppError::Input(format!(
            "Failed to select/delete/paste: {}",
            stderr
        )))
    }
}

/// Activate a specific application
#[cfg(target_os = "macos")]
pub fn activate_app(app_name: &str) -> Result<()> {
    let script = format!(
        r#"
        tell application "{}" to activate
        delay 0.1
        "#,
        app_name.replace("\"", "\\\"")
    );

    let output = Command::new("osascript")
        .arg("-e")
        .arg(&script)
        .output()
        .map_err(|e| AppError::Input(format!("Failed to run AppleScript: {}", e)))?;

    if output.status.success() {
        Ok(())
    } else {
        let stderr = String::from_utf8_lossy(&output.stderr);
        Err(AppError::Input(format!("Failed to activate app: {}", stderr)))
    }
}

#[cfg(not(target_os = "macos"))]
pub fn activate_app(_app_name: &str) -> Result<()> {
    Ok(())
}

/// Paste using AppleScript
#[cfg(target_os = "macos")]
fn paste_with_applescript() -> Result<()> {
    let script = r#"
        tell application "System Events"
            keystroke "v" using command down
        end tell
    "#;

    let output = Command::new("osascript")
        .arg("-e")
        .arg(script)
        .output()
        .map_err(|e| AppError::Input(format!("Failed to run AppleScript: {}", e)))?;

    if output.status.success() {
        Ok(())
    } else {
        let stderr = String::from_utf8_lossy(&output.stderr);
        Err(AppError::Input(format!("AppleScript failed: {}", stderr)))
    }
}

/// Check if the app has accessibility permissions on macOS
/// Tries to perform an action that requires accessibility permission
#[cfg(target_os = "macos")]
pub fn check_accessibility_permission() -> bool {
    // Try to get the frontmost application - this requires accessibility permission
    let script = r#"
        tell application "System Events"
            set frontApp to name of first application process whose frontmost is true
            return frontApp
        end tell
    "#;

    match Command::new("osascript").arg("-e").arg(script).output() {
        Ok(output) => {
            // If we can successfully get the frontmost app name, we have permission
            output.status.success() && !output.stdout.is_empty()
        }
        Err(_) => false,
    }
}

#[cfg(not(target_os = "macos"))]
pub fn check_accessibility_permission() -> bool {
    true
}

/// Request accessibility permissions on macOS (opens system preferences)
#[cfg(target_os = "macos")]
pub fn request_accessibility_permission() {
    let _ = Command::new("open")
        .arg("x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility")
        .spawn();
}

#[cfg(not(target_os = "macos"))]
pub fn request_accessibility_permission() {
    // No-op on other platforms
}
