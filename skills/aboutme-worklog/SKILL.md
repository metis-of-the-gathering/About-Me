---
name: aboutme-worklog
description: "Work through GitHub issues in AboutMe repo - create issues and log all findings/learnings as comments"
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [GitHub, Issues, Worklog, AboutMe, Documentation]
    related_skills: [github-issue-worklog, github-issues]
---

# AboutMe Worklog Workflow

Create GitHub issues in the AboutMe repo and log all findings, learnings, and progress as issue comments.

## Core Workflow

When you say "make a new issue", this means:
1. Create an issue in `metis-of-the-gathering/About-Me`
2. Log the initial task/goal in the issue body
3. Add ALL subsequent findings, research, and learnings as comments

## Creating a New Issue

```bash
# Create worklog issue
./create-worklog.sh "Worklog: [Topic]" "[Brief description]"
```

Or manually:
```bash
gh issue create \
  --repo metis-of-the-gathering/About-Me \
  --title "Worklog: [Topic]" \
  --body "## Goal
        
[What you're investigating or building]

## Progress Tracking
- [ ] Started
- [ ] Research complete
- [ ] Findings documented"
```

## Logging Findings as Comments

**Always add findings as comments, not in the issue body:**

```bash
# Log a finding
gh issue comment <ISSUE_NUM> --repo metis-of-the-gathering/About-Me \
  --body "## Finding: [Topic]

**Context:** [What led to this]
**Result:** [What was discovered]
**Evidence:** [Links, code, screenshots]"

# Log an experiment
gh issue comment <ISSUE_NUM> --repo metis-of-the-gathering/About-Me \
  --body "## Experiment: [Description]

**Hypothesis:** [Expected outcome]
**Test:** [What was tried]
**Result:** [What happened]
**Conclusion:** [What it means]"

# Log research/learning
gh issue comment <ISSUE_NUM> --repo metis-of-the-gathering/About-Me \
  --body "## Research Note: [Topic]

**Source:** [Where from]
**Key Points:**
- Point 1
- Point 2

**Implications:** [How this affects the work]"
```

## Comment Templates

### Investigative Finding
```
## Finding: [Brief title]

**Context:** [What prompted this investigation]
**Method:** [How you discovered it]
**Result:** [What you found]
**Significance:** [Why it matters]
```

### Experiment Result
```
## Experiment: [What was tested]

**Hypothesis:** [Expected outcome]
**Approach:** [What was done]
**Result:** [What actually happened]
**Learning:** [What this teaches us]
```

### Documentation/Resource
```
## Resource: [Title]

**Source:** [URL, file, person]
**Key Info:**
- Detail 1
- Detail 2

**Relevance:** [How it applies to current work]
```

## Finalizing

Add a summary comment and close:
```bash
gh issue comment <ISSUE_NUM> --body "## Summary

**Goal:** [Accomplished/Not accomplished]

**Key Learnings:**
1. [Most important discovery]
2. [Second key finding]

**Artifacts:** [Files, code, docs created]"

gh issue close <ISSUE_NUM>
```