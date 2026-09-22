from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Deque, Dict, Iterable, List, Optional


@dataclass
class RollingRingBuffer:
    """A lightweight rolling buffer for live seismic data.

    The buffer keeps a short time window in memory and can flush fixed-length
    windows to MiniSEED packets. This removes the repo's daily batch file pattern
    without requiring a full high-end streaming stack.
    """

    sample_rate_hz: float = 750.0
    window_seconds: float = 60.0
    channels: int = 3
    _buffers: Dict[int, Deque[float]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.samples_per_window = int(self.sample_rate_hz * self.window_seconds)
        for channel in range(self.channels):
            self._buffers.setdefault(channel, deque(maxlen=self.samples_per_window))

    def append(self, samples: Iterable[float], channel: int) -> None:
        if channel < 0 or channel >= self.channels:
            raise ValueError(f"Channel must be between 0 and {self.channels - 1}.")

        data = self._buffers.setdefault(channel, deque(maxlen=self.samples_per_window))
        for value in samples:
            data.append(float(value))

    def append_multichannel(self, frame: Iterable[Iterable[float]] | Iterable[float]) -> None:
        # Accept either a row-wise frame of channel arrays or a single flat frame of
        # per-channel values from the ADC read.
        first_value = next(iter(frame), None)
        if first_value is None:
            return

        if isinstance(first_value, (int, float)):
            for channel_idx, value in enumerate(frame):
                if channel_idx >= self.channels:
                    break
                self.append([float(value)], channel_idx)
            return

        for channel_idx, channel_values in enumerate(frame):
            if channel_idx >= self.channels:
                break
            self.append(channel_values, channel_idx)

    def sample_count(self, channel: int) -> int:
        return len(self._buffers.get(channel, deque()))

    def flush_window(self) -> Dict[int, List[float]]:
        window = {channel: list(values) for channel, values in self._buffers.items()}
        for channel in range(self.channels):
            self._buffers[channel].clear()
        return window

    def write_miniseed_packets(
        self,
        outdir: str,
        start_time,
        station_name: str = "SeisBerry",
        network: str = "USA",
        location: str = "",
    ) -> List[str]:
        """Write one-minute MiniSEED windows to disk.

        If ObsPy is not installed, this raises a clear RuntimeError so the caller
        can decide whether to fall back to a file-based placeholder or alternate
        tooling.
        """
        try:
            import numpy as np
            from obspy import Stream, Trace
            from obspy.core import UTCDateTime
        except ImportError as exc:  # pragma: no cover - runtime optional dependency
            raise RuntimeError("ObsPy is required for MiniSEED output.") from exc

        output_dir = Path(outdir)
        output_dir.mkdir(parents=True, exist_ok=True)
        written: List[str] = []

        window = self.flush_window()
        for channel, values in window.items():
            if not values:
                continue
            data = np.asarray(values, dtype=np.float32)
            stats = {
                "network": network,
                "station": station_name,
                "location": location,
                "channel": f"BH{channel + 1}",
                "npts": len(data),
                "sampling_rate": self.sample_rate_hz,
                "starttime": UTCDateTime(start_time),
                "mseed": {"dataquality": "D"},
            }
            trace = Trace(data=data, header=stats)
            stream = Stream(traces=[trace])
            filename = output_dir / f"{UTCDateTime(start_time).strftime('%Y%m%dT%H%M%S')}_BH{channel + 1}.mseed"
            stream.write(str(filename), format="MSEED")
            written.append(str(filename))
        return written
