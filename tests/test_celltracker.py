"""Cell tracker tests on synthetic 3D sequences (Kalman + Hungarian + lineage)."""
import numpy as np

from celltracker import (
    CellTracker,
    Detection,
    KalmanFilter3D,
    associate,
    build_cost_matrix,
    count_divisions,
    daughters_of,
    lineage_rows,
    validate_lineage,
    write_res_track,
)
from celltracker.synthetic import dividing_track, linear_tracks


def test_kalman_tracks_constant_velocity():
    kf = KalmanFilter3D([0, 0, 0])
    truth = np.array([2.0, -1.0, 0.5])
    for step in range(1, 15):
        kf.predict()
        kf.update(truth * step + np.random.normal(0, 0.1, 3))
    # After warm-up the velocity estimate should be close to truth.
    assert np.allclose(kf.velocity, truth, atol=0.5)


def test_hungarian_is_optimal_not_greedy():
    # Two tracks, two dets where greedy nearest would mis-assign; Hungarian fixes it.
    tracks = [(np.array([0.0, 0, 0]), 100.0), (np.array([10.0, 0, 0]), 100.0)]
    dets = [Detection(9, 0, 0, 100), Detection(1, 0, 0, 100)]
    matched, ut, ud = associate(tracks, dets, gating_radius=50)
    pairing = dict(matched)
    assert pairing[0] == 1 and pairing[1] == 0  # track0->det@1, track1->det@9
    assert ut == [] and ud == []


def test_gating_rejects_far_detections():
    tracks = [(np.array([0.0, 0, 0]), 100.0)]
    dets = [Detection(500, 500, 500, 100)]
    matched, ut, ud = associate(tracks, dets, gating_radius=35)
    assert matched == [] and ut == [0] and ud == [0]


def test_tracks_persist_across_frames():
    tracker = CellTracker()
    frames = linear_tracks(n_cells=3, n_frames=12, seed=1)
    tracker.run(frames)
    # 3 cells tracked as a small, stable number of tracks (allow a couple of breaks).
    assert 3 <= len(tracker.tracks) <= 6
    longest = max(len(t.positions) for t in tracker.tracks.values())
    assert longest >= 8


def test_mitosis_detection_and_lineage():
    tracker = CellTracker(division_volume_ratio=0.7)
    tracker.run(dividing_track(n_frames=10))
    assert count_divisions(tracker) >= 1
    # The parent has at least one daughter pointing back at it.
    parents = {t.parent_id for t in tracker.tracks.values() if t.parent_id != 0}
    assert parents
    for pid in parents:
        assert len(daughters_of(tracker, pid)) >= 1


def test_res_track_format_valid(tmp_path):
    tracker = CellTracker()
    tracker.run(dividing_track(n_frames=8))
    rows = lineage_rows(tracker)
    validate_lineage(rows)  # raises on bad frames / dangling parent
    path = write_res_track(tracker, tmp_path / "res_track.txt")
    text = path.read_text().strip().splitlines()
    assert len(text) == len(rows)
    for line in text:
        parts = line.split()
        assert len(parts) == 4 and all(p.lstrip("-").isdigit() for p in parts)


def test_cost_matrix_shapes():
    tracks = [(np.array([0.0, 0, 0]), 100.0), (np.array([5.0, 0, 0]), 100.0)]
    dets = [Detection(0, 0, 0, 100), Detection(5, 0, 0, 100), Detection(99, 99, 99, 100)]
    cost = build_cost_matrix(tracks, dets, gating_radius=35)
    assert cost.shape == (2, 3)
    assert cost[0, 0] < cost[0, 2]  # near detection cheaper than the gated-out far one
