#!/bin/bash
# Quick worklog issue creator
# Usage: ./create-worklog.sh "Worklog: Investigating X" "Description of what you're doing"

set -e

REPO="${WORKLOG_REPO:-metis-of-the-gathering/About-Me}"
TITLE="$1"
DESCRIPTION="$2"

if [ -z "$TITLE" ]; then
    echo "Usage: create-worklog.sh \"Worklog: Title\" \"Description\""
    exit 1
fi

echo "Creating worklog issue in $REPO..."

# Use heredoc to avoid shell escaping issues with special characters
BODY_FILE=$(mktemp)
cat > "$BODY_FILE" << EOF
## Worklog

$DESCRIPTION

## Progress

- [ ] Starting investigation
- [ ] Research phase
- [ ] Implementation
- [ ] Complete

---
*This is a worklog issue - findings will be added as comments*
EOF

ISSUE_URL=$(gh issue create \
    --title "$TITLE" \
    --body-file "$BODY_FILE" \
    --repo "$REPO")

rm -f "$BODY_FILE"

ISSUE_NUM=$(echo "$ISSUE_URL" | grep -oP '#\d+' | tr -d '#')

echo "✓ Created worklog issue #$ISSUE_NUM"
echo "URL: $ISSUE_URL"
echo ""
echo "To add findings:"
echo "  gh issue comment $ISSUE_NUM --repo $REPO --body \"## Finding: ...\""