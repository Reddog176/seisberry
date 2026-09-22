from __future__ import annotations

import os
import platform
from pathlib import Path


def detect_runtime_architecture() -> str:
    """Return the platform architecture and a human-readable compatibility flag."""
    machine = platform.machine().lower()
    if "arm64" in machine or machine in {"aarch64"}:
        return "64-bit ARM"
    if "armv7" in machine or "armv6" in machine:
        return "32-bit ARM"
    if "x86_64" in machine or "amd64" in machine:
        return "64-bit x86"
    return platform.architecture()[0] or "unknown"


def is_64bit_runtime() -> bool:
    arch = detect_runtime_architecture()
    return "64-bit" in arch


def assert_64bit_runtime() -> None:
    """Warn on 32-bit Raspberry Pi images; the live model assumes 64-bit hardware."""
    if not is_64bit_runtime():
        raise RuntimeWarning(
            "Seisberry live streaming assumes a 64-bit Raspberry Pi runtime. "
            "Older 32-bit images are not recommended for the live model because they "
            "trigger the memory and decimation workaround that this project is moving away from."
        )


def write_runtime_notice() -> str:
    arch = detect_runtime_architecture()
    if is_64bit_runtime():
        return f"Runtime is {arch}; full-resolution live acquisition is enabled."
    return f"Runtime is {arch}; 32-bit compatibility is deprecated for the live workflow."
