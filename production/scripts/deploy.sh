#!/bin/bash
# Echo Phoenix Control Service - Deployment Script
# One-command deployment to Fly.io or Railway

set -e

echo "=========================================="
echo "Echo Phoenix Control Service - Deployment"
echo "=========================================="

# Configuration
APP_NAME="${APP_NAME:-echo-phoenix}"
REGION="${REGION:-iad}"
ENVIRONMENT="${ENVIRONMENT:-production}"

# Check for required environment variables
check_env() {
    local var_name=$1
    if [ -z "${!var_name}" ]; then
        echo "ERROR: $var_name is not set"
        exit 1
    fi
}

# Deployment to Fly.io
deploy_fly() {
    echo ""
    echo "Deploying to Fly.io..."
    echo ""
    
    # Check if flyctl is installed
    if ! command -v flyctl &> /dev/null; then
        echo "Installing flyctl..."
        curl -L https://fly.io/install.sh | sh
        export PATH="$HOME/.fly/bin:$PATH"
    fi
    
    # Check if app exists
    if ! flyctl apps list | grep -q "$APP_NAME"; then
        echo "Creating new Fly.io app: $APP_NAME"
        flyctl apps create "$APP_NAME" --org personal
    fi
    
    # Set secrets
    echo "Setting secrets..."
    flyctl secrets set \
        AIRTABLE_API_KEY="$AIRTABLE_API_KEY" \
        AIRTABLE_BASE_ID="$AIRTABLE_BASE_ID" \
        STRIPE_SECRET_KEY="$STRIPE_SECRET_KEY" \
        STRIPE_WEBHOOK_SECRET="$STRIPE_WEBHOOK_SECRET" \
        WEBHOOK_SECRET="$WEBHOOK_SECRET" \
        ENVIRONMENT="$ENVIRONMENT" \
        T_CRITICAL="0.9" \
        --app "$APP_NAME"
    
    # Deploy
    echo "Deploying application..."
    flyctl deploy --app "$APP_NAME" --region "$REGION"
    
    # Get URL
    APP_URL=$(flyctl info --app "$APP_NAME" -j | jq -r '.Hostname')
    echo ""
    echo "=========================================="
    echo "Deployment Complete!"
    echo "=========================================="
    echo "App URL: https://$APP_URL"
    echo ""
    echo "Endpoints:"
    echo "  - Health: https://$APP_URL/health"
    echo "  - Observe: https://$APP_URL/observe"
    echo "  - Control: https://$APP_URL/control"
    echo "  - Metrics: https://$APP_URL/metrics"
    echo "  - Kill: https://$APP_URL/kill"
    echo ""
}

# Deployment to Railway
deploy_railway() {
    echo ""
    echo "Deploying to Railway..."
    echo ""
    
    # Check if railway is installed
    if ! command -v railway &> /dev/null; then
        echo "Installing Railway CLI..."
        npm install -g @railway/cli
    fi
    
    # Login check
    if ! railway whoami &> /dev/null; then
        echo "Please login to Railway first: railway login"
        exit 1
    fi
    
    # Set environment variables
    echo "Setting environment variables..."
    railway variables set \
        AIRTABLE_API_KEY="$AIRTABLE_API_KEY" \
        AIRTABLE_BASE_ID="$AIRTABLE_BASE_ID" \
        STRIPE_SECRET_KEY="$STRIPE_SECRET_KEY" \
        STRIPE_WEBHOOK_SECRET="$STRIPE_WEBHOOK_SECRET" \
        WEBHOOK_SECRET="$WEBHOOK_SECRET" \
        ENVIRONMENT="$ENVIRONMENT" \
        T_CRITICAL="0.9"
    
    # Deploy
    echo "Deploying application..."
    railway up
    
    echo ""
    echo "=========================================="
    echo "Deployment Complete!"
    echo "=========================================="
    echo "Check Railway dashboard for URL"
    echo ""
}

# Local Docker deployment
deploy_local() {
    echo ""
    echo "Deploying locally with Docker..."
    echo ""
    
    # Build image
    echo "Building Docker image..."
    docker build -t echo-phoenix:latest .
    
    # Stop existing container
    docker stop echo-phoenix 2>/dev/null || true
    docker rm echo-phoenix 2>/dev/null || true
    
    # Run container
    echo "Starting container..."
    docker run -d \
        --name echo-phoenix \
        -p 8000:8000 \
        -e AIRTABLE_API_KEY="$AIRTABLE_API_KEY" \
        -e AIRTABLE_BASE_ID="$AIRTABLE_BASE_ID" \
        -e STRIPE_SECRET_KEY="$STRIPE_SECRET_KEY" \
        -e STRIPE_WEBHOOK_SECRET="$STRIPE_WEBHOOK_SECRET" \
        -e WEBHOOK_SECRET="$WEBHOOK_SECRET" \
        -e ENVIRONMENT="$ENVIRONMENT" \
        -e T_CRITICAL="0.9" \
        echo-phoenix:latest
    
    echo ""
    echo "=========================================="
    echo "Local Deployment Complete!"
    echo "=========================================="
    echo "App URL: http://localhost:8000"
    echo ""
    echo "Endpoints:"
    echo "  - Health: http://localhost:8000/health"
    echo "  - Observe: http://localhost:8000/observe"
    echo "  - Control: http://localhost:8000/control"
    echo "  - Metrics: http://localhost:8000/metrics"
    echo ""
}

# Main
case "${1:-local}" in
    fly)
        check_env AIRTABLE_API_KEY
        check_env AIRTABLE_BASE_ID
        deploy_fly
        ;;
    railway)
        check_env AIRTABLE_API_KEY
        check_env AIRTABLE_BASE_ID
        deploy_railway
        ;;
    local)
        deploy_local
        ;;
    *)
        echo "Usage: $0 {fly|railway|local}"
        echo ""
        echo "Options:"
        echo "  fly     - Deploy to Fly.io"
        echo "  railway - Deploy to Railway"
        echo "  local   - Deploy locally with Docker"
        exit 1
        ;;
esac
