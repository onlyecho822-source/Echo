#!/bin/bash
#
# Echo Local Autonomy Fallback System
#
# This script ensures critical operations continue even if all cloud services fail.
# Runs on developer machine or private VPS as a systemd service.
#
# Usage:
#   ./local_fallback.sh          # Run once
#   ./local_fallback.sh --loop   # Run continuously (for systemd)
#

set -euo pipefail

# Configuration
ECHO_HOME="${ECHO_HOME:-/opt/echo}"
LOG_FILE="${LOG_FILE:-/var/log/echo/fallback.log}"
CHECK_INTERVAL="${CHECK_INTERVAL:-300}"  # 5 minutes
WATCHDOG_URL="${WATCHDOG_URL:-https://watchdog.echo-sovereign.com}"

# Service health endpoints
RENDER_HEALTH_URL="${RENDER_HEALTH_URL:-}"
VERCEL_HEALTH_URL="${VERCEL_HEALTH_URL:-}"
AWS_HEALTH_URL="${AWS_HEALTH_URL:-}"

# Ensure log directory exists
mkdir -p "$(dirname "$LOG_FILE")"

# Logging function
log() {
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] ERROR: $1" | tee -a "$LOG_FILE" >&2
}

# Check if a service is healthy
check_service_health() {
    local service_name="$1"
    local health_url="$2"

    if [ -z "$health_url" ]; then
        log "⚠️  No health URL configured for $service_name"
        return 1
    fi

    if curl -f -s --max-time 10 "$health_url" > /dev/null 2>&1; then
        log "✅ $service_name is healthy"
        return 0
    else
        log "❌ $service_name is unresponsive"
        return 1
    fi
}

# Execute local fallback operations
execute_fallback() {
    log "🚨 EXECUTING LOCAL FALLBACK MODE"

    # Notify watchdog that fallback is active
    notify_watchdog_fallback_active

    # Run critical profit engines locally
    if [ -f "$ECHO_HOME/scripts/profit_scanner.py" ]; then
        log "Running profit scanner..."
        python3 "$ECHO_HOME/scripts/profit_scanner.py" >> "$LOG_FILE" 2>&1 || \
            log_error "Profit scanner failed"
    fi

    # Run AI agent orchestrator locally
    if [ -f "$ECHO_HOME/scripts/ai_orchestrator.py" ]; then
        log "Running AI orchestrator..."
        python3 "$ECHO_HOME/scripts/ai_orchestrator.py" >> "$LOG_FILE" 2>&1 || \
            log_error "AI orchestrator failed"
    fi

    # Process pending Stripe webhooks
    if [ -f "$ECHO_HOME/scripts/stripe_webhook_processor.py" ]; then
        log "Processing Stripe webhooks..."
        python3 "$ECHO_HOME/scripts/stripe_webhook_processor.py" >> "$LOG_FILE" 2>&1 || \
            log_error "Stripe processor failed"
    fi

    # Health check Echo Core
    if [ -f "$ECHO_HOME/scripts/health_check.py" ]; then
        log "Running health check..."
        python3 "$ECHO_HOME/scripts/health_check.py" >> "$LOG_FILE" 2>&1 || \
            log_error "Health check failed"
    fi

    log "✅ Local fallback cycle complete"
}

# Notify watchdog that fallback mode is active
notify_watchdog_fallback_active() {
    if [ -n "$WATCHDOG_URL" ]; then
        curl -X POST "$WATCHDOG_URL/fallback-active" \
            -H "Content-Type: application/json" \
            -d "{\"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\", \"hostname\": \"$(hostname)\"}" \
            --max-time 10 \
            > /dev/null 2>&1 || \
            log_error "Failed to notify watchdog"
    fi
}

# Check all cloud services
check_all_services() {
    local any_service_down=false

    if [ -n "$RENDER_HEALTH_URL" ]; then
        check_service_health "Render" "$RENDER_HEALTH_URL" || any_service_down=true
    fi

    if [ -n "$VERCEL_HEALTH_URL" ]; then
        check_service_health "Vercel" "$VERCEL_HEALTH_URL" || any_service_down=true
    fi

    if [ -n "$AWS_HEALTH_URL" ]; then
        check_service_health "AWS Lambda" "$AWS_HEALTH_URL" || any_service_down=true
    fi

    if [ "$any_service_down" = true ]; then
        return 1
    else
        return 0
    fi
}

# Single check cycle
run_check_cycle() {
    log "--- Starting fallback check cycle ---"

    if ! check_all_services; then
        log "⚠️  One or more cloud services are down"
        execute_fallback
    else
        log "✅ All cloud services healthy, standing by"
    fi

    log "--- Check cycle complete ---"
}

# Continuous monitoring loop
run_loop() {
    log "🔍 Echo Local Fallback started"
    log "Check interval: $CHECK_INTERVAL seconds"
    log "Echo home: $ECHO_HOME"

    while true; do
        run_check_cycle
        sleep "$CHECK_INTERVAL"
    done
}

# Main execution
main() {
    if [ "${1:-}" = "--loop" ] || [ "${1:-}" = "-l" ]; then
        run_loop
    else
        run_check_cycle
    fi
}

# Trap signals for graceful shutdown
trap 'log "Received shutdown signal, exiting..."; exit 0' SIGTERM SIGINT

main "$@"
