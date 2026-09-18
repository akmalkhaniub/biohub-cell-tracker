"""3D constant-velocity Kalman filter for cell centroid tracking.

State x = [px, py, pz, vx, vy, vz]. Standard predict/update with anisotropic z
measurement noise (z resolution is typically coarser in light-sheet microscopy).
"""
from __future__ import annotations

import numpy as np


class KalmanFilter3D:
    def __init__(self, pos: np.ndarray, dt: float = 1.0, z_anisotropy: float = 2.0,
                 process_var: float = 1.0, meas_var: float = 4.0) -> None:
        pos = np.asarray(pos, dtype=np.float64).reshape(3)
        self.x = np.concatenate([pos, np.zeros(3)])  # start at rest

        # State transition (constant velocity).
        self.F = np.eye(6)
        for i in range(3):
            self.F[i, i + 3] = dt

        # Measurement matrix (observe position only).
        self.H = np.zeros((3, 6))
        self.H[0, 0] = self.H[1, 1] = self.H[2, 2] = 1.0

        # Covariances.
        self.P = np.eye(6) * 10.0
        q = process_var
        self.Q = np.eye(6) * q
        self.Q[3:, 3:] *= 0.25  # velocity drifts more slowly
        self.R = np.diag([meas_var, meas_var, meas_var * (z_anisotropy ** 2)])

    @property
    def position(self) -> np.ndarray:
        return self.x[:3].copy()

    @property
    def velocity(self) -> np.ndarray:
        return self.x[3:].copy()

    def predict(self) -> np.ndarray:
        self.x = self.F @ self.x
        self.P = self.F @ self.P @ self.F.T + self.Q
        return self.position

    def update(self, measurement: np.ndarray) -> None:
        z = np.asarray(measurement, dtype=np.float64).reshape(3)
        y = z - self.H @ self.x
        S = self.H @ self.P @ self.H.T + self.R
        K = self.P @ self.H.T @ np.linalg.inv(S)
        self.x = self.x + K @ y
        self.P = (np.eye(6) - K @ self.H) @ self.P
