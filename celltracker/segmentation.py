"""Classical 3D nuclei segmentation — detections from a raw volume without a trained model.

Turns a (D, H, W) intensity volume into cell-centroid detections via intensity
thresholding + connected-component labeling (``scipy.ndimage``), with anisotropic-aware
centroids and volume estimates. This closes the "needs a segmentation model" gap: it is a
real, dependency-light detector (Otsu-style threshold + CCL) that feeds the tracker, and
can be swapped for a StarDist-3D / U-Net model later for higher recall.
"""
from __future__ import annotations

import numpy as np
from scipy import ndimage

from .association import Detection


def _otsu_threshold(vol: np.ndarray) -> float:
    """Otsu's method on a flattened intensity histogram."""
    hist, edges = np.histogram(vol.ravel(), bins=64)
    hist = hist.astype(float)
    total = hist.sum()
    if total == 0:
        return float(vol.mean())
    centers = (edges[:-1] + edges[1:]) / 2
    w0 = np.cumsum(hist)
    w1 = total - w0
    mu0 = np.cumsum(hist * centers) / np.clip(w0, 1, None)
    mu_total = (hist * centers).sum() / total
    mu1 = (mu_total * total - np.cumsum(hist * centers)) / np.clip(w1, 1, None)
    between = w0 * w1 * (mu0 - mu1) ** 2
    return float(centers[int(np.argmax(between))])


def segment_volume(
    volume: np.ndarray,
    threshold: float | None = None,
    min_voxels: int = 3,
    z_anisotropy: float = 1.0,
) -> list[Detection]:
    """Detect nuclei centroids in a (D, H, W) volume.

    Returns Detections with (x=col, y=row, z=depth) centroids and a `volume` = voxel count.
    """
    vol = np.asarray(volume, dtype=np.float32)
    thr = _otsu_threshold(vol) if threshold is None else threshold
    mask = vol > thr

    labels, n = ndimage.label(mask)
    if n == 0:
        return []

    detections: list[Detection] = []
    sizes = ndimage.sum(np.ones_like(labels), labels, index=range(1, n + 1))
    centroids = ndimage.center_of_mass(vol, labels, index=range(1, n + 1))
    for i, (cz, cy, cx) in enumerate(centroids):
        if sizes[i] < min_voxels:
            continue
        detections.append(
            Detection(x=float(cx), y=float(cy), z=float(cz) * z_anisotropy, volume=float(sizes[i]))
        )
    return detections
