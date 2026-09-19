"""Classical 3D segmentation: detection accuracy + full volume→segment→track path."""
import numpy as np
from celltracker import segment_volume, CellTracker
from celltracker.synthetic import make_volume


GT = [(6, 20, 20), (6, 20, 44), (6, 44, 32)]  # (z, y, x) centroids, well separated


def test_segments_all_blobs():
    vol = make_volume(GT, shape=(12, 64, 64), radius=3.0)
    dets = segment_volume(vol, min_voxels=3)
    # Recall: every GT blob has a detection whose centroid is within tolerance.
    matched = 0
    for (gz, gy, gx) in GT:
        if any(abs(d.z - gz) < 3 and abs(d.y - gy) < 3 and abs(d.x - gx) < 3 for d in dets):
            matched += 1
    assert matched == len(GT), f"recall {matched}/{len(GT)}"
    # Precision: not wildly over-segmenting.
    assert len(dets) <= len(GT) + 1


def test_empty_volume_no_detections():
    vol = np.full((8, 32, 32), 20.0, dtype=np.float32)
    assert segment_volume(vol, threshold=100.0) == []


def test_end_to_end_volume_to_tracks():
    tracker = CellTracker()
    # Two frames: blobs drift slightly → should form persistent tracks.
    for f in range(6):
        centroids = [(6, 20 + f, 20), (6, 20, 44 - f), (6, 44, 32)]
        dets = segment_volume(make_volume(centroids, seed=f), min_voxels=3)
        tracker.update(f, dets)
    assert 3 <= len(tracker.tracks) <= 6  # 3 cells, allow a couple of breaks
    longest = max(len(t.positions) for t in tracker.tracks.values())
    assert longest >= 4
