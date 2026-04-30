---
name: github-issue-worklog
description: "Create and work through GitHub issues as work logs - track findings, learnings, and progress as issue comments"
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [GitHub, Issues, Worklog, Research, Documentation]
    related_skills: [github-issues, github-auth, writing-plans]
---

# GitHub Issue Worklog Workflow

Create GitHub issues as work logs and track findings, research, and progress through issue comments.

## When to Use

Use this skill when:
- Starting research or investigation work
- Documenting learnings that should persist
- Tracking progress on ambiguous or evolving tasks
- Creating a knowledge base of discoveries
- Working through complex problems that need documentation

## Core Pattern

1. **Create an issue** in a designated "AboutMe" or worklog repository
2. **Log initial context** as the issue body
3. **Add findings as comments** - experiments, discoveries, learnings
4. **Update the issue** as work progresses
5. **Close when complete** with final summary

## Issue Creation

### Create Worklog Issue

```bash
# Determine repository (use AboutMe repo or current project)
REPO="${WORKLOG_REPO:-metis-of-the-gathering/About-Me}"

# Create issue with initial context
gh issue create \
  --repo "$REPO" \
  --title "Worklog: [Brief description of investigation]" \
  --body "## Investigation Goal

[What you're investigating or building]

## Initial Context

[Any relevant starting information, constraints, resources]

## Approach

[Planned or actual approach to the work]

## Progress Tracking

- [ ] Initial setup
- [ ] Research phase
- [ ] Implementation/experiments
- [ ] Documentation complete"
```

### Issue Naming Convention

- `Worklog: Research into X` - research investigations
- `Worklog: Building Y` - feature implementation
- `Worklog: Debugging Z` - troubleshooting sessions
- `Worklog: Learning A` - educational/exploration work

## Adding Findings as Comments

### Log a Finding

```bash
gh issue comment <ISSUE_NUMBER> --repo "$REPO" --body "## Finding: [Topic]

**Context:** [What led to this discovery]

**Result:** [What was found]

**Details:**
- Specific details
- Code snippets
- Links to resources

**Next steps:** [What this enables or what to try next]"
```

### Log Experimental Results

```bash
gh issue comment <ISSUE_NUMBER> --repo "$REPO" --body "## Experiment: [Description]

**Hypothesis:** [What you expected]

**Test:** [What you tried]

**Result:** [What happened]

**Conclusion:** [What it means]"
```

### Log Learning/Research

```bash
gh issue comment <ISSUE_NUMBER> --repo "$REPO" --body "## Research Note: [Topic]

**Source:** [Documentation, code, person]

**Key Points:**
- Important detail 1
- Important detail 2

**Implications:** [How this affects the work]"
```

## Workflow Templates

### Research Investigation Template

```bash
# 1. Create issue
gh issue create \
  --title "Worklog: Research [topic]" \
  --body "## Research Question
[What am I trying to learn/answer]

## Resources to Investigate
- [ ] [Resource 1]
- [ ] [Resource 2]
- [ ] [Resource 3]

## Findings Log
(Comments will be added here as findings accumulate)"

# Save the issue number
ISSUE_NUM=$(gh issue list --repo "$REPO" --search "Worklog: Research [topic]" --json number --jq '.[0].number')
```

### Feature Investigation Template

```bash
gh issue create \
  --title "Worklog: [Feature name] investigation" \
  --body "## Goal
[Build/understand this feature]

## Constraints
[Any limitations, requirements]

## Approach
1. Understand existing code
2. Identify patterns to follow
3. Plan implementation

## Progress
- [ ] Code review complete
- [ ] Pattern identified
- [ ] Implementation plan ready"
```

## Progress Tracking

### Mark Task Complete

```bash
# Comment on progress
gh issue comment $ISSUE_NUM --body "## Progress Update

Completed: [what was done]
Next: [what's coming up]"
```

### Update Checklist

```bash
# View current issue
gh issue view $ISSUE_NUM --repo "$REPO"

# Comment with updated checklist
gh issue comment $ISSUE_NUM --body "## Status Update

- [x] Done item 1
- [x] Done item 2
- [ ] Next item"
```

## Closing the Worklog

### Final Summary

```bash
gh issue comment $ISSUE_NUM --body "## Final Summary

**Goal Achieved:** [Yes/Partially/No]

**Key Findings:**
1. [Most important discovery]
2. [Second key finding]

**Artifacts Created:**
- [Files, code, documentation]

**Next Steps:**
- [Follow-up work needed]

**Time Spent:** [Approximately X hours]"

gh issue close $ISSUE_NUM --repo "$REPO"
```

### Convert to Implementation Plan

If the worklog leads to concrete implementation:

```bash
# Use the worklog contents to create a plan
# The comments contain the research and decisions

# Then use writing-plans skill to create the plan
# Reference the issue number in the plan for context
```

## Integration with Other Skills

### With writing-plans

After investigation worklog is complete:

1. Read the issue and comments
2. Extract the implementation decisions
3. Create a formal plan using `writing-plans`
4. Reference the worklog issue for context

```bash
# Get all issue data including comments
gh issue view $ISSUE_NUM --repo "$REPO"

# Create implementation plan
# "Based on worklog issue #$ISSUE_NUM, here's the implementation plan..."
```

### With subagent-driven-development

For complex investigations:

1. Create worklog issue
2. Delegate research tasks to subagents
3. Each subagent logs findings as comments
4. Synthesize findings into final summary

## Quick Reference

| Action | Command |
|--------|---------|
| Create worklog | `gh issue create --title "Worklog: ..." --body-file /tmp/body.md --repo $REPO` |
| Log finding | `gh issue comment <N> --body "$(cat <<'EOF'...)"` or `--body-file` |
| Log experiment | `gh issue comment <N> --body "## Experiment: ..."` |
| Update status | `gh issue comment <N> --body "## Progress: ..."` |
| Final summary | `gh issue comment <N> --body "## Summary: ..."` then `gh issue close <N>` |
| View worklog | `gh issue view <N> --repo $REPO` |

## Best Practices

- **One worklog per investigation** - keep topics focused
- **Timestamp important comments** - helps with chronology
- **Use markdown formatting** - makes logs scannable
- **Link related issues** - cross-reference when relevant
- **Keep the summary updated** - edit the top comment as understanding evolves

## Pitfall: Bash Escaping in Body Text

When using `gh issue create` or `gh issue comment` with markdown containing:
- Backticks (`` `code` ``)
- Dollar signs (`$VAR`)
- Quotes mixed with heredocs

The shell may interpret special characters incorrectly.

**Solutions:**

1. **Use heredoc for complex bodies:**
```bash
gh issue comment $ISSUE_NUM --body "$(cat <<'EOF'
## Finding: Complex content

**Code example:**
\`\`\`
def function():
    return $value  # won't be interpreted
\`\`\`
EOF
)"
```

2. **Escape special characters:**
```bash
gh issue comment $ISSUE_NUM --body "## Finding: Use backslash
    
\`\`\`code block\`\`\` \`command\` and \$variable"
```

3. **Pass body via file:**
```bash
echo "## Finding content" > /tmp/body.md
gh issue create --title "..." --body-file /tmp/body.md
```"