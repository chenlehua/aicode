use tauri::{AppHandle, Emitter, Manager, Runtime};
use tauri_plugin_global_shortcut::{
    Code, GlobalShortcutExt, Modifiers, Shortcut, ShortcutState,
};

use crate::error::{AppError, Result};
use crate::input::get_frontmost_app;
use crate::state::AppStateHandle;

/// Parse a hotkey string like "CommandOrControl+Shift+\" into Shortcut
pub fn parse_hotkey(hotkey_str: &str) -> Result<Shortcut> {
    let parts: Vec<&str> = hotkey_str.split('+').collect();
    if parts.is_empty() {
        return Err(AppError::Config("Empty hotkey string".to_string()));
    }

    let mut modifiers = Modifiers::empty();
    let mut key_code: Option<Code> = None;

    for part in parts {
        let part_lower = part.to_lowercase();
        match part_lower.as_str() {
            "commandorcontrol" | "cmdorctrl" | "command" | "cmd" | "super" => {
                modifiers |= Modifiers::SUPER;
            }
            "control" | "ctrl" => {
                modifiers |= Modifiers::CONTROL;
            }
            "shift" => {
                modifiers |= Modifiers::SHIFT;
            }
            "alt" | "option" => {
                modifiers |= Modifiers::ALT;
            }
            "meta" => {
                modifiers |= Modifiers::META;
            }
            "\\" | "backslash" => {
                key_code = Some(Code::Backslash);
            }
            "/" | "slash" => {
                key_code = Some(Code::Slash);
            }
            "space" => {
                key_code = Some(Code::Space);
            }
            "enter" | "return" => {
                key_code = Some(Code::Enter);
            }
            "tab" => {
                key_code = Some(Code::Tab);
            }
            "escape" | "esc" => {
                key_code = Some(Code::Escape);
            }
            "backspace" => {
                key_code = Some(Code::Backspace);
            }
            "delete" => {
                key_code = Some(Code::Delete);
            }
            "up" | "arrowup" => {
                key_code = Some(Code::ArrowUp);
            }
            "down" | "arrowdown" => {
                key_code = Some(Code::ArrowDown);
            }
            "left" | "arrowleft" => {
                key_code = Some(Code::ArrowLeft);
            }
            "right" | "arrowright" => {
                key_code = Some(Code::ArrowRight);
            }
            "f1" => key_code = Some(Code::F1),
            "f2" => key_code = Some(Code::F2),
            "f3" => key_code = Some(Code::F3),
            "f4" => key_code = Some(Code::F4),
            "f5" => key_code = Some(Code::F5),
            "f6" => key_code = Some(Code::F6),
            "f7" => key_code = Some(Code::F7),
            "f8" => key_code = Some(Code::F8),
            "f9" => key_code = Some(Code::F9),
            "f10" => key_code = Some(Code::F10),
            "f11" => key_code = Some(Code::F11),
            "f12" => key_code = Some(Code::F12),
            s if s.len() == 1 => {
                let c = s.chars().next().unwrap_or('a');
                key_code = Some(match c {
                    'a' => Code::KeyA,
                    'b' => Code::KeyB,
                    'c' => Code::KeyC,
                    'd' => Code::KeyD,
                    'e' => Code::KeyE,
                    'f' => Code::KeyF,
                    'g' => Code::KeyG,
                    'h' => Code::KeyH,
                    'i' => Code::KeyI,
                    'j' => Code::KeyJ,
                    'k' => Code::KeyK,
                    'l' => Code::KeyL,
                    'm' => Code::KeyM,
                    'n' => Code::KeyN,
                    'o' => Code::KeyO,
                    'p' => Code::KeyP,
                    'q' => Code::KeyQ,
                    'r' => Code::KeyR,
                    's' => Code::KeyS,
                    't' => Code::KeyT,
                    'u' => Code::KeyU,
                    'v' => Code::KeyV,
                    'w' => Code::KeyW,
                    'x' => Code::KeyX,
                    'y' => Code::KeyY,
                    'z' => Code::KeyZ,
                    '0' => Code::Digit0,
                    '1' => Code::Digit1,
                    '2' => Code::Digit2,
                    '3' => Code::Digit3,
                    '4' => Code::Digit4,
                    '5' => Code::Digit5,
                    '6' => Code::Digit6,
                    '7' => Code::Digit7,
                    '8' => Code::Digit8,
                    '9' => Code::Digit9,
                    _ => return Err(AppError::Config(format!("Unknown key: {}", c))),
                });
            }
            _ => {
                log::warn!("Unknown hotkey part: {}", part);
            }
        }
    }

    let code = key_code.ok_or_else(|| AppError::Config("No key specified in hotkey".to_string()))?;

    Ok(Shortcut::new(
        if modifiers.is_empty() { None } else { Some(modifiers) },
        code,
    ))
}

/// Register a global shortcut with the given hotkey string
pub fn register_shortcut<R: Runtime>(app: &AppHandle<R>, hotkey_str: &str) -> Result<()> {
    let shortcut = parse_hotkey(hotkey_str)?;

    app.global_shortcut()
        .on_shortcut(shortcut, move |app, _shortcut, event| {
            if event.state == ShortcutState::Pressed {
                log::info!("Global shortcut triggered");

                // IMPORTANT: Capture the frontmost app IMMEDIATELY when hotkey is pressed
                // This is before any UI changes happen, so we get the correct target app
                let target_app = get_frontmost_app();
                log::info!("Target app captured on hotkey press: {:?}", target_app);

                // Store the target app in state
                if let Some(state) = app.try_state::<AppStateHandle>() {
                    // Use a blocking task to set the target app since we can't await here
                    let state_clone = state.inner().clone();
                    let target = target_app.clone();
                    std::thread::spawn(move || {
                        let rt = tokio::runtime::Builder::new_current_thread()
                            .enable_all()
                            .build()
                            .expect("Failed to create runtime");
                        rt.block_on(async {
                            state_clone.set_target_app(target).await;
                        });
                    });
                }

                if let Err(e) = app.emit("toggle-recording", ()) {
                    log::error!("Failed to emit toggle-recording event: {}", e);
                }
            }
        })
        .map_err(|e| AppError::Config(format!("Failed to register shortcut: {}", e)))?;

    log::info!("Global shortcut registered: {}", hotkey_str);
    Ok(())
}

/// Unregister all shortcuts and register a new one
pub fn update_shortcut<R: Runtime>(app: &AppHandle<R>, hotkey_str: &str) -> Result<()> {
    // Unregister all existing shortcuts
    app.global_shortcut()
        .unregister_all()
        .map_err(|e| AppError::Config(format!("Failed to unregister shortcuts: {}", e)))?;

    // Register the new shortcut
    register_shortcut(app, hotkey_str)?;

    Ok(())
}

pub fn unregister_shortcuts<R: Runtime>(app: &AppHandle<R>) -> Result<()> {
    app.global_shortcut()
        .unregister_all()
        .map_err(|e| AppError::Config(format!("Failed to unregister shortcuts: {}", e)))?;
    log::info!("Global shortcuts unregistered");
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parse_hotkey() {
        // Test various hotkey formats
        assert!(parse_hotkey("CommandOrControl+Shift+\\").is_ok());
        assert!(parse_hotkey("Ctrl+Alt+A").is_ok());
        assert!(parse_hotkey("F12").is_ok());
        assert!(parse_hotkey("Shift+Space").is_ok());
        assert!(parse_hotkey("CommandOrControl+R").is_ok());

        // Test invalid hotkey
        assert!(parse_hotkey("").is_err());
    }
}
