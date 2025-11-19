"""
Hydra Dashboard API
===================

RESTful API endpoints for the Hydra dashboard.
"""

try:
    from flask import Blueprint, jsonify, request
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    # Create dummy Blueprint for type hints
    class Blueprint:
        pass

from typing import Any, Dict

# Create blueprint
if FLASK_AVAILABLE:
    api_blueprint = Blueprint('api', __name__, url_prefix='/api')
else:
    api_blueprint = None


def create_api_blueprint(orchestrator: Any) -> Blueprint:
    """Create API blueprint with orchestrator access"""
    if not FLASK_AVAILABLE:
        raise ImportError("Flask required for API")

    bp = Blueprint('api', __name__, url_prefix='/api')

    @bp.route('/health')
    def health():
        """Health check endpoint"""
        return jsonify({
            "status": "healthy",
            "service": "hydra"
        })

    @bp.route('/status')
    def status():
        """Get system status"""
        return jsonify(orchestrator.get_status())

    @bp.route('/tentacles')
    def list_tentacles():
        """List all tentacles"""
        tentacles = []
        for tid in orchestrator.list_tentacles():
            tentacle = orchestrator.get_tentacle(tid)
            if tentacle:
                tentacles.append(tentacle.get_info())
        return jsonify(tentacles)

    @bp.route('/tentacle/<tentacle_id>')
    def get_tentacle(tentacle_id: str):
        """Get tentacle details"""
        tentacle = orchestrator.get_tentacle(tentacle_id)
        if not tentacle:
            return jsonify({"error": "Tentacle not found"}), 404
        return jsonify(tentacle.get_info())

    @bp.route('/tentacle/<tentacle_id>/mode', methods=['PUT'])
    def set_tentacle_mode(tentacle_id: str):
        """Set tentacle mode"""
        data = request.json
        mode = data.get('mode')
        # Implementation would go here
        return jsonify({"status": "updated"})

    @bp.route('/execute', methods=['POST'])
    def execute_task():
        """Execute a task"""
        data = request.json

        import asyncio
        loop = asyncio.new_event_loop()

        try:
            result = loop.run_until_complete(
                orchestrator.execute(
                    task_type=data.get('type', 'general'),
                    payload=data.get('payload', {}),
                    timeout=data.get('timeout', 60)
                )
            )

            return jsonify({
                "task_id": result.task_id,
                "success": result.success,
                "data": result.data,
                "error": result.error
            })
        finally:
            loop.close()

    @bp.route('/swarms')
    def list_swarms():
        """List all swarms"""
        if hasattr(orchestrator, 'swarm_factory'):
            return jsonify(orchestrator.swarm_factory.list_swarms())
        return jsonify([])

    @bp.route('/swarm/templates')
    def list_templates():
        """List swarm templates"""
        if hasattr(orchestrator, 'swarm_factory'):
            return jsonify(orchestrator.swarm_factory.list_templates())
        return jsonify([])

    @bp.route('/swarm/create', methods=['POST'])
    def create_swarm():
        """Create a new swarm"""
        data = request.json
        template = data.get('template')

        if not hasattr(orchestrator, 'swarm_factory'):
            return jsonify({"error": "Swarm factory not available"}), 500

        import asyncio
        loop = asyncio.new_event_loop()

        try:
            swarm_id = loop.run_until_complete(
                orchestrator.swarm_factory.create_swarm(template_name=template)
            )
            return jsonify({"swarm_id": swarm_id})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        finally:
            loop.close()

    @bp.route('/swarm/<swarm_id>')
    def get_swarm(swarm_id: str):
        """Get swarm status"""
        if not hasattr(orchestrator, 'swarm_factory'):
            return jsonify({"error": "Swarm factory not available"}), 500

        status = orchestrator.swarm_factory.get_swarm_status(swarm_id)
        if not status:
            return jsonify({"error": "Swarm not found"}), 404

        return jsonify(status)

    @bp.route('/swarm/<swarm_id>/mission', methods=['POST'])
    def execute_mission(swarm_id: str):
        """Execute a mission with a swarm"""
        data = request.json
        mission = data.get('mission', {})

        if not hasattr(orchestrator, 'swarm_factory'):
            return jsonify({"error": "Swarm factory not available"}), 500

        import asyncio
        loop = asyncio.new_event_loop()

        try:
            result = loop.run_until_complete(
                orchestrator.swarm_factory.execute_mission(swarm_id, mission)
            )
            return jsonify(result)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        finally:
            loop.close()

    @bp.route('/swarm/<swarm_id>', methods=['DELETE'])
    def dissolve_swarm(swarm_id: str):
        """Dissolve a swarm"""
        if not hasattr(orchestrator, 'swarm_factory'):
            return jsonify({"error": "Swarm factory not available"}), 500

        import asyncio
        loop = asyncio.new_event_loop()

        try:
            success = loop.run_until_complete(
                orchestrator.swarm_factory.dissolve_swarm(swarm_id)
            )
            return jsonify({"success": success})
        finally:
            loop.close()

    return bp
