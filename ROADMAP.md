# Roadmap & Milestones: 3D Spatiotemporal Cell Tracker
**Hackathon:** Biohub - Cell Tracking During Development  
**Target:** Kaggle Code Competition  

---

> **Status legend (updated 2026-09-18):** `[x]` implemented in code · `[~]` partial / stand-in (working JS logic, not the production stack named) · `[ ]` not started.
> **Reality note:** **Rebuilt in Python** (`celltracker/` package; old Node prototype under `legacy-js/`). Real 3D constant-velocity Kalman filter, **Hungarian** optimal association via `scipy.optimize.linear_sum_assignment` (gated distance+volume cost), track lifecycle + mitosis detection, and CTC `res_track.txt` lineage export. 7 pytest cases pass (incl. a greedy-vs-Hungarian optimality case). Assumes detections are provided; a 3D segmentation model upstream is the remaining piece. The displayed 0.982 TRA figure was a hardcoded demo value and is gone.

## Phase 1: Data Pipeline & Volumetric Preprocessing (Milestone 1)
- [ ] Load and unpack multi-gigabyte 3D time-lapse TIFF/HDF5 image series.
- [ ] Implement voxel intensity normalization, anisotropic voxel resampling, and background rolling-ball filtering.
- [ ] Build visual inspection tool using Napari / 3D PyVista to render volumes and ground-truth centroids.

## Phase 2: 3D Nuclei Instance Segmentation (Milestone 2)
- [ ] Train 3D Residual U-Net / StarDist-3D model predicting object probabilities and radial distances.
- [ ] Implement connected component watershed post-processing on GPU via CuPy.
- [ ] Validate 3D IoU and precision against annotated training subvolumes.

## Phase 3: Trajectory Linking & Mitotic Graph Solver (Milestone 3)
- [x] Implement 3D Kalman Filter estimating $(x, y, z, v_x, v_y, v_z)$ for every active track.
- [x] Build Hungarian algorithm matcher with gated distance thresholds.
- [x] Add mitosis branch detector identifying cell division events and updating lineage trees.
- [~] Benchmark MOTA and association metrics on validation sequences. *(demo metric, not scored on real data)*

## Phase 4: Kaggle Offline Packaging & Submission (Milestone 4)
- [ ] Optimize inference loop with batch slice streaming to prevent out-of-memory crashes.
- [ ] Package weights and PyTorch models into offline Kaggle dataset.
- [ ] Execute dry-run on hidden test split simulator and submit notebook.
