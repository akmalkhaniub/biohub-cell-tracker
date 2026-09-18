# 🔬 3D Spatiotemporal Cell Tracker — Biohub Challenge

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB.svg)](https://www.python.org)
[![SciPy](https://img.shields.io/badge/SciPy-Hungarian-8CAAE6.svg)](https://scipy.org)
[![Kaggle](https://img.shields.io/badge/Kaggle-Biohub%20Cell%20Tracking-20BEFF.svg)](https://www.kaggle.com/competitions)

> **Built for the [Biohub — Cell Tracking During Development](https://www.kaggle.com/competitions) Kaggle competition.**

Tracks dividing cells across 3D microscopy time-lapses: **Kalman**-predicted motion,
**Hungarian** optimal data association (`scipy.optimize.linear_sum_assignment`), mitosis
detection, and a lineage forest exported in the **Cell Tracking Challenge (CTC)**
`res_track.txt` format.

> **Note:** rebuilt from a Node.js prototype (kept under [`legacy-js/`](./legacy-js)) into
> the correct stack — a **Python** tracking package that emits a CTC submission.

## Pipeline

```
per-frame 3D detections (x, y, z, volume)
   → Kalman predict          constant-velocity filter, anisotropic z (kalman.py)
   → Hungarian associate      cost = spatial (anisotropic) + volume, gated (association.py)
   → update / birth / death   track lifecycle with miss tolerance (tracker.py)
   → mitosis detection        small-volume child near a matched parent → division
   → lineage export           CTC res_track.txt: "L B E P" (lineage.py)
```

The association is genuinely optimal (Hungarian), not greedy nearest-neighbor — the tests
include a case where greedy would mis-assign and Hungarian recovers the correct pairing.

## Run

```bash
pip install -r requirements-dev.txt && pip install -e .
pytest -q                       # Kalman, Hungarian, tracking, mitosis, CTC-format tests
python notebooks/kaggle_run.py  # synthetic demo -> res_track.txt (wire load_frames for real data)
```

## Scope & honesty

The tracking-by-detection stage is real and self-contained (NumPy + SciPy). It assumes
**detections are provided** — a 3D segmentation model (StarDist-3D / U-Net) upstream is
what turns raw light-sheet volumes into centroids, and is the remaining piece for a
full competition entry. Tests validate the Kalman filter, Hungarian optimality, gating,
multi-frame persistence, mitosis + lineage, and the exact CTC output format on synthetic
sequences; real scoring happens on Kaggle's hidden data.
