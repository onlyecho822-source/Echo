#!/bin/bash
###############################################################################
# AUTOMATED DAILY SYSTEM REPORT
# Runs Nexus CLI report command and saves results
#
# Author: EchoNate
# Timestamp: 07:35 Jan 07 2026
# Schedule: Daily at 00:00 UTC
###############################################################################

# Configuration
ECHO_DIR="/home/ubuntu/Echo"
NEXUS_CLI="$ECHO_DIR/nexus_cli.py"
REPORT_DIR="$ECHO_DIR/reports/daily"
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
DATE=$(date +"%Y-%m-%d")
LOG_FILE="$ECHO_DIR/logs/auto_report.log"

# Create directories if they don't exist
mkdir -p "$REPORT_DIR"
mkdir -p "$ECHO_DIR/logs"

# Log function
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S UTC')] $1" | tee -a "$LOG_FILE"
}

# Start report
log "========================================="
log "STARTING AUTOMATED DAILY REPORT"
log "========================================="

# Change to Echo directory
cd "$ECHO_DIR" || {
    log "ERROR: Could not change to Echo directory"
    exit 1
}

# Generate daily report
log "Generating daily report..."
REPORT_FILE="$REPORT_DIR/daily_report_$DATE.txt"

{
    echo "╔═══════════════════════════════════════════════════════════╗"
    echo "║         ECHO UNIVERSE AUTOMATED DAILY REPORT             ║"
    echo "╚═══════════════════════════════════════════════════════════╝"
    echo ""
    echo "📅 Date: $DATE"
    echo "⏰ Generated: $(date +'%Y-%m-%d %H:%M:%S UTC')"
    echo ""
    echo "═══════════════════════════════════════════════════════════"
    echo ""
    
    # Run daily report
    python3 "$NEXUS_CLI" report daily 2>&1
    
    echo ""
    echo "═══════════════════════════════════════════════════════════"
    echo ""
    
    # System status
    echo "📊 CURRENT SYSTEM STATUS"
    echo ""
    python3 "$NEXUS_CLI" status 2>&1
    
    echo ""
    echo "═══════════════════════════════════════════════════════════"
    echo ""
    
    # Recent ledger entries
    echo "📖 RECENT LEDGER ENTRIES (Last 20)"
    echo ""
    python3 "$NEXUS_CLI" ledger --lines 20 2>&1
    
    echo ""
    echo "═══════════════════════════════════════════════════════════"
    echo ""
    
    # Ledger verification
    echo "🔐 LEDGER INTEGRITY CHECK"
    echo ""
    python3 "$NEXUS_CLI" verify 2>&1
    
    echo ""
    echo "═══════════════════════════════════════════════════════════"
    echo "Report generated at: $(date +'%Y-%m-%d %H:%M:%S UTC')"
    echo "═══════════════════════════════════════════════════════════"
    
} > "$REPORT_FILE" 2>&1

if [ $? -eq 0 ]; then
    log "✅ Daily report generated successfully: $REPORT_FILE"
else
    log "❌ Error generating daily report"
    exit 1
fi

# Create symlink to latest report
ln -sf "$REPORT_FILE" "$REPORT_DIR/latest.txt"
log "🔗 Symlink created: $REPORT_DIR/latest.txt"

# Upload to Google Drive (if rclone configured)
if command -v rclone &> /dev/null; then
    log "📤 Uploading report to Google Drive..."
    rclone copy "$REPORT_FILE" manus_google_drive:Echo-Arsenal/Reports/Daily/ --config /home/ubuntu/.gdrive-rclone.ini 2>&1 | tee -a "$LOG_FILE"
    
    if [ ${PIPESTATUS[0]} -eq 0 ]; then
        log "✅ Report uploaded to Google Drive"
    else
        log "⚠️  Warning: Could not upload to Google Drive"
    fi
fi

# Cleanup old reports (keep last 30 days)
log "🧹 Cleaning up old reports..."
find "$REPORT_DIR" -name "daily_report_*.txt" -mtime +30 -delete 2>&1 | tee -a "$LOG_FILE"
log "✅ Cleanup complete"

# Commit report to Git (optional)
if [ -d "$ECHO_DIR/.git" ]; then
    log "📝 Committing report to Git..."
    git add "$REPORT_FILE" 2>&1 | tee -a "$LOG_FILE"
    git commit -m "📊 Automated Daily Report - $DATE" 2>&1 | tee -a "$LOG_FILE"
    
    if [ ${PIPESTATUS[0]} -eq 0 ]; then
        log "✅ Report committed to Git"
    else
        log "ℹ️  No changes to commit"
    fi
fi

log "========================================="
log "AUTOMATED DAILY REPORT COMPLETE"
log "========================================="
log ""

exit 0
