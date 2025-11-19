"""
Hydra Dashboard Application
===========================

Main Flask/FastAPI application for the control center.
"""

from typing import Any, Dict, Optional
import asyncio
import logging
from datetime import datetime

try:
    from flask import Flask, render_template_string, jsonify, request
    from flask_socketio import SocketIO, emit
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

from ..config import DashboardConfig
from ..core.orchestrator import HydraOrchestrator


# Dashboard HTML Template
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hydra Control Center</title>
    <style>
        :root {
            --bg-dark: #0a0a0f;
            --bg-card: #12121a;
            --accent: #00ff88;
            --accent-dim: #00aa55;
            --text: #e0e0e0;
            --text-dim: #888;
            --danger: #ff4444;
            --warning: #ffaa00;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            background: var(--bg-dark);
            color: var(--text);
            font-family: 'Courier New', monospace;
            min-height: 100vh;
        }

        .header {
            background: linear-gradient(90deg, var(--bg-card), transparent);
            padding: 20px;
            border-bottom: 1px solid var(--accent-dim);
        }

        .header h1 {
            color: var(--accent);
            font-size: 2em;
            text-shadow: 0 0 10px var(--accent);
        }

        .header .subtitle {
            color: var(--text-dim);
            font-size: 0.9em;
        }

        .container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            padding: 20px;
        }

        .card {
            background: var(--bg-card);
            border: 1px solid #333;
            border-radius: 8px;
            padding: 20px;
            transition: border-color 0.3s;
        }

        .card:hover {
            border-color: var(--accent-dim);
        }

        .card h2 {
            color: var(--accent);
            font-size: 1.2em;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid #333;
        }

        .tentacle-list {
            list-style: none;
        }

        .tentacle-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px;
            margin: 5px 0;
            background: rgba(0, 255, 136, 0.05);
            border-radius: 4px;
        }

        .tentacle-name {
            font-weight: bold;
        }

        .status {
            padding: 3px 8px;
            border-radius: 3px;
            font-size: 0.8em;
        }

        .status-active {
            background: var(--accent);
            color: var(--bg-dark);
        }

        .status-dormant {
            background: var(--text-dim);
            color: var(--bg-dark);
        }

        .status-open {
            background: var(--danger);
            color: white;
        }

        .metric {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #222;
        }

        .metric-value {
            color: var(--accent);
            font-weight: bold;
        }

        .swarm-control {
            margin-top: 15px;
        }

        .btn {
            background: var(--accent-dim);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 4px;
            cursor: pointer;
            font-family: inherit;
            margin: 5px;
            transition: background 0.3s;
        }

        .btn:hover {
            background: var(--accent);
            color: var(--bg-dark);
        }

        .btn-danger {
            background: var(--danger);
        }

        .terminal {
            background: #000;
            border: 1px solid #333;
            border-radius: 4px;
            padding: 15px;
            font-size: 0.85em;
            max-height: 300px;
            overflow-y: auto;
        }

        .terminal-line {
            padding: 2px 0;
        }

        .terminal-line.info {
            color: var(--accent);
        }

        .terminal-line.warning {
            color: var(--warning);
        }

        .terminal-line.error {
            color: var(--danger);
        }

        .input-group {
            display: flex;
            gap: 10px;
            margin-top: 10px;
        }

        .input-group input {
            flex: 1;
            background: #000;
            border: 1px solid #333;
            color: var(--text);
            padding: 10px;
            border-radius: 4px;
            font-family: inherit;
        }

        .input-group input:focus {
            outline: none;
            border-color: var(--accent);
        }

        .grid-2 {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }

        .live-indicator {
            width: 8px;
            height: 8px;
            background: var(--accent);
            border-radius: 50%;
            display: inline-block;
            animation: pulse 2s infinite;
            margin-right: 8px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🐙 HYDRA CONTROL CENTER</h1>
        <div class="subtitle">
            <span class="live-indicator"></span>
            Multi-AI Fusion Cybersecurity System | Codename: Moses
        </div>
    </div>

    <div class="container">
        <!-- System Status -->
        <div class="card">
            <h2>⚡ System Status</h2>
            <div class="metric">
                <span>Status</span>
                <span class="metric-value" id="system-status">Loading...</span>
            </div>
            <div class="metric">
                <span>Uptime</span>
                <span class="metric-value" id="uptime">--</span>
            </div>
            <div class="metric">
                <span>Active Tentacles</span>
                <span class="metric-value" id="active-tentacles">0</span>
            </div>
            <div class="metric">
                <span>Tasks Completed</span>
                <span class="metric-value" id="tasks-completed">0</span>
            </div>
            <div class="metric">
                <span>Tokens/min</span>
                <span class="metric-value" id="tokens-per-min">0</span>
            </div>
        </div>

        <!-- Tentacles -->
        <div class="card">
            <h2>🦑 Tentacles</h2>
            <ul class="tentacle-list" id="tentacle-list">
                <li class="tentacle-item">
                    <span>Loading tentacles...</span>
                </li>
            </ul>
        </div>

        <!-- Swarm Control -->
        <div class="card">
            <h2>🐝 Swarm Control</h2>
            <div class="grid-2">
                <button class="btn" onclick="createSwarm('pentest')">+ Pentest Swarm</button>
                <button class="btn" onclick="createSwarm('forensics')">+ Forensics Swarm</button>
                <button class="btn" onclick="createSwarm('audit')">+ Audit Swarm</button>
                <button class="btn" onclick="createSwarm('recon')">+ Recon Swarm</button>
            </div>
            <div id="active-swarms" style="margin-top: 15px;">
                <div class="metric">
                    <span>Active Swarms</span>
                    <span class="metric-value" id="swarm-count">0</span>
                </div>
            </div>
        </div>

        <!-- Quick Actions -->
        <div class="card">
            <h2>🎯 Quick Actions</h2>
            <div class="input-group">
                <input type="text" id="target-input" placeholder="Enter target (IP/domain)">
                <button class="btn" onclick="quickRecon()">Recon</button>
            </div>
            <div class="input-group">
                <input type="text" id="cve-input" placeholder="CVE ID (e.g., CVE-2024-1234)">
                <button class="btn" onclick="lookupCVE()">Lookup</button>
            </div>
            <div class="swarm-control">
                <button class="btn" onclick="emergencyStop()">⚠️ Emergency Stop</button>
            </div>
        </div>

        <!-- Activity Log -->
        <div class="card" style="grid-column: span 2;">
            <h2>📜 Activity Log</h2>
            <div class="terminal" id="activity-log">
                <div class="terminal-line info">[SYSTEM] Hydra Control Center initialized</div>
                <div class="terminal-line info">[SYSTEM] Waiting for connection...</div>
            </div>
        </div>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <script>
        // Socket.IO connection
        const socket = io();

        // Update functions
        function updateStatus(data) {
            document.getElementById('system-status').textContent = data.running ? 'ONLINE' : 'OFFLINE';
            document.getElementById('uptime').textContent = formatUptime(data.uptime_seconds);
            document.getElementById('active-tentacles').textContent = data.tentacles?.count || 0;
            document.getElementById('tasks-completed').textContent = data.brain?.tasks_completed || 0;
            document.getElementById('tokens-per-min').textContent = data.load?.tokens_per_minute || 0;

            // Update tentacle list
            updateTentacleList(data.tentacles);
        }

        function updateTentacleList(tentacles) {
            if (!tentacles || !tentacles.health) return;

            const list = document.getElementById('tentacle-list');
            list.innerHTML = '';

            for (const [id, health] of Object.entries(tentacles.health)) {
                const item = document.createElement('li');
                item.className = 'tentacle-item';

                const statusClass = health.state === 'closed' ? 'status-active' :
                                   health.state === 'open' ? 'status-open' : 'status-dormant';

                item.innerHTML = `
                    <span class="tentacle-name">${id}</span>
                    <span>
                        <span class="status ${statusClass}">${health.state}</span>
                        <span style="margin-left: 10px; color: var(--text-dim);">
                            ${(health.success_rate * 100).toFixed(0)}%
                        </span>
                    </span>
                `;
                list.appendChild(item);
            }
        }

        function formatUptime(seconds) {
            if (!seconds) return '--';
            const h = Math.floor(seconds / 3600);
            const m = Math.floor((seconds % 3600) / 60);
            const s = Math.floor(seconds % 60);
            return `${h}h ${m}m ${s}s`;
        }

        function addLog(message, type = 'info') {
            const log = document.getElementById('activity-log');
            const line = document.createElement('div');
            line.className = `terminal-line ${type}`;
            const time = new Date().toLocaleTimeString();
            line.textContent = `[${time}] ${message}`;
            log.appendChild(line);
            log.scrollTop = log.scrollHeight;
        }

        // Actions
        async function createSwarm(template) {
            addLog(`Creating ${template} swarm...`);
            try {
                const response = await fetch('/api/swarm/create', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({template: template})
                });
                const data = await response.json();
                addLog(`Swarm created: ${data.swarm_id}`, 'info');
                updateSwarmCount();
            } catch (e) {
                addLog(`Error creating swarm: ${e}`, 'error');
            }
        }

        async function quickRecon() {
            const target = document.getElementById('target-input').value;
            if (!target) {
                addLog('Please enter a target', 'warning');
                return;
            }
            addLog(`Starting reconnaissance on ${target}...`);
            try {
                const response = await fetch('/api/task/recon', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({target: target})
                });
                const data = await response.json();
                addLog(`Recon task submitted: ${data.task_id}`, 'info');
            } catch (e) {
                addLog(`Error: ${e}`, 'error');
            }
        }

        async function lookupCVE() {
            const cve = document.getElementById('cve-input').value;
            if (!cve) {
                addLog('Please enter a CVE ID', 'warning');
                return;
            }
            addLog(`Looking up ${cve}...`);
            // API call would go here
        }

        function emergencyStop() {
            if (confirm('Are you sure you want to emergency stop all operations?')) {
                addLog('EMERGENCY STOP ACTIVATED', 'error');
                fetch('/api/system/stop', {method: 'POST'});
            }
        }

        function updateSwarmCount() {
            fetch('/api/swarms')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('swarm-count').textContent = data.length || 0;
                });
        }

        // Socket events
        socket.on('connect', () => {
            addLog('Connected to Hydra backend', 'info');
        });

        socket.on('status_update', (data) => {
            updateStatus(data);
        });

        socket.on('log', (data) => {
            addLog(data.message, data.type);
        });

        // Initial load
        fetch('/api/status')
            .then(r => r.json())
            .then(updateStatus)
            .catch(() => addLog('Failed to connect to backend', 'error'));

        updateSwarmCount();

        // Periodic refresh
        setInterval(() => {
            fetch('/api/status')
                .then(r => r.json())
                .then(updateStatus)
                .catch(() => {});
        }, 5000);
    </script>
