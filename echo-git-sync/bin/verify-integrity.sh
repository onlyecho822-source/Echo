#!/bin/bash
set -euo pipefail
# verify-integrity.sh - Generate deterministic SHA-256 repository hash

echo "🔍 Generating Integrity Hash..."

# Fix: Exclude self, git metadata, and logs to ensure mathematical purity
HASH=$(find . -type f \
    -not -path "./.git/*" \
    -not -path "./node_modules/*" \
    -not -path "./bin/*" \
    -not -name "integrity.log" \
    -not -name ".DS_Store" \
    -exec sha256sum {} \; 2>/dev/null | \
    sort -k 2 | \
    sha256sum | \
    cut -d' ' -f1)

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
COMMIT=$(git rev-parse --short HEAD 2>/dev/null || echo "NO_COMMIT")

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "INTEGRITY REPORT"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Timestamp:  $TIMESTAMP"
echo "Commit:     $COMMIT"
echo "Hash:       $HASH"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Append to immutable log
echo "$TIMESTAMP $COMMIT $HASH" >> integrity.log
