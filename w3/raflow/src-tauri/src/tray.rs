use tauri::{
    image::Image,
    menu::{Menu, MenuItem},
    tray::{TrayIcon, TrayIconBuilder},
    AppHandle, Emitter, Manager, Runtime,
};

use crate::error::{AppError, Result};

// Embed tray icon at compile time
const TRAY_ICON_BYTES: &[u8] = include_bytes!("../icons/tray-icon@2x.png");

pub fn create_tray<R: Runtime>(app: &AppHandle<R>) -> Result<TrayIcon<R>> {
    let toggle = MenuItem::with_id(app, "toggle", "Start Recording (⌘⇧\\)", true, None::<&str>)
        .map_err(|e| AppError::Config(e.to_string()))?;

    let settings = MenuItem::with_id(app, "settings", "Settings...", true, None::<&str>)
        .map_err(|e| AppError::Config(e.to_string()))?;

    let about = MenuItem::with_id(app, "about", "About Raflow", true, None::<&str>)
        .map_err(|e| AppError::Config(e.to_string()))?;

    let quit =
        MenuItem::with_id(app, "quit", "Quit", true, None::<&str>).map_err(|e| AppError::Config(e.to_string()))?;

    let menu = Menu::with_items(app, &[&toggle, &settings, &about, &quit])
        .map_err(|e| AppError::Config(e.to_string()))?;

    // Load the dedicated tray icon
    let tray_icon = Image::from_bytes(TRAY_ICON_BYTES)
        .map_err(|e| AppError::Config(format!("Failed to load tray icon: {}", e)))?;

    let tray = TrayIconBuilder::new()
        .icon(tray_icon)
        .icon_as_template(true)
        .menu(&menu)
        .show_menu_on_left_click(false)
        .tooltip("Raflow - Speech to Text")
        .on_menu_event(move |app, event| {
            let id = event.id.as_ref();
            match id {
                "quit" => {
                    log::info!("Quit requested from tray menu");
                    app.exit(0);
                }
                "toggle" => {
                    log::info!("Toggle recording from tray menu");
                    if let Err(e) = app.emit("toggle-recording", ()) {
                        log::error!("Failed to emit toggle-recording event: {}", e);
                    }
                }
                "settings" => {
                    log::info!("Settings requested from tray menu");
                    if let Some(window) = app.get_webview_window("main") {
                        if let Err(e) = window.show() {
                            log::error!("Failed to show window: {}", e);
                        }
                        if let Err(e) = window.set_focus() {
                            log::error!("Failed to focus window: {}", e);
                        }
                    }
                }
                "about" => {
                    log::info!("About clicked");
                    // TODO: Show about dialog
                }
                _ => {
                    log::warn!("Unknown menu event: {}", id);
                }
            }
        })
        .build(app)
        .map_err(|e| AppError::Config(e.to_string()))?;

    log::info!("System tray created");
    Ok(tray)
}

pub fn update_tray_menu<R: Runtime>(
    tray: &TrayIcon<R>,
    app: &AppHandle<R>,
    is_recording: bool,
) -> Result<()> {
    let toggle_text = if is_recording {
        "Stop Recording (⌘⇧\\)"
    } else {
        "Start Recording (⌘⇧\\)"
    };

    let toggle = MenuItem::with_id(app, "toggle", toggle_text, true, None::<&str>)
        .map_err(|e| AppError::Config(e.to_string()))?;

    let settings = MenuItem::with_id(app, "settings", "Settings...", true, None::<&str>)
        .map_err(|e| AppError::Config(e.to_string()))?;

    let about = MenuItem::with_id(app, "about", "About Raflow", true, None::<&str>)
        .map_err(|e| AppError::Config(e.to_string()))?;

    let quit =
        MenuItem::with_id(app, "quit", "Quit", true, None::<&str>).map_err(|e| AppError::Config(e.to_string()))?;

    let menu = Menu::with_items(app, &[&toggle, &settings, &about, &quit])
        .map_err(|e| AppError::Config(e.to_string()))?;

    tray.set_menu(Some(menu))
        .map_err(|e| AppError::Config(e.to_string()))?;

    Ok(())
}
