# Instagram Splitter (Local Fullstack Python App)

Upload an image in your browser, split it into tiles, and download tiles for Instagram posting.

## Features

- Upload image from browser
- Split mode: both (grid), vertical, or horizontal
- Split line preview and tile gallery
- Download all tiles as one ZIP
- Select specific tiles and download selected ZIP
- Optional separate file download links per tile
- Quality-preserving split flow (no upscale/resize interpolation)
- Tiles exported as PNG to minimize compression artifacts

## Clean Architecture (Refactor)

Project is now organized so developers can extend features safely:

- app.py: minimal entrypoint
- ig_splitter/config.py: constants and app limits
- ig_splitter/models.py: request/result data models
- ig_splitter/services/image_service.py: splitting and grid logic
- ig_splitter/services/storage_service.py: file persistence and ZIP utilities
- ig_splitter/web/routes.py: Flask routes and request validation
- templates/index.html: UI and interaction flow
- static/style.css: styling and responsive behavior

## Prerequisites

Before running locally, install:

- Python 3.10 or newer (recommended: Python 3.11+)
- pip (comes with Python)
- A terminal (PowerShell on Windows is fine)

Optional but recommended:

- VS Code with Python extension
- Git (for cloning and version control)

Check versions:

```powershell
python --version
pip --version
```

If `python` is not recognized on Windows, try:

```powershell
py --version
```

## Project Setup (First Time)

1. Go to the project folder:

```powershell
cd c:\Users\henry\Desktop\selflearn\python\ig-splitter
```

2. Create virtual environment:

```powershell
python -m venv .venv
```

3. Activate virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, run this once in PowerShell (CurrentUser scope):

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

4. Install dependencies:

```powershell
pip install -r requirements.txt
```

## How To Run Locally

1. Make sure virtual environment is activated.
2. Start the app:

```powershell
python app.py
```

3. Open browser:

- http://127.0.0.1:5000

4. Use the app:

- Upload image
- Choose split mode and grid values
- Process image
- Download all tiles as ZIP or download needed tiles

## Run Without Web UI (CLI)

You can run this project fully from terminal/prompt mode:

```powershell
python -m ig_splitter.cli --input "C:/path/image.jpg" --rows 3 --cols 3 --split-mode both --download-mode zip
```

Examples:

```powershell
python -m ig_splitter.cli --input "C:/path/image.jpg" --split-mode vertical --cols 4 --download-mode zip
python -m ig_splitter.cli --input "C:/path/image.jpg" --split-mode horizontal --rows 5 --download-mode nozip
```

Outputs are generated in `runs/<run_id>/`.

## Agent Skill File

Non-web execution skill for agent workflows is available at:

- `.github/skills/ig-splitter-non-web/SKILL.md`

## Run Tests

After activating `.venv`, run:

```powershell
python -m pytest -q
```

Test coverage includes unit tests for service/helper functions and integration/regression tests for upload, split modes, and download flows.

## Guidelines To Run Python For This Project

- Always run inside virtual environment (`.venv`) so dependency versions stay stable.
- Use `python -m pip install ...` if `pip` command points to wrong Python.
- Keep dependencies in `requirements.txt` updated when adding packages.
- Avoid running with global Python packages for project work.
- Use clear terminal output and stop the server with `Ctrl + C`.
- Keep route handlers thin; put business logic in `ig_splitter/services`.
- Add constants to `ig_splitter/config.py` instead of hardcoding values.
- Prefer typed dataclasses in `ig_splitter/models.py` for data passed to templates.

Recommended commands:

```powershell
python -m pip install -r requirements.txt
python app.py
```

## Troubleshooting

- Port already in use:
	- Stop other process using port 5000 or run with another port by editing app startup.
- Module not found:
	- Activate `.venv`, then reinstall requirements.
- Pillow install problems:
	- Upgrade pip first: `python -m pip install --upgrade pip`
- Browser not opening:
	- Copy and paste URL manually into browser.

## Notes

- Supported image formats: PNG, JPG, JPEG, WEBP
- Split tiles are exported as PNG for better quality retention
- Upload size is not limited by app config
- ZIP downloads store files without deflate compression
- Generated output is saved in `runs/`
