# --- preflight_check.py ---
"""Preflight validation utilities.

This module performs a lightweight validation of the repository layout before
the rest of the analyzer is executed.  It is intentionally simple so that it can
run in constrained environments without pulling in heavy dependencies.
"""

from __future__ import annotations

import os
import sys
from typing import Iterable


def _check_required_directories(dirs: Iterable[str]) -> list[str]:
    """Return a list of directories that do not exist."""
    missing = []
    for d in dirs:
        if not os.path.isdir(d):
            missing.append(d)
    return missing


def _check_vendor_yamls(config_dir: str) -> bool:
    """Return ``True`` if the vendor config directory contains YAML files."""
    if not os.path.isdir(config_dir):
        return False
    for name in os.listdir(config_dir):
        if name.lower().endswith(('.yaml', '.yml')):
            return True
    return False


def _check_onnx_models(models_dir: str) -> bool:
    """Return ``True`` if at least one ``.onnx`` file exists under ``models_dir``."""
    if not os.path.isdir(models_dir):
        return False
    for root, _, files in os.walk(models_dir):
        for f in files:
            if f.lower().endswith('.onnx'):
                return True
    return False


def run_preflight() -> int:
    """Perform basic repository sanity checks.

    Checks for required directories, vendor YAML configuration files and ONNX
    models.  A non-zero status code is returned if any check fails.
    """

    required_dirs = [
        "modular_analyzer/configs",
        "modular_analyzer/models",
        "modular_analyzer/templates",
        "output",
    ]

    missing_dirs = _check_required_directories(required_dirs)
    if missing_dirs:
        print("[Preflight] Missing directories:")
        for d in missing_dirs:
            print(f"  - {d}")
        return 1

    if not _check_vendor_yamls("modular_analyzer/configs"):
        print("[Preflight] No vendor YAML files found in modular_analyzer/configs")
        return 1

    if not _check_onnx_models("modular_analyzer/models"):
        print("[Preflight] No ONNX model files found in modular_analyzer/models")
        return 1

    print("[Preflight] All checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(run_preflight())
