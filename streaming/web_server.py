from __future__ import annotations

import html
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Optional


class HelicolorderHTTPHandler(BaseHTTPRequestHandler):
    """Serve the live helicorder SVG and a simple dashboard page."""

    def do_GET(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
        root = Path(os.environ.get("SEISBERRY_HELICORDER_DIR", "data/helicorder")).resolve()
        image_path = root / "helicorder.svg"

        if self.path in ("/", "/index.html"):
            page = self._dashboard_html()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(page.encode("utf-8"))))
            self.end_headers()
            self.wfile.write(page.encode("utf-8"))
            return

        if self.path == "/helicorder.svg":
            if image_path.exists():
                payload = image_path.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "image/svg+xml")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
                return

            self.send_response(404)
            self.end_headers()
            return

        if self.path == "/status":
            payload = json.dumps(self._status_payload()).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return

        self.send_response(404)
        self.end_headers()

    def _status_payload(self) -> dict:
        status = {
            "station": os.environ.get("SEISBERRY_STATION", "SeisBerry"),
            "healthy": True,
            "watchdog_enabled": True,
            "sample_gap_seconds": None,
            "disk_free_gb": None,
            "cpu_load": None,
            "message": "watchdog not configured",
        }

        watchdog = os.environ.get("SEISBERRY_WATCHDOG_STATUS")
        if watchdog:
            try:
                status.update(json.loads(watchdog))
            except json.JSONDecodeError:
                pass
        return status

    def _dashboard_html(self) -> str:
        title = html.escape(os.environ.get("SEISBERRY_STATION", "SeisBerry"))
        return f"""
<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <meta http-equiv="refresh" content="10" />
    <title>{title} helicorder</title>
    <style>
      body {{ font-family: sans-serif; background: #10151b; color: #e7edf3; margin: 0; padding: 24px; }}
      .panel {{ max-width: 1300px; margin: 0 auto; background: #1a2430; border-radius: 10px; padding: 16px; box-shadow: 0 10px 22px rgba(0,0,0,0.25); }}
      img {{ width: 100%; height: auto; border-radius: 8px; background: #fff; }}
      h1 {{ margin-top: 0; }}
      .status {{ margin-top: 16px; padding: 12px 14px; border-radius: 8px; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); }}
      .ok {{ color: #8fe3b1; }}
      .warn {{ color: #ffcb7d; }}
      .bad {{ color: #ff9a9a; }}
    </style>
  </head>
  <body>
    <div class="panel">
      <h1>{title} live helicorder</h1>
      <div id="status" class="status"><strong>Loading station status…</strong></div>
      <img src="/helicorder.svg" alt="Live helicorder" />
    </div>
    <script>
      async function loadStatus() {{
        try {{
          const res = await fetch('/status');
          const data = await res.json();
          const panel = document.getElementById('status');
          const ok = data.healthy === true;
          panel.className = 'status ' + (ok ? 'ok' : 'bad');
          panel.innerHTML = '<strong>Station:</strong> ' + data.station + ' &nbsp;|&nbsp; <strong>Health:</strong> ' + (ok ? 'healthy' : 'degraded') + ' &nbsp;|&nbsp; <strong>Message:</strong> ' + (data.message || 'n/a');
          if (data.sample_gap_seconds !== null) panel.innerHTML += ' &nbsp;|&nbsp; <strong>Gap:</strong> ' + data.sample_gap_seconds.toFixed(1) + 's';
        }} catch (error) {{
          document.getElementById('status').className = 'status warn';
          document.getElementById('status').innerHTML = '<strong>Station status unavailable</strong>';
        }}
      }}
      loadStatus();
      setInterval(loadStatus, 15000);
    </script>
  </body>
</html>
"""

    def log_message(self, format: str, *args) -> None:  # noqa: A003 - override required signature
        return


def serve_web_ui(host: str = "0.0.0.0", port: int = 8080, bind_and_serve: bool = True) -> Optional[ThreadingHTTPServer]:
    if not bind_and_serve:
        return None

    server = ThreadingHTTPServer((host, port), HelicolorderHTTPHandler)
    print(f"Serving Seisberry helicorder dashboard on http://{host}:{port}")
    server.serve_forever()
    return server


if __name__ == "__main__":
    serve_web_ui()
