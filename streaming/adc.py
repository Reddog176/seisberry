from __future__ import annotations

import random
import time
from dataclasses import dataclass
from typing import List, Sequence


@dataclass
class ADCDriver:
    """Minimal ADC abstraction for the Seisberry capture chain.

    The repository already ships a C ADS1256 sampler, and the live path here is
    intentionally designed as a drop-in replacement/fallback when the C sampler is
    not used directly. The default behavior is a local simulator so the Python
    streaming stack is importable and testable on any machine.
    """

    channels: int = 3
    sample_rate_hz: float = 750.0
    use_simulation: bool = True
    _spi = None

    def __post_init__(self) -> None:
        self._last_read = time.monotonic()
        self._sim_offset = [0.0 for _ in range(self.channels)]

    def read_frame(self) -> List[float]:
        """Read one complete frame for the configured number of channels."""
        if self.use_simulation:
            return self._read_simulated_frame()
        return self._read_hardware_frame()

    def _read_simulated_frame(self) -> List[float]:
        frame: List[float] = []
        for idx in range(self.channels):
            noise = random.gauss(0.0, 0.05)
            drift = 0.02 * idx
            self._sim_offset[idx] += 0.001 * random.uniform(-1.0, 1.0)
            value = noise + drift + self._sim_offset[idx]
            frame.append(value)
        self._last_read = time.monotonic()
        return frame

    def _read_hardware_frame(self) -> List[float]:
        try:
            import spidev
        except ImportError as exc:  # pragma: no cover - runtime optional dependency
            raise RuntimeError("SPI ADC support is unavailable; use the simulation mode or install spidev.") from exc

        if self._spi is None:
            self._spi = spidev.SpiDev()
            self._spi.open(0, 0)
            self._spi.max_speed_hz = 1000000

        raw = []
        for _ in range(self.channels):
            try:
                sample = self._spi.readbytes(3)
            except Exception:
                sample = [0, 0, 0]
            raw.append(float(int.from_bytes(bytes(sample), byteorder='big', signed=False) / 8388608.0))
        return raw
