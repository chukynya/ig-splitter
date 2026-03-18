from __future__ import annotations

import io
import uuid
from datetime import datetime
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from PIL import Image
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename


def make_run_dir(runs_dir: Path) -> Path:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_id = f"{stamp}_{uuid.uuid4().hex[:8]}"
    run_dir = runs_dir / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def read_uploaded_image(upload: FileStorage) -> Image.Image:
    return Image.open(io.BytesIO(upload.read()))


def save_original(source: Image.Image, run_dir: Path, original_name: str) -> str:
    base_name = Path(secure_filename(original_name) or "upload").stem
    uploaded_name = f"uploaded_{base_name}.png"
    source.convert("RGB").save(run_dir / uploaded_name, format="PNG", optimize=True)
    return uploaded_name


def tile_filename(index: int, rows: int, cols: int, split_mode: str) -> str:
    row = index // cols + 1
    col = index % cols + 1

    if split_mode == "vertical":
        return f"tile_v{col}.png"
    if split_mode == "horizontal":
        return f"tile_h{row}.png"
    return f"tile_r{row}_c{col}.png"


def save_tiles(tiles: list[Image.Image], run_dir: Path, rows: int, cols: int, split_mode: str) -> list[str]:
    names: list[str] = []
    for index, tile in enumerate(tiles):
        name = tile_filename(index, rows, cols, split_mode)
        tile.convert("RGB").save(run_dir / name, format="PNG", optimize=True)
        names.append(name)
    return names


def create_zip(run_dir: Path, tile_names: list[str], zip_name: str = "instagram_tiles.zip") -> str:
    zip_path = run_dir / zip_name
    with ZipFile(zip_path, "w", compression=ZIP_DEFLATED) as zip_file:
        for tile_name in tile_names:
            zip_file.write(run_dir / tile_name, arcname=tile_name)
    return zip_name


def sanitize_and_filter_tile_names(run_dir: Path, selected_tiles: list[str]) -> list[str]:
    valid_tiles: list[str] = []
    for name in selected_tiles:
        if not name or "/" in name or "\\" in name:
            continue
        tile_path = run_dir / name
        if tile_path.exists() and tile_path.is_file():
            valid_tiles.append(name)
    return valid_tiles


def selected_zip_name() -> str:
    return f"selected_tiles_{uuid.uuid4().hex[:6]}.zip"
