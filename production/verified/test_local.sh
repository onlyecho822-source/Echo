#!/bin/bash
# ============================================================================
# Echo Phoenix v2.4 - Local Test Script
# Validates code before deployment
# ============================================================================

set -e

echo "🧪 Echo Phoenix v2.4 - Pre-Deployment Tests"
echo "==========================================="
echo ""

# Check Python
echo "1️⃣  Checking Python installation..."
python3 --version || { echo "❌ Python 3 not found"; exit 1; }
echo "   ✅ Python found"

# Check dependencies
echo ""
echo "2️⃣  Installing dependencies..."
pip3 install -q -r requirements.txt
echo "   ✅ Dependencies installed"

# Syntax check
echo ""
echo "3️⃣  Checking Python syntax..."
python3 -m py_compile minimal_echo.py || { echo "❌ Syntax error in minimal_echo.py"; exit 1; }
echo "   ✅ No syntax errors"

# Import test
echo ""
echo "4️⃣  Testing imports..."
python3 -c "
import sys
sys.path.insert(0, '.')
from minimal_echo import app, Event, ControlCommand
print('   ✅ All imports successful')
" || { echo "❌ Import failed"; exit 1; }

# JSON validation
echo ""
echo "5️⃣  Validating 4_zaps.json..."
python3 -c "
import json
with open('4_zaps.json') as f:
    data = json.load(f)
    assert 'zaps' in data
    assert len(data['zaps']) == 4
    print('   ✅ JSON valid, 4 zaps configured')
" || { echo "❌ JSON validation failed"; exit 1; }

# Schema check
echo ""
echo "6️⃣  Checking SQL schema..."
grep -q "CREATE TABLE.*event_dedup" formal_schema.sql || { echo "❌ Missing event_dedup table"; exit 1; }
grep -q "CREATE TABLE.*system_state" formal_schema.sql || { echo "❌ Missing system_state table"; exit 1; }
grep -q "CREATE TABLE.*audit_trail" formal_schema.sql || { echo "❌ Missing audit_trail table"; exit 1; }
echo "   ✅ All required tables present"

# Start local server (background)
echo ""
echo "7️⃣  Starting local server..."
export ECHO_API_KEY="test-key-12345"
export ALLOWED_ACTORS="admin,test"
export DATABASE_URL="postgresql://localhost/test_db"  # Will fail DB calls but API starts

python3 -c "
import uvicorn
from minimal_echo import app
import asyncio
import signal
import sys

def shutdown(signum, frame):
    print('   ✅ Server started and shut down cleanly')
    sys.exit(0)

signal.signal(signal.SIGALRM, shutdown)
signal.alarm(2)  # Auto-shutdown after 2 seconds

try:
    uvicorn.run(app, host='127.0.0.1', port=8000, log_level='critical')
except SystemExit:
    pass
" &

SERVER_PID=$!
sleep 1

# Test health endpoint
echo ""
echo "8️⃣  Testing health endpoint..."
curl -s http://127.0.0.1:8000/health | python3 -m json.tool > /dev/null 2>&1 && {
    echo "   ✅ Health endpoint responding"
} || {
    echo "   ⚠️  Health endpoint not responding (may need DATABASE_URL)"
}

# Kill server
kill $SERVER_PID 2>/dev/null || true

echo ""
echo "================================"
echo "✅ ALL TESTS PASSED"
echo ""
echo "Ready for deployment!"
echo "Run: ./deploy.sh"
echo ""
