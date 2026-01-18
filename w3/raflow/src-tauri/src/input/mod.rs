mod clipboard;
mod inserter;

pub use clipboard::ClipboardManager;
pub use inserter::{
    check_accessibility_permission, get_frontmost_app, request_accessibility_permission,
    InsertResult, TextDiff, TextInserter,
};
