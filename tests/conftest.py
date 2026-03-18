from __future__ import annotations

import io
from pathlib import Path

import pytest
from PIL import Image

import ig_splitter.web.routes as routes
from ig_splitter import create_app


@pytest.fixture
def temp_runs_dir(tmp_path: Path) -> Path:
    runs_dir = tmp_path / "runs"
    runs_dir.mkdir()
    return runs_dir


@pytest.fixture(autouse=True)
def patch_runs_dir(monkeypatch: pytest.MonkeyPatch, temp_runs_dir: Path) -> None:
    monkeypatch.setattr(routes, "RUNS_DIR", temp_runs_dir)


@pytest.fixture
def app():
    flask_app = create_app()
    flask_app.config.update(TESTING=True)
    return flask_app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def sample_image_bytes() -> bytes:
    image = Image.new("RGB", (120, 80), color=(80, 140, 220))
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()
