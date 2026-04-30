#!/bin/bash
# Create a new AboutMe worklog issue
# Usage: ./create-worklog.sh "Worklog: Topic" "Description of what you're investigating"

set -e

TITLE="$1"
DESCRIPTION="$2"

if [ -z "$TITLE" ]; then
    echo "Usage: create-worklog.sh \"Worklog: Topic\" \"Description\""
    exit 1
fi

REPO="metis-of-the-gathering/About-Me"

echo "Creating worklog issue in $REPO..."

# Create temp file for body
BODY_FILE=$(mktemp)
cat > "$BODY_FILE" << EOF
## Worklog

$DESCRIPTION

## Progress

- [ ] Starting investigation
- [ ] Research phase
- [ ] Documented findings
- [ ] Complete

---
*Findings will be added as comments*
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
echo "  gh issue comment $ISSUE_NUM --body \"## Finding: ...\""