from __future__ import annotations

import io
import re
from pathlib import Path


def _multipart_image(sample_image_bytes: bytes, name: str = "sample.png"):
    return (io.BytesIO(sample_image_bytes), name)


def _latest_run_dir(temp_runs_dir: Path) -> Path:
    run_dirs = sorted([path for path in temp_runs_dir.iterdir() if path.is_dir()])
    assert run_dirs, "No run directory created"
    return run_dirs[-1]


def _extract_run_id(html: str) -> str:
    match = re.search(r'name="run_id" value="([^"]+)"', html)
    assert match is not None
    return match.group(1)


def test_index_page_renders(client) -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert b"Instagram Splitter" in response.data


def test_process_image_grid_mode(client, sample_image_bytes, temp_runs_dir: Path) -> None:
    response = client.post(
        "/process",
        data={
            "image": _multipart_image(sample_image_bytes),
            "rows": "2",
            "cols": "3",
            "split_mode": "both",
            "download_mode": "zip",
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 200
    run_dir = _latest_run_dir(temp_runs_dir)
    tiles = list(run_dir.glob("tile_*.png"))
    assert len(tiles) == 6
    assert (run_dir / "instagram_tiles.zip").exists()


def test_process_image_vertical_mode_regression(client, sample_image_bytes, temp_runs_dir: Path) -> None:
    response = client.post(
        "/process",
        data={
            "image": _multipart_image(sample_image_bytes),
            "rows": "5",
            "cols": "4",
            "split_mode": "vertical",
            "download_mode": "zip",
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 200
    run_dir = _latest_run_dir(temp_runs_dir)
    tiles = sorted(run_dir.glob("tile_v*.png"))
    assert len(tiles) == 4


def test_process_image_horizontal_mode_regression(client, sample_image_bytes, temp_runs_dir: Path) -> None:
    response = client.post(
        "/process",
        data={
            "image": _multipart_image(sample_image_bytes),
            "rows": "4",
            "cols": "7",
            "split_mode": "horizontal",
            "download_mode": "zip",
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 200
    run_dir = _latest_run_dir(temp_runs_dir)
    tiles = sorted(run_dir.glob("tile_h*.png"))
    assert len(tiles) == 4


def test_process_image_rejects_unsupported_type(client) -> None:
    response = client.post(
        "/process",
        data={
            "image": (io.BytesIO(b"hello"), "bad.txt"),
        },
        content_type="multipart/form-data",
    )
    assert response.status_code == 200
    assert b"Unsupported file type" in response.data


def test_download_selected_zip(client, sample_image_bytes, temp_runs_dir: Path) -> None:
    process_response = client.post(
        "/process",
        data={
            "image": _multipart_image(sample_image_bytes),
            "rows": "2",
            "cols": "2",
            "split_mode": "both",
            "download_mode": "zip",
        },
        content_type="multipart/form-data",
    )
    assert process_response.status_code == 200

    html = process_response.data.decode("utf-8")
    run_id = _extract_run_id(html)

    run_dir = _latest_run_dir(temp_runs_dir)
    tile_names = sorted(path.name for path in run_dir.glob("tile_*.png"))
    assert len(tile_names) == 4

    response = client.post(
        "/download-selected-zip",
        data={
            "run_id": run_id,
            "tile": tile_names[:2],
        },
    )

    assert response.status_code == 200
    assert "attachment" in response.headers.get("Content-Disposition", "")


def test_serve_generated_file_download_flag(client, sample_image_bytes, temp_runs_dir: Path) -> None:
    process_response = client.post(
        "/process",
        data={
            "image": _multipart_image(sample_image_bytes),
            "rows": "1",
            "cols": "2",
            "split_mode": "both",
            "download_mode": "zip",
        },
        content_type="multipart/form-data",
    )
    assert process_response.status_code == 200

    run_dir = _latest_run_dir(temp_runs_dir)
    run_id = run_dir.name
    tile_name = sorted(path.name for path in run_dir.glob("tile_*.png"))[0]

    response = client.get(f"/runs/{run_id}/{tile_name}?download=1")
    assert response.status_code == 200
    assert "attachment" in response.headers.get("Content-Disposition", "")
