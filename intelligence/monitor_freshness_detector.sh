#!/bin/bash
#
# Freshness Detector Intelligence Monitoring
# Tracks GitHub activity, user engagement, and market signals
#

set -e

REPO="onlyecho822-source/freshness-detector"
REPORT_DIR="/home/ubuntu/Echo/intelligence/reports"
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
REPORT_FILE="$REPORT_DIR/freshness_detector_$TIMESTAMP.md"

mkdir -p "$REPORT_DIR"

echo "# Freshness Detector Intelligence Report" > "$REPORT_FILE"
echo "**Generated:** $(date)" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# Repository metrics
echo "## Repository Metrics" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

STARS=$(gh api repos/$REPO --jq '.stargazers_count')
WATCHERS=$(gh api repos/$REPO --jq '.subscribers_count')
FORKS=$(gh api repos/$REPO --jq '.forks_count')
OPEN_ISSUES=$(gh api repos/$REPO --jq '.open_issues_count')

echo "- **Stars:** $STARS" >> "$REPORT_FILE"
echo "- **Watchers:** $WATCHERS" >> "$REPORT_FILE"
echo "- **Forks:** $FORKS" >> "$REPORT_FILE"
echo "- **Open Issues:** $OPEN_ISSUES" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# Recent activity
echo "## Recent Activity (Last 7 Days)" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# Stars
echo "### New Stars" >> "$REPORT_FILE"
gh api "repos/$REPO/stargazers" \
  --header "Accept: application/vnd.github.star+json" \
  --jq '.[] | select(.starred_at > (now - 7*24*60*60 | todate)) | "- [\(.user.login)](\(.user.html_url)) - \(.starred_at)"' \
  >> "$REPORT_FILE" 2>/dev/null || echo "- None" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# Issues
echo "### New Issues" >> "$REPORT_FILE"
gh issue list --repo "$REPO" --limit 10 --json number,title,author,createdAt,labels \
  --jq '.[] | "- [#\(.number)](\(.url)) \(.title) by @\(.author.login) (\(.createdAt | split("T")[0]))"' \
  >> "$REPORT_FILE" 2>/dev/null || echo "- None" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# Use case submissions
echo "### Use Case Submissions" >> "$REPORT_FILE"
gh issue list --repo "$REPO" --label "use-case" --limit 5 --json number,title,author,body \
  --jq '.[] | "#### [\(.title)](https://github.com/'$REPO'/issues/\(.number))\n- **Author:** @\(.author.login)\n- **Excerpt:** \(.body | split("\n")[0:3] | join(" "))\n"' \
  >> "$REPORT_FILE" 2>/dev/null || echo "- None yet" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# Discussions
echo "### Discussions" >> "$REPORT_FILE"
gh api "repos/$REPO/discussions" --jq '.[] | "- [\(.title)](\(.url)) by @\(.author.login)"' \
  >> "$REPORT_FILE" 2>/dev/null || echo "- None yet" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# Traffic (requires push access)
echo "## Traffic Data" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
gh api "repos/$REPO/traffic/views" --jq '"- **Total views (14 days):** \(.count)\n- **Unique visitors:** \(.uniques)"' \
  >> "$REPORT_FILE" 2>/dev/null || echo "- Not available (requires push access)" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# Clone data
gh api "repos/$REPO/traffic/clones" --jq '"- **Total clones (14 days):** \(.count)\n- **Unique cloners:** \(.uniques)"' \
  >> "$REPORT_FILE" 2>/dev/null || echo "- Not available" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# Referrers
echo "## Top Referrers" >> "$REPORT_FILE"
gh api "repos/$REPO/traffic/popular/referrers" --jq '.[] | "- **\(.referrer):** \(.count) views (\(.uniques) unique)"' \
  >> "$REPORT_FILE" 2>/dev/null || echo "- Not available" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# Intelligence analysis
echo "## Intelligence Analysis" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# Qualified leads (stars from AI/ML organizations)
echo "### Qualified Leads" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
echo "**Criteria:** Stars from users with AI/ML keywords in bio/repos" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

gh api "repos/$REPO/stargazers" --jq '.[].user.login' | head -20 | while read username; do
  USER_DATA=$(gh api "users/$username" 2>/dev/null || echo "{}")
  BIO=$(echo "$USER_DATA" | jq -r '.bio // empty')
  COMPANY=$(echo "$USER_DATA" | jq -r '.company // empty')
  
  if echo "$BIO $COMPANY" | grep -iE "(ai|ml|machine learning|data science|llm|model)" > /dev/null; then
    echo "- **@$username** - $COMPANY - $BIO" >> "$REPORT_FILE"
  fi
done

if ! grep -q "^- \*\*@" "$REPORT_FILE"; then
  echo "- No qualified leads identified yet" >> "$REPORT_FILE"
fi
echo "" >> "$REPORT_FILE"

# Summary
echo "## Summary" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
echo "- **Total engagement:** $((STARS + WATCHERS + FORKS)) interactions" >> "$REPORT_FILE"
echo "- **Signal strength:** $([ $STARS -gt 10 ] && echo "Strong" || [ $STARS -gt 3 ] && echo "Moderate" || echo "Weak")" >> "$REPORT_FILE"
echo "- **Next action:** $([ $OPEN_ISSUES -gt 0 ] && echo "Respond to issues" || echo "Monitor for 7 more days")" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# Output to console
cat "$REPORT_FILE"

echo ""
echo "---"
echo "Report saved to: $REPORT_FILE"
echo "Run again in 7 days: $(date -d '+7 days' +"%Y-%m-%d")"
