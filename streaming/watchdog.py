from __future__ import annotations

import os
import shutil
import time
from typing import Any, Dict, Optional


class StationWatchdog:
    """Simple health monitor for the live Seisberry stack."""

    def __init__(
        self,
        max_sample_gap_seconds: float = 30.0,
        min_free_disk_gb: float = 2.0,
        max_cpu_load: float = 2.5,
        alert_cooldown_seconds: float = 300.0,
        enabled: bool = True,
    ) -> None:
        self.max_sample_gap_seconds = float(max_sample_gap_seconds)
        self.min_free_disk_gb = float(min_free_disk_gb)
        self.max_cpu_load = float(max_cpu_load)
        self.alert_cooldown_seconds = float(alert_cooldown_seconds)
        self.enabled = bool(enabled)
        self._last_sample_time: Optional[float] = None
        self._last_alert_time: Optional[float] = None

    def record_sample(self, timestamp: Optional[float] = None) -> None:
        if not self.enabled:
            return
        self._last_sample_time = time.time() if timestamp is None else float(timestamp)

    def _load_average(self) -> float:
        try:
            return max(os.getloadavg()) if hasattr(os, "getloadavg") else 0.0
        except (AttributeError, OSError):
            return 0.0

    def _disk_free_gb(self) -> float:
        usage = shutil.disk_usage("/")
        return usage.free / (1024 ** 3)

    def check(self) -> Dict[str, Any]:
        if not self.enabled:
            return {"ok": True, "enabled": False, "message": "watchdog disabled"}

        now = time.time()
        gap_seconds = float("inf") if self._last_sample_time is None else max(0.0, now - self._last_sample_time)
        disk_free_gb = self._disk_free_gb()
        cpu_load = self._load_average()

        ok = (
            gap_seconds <= self.max_sample_gap_seconds and
            disk_free_gb >= self.min_free_disk_gb and
            cpu_load <= self.max_cpu_load
        )

        return {
            "ok": ok,
            "enabled": True,
            "sample_gap_seconds": gap_seconds,
            "disk_free_gb": disk_free_gb,
            "cpu_load": cpu_load,
            "message": "station healthy" if ok else "station health degraded",
        }

    def should_alert(self) -> bool:
        if self._last_alert_time is None:
            return True
        return (time.time() - self._last_alert_time) >= self.alert_cooldown_seconds

    def mark_alert_sent(self) -> None:
        self._last_alert_time = time.time()
