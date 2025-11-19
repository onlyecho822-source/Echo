/**
 * Echo Hearing Aid - Web Server
 * Provides REST API and web interface for the hearing aid prototype
 */

const express = require('express');
const cors = require('cors');
const path = require('path');
const HearingAidDevice = require('./deviceController');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static('public'));

// Device instance
const device = new HearingAidDevice({
  mode: 'language-learning',
  sensitivity: 1.2,
});

// Initialize device on startup
device.initialize();
const selfTest = device.performSelfTest();
console.log('Self-test results:', selfTest);

// ============================================
// API ENDPOINTS
// ============================================

/**
 * POST /api/audio/process
 * Process audio samples and return vibration command
 */
app.post('/api/audio/process', (req, res) => {
  try {
    const { samples } = req.body;

    if (!Array.isArray(samples) || samples.length === 0) {
      return res.status(400).json({ error: 'Invalid audio samples' });
    }

    const audioData = new Float32Array(samples);
    const result = device.processAudio(audioData);

    res.json({
      success: true,
      data: result,
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * POST /api/vibration/execute
 * Execute a vibration command
 */
app.post('/api/vibration/execute', (req, res) => {
  try {
    const { vibrationCommand } = req.body;

    if (!vibrationCommand) {
      return res.status(400).json({ error: 'Vibration command required' });
    }

    const result = device.executeVibration(vibrationCommand);

    res.json({
      success: true,
      data: result,
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * GET /api/device/status
 * Get current device status
 */
app.get('/api/device/status', (req, res) => {
  try {
    const status = device.getStatus();
    res.json({
      success: true,
      data: status,
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * GET /api/device/stats
 * Get session statistics
 */
app.get('/api/device/stats', (req, res) => {
  try {
    const stats = device.getSessionStats();
    res.json({
      success: true,
      data: stats,
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * POST /api/device/mode
 * Set device mode
 */
app.post('/api/device/mode', (req, res) => {
  try {
    const { mode } = req.body;

    if (!mode) {
      return res.status(400).json({ error: 'Mode required' });
    }

    const result = device.setMode(mode);
    res.json({
      success: true,
      data: result,
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * POST /api/device/sensitivity
 * Set device sensitivity
 */
app.post('/api/device/sensitivity', (req, res) => {
  try {
    const { level } = req.body;

    if (level === undefined) {
      return res.status(400).json({ error: 'Sensitivity level required' });
    }

    const result = device.setSensitivity(level);
    res.json({
      success: true,
      data: result,
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * POST /api/device/vibration-toggle
 * Enable/disable vibration
 */
app.post('/api/device/vibration-toggle', (req, res) => {
  try {
    const { enabled } = req.body;

    if (enabled === undefined) {
      return res.status(400).json({ error: 'Enabled flag required' });
    }

    const result = device.setVibrationEnabled(enabled);
    res.json({
      success: true,
      data: result,
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * GET /api/device/locations
 * Get supported vibration locations
 */
app.get('/api/device/locations', (req, res) => {
  try {
    const locations = device.getVibrationLocations();
    res.json({
      success: true,
      data: { locations },
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * POST /api/device/test
 * Run device self-test
 */
app.post('/api/device/test', (req, res) => {
  try {
    const results = device.performSelfTest();
    res.json({
      success: true,
      data: results,
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * GET /health
 * Health check endpoint
 */
app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    service: 'Echo Hearing Aid Prototype',
    timestamp: new Date().toISOString(),
  });
});

/**
 * GET /
 * Root endpoint - serve API documentation
 */
app.get('/', (req, res) => {
  res.send(`
    <!DOCTYPE html>
    <html>
    <head>
      <title>Echo Hearing Aid - API Documentation</title>
      <style>
        body { font-family: Arial, sans-serif; max-width: 1000px; margin: 40px auto; padding: 20px; }
        h1 { color: #333; }
        .endpoint { background: #f5f5f5; padding: 15px; margin: 10px 0; border-left: 4px solid #2196F3; }
        .method { font-weight: bold; color: #2196F3; }
        code { background: #e0e0e0; padding: 2px 6px; border-radius: 3px; }
      </style>
    </head>
    <body>
      <h1>🎧 Echo Hearing Aid Prototype - API Documentation</h1>

      <h2>Overview</h2>
      <p>This is a medical device prototype for a hearing aid that converts audio frequencies into vibration patterns to help users perceive sound through tactile feedback.</p>

      <h2>API Endpoints</h2>

      <div class="endpoint">
        <p><span class="method">POST</span> <code>/api/audio/process</code></p>
        <p>Process audio samples and return vibration command</p>
        <p><strong>Body:</strong> { "samples": [0.1, 0.2, ...] }</p>
      </div>

      <div class="endpoint">
        <p><span class="method">POST</span> <code>/api/vibration/execute</code></p>
        <p>Execute a vibration command on the device</p>
        <p><strong>Body:</strong> { "vibrationCommand": {...} }</p>
      </div>

      <div class="endpoint">
        <p><span class="method">GET</span> <code>/api/device/status</code></p>
        <p>Get current device status and configuration</p>
      </div>

      <div class="endpoint">
        <p><span class="method">GET</span> <code>/api/device/stats</code></p>
        <p>Get session statistics</p>
      </div>

      <div class="endpoint">
        <p><span class="method">POST</span> <code>/api/device/mode</code></p>
        <p>Set device mode (standard, language-learning, music)</p>
        <p><strong>Body:</strong> { "mode": "language-learning" }</p>
      </div>

      <div class="endpoint">
        <p><span class="method">POST</span> <code>/api/device/sensitivity</code></p>
        <p>Set device sensitivity (0.1 - 3.0)</p>
        <p><strong>Body:</strong> { "level": 1.5 }</p>
      </div>

      <div class="endpoint">
        <p><span class="method">POST</span> <code>/api/device/vibration-toggle</code></p>
        <p>Enable or disable vibration feedback</p>
        <p><strong>Body:</strong> { "enabled": true }</p>
      </div>

      <div class="endpoint">
        <p><span class="method">GET</span> <code>/api/device/locations</code></p>
        <p>Get supported vibration locations</p>
      </div>

      <div class="endpoint">
        <p><span class="method">POST</span> <code>/api/device/test</code></p>
        <p>Run device self-test</p>
      </div>

      <h2>Key Features</h2>
      <ul>
        <li>Real-time audio frequency analysis</li>
        <li>Adaptive vibration pattern generation</li>
        <li>Language learning mode with enhanced speech frequencies</li>
        <li>Configurable sensitivity levels</li>
        <li>Multiple vibration locations (chest, wrist, fingertip, temple)</li>
        <li>Session statistics tracking</li>
      </ul>

      <h2>Device Modes</h2>
      <ul>
        <li><strong>Standard:</strong> Normal audio processing</li>
        <li><strong>Language Learning:</strong> Enhanced speech frequency perception</li>
        <li><strong>Music:</strong> Full frequency range emphasis</li>
      </ul>

      <p style="margin-top: 40px; color: #999;">Echo Hearing Aid Prototype v0.1.0</p>
    </body>
    </html>
  `);
});

// Start server
app.listen(PORT, () => {
  console.log(`\n✅ Echo Hearing Aid Server running on http://localhost:${PORT}`);
  console.log(`📚 API Documentation: http://localhost:${PORT}`);
  console.log(`🏥 Health Check: http://localhost:${PORT}/health`);
});

// Graceful shutdown
process.on('SIGINT', () => {
  console.log('\n\nShutting down gracefully...');
  device.shutdown();
  process.exit(0);
});
