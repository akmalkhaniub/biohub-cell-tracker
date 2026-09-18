"""Biohub cell-tracking Kaggle entry point.

Wire `load_frames` to the competition's per-timepoint 3D detections (or run a
segmentation model first), then this tracks them and writes CTC res_track.txt.
Runs a synthetic demo when no data is present.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from celltracker import CellTracker, write_res_track, count_divisions  # noqa: E402
from celltracker.synthetic import dividing_track  # noqa: E402


def load_frames():
    # Placeholder: return list[list[Detection]] per timepoint from the competition data.
    return None


def main() -> int:
    frames = load_frames() or dividing_track(n_frames=12)
    tracker = CellTracker()
    tracker.run(frames)
    out = "/kaggle/working/res_track.txt" if Path("/kaggle/working").exists() else "res_track.txt"
    write_res_track(tracker, out)
    print(f"Tracked {len(tracker.tracks)} tracks ({count_divisions(tracker)} divisions) -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
