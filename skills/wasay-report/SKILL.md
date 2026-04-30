---
name: wasay-report
description: Generate Asana report with filtered Tomorrow/This Week sections and overdue highlighting
category: productivity

trigger_words:
  - "asana report"
  - "task report"

prerequisites:
  - ASANA_ACCESS_TOKEN environment variable
  - EMAIL_PASSWORD for sending emails (optional for display-only)

---

## Overview

Fetches assigned tasks from an Asana project with smart filtering:

- **⚡ New** - tasks newly added awaiting work
- **🌞 Today** - tasks scheduled for current day (always shown)
- **🌸 Tomorrow** - only tasks due today or older (skips if empty)
- **🌸 This Week** - only tasks due today or older (skips if empty)
- **📅 Backlog** - incomplete tasks regardless of due date

## Key Filters

- **Tomorrow & This Week sections**: Only include tasks with `due_on` date ≤ today. Tasks due in the future are excluded.
- **Overdue detection**: Tasks with `due_on` before today are marked with ⚠️
- **Tasks without due dates**: Only shown in New and Today sections

## Quick Run

```python
import requests
from datetime import datetime, timezone

TOKEN = os.environ.get("ASANA_ACCESS_TOKEN", "YOUR_TOKEN_HERE")
headers = {"Authorization": f"Bearer {TOKEN}"}
ASSIGNEE_GID = "YOUR_ASSIGNEE_GID"  # Get from Asana API or URL
TODAY = datetime.now(timezone.utc).date()

SECTIONS = {
    "⚡ New": "SECTION_GID_1",
    "🌞 Today": "SECTION_GID_2",
    "🌸 Tomorrow": "SECTION_GID_3",
    "🌸 This Week": "SECTION_GID_4",
    "📅 Backlog": "SECTION_GID_5"
}

def fetch_tasks(section_gid):
    response = requests.get(
        f"https://app.asana.com/api/1.0/sections/{section_gid}/tasks",
        headers=headers,
        params={"opt_fields": "name,assignee.gid,due_on,completed"}
    )
    return response.json().get("data", [])

# ... rest of the logic follows same pattern
```

## Email Configuration

To send via email, add to `~/.profile`:
```bash
export EMAIL_PASSWORD="your_smtp_password"
```

Email uses SSL SMTP on port 465. Configure your SMTP server details.

## Daily Cron

Set up the daily cron job:
```bash
cronjob action=create name=asana-daily-report schedule="0 2 * * *" skills="wasay-report" prompt="Run the asana report and send email"
```

## Customization Notes

- Replace `YOUR_TOKEN_HERE` with your Asana personal access token
- Replace `ASSIGNEE_GID` with the Asana GID of the user whose tasks you want to fetch
- Replace `SECTION_GID_X` with your actual section GIDs from the Asana project
- Find section GIDs by opening the project in Asana and checking the URL when clicking on each section