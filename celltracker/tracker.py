"""Multi-object 3D cell tracker: Kalman prediction + Hungarian association +
mitosis (division) detection, producing a lineage forest.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .association import Detection, associate
from .kalman import KalmanFilter3D


@dataclass
class Track:
    track_id: int
    kf: KalmanFilter3D
    volume: float
    start_frame: int
    end_frame: int
    parent_id: int = 0  # CTC convention: 0 = no parent
    positions: dict[int, np.ndarray] = field(default_factory=dict)
    active: bool = True
    misses: int = 0

    @property
    def pos(self) -> np.ndarray:
        return self.kf.position


class CellTracker:
    def __init__(
        self,
        gating_radius: float = 35.0,
        z_anisotropy: float = 2.0,
        max_misses: int = 2,
        division_volume_ratio: float = 0.65,
    ) -> None:
        self.gating_radius = gating_radius
        self.z_anisotropy = z_anisotropy
        self.max_misses = max_misses
        self.division_volume_ratio = division_volume_ratio
        self.tracks: dict[int, Track] = {}
        self._next_id = 1

    def _new_track(self, det: Detection, frame: int, parent_id: int = 0) -> Track:
        tid = self._next_id
        self._next_id += 1
        kf = KalmanFilter3D(det.pos, z_anisotropy=self.z_anisotropy)
        track = Track(track_id=tid, kf=kf, volume=det.volume, start_frame=frame, end_frame=frame, parent_id=parent_id)
        track.positions[frame] = det.pos
        self.tracks[tid] = track
        return track

    def update(self, frame: int, detections: list[Detection]) -> dict:
        active = [t for t in self.tracks.values() if t.active]
        # Snapshot volumes BEFORE matching overwrites them, so mitosis (a daughter is
        # ~half the *parent's previous* volume) is measured against the true parent size.
        pre_vol = {t.track_id: t.volume for t in active}
        for t in active:
            t.kf.predict()
        states = [(t.pos, t.volume) for t in active]

        matched, unmatched_tracks, unmatched_dets = associate(
            states, detections, gating_radius=self.gating_radius, z_anisotropy=self.z_anisotropy
        )

        matched_track_idx = {i for i, _ in matched}
        for ti, di in matched:
            t = active[ti]
            det = detections[di]
            t.kf.update(det.pos)
            t.volume = det.volume
            t.end_frame = frame
            t.misses = 0
            t.positions[frame] = t.kf.position

        # Unmatched tracks: age; retire after too many misses.
        for ti in unmatched_tracks:
            t = active[ti]
            t.misses += 1
            if t.misses > self.max_misses:
                t.active = False

        # Mitosis: a much-smaller-volume unmatched detection near a just-matched
        # parent implies a division -> spawn a child pointing at the parent.
        births: list[Track] = []
        divisions = 0
        for di in unmatched_dets:
            det = detections[di]
            parent = self._nearest_recent_parent(det, matched, active, frame)
            parent_vol = pre_vol.get(parent.track_id, parent.volume) if parent is not None else 0.0
            if parent is not None and det.volume <= parent_vol * self.division_volume_ratio:
                births.append(self._new_track(det, frame, parent_id=parent.track_id))
                divisions += 1
            else:
                births.append(self._new_track(det, frame))

        return {
            "frame": frame,
            "active_tracks": sum(1 for t in self.tracks.values() if t.active),
            "matched": len(matched),
            "new_tracks": len(births),
            "divisions": divisions,
        }

    def _nearest_recent_parent(self, det: Detection, matched, active, frame: int) -> Track | None:
        best = None
        best_d = self.gating_radius
        for ti, _di in matched:
            t = active[ti]
            d = det.pos - t.pos
            d[2] *= self.z_anisotropy
            dist = float(np.linalg.norm(d))
            if dist < best_d:
                best_d = dist
                best = t
        return best

    def run(self, frames: list[list[Detection]]) -> list[dict]:
        return [self.update(f_idx, dets) for f_idx, dets in enumerate(frames)]
