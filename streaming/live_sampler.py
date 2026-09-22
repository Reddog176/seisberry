from __future__ import annotations

import os
import time
from pathlib import Path
from typing import List

from .adc import ADCDriver
from .notifications import AppriseNotifier
from .ring_buffer import RollingRingBuffer
from .seedlink_server import SeedLinkBridge
from .trigger import detect_events
from .watchdog import StationWatchdog


class LiveSeisberrySampler:
    """Python-side real-time sampling loop for the Seisberry stack.

    This mirrors the intended production flow:
      1. read ADC samples,
      2. append into a rolling ring buffer,
      3. periodically emit MiniSEED packet windows,
      4. run lightweight trigger detection,
      5. refresh a helicorder preview.
    """

    def __init__(
        self,
        adc: ADCDriver | None = None,
        sample_rate_hz: float = 750.0,
        channels: int = 3,
        window_seconds: float = 60.0,
        miniseed_dir: str | os.PathLike[str] = "data/miniseed",
        helicorder_dir: str | os.PathLike[str] = "data/helicorder",
        station_name: str = "SeisBerry",
        network: str = "USA",
        location: str = "",
        seedlink_bridge: SeedLinkBridge | None = None,
        watchdog: StationWatchdog | None = None,
        notifier: AppriseNotifier | None = None,
    ) -> None:
        self.adc = adc or ADCDriver(channels=channels, sample_rate_hz=sample_rate_hz)
        self.buffer = RollingRingBuffer(sample_rate_hz=sample_rate_hz, window_seconds=window_seconds, channels=channels)
        self.miniseed_dir = Path(miniseed_dir)
        self.helicorder_dir = Path(helicorder_dir)
        self.station_name = station_name
        self.network = network
        self.location = location
        self.sample_rate_hz = sample_rate_hz
        self.seedlink_bridge = seedlink_bridge
        self.watchdog = watchdog
        self.notifier = notifier
        self._last_packet_time = time.time()

    def capture_once(self) -> List[float]:
        frame = self.adc.read_frame()
        self.buffer.append_multichannel(frame)
        return frame

    def run(self, duration_seconds: float | None = None, packet_interval_seconds: float = 60.0) -> List[str]:
        """Run a capture loop for a limited duration.

        For a true Pi service, this would run under systemd and continue forever.
        """
        start = time.time()
        written: List[str] = []
        while True:
            frame = self.capture_once()
            if self.watchdog is not None:
                self.watchdog.record_sample()
                health = self.watchdog.check()
                os.environ["SEISBERRY_WATCHDOG_STATUS"] = str(health)
                if not health["ok"] and self.watchdog.should_alert():
                    if self.notifier is not None:
                        self.notifier.send("Seisberry station alert", f"Station health degraded: {health}")
                    self.watchdog.mark_alert_sent()
            now = time.time()
            if now - self._last_packet_time >= packet_interval_seconds:
                packet_files = self.buffer.write_miniseed_packets(
                    str(self.miniseed_dir),
                    start_time=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now - packet_interval_seconds)),
                    station_name=self.station_name,
                    network=self.network,
                    location=self.location,
                )
                if self.seedlink_bridge is not None:
                    current_window = self.buffer.flush_window()
                    self.seedlink_bridge.publish(current_window)
                written.extend(packet_files)
                self._last_packet_time = now
                self._refresh_helicorder()

            if duration_seconds is not None and (time.time() - start) >= duration_seconds:
                break
            time.sleep(1.0 / max(1.0, self.sample_rate_hz))

        return written

    def _refresh_helicorder(self) -> None:
        from .helicorder import render_helicorder

        current_window = self.buffer.flush_window()
        rows = [current_window[i] for i in sorted(current_window.keys()) if current_window[i]]
        self.helicorder_dir.mkdir(parents=True, exist_ok=True)
        render_helicorder(rows, self.helicorder_dir / "helicorder.svg")

    def detect_recent_trigger(self) -> List[tuple[int, int]]:
        current_window = self.buffer.flush_window()
        combined = []
        for channel in sorted(current_window):
            combined.extend(current_window[channel])
        return detect_events(combined, sample_rate_hz=self.sample_rate_hz)
