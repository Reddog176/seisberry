# AGENTS.md

## Repository overview
This repository is now centered on the Seisberry live-streaming architecture. The active runtime path is a continuous Raspberry Pi acquisition pipeline that buffers samples, writes short MiniSEED windows, runs live triggers, and serves a helicorder dashboard.

## Primary file groups
- `streaming/`: active live acquisition and visualization stack; this is the default project path.
- `legacy/`: archived historical batch-processing scripts retained for reference only.
- `*.scad`: OpenSCAD models for the seismometer support hardware.
- `seisberry.ipynb`: notebook with project documentation and analysis examples.

## Working conventions
- Keep changes small and compatible with Python 3.
- Prefer minimal dependency additions. The project relies on scientific Python tooling (`numpy`, `obspy`, `requests`) and Raspberry Pi conventions.
- Treat the live streaming workflow as the supported default for all new work.
- The old daily batch scripts are intentionally archived and should not be used as the primary path unless explicitly debugging historical behavior.
- When editing acquisition or processing code, prefer direct, readable logic over heavy refactors.

## Validation
Before finishing work, run the most relevant validation available for the changed behavior. For Python code, a good baseline is:

```bash
python -m compileall .
```

This is a lightweight verification step for syntax errors without requiring the full seismograph runtime.

## Notes for future agents
- The project is scientific and hardware-oriented; be careful with time-series and file path logic.
- Document any new configuration parameters near the top of the relevant script.
- If a task touches Raspberry-specific assumptions, explain the impact on Pi deployment in the summary.
