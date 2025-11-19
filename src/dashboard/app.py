"""
Echo Universe - Dashboard Application
Flask-based web dashboard for API integration management.
"""

import logging
from datetime import datetime
from flask import Flask, Blueprint, render_template, jsonify, request

import sys
sys.path.insert(0, str(__file__).rsplit("/", 3)[0])

from config.settings import DashboardConfig, EchoMetadata, LOGGING_CONFIG
from src.api_connectors import (
    GitHubConnector,
    OpenAIConnector,
    AnthropicConnector,
    ZapierConnector,
    AutomateConnector,
    OpenSourceConnector
)

# Configure logging
logging.config.dictConfig(LOGGING_CONFIG) if hasattr(logging, 'config') else None
logger = logging.getLogger(__name__)

# Create blueprint for dashboard routes
dashboard_bp = Blueprint(
    'dashboard',
    __name__,
    template_folder='../../templates',
    static_folder='../../static'
)

# Global connector instances
connectors = {}


def init_connectors():
    """Initialize all API connectors."""
    global connectors
    connectors = {
        'github': GitHubConnector(),
        'openai': OpenAIConnector(),
        'anthropic': AnthropicConnector(),
        'zapier': ZapierConnector(),
        'automate': AutomateConnector(),
        'opensource': OpenSourceConnector()
    }
    return connectors


def create_app(config_class=DashboardConfig):
    """
    Application factory for the Echo Universe Dashboard.

    Args:
        config_class: Configuration class to use

    Returns:
        Configured Flask application
    """
    app = Flask(
        __name__,
        template_folder='../../templates',
        static_folder='../../static'
    )

    # Configure app
    app.config['SECRET_KEY'] = config_class.SECRET_KEY
    app.config['DEBUG'] = config_class.DEBUG

    # Initialize connectors
    init_connectors()

    # Register blueprint
    app.register_blueprint(dashboard_bp)

    # Add context processors
    @app.context_processor
    def inject_metadata():
        return {
            'echo_version': EchoMetadata.VERSION,
            'echo_codename': EchoMetadata.CODENAME,
            'current_year': datetime.utcnow().year
        }

    logger.info(f"Echo Universe Dashboard initialized - {EchoMetadata.CODENAME}")
    return app


# Dashboard Routes

@dashboard_bp.route('/')
def index():
    """Main dashboard page."""
    return render_template('dashboard.html', connectors=connectors)


@dashboard_bp.route('/api/status')
def api_status():
    """Get status of all API connectors."""
    status = {}
    for name, connector in connectors.items():
        status[name] = connector.get_status()
    return jsonify({
        'success': True,
        'timestamp': datetime.utcnow().isoformat(),
        'connectors': status
    })


@dashboard_bp.route('/api/test/<connector_name>')
def test_connector(connector_name):
    """Test a specific API connector."""
    if connector_name not in connectors:
        return jsonify({
            'success': False,
            'error': f'Connector "{connector_name}" not found'
        }), 404

    connector = connectors[connector_name]
    result = connector.test_connection()
    return jsonify(result.to_dict())


@dashboard_bp.route('/api/test-all')
def test_all_connectors():
    """Test all API connectors."""
    results = {}
    for name, connector in connectors.items():
        result = connector.test_connection()
        results[name] = result.to_dict()

    return jsonify({
        'success': True,
        'timestamp': datetime.utcnow().isoformat(),
        'results': results
    })


# GitHub Routes

@dashboard_bp.route('/api/github/repos')
def github_repos():
    """List GitHub repositories."""
    result = connectors['github'].list_repositories()
    return jsonify(result.to_dict())


@dashboard_bp.route('/api/github/repo/<path:repo_name>')
def github_repo_detail(repo_name):
    """Get GitHub repository details."""
    result = connectors['github'].get_repository(repo_name)
    return jsonify(result.to_dict())


# AI Routes (OpenAI & Claude)

@dashboard_bp.route('/api/ai/chat', methods=['POST'])
def ai_chat():
    """Send a message to AI (OpenAI or Claude)."""
    data = request.get_json()
    provider = data.get('provider', 'openai')
    message = data.get('message', '')
    system = data.get('system', None)

    if not message:
        return jsonify({'success': False, 'error': 'Message required'}), 400

    if provider == 'openai':
        result = connectors['openai'].simple_prompt(message, system)
    elif provider == 'anthropic':
        result = connectors['anthropic'].simple_prompt(message, system)
    else:
        return jsonify({'success': False, 'error': f'Unknown provider: {provider}'}), 400

    return jsonify(result.to_dict())


