# Seisberry live streaming stack

This directory contains the active Seisberry runtime path. It replaces the old daily batch workflow with a continuous acquisition model designed for Raspberry Pi deployment.

## Components

- `adc.py`: low-level ADC abstraction with a simulator fallback for local testing.
- `ring_buffer.py`: rolling buffer and one-minute MiniSEED packet writing.
- `trigger.py`: real-time STA/LTA event detection.
- `seedlink_server.py`: SeedLink bridge for optional live distribution.
- `watchdog.py`: health monitor for sample gaps, disk space, and CPU load.
- `ntp.py`: lightweight NTP config helper for Raspberry Pi time sync.
- `notifications.py`: generic Apprise notifier for alerts.
- `helicorder.py`: SVG helicorder preview generation.
- `live_sampler.py`: capture loop that reads ADC data, buffers it, writes packets, refreshes a helicorder, and runs health checks.
- `web_server.py`: serves the live dashboard, helicorder image, and station status JSON.
- `dashboard.py`: starts the sampler together with the browser dashboard.
- `config.toml`: external configuration for station, stream, watchdog, NTP, and alert settings.

## Intended flow

1. Read live ADC samples on the Raspberry Pi.
2. Append them to a short rolling buffer.
3. Every minute, flush the current window and write MiniSEED files.
4. Apply STA/LTA triggering to detect local events in real time.
5. Refresh an SVG helicorder image for browser-based observing.
6. Run watchdog health checks on timing, disk capacity, and CPU load.
7. Send alerts via Apprise if the station drifts out of tolerance.
8. Optionally publish to SeedLink or a ringserver for standard seismic clients.

## Deployment notes

This is the default project path for new installs. The historical daily batch scripts are archived under [legacy](../legacy) and are no longer the active deployment model.

Use a 64-bit Raspberry Pi OS image for the live runtime. The project deliberately rejects 32-bit installs because the live path is designed around the newer 64-bit acquisition stack and removes the older memory workaround assumptions.

For a fresh Pi image, leave `simulate_adc = false` in [config.toml](config.toml). Set it to `true` only for local development or CI test runs where you do not want to touch the ADC hardware.

The live pipeline is designed to be operationally resilient:

```toml
[watchdog]
enabled = true
max_sample_gap_seconds = 30.0
min_free_disk_gb = 2.0
max_cpu_load = 2.5
alert_cooldown_seconds = 300.0

[ntp]
enabled = true
servers = "0.pool.ntp.org 1.pool.ntp.org 2.pool.ntp.org"

[notifications]
aps = [
  "discord://token@channel",
  "mailto://user@example.com"
]
```

Apprise can target many notification systems through URL strings, so this avoids tying the project to a single vendor-specific alert service.

SeedLink remains optional and disabled by default in [config.toml](config.toml). Set `seedlink_enabled = true` only when you are ready to publish live traces to a SeedLink target or ringserver.

The dashboard exposes the station health on the status endpoint:

```text
http://<pi-host>:8080/status
```

This JSON payload provides the current health summary for the local station.
