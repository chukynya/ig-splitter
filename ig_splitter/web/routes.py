from __future__ import annotations

from flask import Blueprint, abort, render_template, request, send_from_directory

from ig_splitter.config import (
    ALLOWED_DOWNLOAD_MODES,
    ALLOWED_EXTENSIONS,
    ALLOWED_SPLIT_MODES,
    DEFAULT_COLS,
    DEFAULT_ROWS,
    MAX_ROWS_COLS,
    RUNS_DIR,
)
from ig_splitter.models import ProcessOptions, ProcessResult
from ig_splitter.services.image_service import (
    line_positions,
    resolve_grid,
    split_image,
    split_mode_label,
    to_template_result,
)
from ig_splitter.services.storage_service import (
    create_zip,
    make_run_dir,
    read_uploaded_image,
    sanitize_and_filter_tile_names,
    save_original,
    save_tiles,
    selected_zip_name,
)

web_bp = Blueprint("web", __name__)


def _allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def _parse_int(value: str | None, fallback: int, minimum: int, maximum: int) -> int:
    try:
        parsed = int(value) if value is not None else fallback
    except (TypeError, ValueError):
        return fallback
    return max(minimum, min(maximum, parsed))


def _parse_split_mode(value: str | None) -> str:
    if value in ALLOWED_SPLIT_MODES:
        return value
    return "both"


def _parse_download_mode(value: str | None) -> str:
    if value in ALLOWED_DOWNLOAD_MODES:
        return value
    return "zip"


def _build_options() -> ProcessOptions:
    return ProcessOptions(
        rows=_parse_int(request.form.get("rows"), DEFAULT_ROWS, 1, MAX_ROWS_COLS),
        cols=_parse_int(request.form.get("cols"), DEFAULT_COLS, 1, MAX_ROWS_COLS),
        split_mode=_parse_split_mode(request.form.get("split_mode")),
        download_mode=_parse_download_mode(request.form.get("download_mode")),
    )


@web_bp.get("/")
def index():
    return render_template("index.html")


@web_bp.post("/process")
def process_image():
    file = request.files.get("image")
    filename = (file.filename or "") if file is not None else ""

    if file is None or filename == "":
        return render_template("index.html", error="Please choose an image to upload.")

    if not _allowed_file(filename):
        return render_template(
            "index.html",
            error="Unsupported file type. Use PNG, JPG, JPEG, or WEBP.",
        )

    options = _build_options()
    resolved_rows, resolved_cols = resolve_grid(options.rows, options.cols, options.split_mode)

    try:
        source = read_uploaded_image(file)
    except Exception:
        return render_template("index.html", error="Could not read this image file.")

    run_dir = make_run_dir(RUNS_DIR)
    run_id = run_dir.name

    uploaded_name = save_original(source, run_dir, filename)
    tiles = split_image(source, resolved_rows, resolved_cols)
    tile_names = save_tiles(tiles, run_dir, resolved_rows, resolved_cols, options.split_mode)
    zip_name = create_zip(run_dir, tile_names)

    result = ProcessResult(
        run_id=run_id,
        uploaded_name=uploaded_name,
        tile_names=tile_names,
        zip_name=zip_name,
        rows=resolved_rows,
        cols=resolved_cols,
        requested_rows=options.rows,
        requested_cols=options.cols,
        split_mode=options.split_mode,
        split_mode_label=split_mode_label(options.split_mode),
        download_mode=options.download_mode,
        count=len(tile_names),
    )

    return render_template(
        "index.html",
        result=to_template_result(result),
        vertical_lines=line_positions(resolved_cols),
        horizontal_lines=line_positions(resolved_rows),
    )


@web_bp.post("/download-selected-zip")
def download_selected_zip():
    run_id = request.form.get("run_id", "")
    selected_tiles = request.form.getlist("tile")

    if not run_id or not selected_tiles:
        abort(400)

    run_dir = RUNS_DIR / run_id
    if not run_dir.exists():
        abort(404)

    valid_tiles = sanitize_and_filter_tile_names(run_dir, selected_tiles)
    if not valid_tiles:
        abort(400)

    zip_name = create_zip(run_dir, valid_tiles, selected_zip_name())
    return send_from_directory(
        run_dir,
        zip_name,
        as_attachment=True,
        download_name="selected_tiles.zip",
    )


@web_bp.get("/runs/<run_id>/<path:filename>")
def serve_generated_file(run_id: str, filename: str):
    run_dir = RUNS_DIR / run_id
    if not run_dir.exists():
        abort(404)

    as_attachment = request.args.get("download") == "1"
    return send_from_directory(run_dir, filename, as_attachment=as_attachment)
