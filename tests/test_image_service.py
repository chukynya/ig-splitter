from __future__ import annotations

from PIL import Image

from ig_splitter.models import ProcessResult
from ig_splitter.services.image_service import (
    crop_to_grid_ratio,
    line_positions,
    resolve_grid,
    split_image,
    split_mode_label,
    to_template_result,
)


def test_resolve_grid_handles_all_modes() -> None:
    assert resolve_grid(3, 4, "both") == (3, 4)
    assert resolve_grid(3, 4, "vertical") == (1, 4)
    assert resolve_grid(3, 4, "horizontal") == (3, 1)


def test_crop_to_grid_ratio_matches_target_ratio() -> None:
    source = Image.new("RGB", (300, 100), color=(1, 2, 3))
    cropped = crop_to_grid_ratio(source, rows=2, cols=2)
    assert cropped.width == cropped.height


def test_split_image_returns_expected_count_and_tile_size() -> None:
    source = Image.new("RGB", (300, 200), color=(2, 3, 4))
    tiles = split_image(source, rows=2, cols=3)
    assert len(tiles) == 6
    assert all(tile.size == (100, 100) for tile in tiles)


def test_split_image_preserves_height_for_1x3_grid() -> None:
    source = Image.new("RGB", (3240, 1350), color=(2, 3, 4))
    tiles = split_image(source, rows=1, cols=3)
    assert len(tiles) == 3
    assert all(tile.size == (1080, 1350) for tile in tiles)


def test_line_positions_returns_even_boundaries() -> None:
    assert line_positions(1) == []
    assert line_positions(4) == [25.0, 50.0, 75.0]


def test_split_mode_label_mappings() -> None:
    assert split_mode_label("both") == "Both (Grid)"
    assert split_mode_label("vertical") == "Vertical"
    assert split_mode_label("horizontal") == "Horizontal"


def test_to_template_result_serializes_dataclass() -> None:
    result = ProcessResult(
        run_id="run123",
        uploaded_name="uploaded.png",
        tile_names=["tile_1.png"],
        zip_name="tiles.zip",
        rows=1,
        cols=1,
        requested_rows=1,
        requested_cols=1,
        split_mode="both",
        split_mode_label="Both (Grid)",
        download_mode="zip",
        count=1,
    )

    payload = to_template_result(result)
    assert payload["run_id"] == "run123"
    assert payload["tile_names"] == ["tile_1.png"]
