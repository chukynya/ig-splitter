from __future__ import annotations

from flask import Flask

import ig_splitter.web.routes as routes


def test_allowed_file() -> None:
    assert routes._allowed_file("pic.jpg")
    assert routes._allowed_file("pic.webp")
    assert not routes._allowed_file("pic.gif")


def test_parse_int_applies_bounds_and_fallback() -> None:
    assert routes._parse_int("5", fallback=3, minimum=1, maximum=10) == 5
    assert routes._parse_int("999", fallback=3, minimum=1, maximum=10) == 10
    assert routes._parse_int("-1", fallback=3, minimum=1, maximum=10) == 1
    assert routes._parse_int("nope", fallback=3, minimum=1, maximum=10) == 3


def test_parse_split_mode() -> None:
    assert routes._parse_split_mode("both") == "both"
    assert routes._parse_split_mode("vertical") == "vertical"
    assert routes._parse_split_mode("horizontal") == "horizontal"
    assert routes._parse_split_mode("unknown") == "both"


def test_parse_download_mode() -> None:
    assert routes._parse_download_mode("zip") == "zip"
    assert routes._parse_download_mode("nozip") == "nozip"
    assert routes._parse_download_mode("other") == "zip"


def test_build_options_from_request_form() -> None:
    app = Flask(__name__)
    with app.test_request_context(
        method="POST",
        data={
            "rows": "4",
            "cols": "5",
            "split_mode": "vertical",
            "download_mode": "nozip",
        },
    ):
        options = routes._build_options()

    assert options.rows == 4
    assert options.cols == 5
    assert options.split_mode == "vertical"
    assert options.download_mode == "nozip"
