#!/bin/bash
# add-remote.sh - Add git remote with URL validation and connection testing

if [ $# -ne 2 ]; then
    echo "Usage: ./bin/add-remote.sh <name> <url>"
    exit 1
fi

NAME="$1"
URL="$2"

# Security: Validate URL format
if [[ ! "$URL" =~ ^(https?://|git@|ssh://|file://) ]]; then
    echo "❌ Invalid URL format. Must start with http://, https://, git@, ssh://, or file://"
    exit 1
fi

if git remote get-url "$NAME" &>/dev/null; then
    echo "⚠️  Remote '$NAME' already exists."
    exit 0
fi

git remote add "$NAME" "$URL"
echo "🔗 Added remote '$NAME'"

echo "🔍 Testing connection..."
if timeout 5 git ls-remote "$NAME" HEAD &>/dev/null; then
    echo "✅ Connection successful! Remote ready."
else
    echo "❌ Connection failed. Removing invalid remote..."
    git remote remove "$NAME"
    exit 1
fi
