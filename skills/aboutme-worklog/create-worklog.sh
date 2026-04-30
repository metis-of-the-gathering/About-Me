#!/bin/bash
# Create a worklog issue in AboutMe repo

if [ -z "$1" ]; then
    echo "Usage: $0 \"Title\" \"Body\""
    exit 1
fi

TITLE="$1"
BODY="${2:-## Goal

## Progress
- [ ] Started
- [ ] Research complete
- [ ] Done}"

source ~/.profile
gh issue create \
  --repo metis-of-the-gathering/About-Me \
  --title "$TITLE" \
  --body "$BODY"