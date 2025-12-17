#!/bin/bash
# sync-all.sh - Parallel multi-provider git synchronization
# Features: Atomic failure tracking, Dry-run, Pre-flight checks

set -o pipefail

# Parse flags
DRY_RUN=0
if [ "$1" = "--dry-run" ]; then
    DRY_RUN=1
fi

REMOTES=$(git remote)
if [ -z "$REMOTES" ]; then
    echo "❌ No git remotes configured."
    echo "   Add one with: ./bin/add-remote.sh <name> <url>"
    exit 1
fi

BRANCH=$(git branch --show-current)
if [ -z "$BRANCH" ]; then
    echo "❌ Not on a branch (detached HEAD)"
    exit 1
fi

# Pre-flight Check (Fast)
echo "🔍 Pre-flight connectivity check..."
for remote in $REMOTES; do
    if ! timeout 5 git ls-remote "$remote" HEAD &>/dev/null; then
        echo "   ⚠️  $remote appears unreachable (will attempt anyway)"
    fi
done

if [ $DRY_RUN -eq 1 ]; then
    echo ""
    echo "🔍 Dry-run: Would push '$BRANCH' to:"
    for remote in $REMOTES; do
        echo "  • $remote ($(git remote get-url "$remote"))"
    done
    exit 0
fi

echo ""
echo "🔄 Syncing '$BRANCH' to $(echo "$REMOTES" | wc -w) remote(s)..."

# Atomic Failure Tracking
FAIL_FILE=$(mktemp)
PIDS=""

for remote in $REMOTES; do
    (
        # Push Branch AND Tags
        if git push "$remote" "$BRANCH" --quiet 2>&1 && \
           git push "$remote" --tags --quiet 2>&1; then
            echo "  ✅ $remote: Synced"
        else
            echo "  ❌ $remote: Failed"
            echo "FAIL" >> "$FAIL_FILE"
            exit 1
        fi
    ) &
    PIDS="$PIDS $!"
done

# Wait for all background jobs
for pid in $PIDS; do
    wait $pid
done

FAIL_COUNT=$(wc -l < "$FAIL_FILE" 2>/dev/null || echo "0")
rm -f "$FAIL_FILE"

echo ""
if [ "$FAIL_COUNT" -eq 0 ]; then
    echo "🏁 Success: All remotes synchronized"
    exit 0
else
    echo "⚠️  Partial success: $FAIL_COUNT remote(s) failed"
    exit 1
fi
