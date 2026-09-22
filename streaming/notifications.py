from __future__ import annotations

import os
from typing import Iterable, List, Optional


class AppriseNotifier:
    """Send alerts through Apprise using a flexible URL list."""

    def __init__(self, urls: Optional[Iterable[str]] = None) -> None:
        self.urls = [str(url).strip() for url in (urls or []) if str(url).strip()]
        env_urls = os.environ.get("SEISBERRY_APPRISE_URLS", "")
        if env_urls:
            for url in env_urls.split(";"):
                if url.strip():
                    self.urls.append(url.strip())

    def is_configured(self) -> bool:
        return bool(self.urls)

    def send(self, title: str, body: str) -> bool:
        if not self.is_configured():
            return False

        try:
            import apprise
        except ImportError:
            print("Apprise is not installed; skipping notification send.")
            return False

        app = apprise.Apprise()
        for url in self.urls:
            app.add(url)

        sent = app.notify(title=title, body=body)
        return bool(sent)
