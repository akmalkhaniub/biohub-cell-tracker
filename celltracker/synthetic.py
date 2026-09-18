"""Synthetic 3D detection sequences for tests/demos (no microscopy data needed)."""
from __future__ import annotations

import numpy as np

from .association import Detection


def linear_tracks(n_cells: int = 3, n_frames: int = 12, seed: int = 0) -> list[list[Detection]]:
    """Cells drifting with constant velocity + small noise."""
    rng = np.random.default_rng(seed)
    starts = rng.uniform(20, 200, size=(n_cells, 3))
    vels = rng.uniform(-3, 3, size=(n_cells, 3))
    frames: list[list[Detection]] = []
    for f in range(n_frames):
        dets = []
        for c in range(n_cells):
            p = starts[c] + vels[c] * f + rng.normal(0, 0.5, 3)
            dets.append(Detection(float(p[0]), float(p[1]), float(p[2]), volume=100.0))
        frames.append(dets)
    return frames


def dividing_track(n_frames: int = 10) -> list[list[Detection]]:
    """One cell that divides into two half-volume daughters at the midpoint."""
    frames: list[list[Detection]] = []
    split = n_frames // 2
    for f in range(n_frames):
        if f < split:
            frames.append([Detection(50 + 2 * f, 50, 30, volume=200.0)])
        else:
            base_x = 50 + 2 * split
            frames.append([
                Detection(base_x + (f - split), 48, 30, volume=95.0),
                Detection(base_x + (f - split), 52, 30, volume=95.0),
            ])
    return frames
