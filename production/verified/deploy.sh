#!/bin/bash
set -e

# ============================================================================
# Echo Phoenix v2.4 - Formal Deployment Script
# Deploys to Fly.io with I1-I4 invariant enforcement
# ============================================================================

echo "🚀 Echo Phoenix v2.4 Deployment"
echo "================================"

# Check prerequisites
command -v fly >/dev/null 2>&1 || { echo "❌ Fly CLI not installed. Run: curl -L https://fly.io/install.sh | sh"; exit 1; }
command -v psql >/dev/null 2>&1 || { echo "⚠️  psql not installed. Database setup will be manual."; }

# Configuration
APP_NAME="${APP_NAME:-echo-phoenix}"
REGION="${REGION:-ord}"  # Chicago - change as needed

echo ""
echo "📋 Configuration:"
echo "   App Name: $APP_NAME"
echo "   Region: $REGION"
echo ""

# Step 1: Create Fly.io app
echo "Step 1: Creating Fly.io app..."
if fly apps list | grep -q "$APP_NAME"; then
    echo "   ℹ️  App $APP_NAME already exists, skipping..."
else
    fly apps create "$APP_NAME" --org personal
fi

# Step 2: Create PostgreSQL database
echo ""
echo "Step 2: Creating PostgreSQL database..."
DB_NAME="${APP_NAME}-db"
if fly postgres list | grep -q "$DB_NAME"; then
    echo "   ℹ️  Database $DB_NAME already exists, skipping..."
else
    fly postgres create --name "$DB_NAME" --region "$REGION" --initial-cluster-size 1 --vm-size shared-cpu-1x --volume-size 1
fi

# Step 3: Attach database to app
echo ""
echo "Step 3: Attaching database to app..."
fly postgres attach "$DB_NAME" --app "$APP_NAME" || echo "   ℹ️  Database already attached"

# Step 4: Set secrets
echo ""
echo "Step 4: Setting secrets..."
read -sp "Enter ECHO_API_KEY (or press Enter to generate): " ECHO_API_KEY
echo ""
if [ -z "$ECHO_API_KEY" ]; then
    ECHO_API_KEY=$(openssl rand -hex 32)
    echo "   Generated API Key: $ECHO_API_KEY"
fi

read -p "Enter ALLOWED_ACTORS (comma-separated, default: admin,ops,security): " ALLOWED_ACTORS
ALLOWED_ACTORS=${ALLOWED_ACTORS:-admin,ops,security}

fly secrets set \
    ECHO_API_KEY="$ECHO_API_KEY" \
    ALLOWED_ACTORS="$ALLOWED_ACTORS" \
    --app "$APP_NAME"

# Step 5: Deploy schema to database
echo ""
echo "Step 5: Deploying database schema..."
echo "   Getting database connection string..."
DB_URL=$(fly postgres connect --app "$DB_NAME" --command "echo \$DATABASE_URL" 2>/dev/null || echo "")

if [ -z "$DB_URL" ]; then
    echo "   ⚠️  Could not auto-detect DATABASE_URL"
    echo "   Please run manually:"
    echo "   fly postgres connect -a $DB_NAME"
    echo "   Then run: \\i formal_schema.sql"
else
    if command -v psql >/dev/null 2>&1; then
        echo "   Deploying schema..."
        psql "$DB_URL" -f formal_schema.sql
        echo "   ✅ Schema deployed"
    else
        echo "   ⚠️  psql not found, manual schema deployment required"
    fi
fi

# Step 6: Create fly.toml
echo ""
echo "Step 6: Creating fly.toml configuration..."
cat > fly.toml <<EOF
app = "$APP_NAME"
primary_region = "$REGION"

[build]
  [build.args]
    PYTHON_VERSION = "3.11"

[env]
  PORT = "8000"
  ENVIRONMENT = "production"

[http_service]
  internal_port = 8000
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true
  min_machines_running = 1
  processes = ["app"]

  [[http_service.checks]]
    grace_period = "10s"
    interval = "30s"
    method = "GET"
    timeout = "5s"
    path = "/health"

[[vm]]
  cpu_kind = "shared"
  cpus = 1
  memory_mb = 256
EOF

echo "   ✅ fly.toml created"

# Step 7: Create Dockerfile
echo ""
echo "Step 7: Creating Dockerfile..."
cat > Dockerfile <<'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY minimal_echo.py .

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "minimal_echo:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

echo "   ✅ Dockerfile created"

# Step 8: Deploy to Fly.io
echo ""
echo "Step 8: Deploying to Fly.io..."
fly deploy --app "$APP_NAME"

# Step 9: Get app URL
echo ""
echo "✅ Deployment Complete!"
echo "================================"
echo ""
APP_URL="https://${APP_NAME}.fly.dev"
echo "🌐 App URL: $APP_URL"
echo "🔑 API Key: $ECHO_API_KEY"
echo ""
echo "Next steps:"
echo "1. Test health endpoint: curl $APP_URL/health"
echo "2. Configure Zapier with URL: $APP_URL"
echo "3. Set ECHO_API_KEY in Zapier: $ECHO_API_KEY"
echo "4. Test event processing: curl -X POST $APP_URL/events -H 'X-API-Key: $ECHO_API_KEY' -d '{...}'"
echo ""
echo "📊 Monitor: fly logs -a $APP_NAME"
echo "🔧 SSH: fly ssh console -a $APP_NAME"
echo "💾 Database: fly postgres connect -a $DB_NAME"
echo ""
