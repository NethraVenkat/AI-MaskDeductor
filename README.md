 # AI-MaskDeductor

Lightweight Django-based surveillance dashboard for mask detection, crowd analytics, and real-time alerts.

## Overview

- Purpose: Provide a web dashboard that displays a live camera feed, real-time mask detection statistics, alerts, crowd analytics, and historical detections.
- Stack: Django (Python), simple JS frontend for polling API endpoints, optional ML model integration in `detector/mask_detector.py`.

## Features

- Start/stop camera control and video feed endpoint
- Real-time stats: total faces, masked, unmasked, compliance rate
- Alerts feed with severity badges
- Crowd analytics and density indicators
- Detections table with timestamps and risk levels

## Repo layout

- `detector/` — Django app with mask detection logic and API views
- `mask_detection_system/` — Django project settings and URLs
- `templates/` — HTML templates used by the dashboard (index.html, dashboards, planner, replay)
- `manage.py` — Django management script
- `requirements.txt` — Python dependencies
- `verify_setup.py` — small sanity-check script

## Requirements

- Python 3.8+ (3.9/3.10 recommended)
- Virtual environment tooling (venv, virtualenv, conda)
- Dependencies listed in `requirements.txt`

## Quick setup

1. Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1  # PowerShell
# or use `source .venv/bin/activate` on macOS/Linux
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Apply migrations and run the development server:

```powershell
python manage.py migrate
python manage.py runserver
```

4. Open the dashboard in your browser:

- http://127.0.0.1:8000/ (or the configured host)

## Running camera & API

The frontend expects the following endpoints (implemented in the `detector` app):

- `POST /api/start_camera/` — start camera stream and model processing
- `POST /api/stop_camera/` — stop camera stream
- `GET /video_feed/` — MJPEG or image endpoint used by the `<img id="videoFeed">`
- `GET /api/stats/` — returns `{ total_faces, masked_count, unmasked_count, compliance_rate, active_alerts }`
- `GET /api/alerts/?limit=N` — returns recent alerts
- `GET /api/detections/?limit=N` — returns recent detection records
- `GET /api/crowd_analytics/?limit=N` — returns recent crowd analytics

Adjust or inspect `detector/views.py` and `detector/mask_detector.py` to customize camera, model, or data formatting.

## Frontend notes

- The main UI is `templates/index.html` and uses client-side polling (10s interval) to refresh stats and tables.
- Poll interval is controlled by `POLL_INTERVAL_MS` in the inline script.
- The image element `videoFeed` points at `/video_feed/` when active.

## Verify installation

Run `python verify_setup.py` to perform quick checks (Python version, required packages, and basic settings).

## Development tips

- If using a physical camera or RTSP stream, implement or adjust the streaming generator in `detector/views.py`.
- If integrating a dedicated ML model, centralize logic in `detector/mask_detector.py` and keep views thin.
- Use Django's logging to track errors and model inference timing.

## Troubleshooting

- If the dashboard shows `Camera Offline` check backend logs and confirm `/api/start_camera/` returns success.
- If polling returns JSON errors, open browser DevTools Network tab to inspect API responses.

## License & Attribution

This project is provided as-is. Add a license file if you plan to redistribute.

## Contact

For questions or improvements, edit the repo or open an issue in your preferred VCS host.