</body>
</html>
"""


class HydraDashboard:
    """
    Web dashboard for the Hydra control center.
    """

    def __init__(
        self,
        orchestrator: HydraOrchestrator,
        config: Optional[DashboardConfig] = None
    ):
        self.orchestrator = orchestrator
        self.config = config or DashboardConfig()
        self.logger = logging.getLogger("hydra.dashboard")

        self.app = None
        self.socketio = None

    def create_app(self) -> Any:
        """Create and configure the Flask app"""
        if not FLASK_AVAILABLE:
            raise ImportError("Flask and Flask-SocketIO required for dashboard")

        app = Flask(__name__)
        app.secret_key = self.config.secret_key

        socketio = SocketIO(app, cors_allowed_origins="*")

        self.app = app
        self.socketio = socketio

        # Register routes
        self._register_routes(app)
        self._register_socket_events(socketio)

        return app

    def _register_routes(self, app: Flask) -> None:
        """Register HTTP routes"""

        @app.route("/")
        def index():
            return render_template_string(DASHBOARD_HTML)

        @app.route("/api/status")
        def get_status():
            return jsonify(self.orchestrator.get_status())

        @app.route("/api/tentacles")
        def get_tentacles():
            return jsonify(self.orchestrator.list_tentacles())

        @app.route("/api/swarms")
        def get_swarms():
            if hasattr(self.orchestrator, 'swarm_factory'):
                return jsonify(self.orchestrator.swarm_factory.list_swarms())
            return jsonify([])

        @app.route("/api/swarm/create", methods=["POST"])
        def create_swarm():
            data = request.json
            template = data.get("template", "recon")

            if hasattr(self.orchestrator, 'swarm_factory'):
                loop = asyncio.new_event_loop()
                swarm_id = loop.run_until_complete(
                    self.orchestrator.swarm_factory.create_swarm(template_name=template)
                )
                loop.close()
                return jsonify({"swarm_id": swarm_id})

            return jsonify({"error": "Swarm factory not available"}), 500

        @app.route("/api/task/recon", methods=["POST"])
        def submit_recon():
            data = request.json
            target = data.get("target", "")

            # Submit to orchestrator
            loop = asyncio.new_event_loop()
            result = loop.run_until_complete(
                self.orchestrator.execute(
                    task_type="recon",
                    payload={"type": "basic", "target": target},
                    timeout=60
                )
            )
            loop.close()

            return jsonify({
                "task_id": result.task_id,
                "success": result.success
            })

        @app.route("/api/system/stop", methods=["POST"])
        def emergency_stop():
            loop = asyncio.new_event_loop()
            loop.run_until_complete(self.orchestrator.stop())
            loop.close()
            return jsonify({"status": "stopped"})

    def _register_socket_events(self, socketio: SocketIO) -> None:
        """Register WebSocket events"""

        @socketio.on("connect")
        def handle_connect():
            status = self.orchestrator.get_status()
            emit("status_update", status)

        @socketio.on("request_status")
        def handle_status_request():
            status = self.orchestrator.get_status()
            emit("status_update", status)

    def run(self, host: Optional[str] = None, port: Optional[int] = None) -> None:
        """Run the dashboard server"""
        if not self.app:
            self.create_app()

        host = host or self.config.host
        port = port or self.config.port

        self.logger.info(f"Starting dashboard on http://{host}:{port}")

        self.socketio.run(
            self.app,
            host=host,
            port=port,
            debug=self.config.debug
        )

    def broadcast_status(self) -> None:
        """Broadcast status update to all connected clients"""
        if self.socketio:
            status = self.orchestrator.get_status()
            self.socketio.emit("status_update", status)

    def broadcast_log(self, message: str, log_type: str = "info") -> None:
        """Broadcast a log message to all clients"""
        if self.socketio:
            self.socketio.emit("log", {"message": message, "type": log_type})


def create_app(orchestrator: HydraOrchestrator) -> Any:
    """Factory function to create dashboard app"""
    dashboard = HydraDashboard(orchestrator)
    return dashboard.create_app()
