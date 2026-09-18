import http from 'http';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { KalmanTracker3D } from './kalman_tracker_3d.js';
import { MitosisLineageGraph } from './mitosis_lineage_graph.js';
import { UltrackHungarianSolver } from './ultrack_hungarian_solver.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const PUBLIC_DIR = path.join(__dirname, 'public');
const PORT = process.env.PORT || 3009;

const tracker = new KalmanTracker3D({ zAnisotropy: 2.0, maxGatingDistance: 40.0 });
const lineage = new MitosisLineageGraph();
const solver = new UltrackHungarianSolver();

const server = http.createServer((req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    res.writeHead(204);
    res.end();
    return;
  }

  // Health check endpoint for container probes & cloud orchestrators
  if (req.url === '/api/health' && req.method === 'GET') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      status: 'online',
      service: 'Biohub Cell Tracker',
      timestamp: new Date().toISOString()
    }));
    return;
  }

  // REST API Routes
  if (req.url === '/api/track/step' && req.method === 'POST') {
    let body = '';
    req.on('data', chunk => { body += chunk; });
    req.on('end', () => {
      try {
        const { frameNumber, detections } = JSON.parse(body);
        const result = tracker.update(frameNumber, detections);
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({
          frameNumber,
          activeTracks: Array.from(tracker.activeTracks.values()),
          lineageTree: Array.from(lineage.lineageTree.entries())
        }));
      } catch (err) {
        res.writeHead(400, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: err.message }));
      }
    });
    return;
  }

  // Static files
  let filePath = path.join(PUBLIC_DIR, req.url === '/' ? 'index.html' : req.url);
  const ext = path.extname(filePath).toLowerCase();
  const mimeTypes = {
    '.html': 'text/html; charset=utf-8',
    '.js': 'application/javascript; charset=utf-8',
    '.css': 'text/css; charset=utf-8',
    '.json': 'application/json; charset=utf-8'
  };

  fs.readFile(filePath, (err, content) => {
    if (err) {
      if (err.code === 'ENOENT') {
        res.writeHead(404, { 'Content-Type': 'text/plain' });
        res.end('404 Not Found');
      } else {
        res.writeHead(500, { 'Content-Type': 'text/plain' });
        res.end('Server Error: ' + err.code);
      }
    } else {
      res.writeHead(200, { 'Content-Type': mimeTypes[ext] || 'application/octet-stream' });
      res.end(content);
    }
  });
});

server.listen(PORT, () => {
  console.log(`🔬 Biohub Cell Tracker Server running at http://localhost:${PORT}`);
});
