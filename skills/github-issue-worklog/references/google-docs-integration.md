# Google Workspace Integration Reference

This reference documents connecting Hermes to Google Docs and Drive via the `google-workspace` skill.

## Prerequisites

1. **Google Cloud Project** with APIs enabled:
   - Google Docs API
   - Google Drive API

2. **OAuth 2.0 Client Credentials** (Desktop app type)
   - Project must be in production OR user added as test user
   - Download JSON credentials file

## Setup

```bash
GSETUP="python ~/.hermes/skills/productivity/google-workspace/scripts/setup.py"
GAPI="python ~/.hermes/skills/productivity/google-workspace/scripts/google_api.py"

# Check current auth status
python3 $GSETUP --check

# If NOT_AUTHENTICATED:
python3 $GSETUP --client-secret /path/to/client_secret.json
python3 $GSETUP --auth-url --services docs,drive
# Visit the URL, authorize, copy the redirect URL
python3 $GSETUP --auth-code "http://localhost:1/?code=4/0A..."
```

## Common Commands

```bash
# Read document
python3 $GAPI docs get DOCUMENT_ID

# Search for documents in Drive
python3 $GAPI drive search "name contains 'Planning'"

# Get document ID then read it
DOC_ID=$(python3 $GAPI drive search "name = 'Project Plan'" --max 1 | jq -r '.[0].id')
python3 $GAPI docs get "$DOC_ID"
```

## Token Management

- Token stored at: `~/.hermes/google_token.json`
- Auto-refreshes via refresh token
- Revoke with: `python3 $GSETUP --revoke`