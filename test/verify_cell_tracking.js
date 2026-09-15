import assert from 'assert';
import { KalmanTracker3D } from '../src/kalman_tracker_3d.js';
import { MitosisLineageGraph } from '../src/mitosis_lineage_graph.js';

console.log('🧪 Starting Biohub 3D Cell Tracking Automated Verification Suite (Kaggle)...\n');

const tracker = new KalmanTracker3D({ zAnisotropy: 2.0, maxGatingDistance: 40.0 });
const lineage = new MitosisLineageGraph();

// Frame 1: Single Mother Cell appears
console.log('1️⃣ Simulating Frame 1: Cell Ingestion & Initial Detection...');
const frame1Dets = [{ x: 100, y: 100, z: 20, volume: 1000 }];
const res1 = tracker.update(1, frame1Dets);
assert(res1.newTracks.length === 1, 'Should initialize 1 new track');
const motherCell = res1.newTracks[0];
console.log(`   ✅ Track initiated: Cell #${motherCell.id} at (${motherCell.x}, ${motherCell.y}, ${motherCell.z}), Volume: ${motherCell.volume}`);

// Frame 2: Mother Cell moves with velocity (dx=+5, dy=+3)
console.log('2️⃣ Simulating Frame 2: Continuous Spatiotemporal Trajectory Migration...');
const frame2Dets = [{ x: 105, y: 103, z: 20, volume: 1020 }];
const res2 = tracker.update(2, frame2Dets);
assert(res2.updatedTracks.length === 1, 'Track should be maintained');
assert(res2.updatedTracks[0].id === motherCell.id, 'Cell ID must remain invariant (zero identity switches)');
console.log(`   ✅ Track maintained: Cell #${motherCell.id} moved to (${motherCell.x}, ${motherCell.y}, ${motherCell.z}) with velocity vx=${motherCell.vx.toFixed(1)}, vy=${motherCell.vy.toFixed(1)}`);

// Frame 3: Mother Cell prepares for division
console.log('3️⃣ Simulating Frame 3: Pre-mitotic elongation...');
const frame3Dets = [{ x: 110, y: 106, z: 20, volume: 1050 }];
tracker.update(3, frame3Dets);

// Frame 4: Mother Cell undergoes mitosis, producing 2 daughter cells
console.log('4️⃣ Simulating Frame 4: Mitotic Cell Division Event (1 -> 2)...');
// Two daughter cells symmetrically positioned around mother's predicted position (115, 109)
const daughterDets = [
  { x: 112, y: 105, z: 20, volume: 510 },
  { x: 118, y: 113, z: 20, volume: 520 }
];

// In frame 4, mother cell splits: one daughter updates the trajectory, second daughter emerges
const res4 = tracker.update(4, daughterDets);
assert(res4.updatedTracks.length === 1, 'One daughter updates the existing trajectory');
assert(res4.newTracks.length === 1, 'Second daughter emerges as a newborn track');
console.log(`   🔬 Detected Mitotic Split: Daughter 1 (Cell #${res4.updatedTracks[0].id}, vol: ${res4.updatedTracks[0].volume}) and Daughter 2 (Cell #${res4.newTracks[0].id}, vol: ${res4.newTracks[0].volume})`);

// Evaluate Mitosis
const mitosisEvent = lineage.evaluateMitosis(res4.updatedTracks[0], res4.newTracks, 1050);
assert(mitosisEvent !== null, 'Mitosis event must be detected');
assert(mitosisEvent.parentCellId === motherCell.id, 'Parent must be Cell #1');
assert(mitosisEvent.daughterCellIds.length === 2, 'Must link 2 daughter cells');
assert(res4.newTracks[0].parentTrackId === motherCell.id, 'Daughter 2 parentTrackId must be set');

console.log('   🌳 Mitotic Division Verified Successfully:');
console.log(`      Parent Track: Cell #${mitosisEvent.parentCellId}`);
console.log(`      Daughter Tracks: Cell #${mitosisEvent.daughterCellIds[0]} & Cell #${mitosisEvent.daughterCellIds[1]}`);
console.log(`      Volume Conservation Ratio: ${mitosisEvent.volumeRatio}x (Valid biological split)`);
console.log(`      Spatial Separation: ${mitosisEvent.centroidDrift}px`);

console.log('\n🎉 ALL BIOHUB 3D CELL TRACKING TESTS PASSED WITH 100% SUCCESS!\n');
