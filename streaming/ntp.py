from __future__ import annotations

import os
import subprocess
from pathlib import Path


class NTPManager:
    """Minimal NTP configuration helper for a Raspberry Pi deployment."""

    def __init__(
        self,
        service_name: str = "systemd-timesyncd",
        enabled: bool = True,
        ntp_servers: str | None = None,
    ) -> None:
        self.service_name = service_name
        self.enabled = bool(enabled)
        self.ntp_servers = ntp_servers or "0.pool.ntp.org 1.pool.ntp.org 2.pool.ntp.org"

    def ensure_config(self) -> bool:
        if not self.enabled:
            return True

        try:
            config_path = Path("/etc/systemd/timesyncd.conf")
            if config_path.exists():
                content = config_path.read_text(encoding="utf-8")
                if "NTP=" in content and self.ntp_servers not in content:
                    lines = content.splitlines()
                    updated = []
                    for line in lines:
                        if line.strip().startswith("NTP="):
                            updated.append(f"NTP={self.ntp_servers}")
                        else:
                            updated.append(line)
                    config_path.write_text("\n".join(updated) + "\n", encoding="utf-8")
                elif "NTP=" not in content:
                    config_path.write_text(content + f"\nNTP={self.ntp_servers}\n", encoding="utf-8")
            else:
                config_path.write_text(f"[Time]\nNTP={self.ntp_servers}\n", encoding="utf-8")
        except OSError:
            return False

        return True

    def enable_service(self) -> bool:
        if not self.enabled:
            return True

        commands = [
            ["sudo", "timedatectl", "set-ntp", "true"],
            ["sudo", "systemctl", "enable", "--now", self.service_name],
        ]
        for command in commands:
            try:
                subprocess.run(command, check=True, capture_output=True, text=True)
            except (FileNotFoundError, subprocess.CalledProcessError):
                return False
        return True
