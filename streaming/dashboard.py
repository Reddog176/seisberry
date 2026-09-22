from __future__ import annotations

import threading
from pathlib import Path

from .live_sampler import LiveSeisberrySampler
from .web_server import serve_web_ui


class LiveDashboard:
    """Runs the live sampler and serves a simple browser dashboard."""

    def __init__(self, sampler: LiveSeisberrySampler) -> None:
        self.sampler = sampler

    def start(self) -> None:
        self.server_thread = threading.Thread(target=serve_web_ui, args=("0.0.0.0", 8080), daemon=True)
        self.server_thread.start()
        self.sampler.run()
