#!/bin/bash
# Observatory Intelligence Monitoring Dashboard
# Tracks demand signals from public infrastructure-observatory repo

set -e

REPO="onlyecho822-source/infrastructure-observatory"
OUTPUT_DIR="/home/ubuntu/Echo/intelligence/reports"
TIMESTAMP=$(date -u +"%Y-%m-%d_%H-%M-%S_UTC")
REPORT_FILE="$OUTPUT_DIR/observatory_intel_$TIMESTAMP.txt"

mkdir -p "$OUTPUT_DIR"

echo "================================================" > "$REPORT_FILE"
echo "INFRASTRUCTURE OBSERVATORY - INTELLIGENCE REPORT" >> "$REPORT_FILE"
echo "Generated: $(date -u)" >> "$REPORT_FILE"
echo "================================================" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# Repository Metrics
echo "## REPOSITORY METRICS" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

STARS=$(gh api "/repos/$REPO" --jq '.stargazers_count')
WATCHERS=$(gh api "/repos/$REPO" --jq '.subscribers_count')
FORKS=$(gh api "/repos/$REPO" --jq '.forks_count')

echo "⭐ Stars: $STARS" >> "$REPORT_FILE"
echo "👁️  Watchers: $WATCHERS" >> "$REPORT_FILE"
echo "🔀 Forks: $FORKS" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# Traffic Data (requires push access)
echo "## TRAFFIC DATA (Last 14 Days)" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

TRAFFIC=$(gh api "/repos/$REPO/traffic/views" 2>/dev/null || echo '{"count":0,"uniques":0}')
VIEWS=$(echo "$TRAFFIC" | jq -r '.count // 0')
UNIQUE_VISITORS=$(echo "$TRAFFIC" | jq -r '.uniques // 0')

echo "📊 Total views: $VIEWS" >> "$REPORT_FILE"
echo "👤 Unique visitors: $UNIQUE_VISITORS" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# Clone Data
CLONES=$(gh api "/repos/$REPO/traffic/clones" 2>/dev/null || echo '{"count":0,"uniques":0}')
CLONE_COUNT=$(echo "$CLONES" | jq -r '.count // 0')
UNIQUE_CLONERS=$(echo "$CLONES" | jq -r '.uniques // 0')

echo "📥 Total clones: $CLONE_COUNT" >> "$REPORT_FILE"
echo "👤 Unique cloners: $UNIQUE_CLONERS" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# Access Requests (Issues with label "access-request")
echo "## LEAD CAPTURE" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

ACCESS_REQUESTS=$(gh issue list --repo "$REPO" --label "access-request" --json number,title,author,createdAt --limit 100)
ACCESS_COUNT=$(echo "$ACCESS_REQUESTS" | jq '. | length')

echo "🔑 Access requests: $ACCESS_COUNT" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

if [ "$ACCESS_COUNT" -gt 0 ]; then
    echo "### Recent Access Requests:" >> "$REPORT_FILE"
    echo "$ACCESS_REQUESTS" | jq -r '.[] | "  #\(.number) - \(.title) (@\(.author.login)) - \(.createdAt)"' >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
fi

# Research Collaboration Requests
COLLAB_REQUESTS=$(gh issue list --repo "$REPO" --label "collaboration" --json number,title,author,createdAt --limit 100)
COLLAB_COUNT=$(echo "$COLLAB_REQUESTS" | jq '. | length')

echo "🔬 Collaboration requests: $COLLAB_COUNT" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

if [ "$COLLAB_COUNT" -gt 0 ]; then
    echo "### Recent Collaboration Requests:" >> "$REPORT_FILE"
    echo "$COLLAB_REQUESTS" | jq -r '.[] | "  #\(.number) - \(.title) (@\(.author.login)) - \(.createdAt)"' >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
fi

# Discussion Activity
DISCUSSIONS=$(gh api "/repos/$REPO/discussions" --paginate 2>/dev/null | jq '. | length' || echo "0")
echo "💬 Total discussions: $DISCUSSIONS" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# Referrers (Top traffic sources)
echo "## TOP REFERRERS (Last 14 Days)" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

REFERRERS=$(gh api "/repos/$REPO/traffic/popular/referrers" 2>/dev/null || echo '[]')
REFERRER_COUNT=$(echo "$REFERRERS" | jq '. | length')

if [ "$REFERRER_COUNT" -gt 0 ]; then
    echo "$REFERRERS" | jq -r '.[] | "  \(.referrer): \(.count) views (\(.uniques) unique)"' >> "$REPORT_FILE"
else
    echo "  No external referrers yet" >> "$REPORT_FILE"
fi
echo "" >> "$REPORT_FILE"

# Summary
echo "## INTELLIGENCE SUMMARY" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

TOTAL_LEADS=$((ACCESS_COUNT + COLLAB_COUNT))
echo "📈 Total qualified leads: $TOTAL_LEADS" >> "$REPORT_FILE"
echo "🎯 Demand signal strength: $([ "$STARS" -gt 10 ] && echo "STRONG" || echo "BUILDING")" >> "$REPORT_FILE"
echo "🔍 Monitoring status: ACTIVE" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

echo "================================================" >> "$REPORT_FILE"
echo "Report saved: $REPORT_FILE" >> "$REPORT_FILE"
echo "================================================" >> "$REPORT_FILE"

# Display report
cat "$REPORT_FILE"

echo ""
echo "✅ Intelligence report generated: $REPORT_FILE"
