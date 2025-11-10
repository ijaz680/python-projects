# TimeTrackr — Productivity Tracker

Lightweight Windows active-window tracker that records how much time you spend per application (optionally by window title), can export CSV reports, and can generate a matplotlib plot.

Requirements
- Python 3.8+
- See `requirements.txt` for dependencies: `psutil`, `pywin32`, `matplotlib`.

Install

1. Create and activate a virtual environment (PowerShell):

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Quick demo

```powershell
python demo.py
```

CLI usage

```powershell
python cli.py --duration 120 --interval 1 --csv report.csv --plot report.png
```

Notes
- The tracker polls the active window every `interval` seconds and accumulates time to the previous active app. It works on Windows only (uses Win32 APIs).
- For long-running usage you might want to run the CLI in the background or convert it into a system tray app.

License: MIT
