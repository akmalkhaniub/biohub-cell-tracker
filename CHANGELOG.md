# Changelog

## [Unreleased]

### Rebuilt in Python for Kaggle (2026-09-18)
Rebuilt from the Node prototype (preserved under `legacy-js/`) into a Python package that
produces a CTC `res_track.txt` tracking submission.

### Added
- `celltracker/kalman.py` — 3D constant-velocity Kalman filter (anisotropic z noise).
- `celltracker/association.py` — Hungarian data association via
  `scipy.optimize.linear_sum_assignment`, with a distance+volume gated cost matrix.
- `celltracker/tracker.py` — multi-object tracker with lifecycle management and mitosis
  (division) detection producing a lineage forest.
- `celltracker/lineage.py` — CTC `res_track.txt` export + validation.
- `celltracker/synthetic.py`, `notebooks/kaggle_run.py`.
- `tests/test_celltracker.py` — 7 pytest cases incl. a greedy-vs-Hungarian optimality
  case, gating, multi-frame persistence, mitosis/lineage, and CTC-format validation.
- `pyproject.toml`, `requirements*.txt`, CI on Python 3.10–3.12.

### Notes
- Tracking-by-detection assumes detections are provided; a 3D segmentation model
  (StarDist-3D/U-Net) upstream is the remaining piece for a full entry.
