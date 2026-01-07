#!/bin/bash
###############################################################################
# INSTALL AUTOMATED REPORTING CRON JOBS
# Sets up all automated reporting schedules
#
# Author: EchoNate
# Timestamp: 07:37 Jan 07 2026
###############################################################################

ECHO_DIR="/home/ubuntu/Echo"
CRON_CONFIG="$ECHO_DIR/scripts/crontab_config.txt"
BACKUP_FILE="/tmp/crontab_backup_$(date +%Y%m%d_%H%M%S).txt"

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║     INSTALLING ECHO UNIVERSE AUTOMATED REPORTING         ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Check if cron config exists
if [ ! -f "$CRON_CONFIG" ]; then
    echo "❌ Error: Cron config not found at $CRON_CONFIG"
    exit 1
fi

# Backup existing crontab
echo "📦 Backing up existing crontab..."
crontab -l > "$BACKUP_FILE" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Existing crontab backed up to: $BACKUP_FILE"
else
    echo "ℹ️  No existing crontab found"
fi

# Remove old Echo Universe cron jobs (if any)
echo "🧹 Removing old Echo Universe cron jobs..."
crontab -l 2>/dev/null | grep -v "/home/ubuntu/Echo" | crontab - 2>/dev/null

# Install new cron jobs
echo "📥 Installing new cron jobs..."
(crontab -l 2>/dev/null; cat "$CRON_CONFIG" | grep -v "^#" | grep -v "^$") | crontab -

if [ $? -eq 0 ]; then
    echo "✅ Cron jobs installed successfully"
else
    echo "❌ Error installing cron jobs"
    echo "🔄 Restoring backup..."
    crontab "$BACKUP_FILE"
    exit 1
fi

# Verify installation
echo ""
echo "📋 Installed cron jobs:"
echo "═══════════════════════════════════════════════════════════"
crontab -l | grep "/home/ubuntu/Echo"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Create initial directories
echo "📁 Creating report directories..."
mkdir -p "$ECHO_DIR/reports/"{daily,weekly,hourly}
mkdir -p "$ECHO_DIR/logs"
echo "✅ Directories created"

# Test daily report script
echo ""
echo "🧪 Testing daily report script..."
"$ECHO_DIR/scripts/auto_daily_report.sh"

if [ $? -eq 0 ]; then
    echo "✅ Daily report script test passed"
else
    echo "⚠️  Warning: Daily report script test failed"
fi

echo ""
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║           AUTOMATED REPORTING INSTALLED                  ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""
echo "📅 Schedule:"
echo "  • Daily reports: 00:00 UTC"
echo "  • Weekly reports: Sunday 23:00 UTC"
echo "  • Hourly status: Every hour"
echo "  • Ledger verify: Every 6 hours"
echo "  • System sync: Every 12 hours"
echo "  • Cleanup: Daily at 03:00 UTC"
echo "  • Backup: Daily at 05:00 UTC"
echo ""
echo "📂 Reports saved to: $ECHO_DIR/reports/"
echo "📝 Logs saved to: $ECHO_DIR/logs/"
echo ""
echo "🔗 View latest report: cat $ECHO_DIR/reports/daily/latest.txt"
echo ""

exit 0
