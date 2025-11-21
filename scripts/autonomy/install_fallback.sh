#!/bin/bash
#
# Install Echo Local Fallback Service
#
# This script sets up the local autonomy fallback system on a Linux machine.
# Run as root or with sudo.
#

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

echo_error() {
    echo -e "${RED}❌ $1${NC}"
}

echo_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo_error "Please run as root or with sudo"
    exit 1
fi

echo_info "Installing Echo Local Fallback Service..."

# 1. Create echo user if it doesn't exist
if ! id -u echo > /dev/null 2>&1; then
    echo_info "Creating echo user..."
    useradd --system --home-dir /opt/echo --shell /bin/bash echo
    echo_success "Echo user created"
else
    echo_info "Echo user already exists"
fi

# 2. Create necessary directories
echo_info "Creating directories..."
mkdir -p /opt/echo/scripts/{autonomy,monitoring}
mkdir -p /opt/echo/data
mkdir -p /var/log/echo
chown -R echo:echo /opt/echo
chown -R echo:echo /var/log/echo
echo_success "Directories created"

# 3. Copy scripts to /opt/echo
echo_info "Copying scripts..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cp "$SCRIPT_DIR/local_fallback.sh" /opt/echo/scripts/autonomy/
chmod +x /opt/echo/scripts/autonomy/local_fallback.sh

if [ -f "$SCRIPT_DIR/../monitoring/watchdog.py" ]; then
    cp "$SCRIPT_DIR/../monitoring/watchdog.py" /opt/echo/scripts/monitoring/
fi

chown -R echo:echo /opt/echo/scripts
echo_success "Scripts copied"

# 4. Install systemd service
echo_info "Installing systemd service..."
cp "$SCRIPT_DIR/echo-fallback.service" /etc/systemd/system/
chmod 644 /etc/systemd/system/echo-fallback.service
systemctl daemon-reload
echo_success "Systemd service installed"

# 5. Create .env file template if it doesn't exist
if [ ! -f /opt/echo/.env ]; then
    echo_info "Creating .env template..."
    cat > /opt/echo/.env << 'EOF'
# Echo Local Fallback Configuration
# Customize these values for your environment

# Service health endpoints
RENDER_HEALTH_URL=https://your-app.onrender.com/health
VERCEL_HEALTH_URL=https://your-site.vercel.app/health
AWS_HEALTH_URL=https://your-lambda-url.amazonaws.com/health

# Watchdog configuration
WATCHDOG_URL=https://watchdog.echo-sovereign.com

# Check interval (seconds)
CHECK_INTERVAL=300

# API keys (use secrets manager in production)
# STRIPE_SECRET_KEY=sk_live_...
# GUMROAD_API_KEY=...
# GITHUB_TOKEN=ghp_...
EOF
    chown echo:echo /opt/echo/.env
    chmod 600 /opt/echo/.env
    echo_success ".env template created at /opt/echo/.env"
    echo_info "⚠️  IMPORTANT: Edit /opt/echo/.env with your actual values"
else
    echo_info ".env file already exists"
fi

# 6. Install Python dependencies
echo_info "Installing Python dependencies..."
if command -v pip3 > /dev/null 2>&1; then
    pip3 install requests boto3 cryptography > /dev/null 2>&1
    echo_success "Python dependencies installed"
else
    echo_error "pip3 not found, please install Python dependencies manually:"
    echo "  pip3 install requests boto3 cryptography"
fi

# 7. Enable and start service
echo ""
echo_info "Service installation complete!"
echo ""
echo "Next steps:"
echo "  1. Edit configuration: sudo nano /opt/echo/.env"
echo "  2. Enable service: sudo systemctl enable echo-fallback"
echo "  3. Start service: sudo systemctl start echo-fallback"
echo "  4. Check status: sudo systemctl status echo-fallback"
echo "  5. View logs: sudo journalctl -u echo-fallback -f"
echo ""
echo_info "Would you like to enable and start the service now? (y/N)"
read -r response

if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    systemctl enable echo-fallback
    systemctl start echo-fallback
    echo_success "Service enabled and started"
    echo ""
    systemctl status echo-fallback --no-pager
else
    echo_info "Service not started. You can start it later with:"
    echo "  sudo systemctl enable echo-fallback"
    echo "  sudo systemctl start echo-fallback"
fi

echo ""
echo_success "Installation complete! 🚀"
