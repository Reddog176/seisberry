from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib  # type: ignore


def load_config(path: str | Path) -> Dict[str, Any]:
    config_file = Path(path)
    if not config_file.exists():
        raise FileNotFoundError(f"Seisberry config not found: {config_file}")

    with config_file.open("rb") as handle:
        return tomllib.load(handle)
