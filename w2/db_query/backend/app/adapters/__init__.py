"""
Database adapters package.

This module automatically discovers and loads all adapter implementations
when the package is imported.
"""

import importlib
import pkgutil
from pathlib import Path

# Auto-discover and import all adapter subpackages
_package_dir = Path(__file__).parent

for _, module_name, is_pkg in pkgutil.iter_modules([str(_package_dir)]):
    if is_pkg and module_name not in ("base", "shared"):
        # Import the package to trigger registration
        importlib.import_module(f".{module_name}", package=__name__)

# Re-export the registry for convenience
from app.core.registry import DatabaseRegistry, detect_database_type

__all__ = ["DatabaseRegistry", "detect_database_type"]
