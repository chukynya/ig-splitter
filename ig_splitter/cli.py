from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image

from ig_splitter.config import (
    ALLOWED_SPLIT_MODES,
    DEFAULT_COLS,
    DEFAULT_ROWS,
    RUNS_DIR,
)
from ig_splitter.services.image_service import resolve_grid, split_image
from ig_splitter.services.storage_service import create_zip, make_run_dir, save_original, save_tiles


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Instagram image splitter CLI")
    parser.add_argument("--input", required=True, help="Path to source image")
    parser.add_argument("--rows", type=int, default=DEFAULT_ROWS, help="Rows for split")
    parser.add_argument("--cols", type=int, default=DEFAULT_COLS, help="Columns for split")
    parser.add_argument(
        "--split-mode",
        default="both",
        choices=sorted(ALLOWED_SPLIT_MODES),
        help="Split mode: both, vertical, horizontal",
    )
    parser.add_argument(
        "--download-mode",
        default="zip",
        choices=["zip", "nozip"],
        help="zip creates a single archive, nozip skips archive creation",
    )
    parser.add_argument(
        "--output-root",
        default=str(RUNS_DIR),
        help="Output folder for generated run directories",
    )
    return parser


def validate_arg(value: int, minimum: int, maximum: int, name: str) -> int:
    if value < minimum:
        raise ValueError(f"{name} must be >= {minimum}")
    if value > maximum:
        raise ValueError(f"{name} must be <= {maximum}")
    return value


def run_cli(
    input_path: Path,
    rows: int,
    cols: int,
    split_mode: str,
    download_mode: str,
    output_root: Path,
) -> dict[str, object]:
    if not input_path.exists() or not input_path.is_file():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    rows = validate_arg(rows, 1, 10, "rows")
    cols = validate_arg(cols, 1, 10, "cols")

    source = Image.open(input_path)
    output_root.mkdir(parents=True, exist_ok=True)
    run_dir = make_run_dir(output_root)

    uploaded_name = save_original(source, run_dir, input_path.name)
    resolved_rows, resolved_cols = resolve_grid(rows, cols, split_mode)
    tiles = split_image(source, rows=resolved_rows, cols=resolved_cols)
    tile_names = save_tiles(tiles, run_dir, resolved_rows, resolved_cols, split_mode)

    zip_name = None
    if download_mode == "zip":
        zip_name = create_zip(run_dir, tile_names)

    return {
        "run_dir": str(run_dir),
        "uploaded_name": uploaded_name,
        "tile_count": len(tile_names),
        "zip_name": zip_name,
        "tiles": tile_names,
        "rows": resolved_rows,
        "cols": resolved_cols,
        "split_mode": split_mode,
    }


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    result = run_cli(
        input_path=Path(args.input),
        rows=args.rows,
        cols=args.cols,
        split_mode=args.split_mode,
        download_mode=args.download_mode,
        output_root=Path(args.output_root),
    )

    print("Done")
    print(f"Output: {result['run_dir']}")
    print(f"Split: {result['split_mode']} ({result['rows']} x {result['cols']})")
    print(f"Tiles: {result['tile_count']}")
    if result["zip_name"] is not None:
        print(f"ZIP: {result['zip_name']}")


if __name__ == "__main__":
    main()
