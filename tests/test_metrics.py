"""Tracking-metric tests on labeled synthetic sequences."""
from celltracker import evaluate_on_synthetic


def test_metrics_are_bounded_and_high_on_clean_tracks():
    m = evaluate_on_synthetic(n_cells=4, n_frames=14, seed=0)
    assert 0.0 <= m.purity <= 1.0
    assert 0.0 <= m.mota <= 1.0
    assert m.gt_detections == 4 * 14
    # Well-separated constant-velocity cells should track near-perfectly.
    assert m.purity >= 0.95
    assert m.mota >= 0.9
    assert m.id_switches <= 1


def test_more_cells_still_tracks_reasonably():
    m = evaluate_on_synthetic(n_cells=6, n_frames=12, seed=3)
    assert m.purity >= 0.9
    assert m.mota >= 0.8
