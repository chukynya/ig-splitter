# IG Splitter Recap (Context-Light)

## 1) What This Project Is

Local Python app that splits one image into Instagram-style tiles.

- Web app: Flask UI for upload, split preview, and downloads.
- Non-web app: CLI entrypoint for automation/chat/bot workflows.
- Focus: split-only pipeline with quality-preserving behavior.

## 2) Current Product Behavior (Important)

- Supports split modes: `both` (grid), `vertical`, `horizontal`.
- Supports custom rows/cols.
- Provides real-time split-line preview in UI.
- Exports tiles as PNG to reduce compression artifacts.
- Allows:
  - download all tiles as ZIP
  - select tiles and download selected ZIP
  - per-tile direct download links

## 3) What Was Intentionally Removed

These features are intentionally removed from runtime logic:

- Upscale
- Enhance
- Any enhancement-only output artifact

Do not re-add unless explicitly requested.

## 4) Quality Rules (Core)

- Split path avoids interpolation resize during tile generation.
- Tiles are saved as lossless PNG.
- Pipeline aims to avoid introducing extra blur/pixelation.

Note: low-detail source images cannot be magically improved; system is designed to avoid making them worse.

## 5) Main Architecture

- `app.py`: thin entrypoint.
- `ig_splitter/__init__.py`: Flask app factory.
- `ig_splitter/config.py`: constants/defaults.
- `ig_splitter/models.py`: dataclasses for options/result.
- `ig_splitter/web/routes.py`: HTTP routes + request validation.
- `ig_splitter/services/image_service.py`: split/grid logic.
- `ig_splitter/services/storage_service.py`: file save/zip helpers.
- `ig_splitter/cli.py`: non-web runner.
- `templates/index.html`: UI + live preview script.
- `static/style.css`: styling.
- `tests/`: unit + integration/regression tests.

## 6) Key Routes / Interfaces

### Web

- `GET /`: main page
- `POST /process`: split image
- `POST /download-selected-zip`: zip selected tiles
- `GET /runs/<run_id>/<filename>`: serve generated files

### CLI

```powershell
python -m ig_splitter.cli --input "C:/path/image.jpg" --rows 3 --cols 3 --split-mode both --download-mode zip
```

## 7) Run + Verify

```powershell
# activate env first
python app.py
python -m pytest -q
```

## 8) Output / Storage

- Generated artifacts go to `runs/<run_id>/`.
- Typical outputs:
  - uploaded preview image
  - tile PNG files
  - ZIP archive(s)

## 9) Guardrails For Future Prompts

- Keep route handlers thin; logic stays in services.
- Preserve split-only behavior unless user explicitly asks otherwise.
- Keep PNG tile output unless user requests a different format.
- Update tests whenever behavior changes.
- Keep docs (`README.md`, skill docs) in sync with behavior changes.

## 10) Quick Prompt Starters

Use these short prompts to continue work without large context:

- "Add feature X while preserving split-only PNG quality pipeline."
- "Refactor service Y, keep routes thin and tests green."
- "Extend CLI for X, update docs/tests accordingly."
- "Do a review for regressions in split modes and downloads."
