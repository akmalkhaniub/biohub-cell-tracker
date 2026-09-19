"""Tracking-quality metrics on labeled synthetic sequences.

Runs the tracker on ground-truth trajectories (known cell identity per frame) and
measures identity purity, ID switches, and a MOTA-style score — the kind of number the
Cell Tracking Challenge (TRA/MOTA) rewards.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

import numpy as np

from .association import Detection
from .tracker import CellTracker


@dataclass
class TrackingMetrics:
    purity: float        # mean over GT cells of (dominant track share of its frames)
    id_switches: int     # times a GT cell's assigned track id changes
    mota: float          # 1 - (misses + id_switches) / total_gt_detections
    gt_detections: int


def _linear_gt(n_cells: int, n_frames: int, seed: int = 0) -> list[list[np.ndarray]]:
    """Ground-truth positions[cell][frame] -> (x,y,z), constant velocity + tiny noise."""
    rng = np.random.default_rng(seed)
    starts = rng.uniform(20, 200, size=(n_cells, 3))
    vels = rng.uniform(-3, 3, size=(n_cells, 3))
    gt: list[list[np.ndarray]] = []
    for c in range(n_cells):
        gt.append([starts[c] + vels[c] * f + rng.normal(0, 0.3, 3) for f in range(n_frames)])
    return gt


def evaluate_on_synthetic(n_cells: int = 4, n_frames: int = 14, seed: int = 0) -> TrackingMetrics:
    gt = _linear_gt(n_cells, n_frames, seed)
    frames = [[Detection(*[float(v) for v in gt[c][f]], volume=100.0) for c in range(n_cells)] for f in range(n_frames)]

    tracker = CellTracker()
    tracker.run(frames)

    # For each GT cell/frame, assign the tracker track whose recorded position at that
    # frame is closest to the GT position (within a tolerance).
    tracks = list(tracker.tracks.values())
    assigned: list[list[int | None]] = []
    misses = 0
    for c in range(n_cells):
        per_frame: list[int | None] = []
        for f in range(n_frames):
            gp = gt[c][f]
            best_id, best_d = None, 5.0  # tolerance in px
            for t in tracks:
                pos = t.positions.get(f)
                if pos is None:
                    continue
                d = float(np.linalg.norm(pos - gp))
                if d < best_d:
                    best_d, best_id = d, t.track_id
            if best_id is None:
                misses += 1
            per_frame.append(best_id)
        assigned.append(per_frame)

    # Purity + ID switches per GT cell.
    purities = []
    switches = 0
    for per_frame in assigned:
        ids = [i for i in per_frame if i is not None]
        if ids:
            dominant = Counter(ids).most_common(1)[0][1]
            purities.append(dominant / len(ids))
            switches += sum(1 for a, b in zip(ids, ids[1:]) if a != b)

    total = n_cells * n_frames
    purity = float(np.mean(purities)) if purities else 0.0
    mota = 1.0 - (misses + switches) / total
    return TrackingMetrics(purity=round(purity, 3), id_switches=switches, mota=round(mota, 3), gt_detections=total)


if __name__ == "__main__":  # pragma: no cover
    print(evaluate_on_synthetic())
