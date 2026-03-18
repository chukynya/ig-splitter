from __future__ import annotations

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RUNS_DIR = BASE_DIR / "runs"
RUNS_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
ALLOWED_SPLIT_MODES = {"both", "vertical", "horizontal"}
ALLOWED_DOWNLOAD_MODES = {"zip", "nozip"}

DEFAULT_ROWS = 3
DEFAULT_COLS = 3

MAX_UPLOAD_MB = 20
MAX_ROWS_COLS = 10
