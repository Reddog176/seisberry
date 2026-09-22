# Copilot instructions for Seisberry

This repository is a Raspberry Pi seismic monitoring project. Keep changes aligned with the project’s lightweight, hardware-focused design.

## Repository context
- The active project runtime now lives under `streaming/`.
- The historical daily-processing scripts are archived under `legacy/` and should be treated as reference material.
- OpenSCAD files describe the physical support structure for the sensor assembly.
- The notebook remains a useful reference for project documentation and examples.

## Expectations for edits
- Favor small, surgical changes.
- Preserve existing configuration variables and comments when possible.
- Avoid introducing new heavy dependencies unless the task truly requires them.
- Be careful with time-series data processing, file paths, and live acquisition assumptions.

## Validation
Use Python syntax validation after edits when practical:

```bash
python -m compileall .
```

This project is not a large web application; correctness and compatibility matter more than stylistic churn.
