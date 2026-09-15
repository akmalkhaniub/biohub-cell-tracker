# Biohub - Cell Tracking During Development

- **Official Challenge URL:** [https://www.kaggle.com/competitions](https://www.kaggle.com/competitions)
- **Organizer:** Chan Zuckerberg Biohub & Kaggle
- **Host Platform:** Kaggle Competitions
- **Total Prize Pool:** $60,000 USD
- **Format:** Code Competition (Offline inference notebook)
- **Primary Themes:** 3D Spatiotemporal Computer Vision, Microscopy, Multi-Object Tracking (MOT), Cell Segmentation

---

## 1. Challenge Overview & Problem Statement
Understanding embryonic development requires tracing how individual cells divide, migrate, and assemble into complex tissues. 

In this competition organized by the Chan Zuckerberg Biohub, participants are provided high-resolution light-sheet fluorescence microscopy videos capturing developing zebrafish embryos over hours. The objective is to detect, segment, and track thousands of moving, dividing cells through 3D space and time $(X, Y, Z, T)$.

### Evaluation Metric
The challenge is scored using a variant of the **Multiple Object Tracking Accuracy (MOTA) and Association Accuracy**, heavily penalizing identity switches, false splits, and lost tracks during cell division.

---

## 2. Selected Architectural Strategy: Spatiotemporal 3D Cell Tracker
1. **Volumetric Instance Segmentation:** Utilizing an isotropic 3D U-Net / StarDist-3D model to predict star-convex polyhedra and instance centroids for each time frame.
2. **Spatiotemporal Association & Graph Linking:** Constructing a directed graph where nodes represent detected cell centroids across time steps $T_i$, and edges represent biological migration or mitotic cell division ($1 \rightarrow 2$).
3. **Kalman Filtering & Linear Sum Assignment:** Optimal bipartite matching via the Hungarian algorithm incorporating spatial velocity, morphology constancy, and division probability.

---

## 3. Directory Structure
```
kaggle-biohub-cell-tracking/
├── README.md               # Challenge rules, microscopy dataset details (this file)
├── SPECIFICATION.md        # 3D segmentation specs, tracking graph mathematics
├── ROADMAP.md              # Research and Kaggle notebook submission milestones
├── src/
│   ├── segmentation_3d.py  # 3D U-Net & StarDist volumetric segmenter
│   ├── tracker.py          # Bipartite matching, Kalman filter, division detector
│   └── evaluate.py         # MOTA and tracking metric evaluation harness
└── notebooks/              # End-to-end Kaggle submission notebook
```
