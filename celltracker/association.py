"""Optimal bipartite data association via the Hungarian algorithm (scipy).

Cost blends anisotropic spatial distance and morphological (volume) consistency,
with a gating radius beyond which matches are forbidden.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.optimize import linear_sum_assignment

_BIG = 1e6  # forbidden-match sentinel (kept finite so the solver is well-posed)


@dataclass
class Detection:
    x: float
    y: float
    z: float
    volume: float = 1.0

    @property
    def pos(self) -> np.ndarray:
        return np.array([self.x, self.y, self.z], dtype=np.float64)


def build_cost_matrix(
    track_states: list[tuple[np.ndarray, float]],
    detections: list[Detection],
    gating_radius: float = 35.0,
    z_anisotropy: float = 2.0,
    dist_weight: float = 0.65,
    vol_weight: float = 0.35,
) -> np.ndarray:
    """Rows = tracks (predicted pos, volume), cols = detections."""
    n, m = len(track_states), len(detections)
    cost = np.full((n, m), _BIG, dtype=np.float64)
    for i, (pos, vol) in enumerate(track_states):
        for j, det in enumerate(detections):
            d = det.pos - pos
            d[2] *= z_anisotropy
            dist = float(np.linalg.norm(d))
            if dist > gating_radius:
                continue
            vol_ratio = abs(vol - det.volume) / max(1.0, vol)
            cost[i, j] = dist_weight * dist + vol_weight * (vol_ratio * gating_radius)
    return cost


def associate(
    track_states: list[tuple[np.ndarray, float]],
    detections: list[Detection],
    **kwargs,
) -> tuple[list[tuple[int, int]], list[int], list[int]]:
    """Return (matched (track_idx, det_idx) pairs, unmatched track idxs, unmatched det idxs)."""
    n, m = len(track_states), len(detections)
    if n == 0:
        return [], [], list(range(m))
    if m == 0:
        return [], list(range(n)), []

    cost = build_cost_matrix(track_states, detections, **kwargs)
    rows, cols = linear_sum_assignment(cost)

    matched: list[tuple[int, int]] = []
    matched_tracks: set[int] = set()
    matched_dets: set[int] = set()
    for r, c in zip(rows, cols):
        if cost[r, c] >= _BIG:  # gated out
            continue
        matched.append((int(r), int(c)))
        matched_tracks.add(int(r))
        matched_dets.add(int(c))

    unmatched_tracks = [i for i in range(n) if i not in matched_tracks]
    unmatched_dets = [j for j in range(m) if j not in matched_dets]
    return matched, unmatched_tracks, unmatched_dets
