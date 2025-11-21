#!/usr/bin/env python3
"""
Echo External Watchdog Service
Independent monitoring system that validates:
1. GitHub Actions are running successfully
2. Profit engines are generating expected revenue
3. Critical services are responding
4. Secrets are not being exposed in logs

Deploy this OUTSIDE GitHub (Render, Vercel, AWS Lambda)
"""

import os
import re
import time
import requests
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('echo.watchdog')


class AlertPriority(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class HealthStatus:
    """Health check result"""
    service: str
    healthy: bool
    message: str
    checked_at: datetime
    response_time_ms: Optional[float] = None


class EchoWatchdog:
    """External monitoring and alerting system"""

    def __init__(self):
        # Alert channels configuration
        self.alert_channels = {
            'slack': os.getenv('SLACK_WEBHOOK_URL'),
            'email': os.getenv('ALERT_EMAIL'),
            'sms': os.getenv('TWILIO_PHONE_NUMBER'),
        }

        # GitHub configuration
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.github_repo = os.getenv('GITHUB_REPO', 'username/Echo')

        # Service endpoints to monitor
        self.service_endpoints = {
            'render_app': os.getenv('RENDER_APP_URL'),
            'vercel_site': os.getenv('VERCEL_SITE_URL'),
            'aws_lambda': os.getenv('AWS_LAMBDA_HEALTH_URL'),
        }

        # Stripe/Gumroad API keys
        self.stripe_key = os.getenv('STRIPE_SECRET_KEY')
        self.gumroad_key = os.getenv('GUMROAD_API_KEY')

        # Check interval (seconds)
        self.check_interval = int(os.getenv('CHECK_INTERVAL', '300'))  # 5 min

        # Secret patterns to detect
        self.secret_patterns = [
            r'(?i)(api[_-]?key|secret[_-]?key)\s*[:=]\s*["\']?[\w-]{20,}',
            r'(?i)stripe_[a-z]+_[a-zA-Z0-9]{24,}',
            r'(?i)sk-[a-zA-Z0-9]{48}',  # OpenAI keys
            r'(?i)AKIA[0-9A-Z]{16}',  # AWS access keys
            r'(?i)ghp_[a-zA-Z0-9]{36}',  # GitHub personal access tokens
        ]

    def run_forever(self):
        """Main monitoring loop"""
        logger.info("🔍 Echo Watchdog started")
        logger.info(f"Check interval: {self.check_interval} seconds")

        while True:
            try:
                self.run_all_checks()
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                self.alert(
                    AlertPriority.CRITICAL,
                    f"Watchdog loop error: {str(e)}"
                )

            time.sleep(self.check_interval)

    def run_all_checks(self):
        """Execute all monitoring checks"""
        logger.info("--- Running health checks ---")

        # Check 1: GitHub Actions health
        github_status = self.check_github_health()
        if not github_status.healthy:
            self.alert(
                AlertPriority.CRITICAL,
                f"GitHub Actions issue: {github_status.message}"
            )

        # Check 2: Service endpoints
        for service_name, endpoint in self.service_endpoints.items():
            if endpoint:
                service_status = self.check_service_health(service_name, endpoint)
                if not service_status.healthy:
                    self.alert(
                        AlertPriority.WARNING,
                        f"{service_name} unhealthy: {service_status.message}"
                    )

        # Check 3: Profit flows
        profit_status = self.check_profit_flows()
        if not profit_status.healthy:
            self.alert(
                AlertPriority.WARNING,
                f"Profit flow issue: {profit_status.message}"
            )

        # Check 4: Secrets exposure scan
        secrets_exposed = self.check_secrets_exposure()
        if secrets_exposed:
            self.alert(
                AlertPriority.CRITICAL,
                f"⚠️ POTENTIAL SECRET EXPOSURE DETECTED: {secrets_exposed}"
            )

        logger.info("--- Health checks complete ---\n")

    def check_github_health(self) -> HealthStatus:
        """Verify GitHub Actions are running as expected"""
        if not self.github_token:
            return HealthStatus(
                service='github',
                healthy=False,
                message='GitHub token not configured',
                checked_at=datetime.now()
            )

        try:
            # Get recent workflow runs
            url = f'https://api.github.com/repos/{self.github_repo}/actions/runs'
            headers = {
                'Authorization': f'token {self.github_token}',
                'Accept': 'application/vnd.github.v3+json'
            }

            start_time = time.time()
            response = requests.get(url, headers=headers, timeout=10)
            response_time = (time.time() - start_time) * 1000

            if response.status_code != 200:
                return HealthStatus(
                    service='github',
                    healthy=False,
                    message=f'API returned {response.status_code}',
                    checked_at=datetime.now(),
                    response_time_ms=response_time
                )

            data = response.json()
            workflow_runs = data.get('workflow_runs', [])

            if not workflow_runs:
                return HealthStatus(
                    service='github',
                    healthy=False,
                    message='No workflow runs found',
                    checked_at=datetime.now(),
                    response_time_ms=response_time
                )

            # Check most recent run
            latest_run = workflow_runs[0]
            run_time = datetime.fromisoformat(
                latest_run['created_at'].replace('Z', '+00:00')
            )
            time_since_run = datetime.now(run_time.tzinfo) - run_time

            # Alert if no runs in last 24 hours
            if time_since_run > timedelta(hours=24):
                return HealthStatus(
                    service='github',
                    healthy=False,
                    message=f'No runs in {time_since_run.total_seconds() / 3600:.1f} hours',
                    checked_at=datetime.now(),
                    response_time_ms=response_time
                )

            # Check for failed runs
            if latest_run['conclusion'] == 'failure':
                return HealthStatus(
                    service='github',
                    healthy=False,
                    message=f'Latest run failed: {latest_run["name"]}',
                    checked_at=datetime.now(),
                    response_time_ms=response_time
                )

            logger.info(f"✅ GitHub Actions healthy (response: {response_time:.0f}ms)")
            return HealthStatus(
                service='github',
                healthy=True,
                message='All checks passed',
                checked_at=datetime.now(),
                response_time_ms=response_time
            )

        except Exception as e:
            logger.error(f"GitHub health check failed: {e}")
            return HealthStatus(
                service='github',
                healthy=False,
                message=str(e),
                checked_at=datetime.now()
            )

    def check_service_health(self, service_name: str, endpoint: str) -> HealthStatus:
        """Check if a service endpoint is responding"""
        try:
            # Add /health to endpoint if not present
            health_url = endpoint
            if not endpoint.endswith('/health'):
                health_url = f"{endpoint.rstrip('/')}/health"

            start_time = time.time()
            response = requests.get(health_url, timeout=10)
            response_time = (time.time() - start_time) * 1000

            if response.status_code == 200:
                logger.info(
                    f"✅ {service_name} healthy (response: {response_time:.0f}ms)"
                )
                return HealthStatus(
                    service=service_name,
                    healthy=True,
                    message='Service responding',
                    checked_at=datetime.now(),
                    response_time_ms=response_time
                )
            else:
                return HealthStatus(
                    service=service_name,
                    healthy=False,
                    message=f'HTTP {response.status_code}',
                    checked_at=datetime.now(),
                    response_time_ms=response_time
                )

        except requests.exceptions.Timeout:
            return HealthStatus(
                service=service_name,
                healthy=False,
                message='Request timeout (>10s)',
                checked_at=datetime.now()
            )
        except Exception as e:
            return HealthStatus(
                service=service_name,
                healthy=False,
                message=str(e),
                checked_at=datetime.now()
            )

    def check_profit_flows(self) -> HealthStatus:
        """Verify revenue streams are active"""
        issues = []

        # Check Stripe recent activity
        if self.stripe_key:
            try:
                stripe_url = 'https://api.stripe.com/v1/events'
                headers = {
                    'Authorization': f'Bearer {self.stripe_key}'
                }
                params = {
                    'limit': 10,
                    'created[gte]': int((datetime.now() - timedelta(days=1)).timestamp())
                }

                response = requests.get(
                    stripe_url,
                    headers=headers,
                    params=params,
                    timeout=10
                )

                if response.status_code == 200:
                    events = response.json().get('data', [])
                    if not events:
                        issues.append('No Stripe events in 24 hours')
                    else:
                        logger.info(f"✅ Stripe active ({len(events)} recent events)")
                else:
                    issues.append(f'Stripe API error: {response.status_code}')

            except Exception as e:
                issues.append(f'Stripe check failed: {str(e)}')

        # Check Gumroad recent activity
        if self.gumroad_key:
            try:
                gumroad_url = 'https://api.gumroad.com/v2/sales'
                params = {
                    'access_token': self.gumroad_key
                }

                response = requests.get(gumroad_url, params=params, timeout=10)

                if response.status_code == 200:
                    sales = response.json().get('sales', [])
                    # Filter last 24 hours
                    recent_sales = [
                        s for s in sales
                        if datetime.fromisoformat(s['created_at']) > datetime.now() - timedelta(days=1)
                    ]
                    if not recent_sales:
                        issues.append('No Gumroad sales in 24 hours')
                    else:
                        logger.info(f"✅ Gumroad active ({len(recent_sales)} recent sales)")
                else:
                    issues.append(f'Gumroad API error: {response.status_code}')

            except Exception as e:
                issues.append(f'Gumroad check failed: {str(e)}')

        if issues:
            return HealthStatus(
                service='profit_flows',
                healthy=False,
                message='; '.join(issues),
                checked_at=datetime.now()
            )

        logger.info("✅ Profit flows healthy")
        return HealthStatus(
            service='profit_flows',
            healthy=True,
            message='All revenue streams active',
            checked_at=datetime.now()
        )

    def check_secrets_exposure(self) -> Optional[str]:
        """Scan GitHub Actions logs for potential secret leaks"""
        if not self.github_token:
            return None

        try:
            # Get recent workflow runs
            url = f'https://api.github.com/repos/{self.github_repo}/actions/runs'
            headers = {
                'Authorization': f'token {self.github_token}',
                'Accept': 'application/vnd.github.v3+json'
            }

            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                return None

            workflow_runs = response.json().get('workflow_runs', [])[:5]  # Check last 5

            for run in workflow_runs:
                # Get logs for this run
                logs_url = run.get('logs_url')
                if not logs_url:
                    continue

                logs_response = requests.get(logs_url, headers=headers, timeout=10)
                if logs_response.status_code != 200:
                    continue

                # Scan logs for secret patterns
                logs_text = logs_response.text

                for pattern in self.secret_patterns:
                    matches = re.findall(pattern, logs_text)
                    if matches:
                        logger.critical(
                            f"⚠️ POTENTIAL SECRET IN LOGS: {run['name']} "
                            f"(run #{run['run_number']})"
                        )
                        return f"Pattern matched in {run['name']}"

            logger.info("✅ No secrets detected in recent logs")
            return None

        except Exception as e:
            logger.error(f"Secrets scan failed: {e}")
            return None

    def alert(self, priority: AlertPriority, message: str):
        """Send alert through configured channels"""
        timestamp = datetime.now().isoformat()
        alert_message = f"[{priority.value.upper()}] {timestamp}\n{message}"

        logger.log(
            logging.CRITICAL if priority == AlertPriority.CRITICAL else logging.WARNING,
            alert_message
        )

        # Send to Slack
        if self.alert_channels['slack']:
            self._send_slack_alert(priority, message)

        # Send email (would integrate with SendGrid/SES)
        if self.alert_channels['email']:
            self._send_email_alert(priority, message)

        # Send SMS for critical alerts (would integrate with Twilio)
        if priority == AlertPriority.CRITICAL and self.alert_channels['sms']:
            self._send_sms_alert(message)

    def _send_slack_alert(self, priority: AlertPriority, message: str):
        """Send alert to Slack"""
        webhook_url = self.alert_channels['slack']
        if not webhook_url:
            return

        color = {
            AlertPriority.INFO: '#36a64f',
            AlertPriority.WARNING: '#ff9900',
            AlertPriority.CRITICAL: '#ff0000',
        }[priority]

        payload = {
            'attachments': [{
                'color': color,
                'title': f'Echo Watchdog Alert - {priority.value.upper()}',
                'text': message,
                'footer': 'Echo Watchdog',
                'ts': int(datetime.now().timestamp())
            }]
        }

        try:
            response = requests.post(webhook_url, json=payload, timeout=10)
            if response.status_code == 200:
                logger.info("✅ Slack alert sent")
            else:
                logger.error(f"Slack alert failed: {response.status_code}")
        except Exception as e:
            logger.error(f"Slack alert error: {e}")

    def _send_email_alert(self, priority: AlertPriority, message: str):
        """Send email alert (placeholder for SendGrid/SES integration)"""
        # TODO: Integrate with SendGrid or AWS SES
        logger.info(f"Email alert would be sent to {self.alert_channels['email']}")

    def _send_sms_alert(self, message: str):
        """Send SMS alert (placeholder for Twilio integration)"""
        # TODO: Integrate with Twilio
        logger.info(f"SMS alert would be sent to {self.alert_channels['sms']}")


# Health endpoint for the watchdog itself
class WatchdogAPI:
    """Simple HTTP API for watchdog status"""

    def __init__(self, watchdog: EchoWatchdog):
        self.watchdog = watchdog
        self.last_check_time = None

    def get_status(self) -> Dict:
        """Return watchdog status"""
        return {
            'status': 'healthy',
            'last_check': self.last_check_time.isoformat() if self.last_check_time else None,
            'check_interval_seconds': self.watchdog.check_interval,
            'monitored_services': list(self.watchdog.service_endpoints.keys()),
        }


if __name__ == '__main__':
    import sys

    # Check if running as web service (Render/Vercel) or standalone
    if os.getenv('PORT'):
        # Web service mode - provide health endpoint
        from flask import Flask, jsonify

        app = Flask(__name__)
        watchdog = EchoWatchdog()
        api = WatchdogAPI(watchdog)

        @app.route('/health')
        def health():
            return jsonify(api.get_status())

        @app.route('/trigger-check')
        def trigger_check():
            """Manually trigger a check"""
            watchdog.run_all_checks()
            api.last_check_time = datetime.now()
            return jsonify({'message': 'Check triggered', 'time': datetime.now().isoformat()})

        # Run watchdog in background thread
        import threading
        def background_monitor():
            while True:
                watchdog.run_all_checks()
                api.last_check_time = datetime.now()
                time.sleep(watchdog.check_interval)

        monitor_thread = threading.Thread(target=background_monitor, daemon=True)
        monitor_thread.start()

        # Start web server
        port = int(os.getenv('PORT', '8000'))
        app.run(host='0.0.0.0', port=port)

    else:
        # Standalone mode - just run monitoring loop
        watchdog = EchoWatchdog()
        watchdog.run_forever()
