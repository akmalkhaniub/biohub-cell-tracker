/**
 * KalmanTracker3D - 3D State Estimation & Motion Tracking
 * Tracks (x, y, z, vx, vy, vz) with anisotropic z-axis compensation.
 */

export class KalmanTracker3D {
  constructor(options = {}) {
    this.zAnisotropy = options.zAnisotropy || 2.0; // Z-axis resolution scaling factor
    this.maxGatingDistance = options.maxGatingDistance || 35.0; // Max permissible movement per frame (pixels)
    this.tracks = new Map(); // trackId -> TrackObject
    this.nextTrackId = 1;
  }

  /**
   * Update active tracks with new 3D detections at frame T
   * @param {number} frameIndex 
   * @param {Array<Object>} detections [{ x, y, z, volume, intensity }]
   * @returns {Object} updated tracks, new tracks, and lost tracks
   */
  update(frameIndex, detections) {
    const updatedTracks = [];
    const unmatchedDetections = [];
    const matchedDetectionIndices = new Set();

    // 1. Predict next position for all existing active tracks
    for (const track of this.tracks.values()) {
      track.predicted = {
        x: track.x + track.vx,
        y: track.y + track.vy,
        z: track.z + track.vz
      };
    }

    // 2. Compute distance cost matrix and find best bipartite matches
    for (const track of this.tracks.values()) {
      let bestDist = Infinity;
      let bestDetIdx = -1;

      for (let i = 0; i < detections.length; i++) {
        if (matchedDetectionIndices.has(i)) continue;

        const det = detections[i];
        const dist = this.calculateAnisotropicDistance(track.predicted, det);

        if (dist < bestDist && dist <= this.maxGatingDistance) {
          bestDist = dist;
          bestDetIdx = i;
        }
      }

      if (bestDetIdx !== -1) {
        matchedDetectionIndices.add(bestDetIdx);
        const match = detections[bestDetIdx];

        // Update velocity (momentum alpha = 0.6)
        track.vx = 0.6 * (match.x - track.x) + 0.4 * track.vx;
        track.vy = 0.6 * (match.y - track.y) + 0.4 * track.vy;
        track.vz = 0.6 * (match.z - track.z) + 0.4 * track.vz;

        // Update position
        track.x = match.x;
        track.y = match.y;
        track.z = match.z;
        track.volume = match.volume;
        track.lastSeenFrame = frameIndex;
        track.history.push({ frame: frameIndex, x: match.x, y: match.y, z: match.z, volume: match.volume });

        updatedTracks.push(track);
      }
    }

    // 3. Initiate new tracks for unmatched detections
    for (let i = 0; i < detections.length; i++) {
      if (!matchedDetectionIndices.has(i)) {
        const det = detections[i];
        const newTrack = {
          id: this.nextTrackId++,
          parentTrackId: null,
          x: det.x,
          y: det.y,
          z: det.z,
          vx: 0,
          vy: 0,
          vz: 0,
          volume: det.volume,
          firstSeenFrame: frameIndex,
          lastSeenFrame: frameIndex,
          history: [{ frame: frameIndex, x: det.x, y: det.y, z: det.z, volume: det.volume }]
        };
        this.tracks.set(newTrack.id, newTrack);
        unmatchedDetections.push(newTrack);
      }
    }

    return {
      activeTracksCount: this.tracks.size,
      updatedTracks,
      newTracks: unmatchedDetections
    };
  }

  calculateAnisotropicDistance(p1, p2) {
    const dx = p1.x - p2.x;
    const dy = p1.y - p2.y;
    const dz = (p1.z - p2.z) * this.zAnisotropy;
    return Math.sqrt(dx * dx + dy * dy + dz * dz);
  }
}
