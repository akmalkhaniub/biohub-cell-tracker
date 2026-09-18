"""Lineage export in the Cell Tracking Challenge (CTC) ``res_track.txt`` format.

Each line: ``L B E P`` — track label L, first frame B, last frame E, parent P
(0 if the track has no parent). This is the acceptance format for CTC/Biohub tracking.
"""
from __future__ import annotations

from pathlib import Path

from .tracker import CellTracker, Track


def lineage_rows(tracker: CellTracker) -> list[tuple[int, int, int, int]]:
    rows = []
    for t in sorted(tracker.tracks.values(), key=lambda x: x.track_id):
        rows.append((t.track_id, t.start_frame, t.end_frame, t.parent_id))
    return rows


def write_res_track(tracker: CellTracker, out_path: str | Path = "res_track.txt") -> Path:
    out = Path(out_path)
    with out.open("w") as fh:
        for label, b, e, p in lineage_rows(tracker):
            fh.write(f"{label} {b} {e} {p}\n")
    return out


def validate_lineage(rows: list[tuple[int, int, int, int]]) -> None:
    """Raise if the lineage is malformed (bad frame order or dangling parent)."""
    labels = {r[0] for r in rows}
    for label, b, e, p in rows:
        assert b <= e, f"track {label}: start {b} > end {e}"
        assert p == 0 or p in labels, f"track {label}: parent {p} not a known label"
        assert p != label, f"track {label}: cannot be its own parent"


def count_divisions(tracker: CellTracker) -> int:
    return sum(1 for t in tracker.tracks.values() if t.parent_id != 0)


def daughters_of(tracker: CellTracker, parent_id: int) -> list[Track]:
    return [t for t in tracker.tracks.values() if t.parent_id == parent_id]
