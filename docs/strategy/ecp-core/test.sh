#!/bin/bash

echo "🧪 Running Echo Coordination System Tests..."

cd ai-coordination/scripts

echo "1. Creating forced disagreement test..."
python3 force_disagreement.py

echo ""
echo "2. Checking consensus..."
python3 consensus_scorer.py handshake_disagreement_20251214_160000

echo ""
echo "3. Finding events needing consensus..."
python3 find_events_for_consensus.py

echo ""
echo "4. Testing human escalation..."
python3 escalate_to_human.py

echo ""
echo "✅ Tests complete!"
echo "Review generated files in:"
echo "  - ai-coordination/events/"
echo "  - ai-coordination/classifications/"
echo "  - ai-coordination/consensus/"
echo "  - ai-coordination/cases/"
echo ""
echo "If GitHub CLI is installed, issues will be created for human review."
