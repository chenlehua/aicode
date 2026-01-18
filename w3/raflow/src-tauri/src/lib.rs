pub mod audio;
pub mod commands;
pub mod error;
pub mod hotkey;
pub mod input;
pub mod settings_store;
pub mod state;
pub mod transcriber;
pub mod tray;

pub use error::{AppError, Result};
pub use state::{create_app_state, AppSettings, AppState, AppStateHandle};
