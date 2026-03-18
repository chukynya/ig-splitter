from __future__ import annotations

import io
from pathlib import Path

from PIL import Image
from werkzeug.datastructures import FileStorage

from ig_splitter.services.storage_service import (
    create_zip,
    make_run_dir,
    read_uploaded_image,
    sanitize_and_filter_tile_names,
    save_original,
    save_tiles,
    selected_zip_name,
    tile_filename,
)


def test_make_run_dir_creates_unique_folder(tmp_path: Path) -> None:
    run1 = make_run_dir(tmp_path)
    run2 = make_run_dir(tmp_path)
    assert run1.exists()
    assert run2.exists()
    assert run1 != run2


def test_read_uploaded_image_opens_valid_image() -> None:
    image = Image.new("RGB", (10, 10), color=(255, 0, 0))
    data = io.BytesIO()
    image.save(data, format="PNG")
    data.seek(0)

    upload = FileStorage(stream=data, filename="sample.png", content_type="image/png")
    opened = read_uploaded_image(upload)
    assert opened.size == (10, 10)


def test_save_original(tmp_path: Path) -> None:
    image = Image.new("RGB", (24, 24), color=(1, 2, 3))
    uploaded_name = save_original(image, tmp_path, "input file.png")

    assert (tmp_path / uploaded_name).exists()


def test_tile_filename_for_modes() -> None:
    assert tile_filename(0, rows=2, cols=3, split_mode="both") == "tile_r1_c1.png"
    assert tile_filename(2, rows=1, cols=3, split_mode="vertical") == "tile_v3.png"
    assert tile_filename(1, rows=3, cols=1, split_mode="horizontal") == "tile_h2.png"


def test_save_tiles_and_create_zip(tmp_path: Path) -> None:
    tiles = [Image.new("RGB", (20, 20), color=(i, i, i)) for i in range(4)]
    names = save_tiles(tiles, tmp_path, rows=2, cols=2, split_mode="both")
    assert len(names) == 4
    assert all((tmp_path / name).exists() for name in names)

    zip_name = create_zip(tmp_path, names)
    assert (tmp_path / zip_name).exists()


def test_sanitize_and_filter_tile_names(tmp_path: Path) -> None:
    valid_file = tmp_path / "tile_r1_c1.png"
    valid_file.write_bytes(b"x")

    selected = ["tile_r1_c1.png", "../evil.jpg", "", "missing.jpg"]
    filtered = sanitize_and_filter_tile_names(tmp_path, selected)
    assert filtered == ["tile_r1_c1.png"]


def test_selected_zip_name_prefix() -> None:
    name = selected_zip_name()
    assert name.startswith("selected_tiles_")
    assert name.endswith(".zip")
