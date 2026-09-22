#!/usr/bin/env python3
"""Simple repo-aware helper for Seisberry tasks.

This is intentionally lightweight and does not replace the full project logic.
It provides a quick summary of the important project areas for an agent or human
operator working in this repository.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main() -> None:
    print("Seisberry repository agent")
    print(f"Repository root: {ROOT}")
    print()
    print("Key areas:")
    print("- Pi_*.py: Raspberry Pi / low-memory processing scripts")
    print("- Daily_processing_v2_0_0.py: desktop or server-side processing flow")
    print("- SEGY_output.py: output generation for seismic data export")
    print("- *.scad: 3D-printable support hardware designs")
    print("- seisberry.ipynb: project notebook and reference documentation")
    print()
    print("Suggested validation:")
    print("  python -m compileall .")


if __name__ == "__main__":
    main()