@dashboard_bp.route('/api/ai/analyze-code', methods=['POST'])
def analyze_code():
    """Analyze code using AI."""
    data = request.get_json()
    code = data.get('code', '')
    language = data.get('language', 'python')
    provider = data.get('provider', 'openai')

    if not code:
        return jsonify({'success': False, 'error': 'Code required'}), 400

    if provider == 'openai':
        result = connectors['openai'].analyze_code(code, language)
    elif provider == 'anthropic':
        result = connectors['anthropic'].code_review(code, language)
    else:
        return jsonify({'success': False, 'error': f'Unknown provider: {provider}'}), 400

    return jsonify(result.to_dict())


# Zapier Routes

@dashboard_bp.route('/api/zapier/trigger', methods=['POST'])
def zapier_trigger():
    """Trigger a Zapier webhook."""
    data = request.get_json()
    webhook_name = data.get('webhook_name')
    payload = data.get('payload', {})

    if webhook_name:
        result = connectors['zapier'].trigger_named_webhook(webhook_name, payload)
    else:
        result = connectors['zapier'].trigger_webhook(payload)

    return jsonify(result.to_dict())


@dashboard_bp.route('/api/zapier/register', methods=['POST'])
def zapier_register():
    """Register a Zapier webhook."""
    data = request.get_json()
    name = data.get('name')
    url = data.get('url')

    if not name or not url:
        return jsonify({'success': False, 'error': 'Name and URL required'}), 400

    result = connectors['zapier'].register_webhook(name, url)
    return jsonify(result.to_dict())


# Power Automate Routes

@dashboard_bp.route('/api/automate/trigger', methods=['POST'])
def automate_trigger():
    """Trigger a Power Automate flow."""
    data = request.get_json()
    flow_url = data.get('flow_url')
    payload = data.get('payload', {})

    if not flow_url:
        return jsonify({'success': False, 'error': 'Flow URL required'}), 400

    result = connectors['automate'].trigger_http_flow(flow_url, payload)
    return jsonify(result.to_dict())


@dashboard_bp.route('/api/automate/teams', methods=['POST'])
def teams_message():
    """Send a message to Microsoft Teams."""
    data = request.get_json()
    webhook_url = data.get('webhook_url')
    message = data.get('message')
    title = data.get('title', 'Echo Universe')

    if not webhook_url or not message:
        return jsonify({'success': False, 'error': 'Webhook URL and message required'}), 400

    result = connectors['automate'].send_teams_message(webhook_url, message, title)
    return jsonify(result.to_dict())


# Open Source API Routes

@dashboard_bp.route('/api/opensource/list')
def opensource_list():
    """List registered open-source APIs."""
    result = connectors['opensource'].list_registered_apis()
    return jsonify(result.to_dict())


@dashboard_bp.route('/api/opensource/call', methods=['POST'])
def opensource_call():
    """Call a registered open-source API."""
    data = request.get_json()
    api_name = data.get('api_name')
    endpoint = data.get('endpoint')
    method = data.get('method', 'GET')
    payload = data.get('data')
    params = data.get('params')

    if not api_name or not endpoint:
        return jsonify({'success': False, 'error': 'API name and endpoint required'}), 400

    result = connectors['opensource'].call_api(
        api_name, endpoint, method, payload, params
    )
    return jsonify(result.to_dict())


@dashboard_bp.route('/api/opensource/ollama', methods=['POST'])
def ollama_generate():
    """Generate text using Ollama."""
    data = request.get_json()
    prompt = data.get('prompt')
    model = data.get('model', 'llama2')

    if not prompt:
        return jsonify({'success': False, 'error': 'Prompt required'}), 400

    result = connectors['opensource'].ollama_generate(prompt, model)
    return jsonify(result.to_dict())


# Echo Universe Routes

@dashboard_bp.route('/api/echo/metadata')
def echo_metadata():
    """Get Echo Universe metadata."""
    return jsonify({
        'success': True,
        'version': EchoMetadata.VERSION,
        'codename': EchoMetadata.CODENAME,
        'fabric_of_zero': EchoMetadata.FABRIC_OF_ZERO,
        'harmonic_directives': EchoMetadata.HARMONIC_DIRECTIVES,
        'components': EchoMetadata.COMPONENTS
    })


@dashboard_bp.route('/api/echo/harmonic-analysis', methods=['POST'])
def harmonic_analysis():
    """Perform harmonic analysis using Claude."""
    data = request.get_json()
    content = data.get('content')

    if not content:
        return jsonify({'success': False, 'error': 'Content required'}), 400

    result = connectors['anthropic'].harmonic_analysis(content)
    return jsonify(result.to_dict())


# Main entry point
if __name__ == '__main__':
    app = create_app()
    app.run(
        host=DashboardConfig.HOST,
        port=DashboardConfig.PORT,
        debug=DashboardConfig.DEBUG
    )
