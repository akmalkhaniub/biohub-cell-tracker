# Technical Specification: 3D Spatiotemporal Cell Tracker
**Project Name:** 3D Spatiotemporal Cell Tracker (Biohub Challenge)  
**Status:** Rebuilt in Python — CTC tracking submission (updated 2026-09-18)  

> **Implementation status (2026-09-18):** Rebuilt from the Node prototype (now under `legacy-js/`) into a Python package (`celltracker/`): a 3D Kalman filter, **Hungarian** optimal association (`scipy.optimize.linear_sum_assignment`) with a gated distance+volume cost, track lifecycle + mitosis detection, and CTC `res_track.txt` lineage export. 7 pytest cases pass. Not built: the 3D segmentation model (StarDist-3D/U-Net) that produces detections from raw volumes; the hardcoded 0.982 TRA demo value is removed.
**Version:** 1.0.0  

---

## 1. System Pipeline
The framework operates as a two-stage tracking-by-detection system tailored to 3D volumetric light-sheet microscopy: volumetric cell detection followed by biological trajectory linking with lineage division tracking.

```mermaid
graph TD
    A[3D Microscopy Volume at time T: D x H x W] --> B[Denoising & Background Subtraction]
    B --> C[3D Residual U-Net / StarDist Centroid Detector]
    C --> D[Predicted Cell Centroids & Radial Distance Polygons]
    D --> E[Kalman State Predictor: Position & Velocity]
    E --> F[Cost Matrix Computation: Distance + Feature Similarity + Division Prior]
    F --> G[Hungarian Bipartite Matcher (Linear Sum Assignment)]
    G -->|Continuous Track| H[Update Existing Cell Trajectory]
    G -->|Cell Division Detected| I[Fork New Daughter Trajectories (Lineage Tree)]
    G -->|Unassigned Centroid| J[Initiate New Track]
    H --> K[Kaggle Lineage & Tracking Submission Format]
    I --> K
    J --> K
```

---

## 2. Mathematical Formulation & Linking Cost

### 2.1 Centroid Distance Metric
For an existing track $i$ at frame $t-1$ with predicted position $\hat{\mathbf{p}}_i^t = (\hat{x}_i, \hat{y}_i, \hat{z}_i)$ and a candidate detection $j$ at frame $t$ with position $\mathbf{p}_j^t$:
$$D_{\text{spatial}}(i, j) = \sqrt{ \Delta x^2 + \Delta y^2 + \alpha \Delta z^2 }$$
*(where $\alpha$ is an anisotropy compensation factor for light-sheet z-axial resolution).*

### 2.2 Combined Association Cost
$$\text{Cost}(i, j) = w_1 D_{\text{spatial}}(i, j) + w_2 D_{\text{volume}}(i, j) + w_3 (1 - S_{\text{intensity}}(i, j))$$

### 2.3 Mitosis / Division Logic
If a single existing track $i$ has two candidate unassigned detections $j_1, j_2$ within a tight spatial radius and the combined volume of $j_1 + j_2 \approx \text{Volume}(i)$, a mitotic division event is scored and parent-daughter lineage links are generated.

---

## 3. Data Formats

### 3.1 Lineage Track Record
```typescript
interface CellTrackRecord {
  cellId: number;
  startFrame: number;
  endFrame: number;
  parentCellId: number; // 0 if root track
  trajectory: Array<{
    frame: number;
    x: number;
    y: number;
    z: number;
    volumeVoxels: number;
  }>;
}
```

---

## 4. Acceptance Criteria
1. Accurate segmentation of dense overlapping cell nuclei in 3D volumes.
2. Low identity-switching rate (< 3% over 100 consecutive time frames).
3. Robust handling of missing detections in intermediate frames via Kalman velocity coasting.
4. Compliant with Kaggle offline execution memory footprint (< 16GB RAM, < 16GB GPU VRAM).
