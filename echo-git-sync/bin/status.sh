#!/bin/bash
# status.sh - System health dashboard

echo "📊 Echo Git Sync Status"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

BRANCH=$(git branch --show-current 2>/dev/null || echo "(detached)")
echo "Branch: $BRANCH"
echo ""

REMOTES=$(git remote)
if [ -n "$REMOTES" ]; then
    for remote in $REMOTES; do
        URL=$(git remote get-url "$remote")
        echo -n "• $remote: "
        if timeout 5 git ls-remote "$remote" HEAD &>/dev/null; then
            echo "✅ Online"
        else
            echo "❌ Offline"
        fi
        echo "  $URL"
    done
else
    echo "⚠️  No remotes configured."
fi
echo ""
if [ -f "integrity.log" ]; then
    echo "Last Integrity Check:"
    tail -1 integrity.log
fi
