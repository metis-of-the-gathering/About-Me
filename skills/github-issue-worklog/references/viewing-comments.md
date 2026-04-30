# Viewing Issue Comments

To see all comments on an issue (important for worklogs):

```bash
# View issue with all comments
gh issue view <ISSUE_NUMBER> --repo "$REPO"

# View just the issue body (no comments)
gh issue view <ISSUE_NUMBER> --repo "$REPO" --json title,body --template '{{.title}}

{{.body}}'

# Get comments as JSON for processing
gh issue view <ISSUE_NUMBER> --repo "$REPO" --json comments
```

## Processing Worklog Comments

When converting a worklog to an implementation plan, you'll want all the comments:

```bash
# Get structured data from the worklog issue
gh issue view $ISSUE_NUM --repo "$REPO" > /tmp/worklog.json

# Extract comments
cat /tmp/worklog.json | python3 -c "
import sys, json
data = json.load(sys.stdin)
for c in data['comments']:
    print(f'=== Comment by {c[\"author\"][\"login\"]} ===')
    print(c['body'])
    print()
"
```