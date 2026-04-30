---
name: server-health-monitoring
description: "Periodic server health checks + Django log monitoring via cron, delivered to Telegram. Covers discovery, script authoring, scheduling, and permission pitfalls on AlmaLinux/systemd."
tags: [devops, monitoring, django, cron, systemd, journalctl, telegram]
---

# Server Health Monitoring

## When to use this skill
- User wants periodic health/status reports delivered to Telegram (or other channels)
- User asks to monitor Django logs, service status, error rates, disk/memory/CPU
- Setting up cron-based monitoring on a systemd server (AlmaLinux, RHEL, CentOS)

---

## Discovery Phase — run these first

```bash
# 1. Running services
systemctl list-units --type=service --state=running

# 2. Find Django apps
find /srv /opt /home /var/www -name "manage.py" 2>/dev/null | head -20

# 3. Read service unit files to find log paths, users, working dirs
systemctl cat <service-name>.service

# 4. Check journal access (hermes user has read access to systemd journal)
journalctl -u <service>.service -n 20 --no-pager
```

### Known stack on metis.the-gathering.earth
- **gathering-app.service** — Gunicorn (Django), user `gatheringprd`, workdir `/srv/www/the-gathering.earth`
- **gathering-qcluster.service** — Django-Q2 async task cluster
- **postgresql-18.service** — Database
- **nginx.service** — Reverse proxy
- **hermes-gateway.service** — Hermes Agent gateway
- **surrealdb** — (container, optional) Knowledge graph for Genesis Brain Light MVP — check with `docker ps -a --filter name=surrealdb`
- Logs accessible via `journalctl` (no direct file access — nginx/app logs in `/var/log/nginx/` and `/srv/www/` are permission-denied for hermes user)

---

## Script Pattern

The health report script lives at `/opt/hermes/.hermes/scripts/server_health_report.py`.

Key sections to include:
1. **Uptime + load** — `uptime` parsed with regex
2. **Memory** — `free -h`
3. **Disk** — `df -h /` with 🟢/🟡/🔴 threshold icons (70%/85%)
4. **Service status** — `systemctl is-active <svc>` for each key service
5. **5xx errors (last 1h)** — `journalctl --since "1 hour ago"` + grep for `" 5[0-9][0-9] "`
6. **Django app errors** — grep for `[ERROR]`, `[CRITICAL]`, `Traceback`, `Internal Server Error`
7. **Q-cluster failures** — journalctl on qcluster service, grep `failed|error|critical`
8. **Traffic summary** — request count + top paths via grep + sort/uniq

See `templates/server_health_report.py` for the full working script.

---

## Cron Job Setup

```python
cronjob(
    action="create",
    name="Server Health Monitor",
    deliver="origin",           # sends report back to same Telegram chat
    enabled_toolsets=["terminal"],
    schedule="every 1h",
    script="server_health_report.py",  # relative to ~/.hermes/scripts/
    prompt="<instructions for what to do with script output>"
)
```

The `script` field runs the script and passes output to the LLM prompt. The prompt should instruct METIS to send the output as-is, optionally prepending an alert line if services are down or errors exceed threshold.

---

## Permission Pitfalls

| Resource | Access as `hermes` | Workaround |
|---|---|---|
| `journalctl` | ✅ Full access | Use `--since`, `--no-pager`, `-u <svc>` |
| `/var/log/nginx/` | ❌ Permission denied | Request nginx group membership or log forwarding |
| `/srv/www/the-gathering.earth/` | ❌ Permission denied | Same — owned by `gatheringprd` |
| `nginx -t` / `nginx -s reload` | ❌ Requires root | Use `sudo` (requires wheel + passwordless sudo config) |
| Writing scripts | ✅ `/opt/hermes/.hermes/scripts/` | Use `write_file()` via execute_code, NOT write_file tool directly (resolves wrong path) |

**Critical:** Use `execute_code` with `from hermes_tools import write_file` to write files — the built-in `write_file` tool resolves paths incorrectly for the hermes user's home at `/opt/hermes/`.

---

## Alert Logic (in cron prompt)

```
If there are 🔴 service failures or high 5xx error counts (>20/hour),
prepend: "🚨 **ACTION REQUIRED** — see details below."
Otherwise send the report as-is with no commentary.
```

---

## Known Patterns / Observations

- **500s on `/` from bots**: Scanners (PROPFIND, `.env` probes, old Firefox UAs) generate 500s on the root URL. These are noise — filter or note in report.
- **Django-Q2 tasks visible**: Q-cluster logs show scheduled task names and modules (e.g. `coherence.iris_realtimekit.realtimekit_downloader`, `agents.metis_telegram_update`). Useful for confirming scheduled jobs ran.
- **Zabbix agent** is installed — may overlap with what we're doing here. Check if alerts already exist before setting up duplicate monitors.

---

## Support Files
- `templates/server_health_report.py` — Full working health report script for this server
- `references/docker-container-disappearance.md` — Investigation pattern when Docker containers vanish unexpectedly
