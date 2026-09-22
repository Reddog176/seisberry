# Seisberry

Seisberry is a three-component Raspberry Pi seismic monitoring project built around a live streaming architecture: rolling data buffers, short MiniSEED packet output, live STA/LTA triggering, and a browser-based helicorder dashboard.

![Seisberry](seisberry.jpg)

## Active project direction

The active runtime for this repository is the live streaming workflow under [streaming](streaming). The historical daily-processing scripts have been archived under [legacy](legacy) for reference only and are no longer the supported deployment path.

## Live streaming architecture

The live system is organized under [streaming](streaming):

- [streaming/adc.py](streaming/adc.py): ADC abstraction with a simulator fallback for development and CI
- [streaming/ring_buffer.py](streaming/ring_buffer.py): rolling window buffer and MiniSEED packet flushing
- [streaming/live_sampler.py](streaming/live_sampler.py): capture loop for the live stream
- [streaming/trigger.py](streaming/trigger.py): real-time STA/LTA triggering
- [streaming/helicorder.py](streaming/helicorder.py): rolling helicorder SVG output
- [streaming/web_server.py](streaming/web_server.py): lightweight web dashboard for the live view
- [streaming/config.toml](streaming/config.toml): external station and stream settings
- [streaming/systemd/seisberry-live.service](streaming/systemd/seisberry-live.service): systemd service for Raspberry Pi deployment

For implementation notes and usage guidance, see [streaming/README.md](streaming/README.md).

## Fresh Pi setup

A bootstrap script is included for a new Raspberry Pi OS image:

- [setup_pi.sh](setup_pi.sh)

This installs Python, creates a venv, installs required packages, copies the repo into place, and enables the live service.

### Raspberry Pi requirements

Use a 64-bit Raspberry Pi OS image. The live stack explicitly rejects 32-bit runtimes because the current acquisition model assumes the newer 64-bit runtime and no longer relies on the older memory workaround assumptions.

### Typical installation flow

```bash
chmod +x setup_pi.sh
./setup_pi.sh
```

Then edit [streaming/config.toml](streaming/config.toml) and set:

```toml
[streaming]
simulate_adc = false
require_64bit = true
```

The runtime also supports operational monitoring and notifications:

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

The Apprise list is generic, so you can use Telegram, Discord, email, Slack, or other supported targets without committing to a single service.

On the Pi, the live service is started through systemd and can be inspected with:

```bash
sudo systemctl status seisberry-live.service
journalctl -u seisberry-live.service -f
```

The live helicorder dashboard is served on port 8080, and the health endpoint is available at:

```text
http://pi-host:8080/status
```

This returns a JSON summary of the current watchdog health and the live station state.

## Archived reference material

The older batch-processing scripts are retained only for historical comparison and debugging work:

- [legacy/README.md](legacy/README.md)
- [legacy/Pi_Daily_processing.py](legacy/Pi_Daily_processing.py)
- [legacy/Pi_Daily_clean.py](legacy/Pi_Daily_clean.py)
- [legacy/Daily_processing_v2_0_0.py](legacy/Daily_processing_v2_0_0.py)
- [legacy/SEGY_output.py](legacy/SEGY_output.py)
- [legacy/Pi_Make_gallery.py](legacy/Pi_Make_gallery.py)

These files are intentionally not part of the supported runtime.

## C code and hardware notes

For the original ADS1256 capture work and hardware references, see the original project notes and the C sampler references linked from the historic project documentation.

## Project references

- Original build guide: https://erellaz.com/blog/seisberry/seisberry-fast-build/
- Help and installation guide: http://erellaz.com/seisberry
- Jupyter notebook reference: https://github.com/erellaz/seisberry/blob/master/seisberry.ipynb

## Notes for maintainers

- Prefer the live streaming workflow for all new deployments.
- Treat the archived batch scripts as historical reference material only.
- Keep station configuration in [streaming/config.toml](streaming/config.toml) rather than hardcoding values in multiple scripts.
- Use the live service for near-real-time monitoring, triggers, and web-based visualization.

