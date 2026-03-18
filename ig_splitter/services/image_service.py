from __future__ import annotations

import math
from dataclasses import asdict

from PIL import Image

from ig_splitter.models import ProcessResult


def resolve_grid(rows: int, cols: int, split_mode: str) -> tuple[int, int]:
    if split_mode == "vertical":
        return 1, cols
    if split_mode == "horizontal":
        return rows, 1
    return rows, cols


def crop_to_grid_ratio(img: Image.Image, rows: int, cols: int) -> Image.Image:
    target_ratio = cols / rows
    current_ratio = img.width / img.height

    if math.isclose(current_ratio, target_ratio, rel_tol=1e-6):
        return img

    if current_ratio > target_ratio:
        new_width = int(img.height * target_ratio)
        left = (img.width - new_width) // 2
        return img.crop((left, 0, left + new_width, img.height))

    new_height = int(img.width / target_ratio)
    top = (img.height - new_height) // 2
    return img.crop((0, top, img.width, top + new_height))


def split_image(img: Image.Image, rows: int, cols: int) -> list[Image.Image]:
    grid_ready = img

    width = grid_ready.width - (grid_ready.width % cols)
    height = grid_ready.height - (grid_ready.height % rows)

    # Keep pixels sharp by center-cropping to divisible dimensions instead of resizing.
    left = (grid_ready.width - width) // 2
    top = (grid_ready.height - height) // 2
    grid_ready = grid_ready.crop((left, top, left + width, top + height))

    tile_w = width // cols
    tile_h = height // rows

    tiles: list[Image.Image] = []
    for row in range(rows):
        for col in range(cols):
            left = col * tile_w
            top = row * tile_h
            tiles.append(grid_ready.crop((left, top, left + tile_w, top + tile_h)))
    return tiles


def line_positions(count: int) -> list[float]:
    if count <= 1:
        return []
    step = 100.0 / count
    return [round(step * i, 2) for i in range(1, count)]


def split_mode_label(split_mode: str) -> str:
    labels = {
        "both": "Both (Grid)",
        "vertical": "Vertical",
        "horizontal": "Horizontal",
    }
    return labels[split_mode]


def to_template_result(result: ProcessResult) -> dict[str, object]:
    return asdict(result)
