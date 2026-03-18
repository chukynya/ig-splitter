from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ProcessOptions:
    rows: int
    cols: int
    split_mode: str
    download_mode: str


@dataclass(frozen=True)
class ProcessResult:
    run_id: str
    uploaded_name: str
    tile_names: list[str]
    zip_name: str
    rows: int
    cols: int
    requested_rows: int
    requested_cols: int
    split_mode: str
    split_mode_label: str
    download_mode: str
    count: int
