from __future__ import annotations

import os
from pathlib import Path

from .adc import ADCDriver
from .config_loader import load_config
from .dashboard import LiveDashboard
from .live_sampler import LiveSeisberrySampler
from .notifications import AppriseNotifier
from .ntp import NTPManager
from .platform import assert_64bit_runtime, write_runtime_notice
from .seedlink_server import SeedLinkBridge
from .watchdog import StationWatchdog


def main() -> None:
    config_path = Path(os.environ.get("SEISBERRY_CONFIG", "streaming/config.toml")).resolve()
    config = load_config(config_path)

    station_cfg = config.get("station", {})
    stream_cfg = config.get("streaming", {})
    watchdog_cfg = config.get("watchdog", {})
    ntp_cfg = config.get("ntp", {})
    notifications_cfg = config.get("notifications", {})

    ntp_manager = NTPManager(
        enabled=bool(ntp_cfg.get("enabled", True)),
        ntp_servers=str(ntp_cfg.get("servers", "0.pool.ntp.org 1.pool.ntp.org 2.pool.ntp.org")),
    )
    ntp_manager.ensure_config()
    ntp_manager.enable_service()

    notifier = AppriseNotifier(urls=notifications_cfg.get("aps", []))

    watchdog = StationWatchdog(
        max_sample_gap_seconds=float(watchdog_cfg.get("max_sample_gap_seconds", 30.0)),
        min_free_disk_gb=float(watchdog_cfg.get("min_free_disk_gb", 2.0)),
        max_cpu_load=float(watchdog_cfg.get("max_cpu_load", 2.5)),
        alert_cooldown_seconds=float(watchdog_cfg.get("alert_cooldown_seconds", 300.0)),
        enabled=bool(watchdog_cfg.get("enabled", True)),
    )

    adc = ADCDriver(
        channels=int(station_cfg.get("channels", 3)),
        sample_rate_hz=float(station_cfg.get("sample_rate_hz", 750.0)),
        use_simulation=bool(stream_cfg.get("simulate_adc", True)),
    )

    seedlink_bridge = SeedLinkBridge(
        host=str(stream_cfg.get("seedlink_host", "0.0.0.0")),
        port=int(stream_cfg.get("seedlink_port", 18000)),
        station=str(station_cfg.get("station", "SeisBerry")),
        network=str(station_cfg.get("network", "USA")),
        location=str(station_cfg.get("location", "")),
        enabled=bool(stream_cfg.get("seedlink_enabled", False)),
    )

    sampler = LiveSeisberrySampler(
        adc=adc,
        sample_rate_hz=float(station_cfg.get("sample_rate_hz", 750.0)),
        channels=int(station_cfg.get("channels", 3)),
        window_seconds=float(stream_cfg.get("window_seconds", 60.0)),
        miniseed_dir=stream_cfg.get("miniseed_dir", "data/miniseed"),
        helicorder_dir=stream_cfg.get("helicorder_dir", "data/helicorder"),
        station_name=str(station_cfg.get("station", "SeisBerry")),
        network=str(station_cfg.get("network", "USA")),
        location=str(station_cfg.get("location", "")),
        seedlink_bridge=seedlink_bridge,
    )

    sampler.watchdog = watchdog
    sampler.notifier = notifier

    print(write_runtime_notice())
    try:
        assert_64bit_runtime()
    except RuntimeWarning as exc:
        print(f"Warning: {exc}")

    print(f"Starting Seisberry live sampler for {sampler.station_name}")
    dashboard = LiveDashboard(sampler)
    dashboard.start()


if __name__ == "__main__":
    main()
