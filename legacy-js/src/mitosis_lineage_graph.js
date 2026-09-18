/**
 * MitosisLineageGraph - Reconstructs Cell Lineage Trees
 * Identifies 1 -> 2 mitotic division events using volume conservation and spatial proximity.
 */

export class MitosisLineageGraph {
  constructor() {
    this.lineageTree = new Map(); // cellId -> { parentId, daughterIds: [] }
    this.mitosisEvents = [];
  }

  /**
   * Evaluate candidate tracks for mitotic cell division events
   * Supports:
   * - Branching split where one daughter inherits track ID and second daughter is newborn
   * - Complete mother termination where two new daughter tracks are born
   */
  evaluateMitosis(parentTrack, newBornTracks, previousParentVolume = null) {
    const parentVol = previousParentVolume || parentTrack.volume;

    // Case 1: Mother track continued as daughter 1, and daughter 2 is newborn
    if (newBornTracks.length === 1) {
      const d2 = newBornTracks[0];
      const d1 = parentTrack;
      const combinedVolume = d1.volume + d2.volume;
      const volumeRatio = combinedVolume / (parentVol || 1);
      const dist = Math.sqrt(
        Math.pow(d1.x - d2.x, 2) +
        Math.pow(d1.y - d2.y, 2) +
        Math.pow(d1.z - d2.z, 2)
      );

      if (dist < 30.0 && volumeRatio >= 0.70 && volumeRatio <= 1.35) {
        const event = {
          parentCellId: parentTrack.id,
          daughterCellIds: [d1.id, d2.id],
          divisionFrame: d2.firstSeenFrame,
          volumeRatio: Number(volumeRatio.toFixed(2)),
          centroidDrift: Number((dist / 2).toFixed(2))
        };

        d2.parentTrackId = parentTrack.id;

        this.lineageTree.set(parentTrack.id, {
          parentId: parentTrack.parentTrackId,
          daughterIds: [d1.id, d2.id]
        });

        this.mitosisEvents.push(event);
        return event;
      }
    }

    // Case 2: Both daughters are newborn
    if (newBornTracks.length >= 2) {
      for (let i = 0; i < newBornTracks.length; i++) {
        for (let j = i + 1; j < newBornTracks.length; j++) {
          const d1 = newBornTracks[i];
          const d2 = newBornTracks[j];

          const midX = (d1.x + d2.x) / 2;
          const midY = (d1.y + d2.y) / 2;
          const midZ = (d1.z + d2.z) / 2;

          const distToParent = Math.sqrt(
            Math.pow(midX - parentTrack.x, 2) +
            Math.pow(midY - parentTrack.y, 2) +
            Math.pow(midZ - parentTrack.z, 2)
          );

          const combinedVolume = d1.volume + d2.volume;
          const volumeRatio = combinedVolume / (parentVol || 1);

          if (distToParent < 25.0 && volumeRatio >= 0.70 && volumeRatio <= 1.35) {
            const event = {
              parentCellId: parentTrack.id,
              daughterCellIds: [d1.id, d2.id],
              divisionFrame: d1.firstSeenFrame,
              volumeRatio: Number(volumeRatio.toFixed(2)),
              centroidDrift: Number(distToParent.toFixed(2))
            };

            d1.parentTrackId = parentTrack.id;
            d2.parentTrackId = parentTrack.id;

            this.lineageTree.set(parentTrack.id, {
              parentId: parentTrack.parentTrackId,
              daughterIds: [d1.id, d2.id]
            });

            this.mitosisEvents.push(event);
            return event;
          }
        }
      }
    }

    return null;
  }
}
