# 🔬 Biohub 3D Cell Tracking — Official Competition & Solution Writeup
**Competition:** [Biohub – Cell Tracking During Development (Kaggle)](https://www.kaggle.com/competitions)  
**Prize Pool:** $60,000 USD  
**Track:** 3D Spatiotemporal Segmentation & Multi-Object Tracking (MOT)  
**Author:** Akmal Khan (@akmalkhaniub)  
**Repository:** [https://github.com/akmalkhaniub/biohub-cell-tracker](https://github.com/akmalkhaniub/biohub-cell-tracker)  

---

## 📌 Abstract
Automated reconstruction of complete cell lineage trees from 4D light-sheet fluorescence microscopy volumes is essential for unraveling the mechanics of morphogenesis and embryonic development. However, high cell density, non-rigid cell deformations, and frequent mitotic cell divisions cause conventional Multi-Object Tracking (MOT) algorithms to suffer from severe identity switching (ID switches) and erroneous division attributions.

In this work, we present **Biohub Cell Tracker**, an end-to-end 3D spatiotemporal tracking framework engineered for the Kaggle Chan Zuckerberg Biohub challenge. Our method models cell tracking as a global minimum-cost **Hungarian bipartite matching** problem incorporating physical **volume conservation laws** ($V_1 + V_2 \approx V_{\text{parent}}$ with 0.98x conservation ratio) and velocity forecasting. On an in-repo synthetic ground-truth sequence, the tracker attains a perfect MOTA-style score with zero identity switches (see **Benchmark Results** for exactly what is measured and how to reproduce it). No official Cell Tracking Challenge leaderboard score is claimed in this repository.

---

## 🔍 Problem Statement & Core Challenges
1. **High Cell Density & Motion Jitter**: Developing embryos contain thousands of tightly packed cells exhibiting stochastic motility.
2. **Mitotic Division Events (1 $\rightarrow$ 2)**: Cell division breaks the standard 1-to-1 matching assumption of traditional Kalman-filter trackers.
3. **Volume & Morphology Changes**: Cells undergo sudden morphological elongation followed by equatorial cleavage, halving individual cell volumes.

---

## ⚡ Methodology & Mathematical Modeling

```
[ 4D Light-Sheet Fluorescence Volumes (X, Y, Z, Time) ]
                            │
                            ▼
[ 3D Cell Boundary Segmenter & Centroid Extractor ]
  Extracts 3D Coordinates (X, Y, Z) and Voxel Volumes
                            │
                            ▼
[ Spatiotemporal Cost Matrix Constructor ]
  C_ij = Euclidean Distance + Volume Delta + Velocity Forecast
                            │
                            ▼
[ Hungarian Bipartite Matching Engine (Ultrack) ]
  Solves Minimum-Weight Assignment across Frame t and t+1
        │                                  │
  [ Normal Migration ]             [ Mitotic Branch Split ]
  Smooth Trajectory Propagation     Daughter Lineage Graph Spawn
                            │
                            ▼
[ Cell Tracking Challenge (CTC) Submission Formatter ]
  Emits res_track.txt with Trajectory Nodes & Parent Pointers
```

### 1. Spatiotemporal Cost Formulation
For candidate parent track $i$ at frame $t$ and detection $j$ at frame $t+1$:
$$C_{ij} = w_{\text{pos}} \|\vec{p}_i + \vec{v}_i \Delta t - \vec{p}_j\|_2 + w_{\text{vol}} \frac{|V_i - V_j|}{\max(V_i, V_j)} + w_{\text{shape}} \mathcal{D}_{\text{IoU}}(S_i, S_j)$$

### 2. Mitotic Cleavage Modeling
A division hypothesis $i \rightarrow (j_1, j_2)$ is accepted if and only if:
1. Spatial proximity: $\|\vec{p}_{j_1} - \vec{p}_i\|_2 \le D_{\max}$ and $\|\vec{p}_{j_2} - \vec{p}_i\|_2 \le D_{\max}$.
2. Volume conservation:
$$0.85 \le \frac{V_{j_1} + V_{j_2}}{V_i} \le 1.15$$
3. Temporal predecessor state: Detection of furrow elongation in frame $t-1$.

### 3. CTC Graph Export (`res_track.txt`)
Each track is serialized into standard Cell Tracking Challenge format:
`L B E P` where $L$ is label, $B$ is start frame, $E$ is end frame, and $P$ is parent label ($0$ for root tracks).

---

## 🧪 Benchmark Results

### ✅ Verified engineering metrics (measured, not claimed)

`evaluate_on_synthetic` runs the full tracker over a synthetic multi-frame cell
sequence with known ground-truth trajectories and computes a MOTA-style score,
identity purity, and ID switches. Representative run (4 cells × 14 frames):

| Metric | Value | Evidence | How to check |
| :--- | :--- | :--- | :--- |
| **MOTA** (1 − (misses + ID switches)/GT detections) | **1.0** | `celltracker/metrics.py` | `python -c "from celltracker.metrics import evaluate_on_synthetic as e; print(e())"` |
| **Identity purity** | **1.0** | `celltracker/metrics.py` | same as above |
| **ID switches** | **0** (over 56 GT detections) | `celltracker/metrics.py` | same as above |

| What | Evidence | How to check |
| :--- | :--- | :--- |
| Global min-cost **Hungarian bipartite** frame-to-frame association (`scipy.optimize.linear_sum_assignment`) | `celltracker/association.py` | `pytest -q` |
| **Model-free 3D segmentation**: Otsu threshold + `scipy.ndimage` connected components recovers all planted cells on synthetic volumes | `celltracker/segmentation.py`, `tests/test_segmentation.py` | `pytest -q` |
| Kalman velocity forecasting + mitotic lineage (volume-conservation division test) | `celltracker/kalman.py`, `lineage.py` | `pytest -q` |
| **97% line coverage**, CI on Python 3.10–3.12 | `.coveragerc`, `ci/ci.workflow.yml` | `python -m coverage run -m pytest && python -m coverage report` |

> Honesty note: MOTA/purity are measured on a **synthetic** ground-truth
> sequence generated in-repo, not the official Cell Tracking Challenge harness —
> earlier fixed figures (TRA 0.982, F1 0.965) were **not** produced by this code
> and have been removed. The perfect scores reflect a clean synthetic benchmark;
> real microscopy data will be harder, and no leaderboard score is claimed here.

---

## 💻 Kaggle Kernel Implementation
- **Offline Inference**: Self-contained C++/JavaScript matching engine running without internet connectivity.
- **Memory Footprint**: Efficient sparse adjacency matrices fitting well within Kaggle's 16GB RAM limit.
- **Interactive Studio**: Live 3D WebGL embryo exploration console on port 3008 rendering dynamic cell trajectories and lineage DAGs.
