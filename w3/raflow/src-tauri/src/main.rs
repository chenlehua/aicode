#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use tauri::Manager;
use tauri_plugin_global_shortcut::GlobalShortcutExt;

use raflow_lib::commands;
use raflow_lib::hotkey;
use raflow_lib::settings_store;
use raflow_lib::state::create_app_state;
use raflow_lib::tray;

fn main() {
    // Initialize logger
    env_logger::Builder::from_env(env_logger::Env::default().default_filter_or("info")).init();

    log::info!("Starting Raflow application...");

    tauri::Builder::default()
        .setup(|app| {
            log::info!("Setting up Raflow...");

            // Initialize global shortcut plugin in setup
            #[cfg(desktop)]
            app.handle().plugin(tauri_plugin_global_shortcut::Builder::new().build())?;

            // Create app state
            let app_state = create_app_state();

            // Load settings from file
            let settings = match settings_store::load_settings() {
                Ok(s) => {
                    log::info!("Settings loaded from file");
                    s
                }
                Err(e) => {
                    log::warn!("Failed to load settings: {}, using defaults", e);
                    raflow_lib::AppSettings::default()
                }
            };

            // Update state with loaded settings
            app_state.update_settings(settings.clone());
            app.manage(app_state);

            // Create system tray
            if let Err(e) = tray::create_tray(app.handle()) {
                log::error!("Failed to create system tray: {}", e);
            }

            // Setup global shortcut from settings
            let hotkey_str = &settings.hotkey;
            if let Err(e) = hotkey::register_shortcut(app.handle(), hotkey_str) {
                log::error!("Failed to setup global shortcut '{}': {}", hotkey_str, e);
                // Try default hotkey as fallback
                if let Err(e2) = hotkey::register_shortcut(app.handle(), "CommandOrControl+Shift+\\") {
                    log::error!("Failed to setup fallback shortcut: {}", e2);
                }
            }

            // Hide main window on startup (tray-only mode)
            if let Some(window) = app.get_webview_window("main") {
                #[cfg(debug_assertions)]
                {
                    // Show window in debug mode for easier development
                    if let Err(e) = window.show() {
                        log::error!("Failed to show window: {}", e);
                    }
                }
                #[cfg(not(debug_assertions))]
                {
                    if let Err(e) = window.hide() {
                        log::error!("Failed to hide window: {}", e);
                    }
                }
            }

            log::info!("Raflow setup completed");
            Ok(())
        })
        .on_window_event(|window, event| {
            // Unregister shortcuts when window is destroyed
            if let tauri::WindowEvent::Destroyed = event {
                if let Err(e) = window.app_handle().global_shortcut().unregister_all() {
                    log::error!("Failed to unregister shortcuts on exit: {}", e);
                }
            }
        })
        .invoke_handler(tauri::generate_handler![
            commands::toggle_recording,
            commands::get_status,
            commands::get_transcript,
            commands::clear_transcript,
            commands::update_settings,
            commands::get_settings,
            commands::load_settings,
            commands::update_hotkey,
            commands::check_accessibility,
            commands::request_accessibility,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
