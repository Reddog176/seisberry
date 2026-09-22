from __future__ import annotations

from typing import List, Tuple


def detect_events(data, sample_rate_hz: float, sta_seconds: float = 5.0, lta_seconds: float = 30.0,
                  on_threshold: float = 5.0, off_threshold: float = 2.5) -> List[Tuple[int, int]]:
    """Return trigger windows using the classic STA/LTA algorithm.

    This is a lightweight real-time event detection feature that can replace the
    repository's current post-facto "USGS said something happened" workflow.
    """
    try:
        import numpy as np
        from obspy.signal.trigger import classic_sta_lta, trigger_onset
    except ImportError as exc:  # pragma: no cover - runtime optional dependency
        raise RuntimeError("ObsPy is required for real-time triggering.") from exc

    if len(data) < 2:
        return []

    data_array = np.asarray(data, dtype=np.float32)
    sta_samples = max(1, int(sta_seconds * sample_rate_hz))
    lta_samples = max(1, int(lta_seconds * sample_rate_hz))
    cft = classic_sta_lta(data_array, sta_samples, lta_samples)
    trigger_indexes = trigger_onset(cft, on_threshold, off_threshold)
    return [(int(start), int(end)) for start, end in trigger_indexes]
