#!/bin/bash

echo "🚀 Setting up Echo Coordination System v1.0..."

# Create directory structure
mkdir -p ai-coordination/{events,classifications,cases,consensus,rulings,messages,receipts,locks,ethics,config,scripts,logs,api}
mkdir -p .github/workflows
mkdir -p docs

# Create .gitkeep files for empty directories
for dir in events classifications cases consensus rulings messages receipts locks logs; do
    touch "ai-coordination/$dir/.gitkeep"
done

# Make scripts executable
chmod +x ai-coordination/scripts/*.py

# Initialize ethics chain log
echo "# Ethics Chain - SHA256 Hash Chain" > ai-coordination/logs/ethics_chain.log
echo "# Format: timestamp | previous_hash + record_hash = new_hash" >> ai-coordination/logs/ethics_chain.log
echo "2025-12-14T00:00:00Z | 0000000000000000000000000000000000000000000000000000000000000000" >> ai-coordination/logs/ethics_chain.log

# Initialize git
git init
git add -A
git commit -m "Initial commit: Echo Coordination System v1.0"

echo ""
echo "✅ Setup complete!"
echo "Next steps:"
echo "1. Run ./test.sh to execute forced disagreement test"
echo "2. Check ai-coordination/consensus/ for divergence analysis"
echo "3. Review README.md for API usage"
echo ""
echo "System is ready for AI-to-AI coordination."
