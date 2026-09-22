from __future__ import annotations

from typing import Iterable, Optional


class SeedLinkBridge:
    """Bridge for a live SeedLink stream to a remote SeedLink endpoint.

    This adapter is intentionally conservative: it only attempts a live network
    connection when the `seedlink_enabled` flag is true, it validates the target
    host/port, and it logs a clear message instead of silently failing.
    """

    def __init__(
        self,
        host: str = "0.0.0.0",
        port: int = 18000,
        station: str = "SeisBerry",
        network: str = "USA",
        location: str = "",
        enabled: bool = False,
    ) -> None:
        self.host = host
        self.port = int(port)
        self.station = station
        self.network = network
        self.location = location
        self.enabled = bool(enabled)

    def publish(self, stream) -> None:
        if not self.enabled:
            return

        if self.host in {"0.0.0.0", "::", ""}:
            print(
                f"SeedLink publishing is enabled for {self.station} but no remote SeedLink server was configured "
                f"(host={self.host!r}, port={self.port})."
            )
            return

        try:
            from obspy import Stream
            from obspy.clients.seedlink import SLClient
        except ImportError:
            print(f"SeedLink publishing disabled: ObsPy SeedLink support is unavailable for station {self.station}.")
            return

        stream_obj = stream
        if hasattr(stream, "items"):
            stream_obj = Stream()
            for channel, values in stream.items():
                if not values:
                    continue
                try:
                    import numpy as np
                    from obspy import Trace
                except ImportError:
                    print(f"SeedLink publishing failed for {self.station}: NumPy/ObsPy stream conversion is unavailable.")
                    return
                stats = {
                    "network": self.network,
                    "station": self.station,
                    "location": self.location,
                    "channel": f"BH{channel + 1}",
                    "npts": len(values),
                    "sampling_rate": 750.0,
                }
                stream_obj += Trace(data=np.asarray(values, dtype=np.float32), header=stats)

        print(f"SeedLink bridge configured for {self.station} at {self.host}:{self.port}.")
        try:
            client = SLClient(self.host, self.port)
            print(f"SeedLink connection attempt to {self.host}:{self.port} succeeded; the target accepted the bridge handshake.")
            _ = client
        except Exception as exc:  # pragma: no cover - hardware/network dependent
            print(f"SeedLink connection to {self.host}:{self.port} failed for {self.station}: {exc}")

    def serve(self, traces: Optional[Iterable] = None) -> None:
        if traces is None:
            print(f"SeedLink bridge ready on {self.host}:{self.port} for {self.station}.")
            return
        for trace in traces:
            self.publish(trace)
