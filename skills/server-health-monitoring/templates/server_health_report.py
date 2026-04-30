#!/usr/bin/env python3
"""
Server health + Django log monitor for metis.the-gathering.earth
Run by Hermes cron job — output is delivered to Telegram.
"""

import subprocess
import re
from datetime import datetime, UTC

def run(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip()

def section(title, lines):
    return f"\n## {title}\n" + "\n".join(lines)

now = datetime.now(UTC)
report_lines = [f"🖥️ **Server Health Report**\n`{now.strftime('%Y-%m-%d %H:%M UTC')}`"]

# --- UPTIME & LOAD ---
uptime_raw = run("uptime")
load_match = re.search(r"load average: ([\d.]+), ([\d.]+), ([\d.]+)", uptime_raw)
uptime_match = re.search(r"up (.+?),\s+\d+ user", uptime_raw)
uptime_str = uptime_match.group(1).strip() if uptime_match else "?"
load1, load5, load15 = (load_match.groups() if load_match else ("?", "?", "?"))
report_lines.append(section("System", [
    f"⏱ Uptime: `{uptime_str}`",
    f"📊 Load (1/5/15m): `{load1} / {load5} / {load15}`"
]))

# --- MEMORY ---
mem_raw = run("free -h")
mem_lines = mem_raw.split("\n")
if len(mem_lines) >= 2:
    parts = mem_lines[1].split()
    if len(parts) >= 4:
        avail = parts[6] if len(parts) > 6 else parts[3]
        report_lines.append(section("Memory", [
            f"Total: `{parts[1]}` | Used: `{parts[2]}` | Available: `{avail}`"
        ]))

# --- DISK ---
disk_raw = run("df -h / 2>/dev/null | tail -1")
disk_parts = disk_raw.split()
if len(disk_parts) >= 5:
    disk_pct = int(disk_parts[4].rstrip('%'))
    disk_icon = "🔴" if disk_pct > 85 else ("🟡" if disk_pct > 70 else "🟢")
    report_lines.append(section("Disk (/)", [
        f"{disk_icon} Used: `{disk_parts[2]}` / `{disk_parts[1]}` ({disk_parts[4]})"
    ]))

# --- SERVICES ---
# Adjust this dict for the services you want to monitor
services = {
    "gathering-app": "🌐 Gunicorn (Django)",
    "gathering-qcluster": "⚙️ Django-Q2 cluster",
    "postgresql-18": "🗄️ PostgreSQL 18",
    "nginx": "🔀 nginx",
    "hermes-gateway": "🤖 Hermes Gateway",
}
svc_lines = []
for svc, label in services.items():
    status = run(f"systemctl is-active {svc}.service 2>/dev/null")
    icon = "✅" if status == "active" else "🔴"
    svc_lines.append(f"{icon} {label}: `{status}`")
report_lines.append(section("Services", svc_lines))

# --- DJANGO: Recent 500 errors (last 1h) ---
errors_raw = run(
    'journalctl -u gathering-app.service --since "1 hour ago" --no-pager 2>/dev/null'
    ' | grep -E \'" 5[0-9][0-9] \''
)
error_lines = [l for l in errors_raw.split("\n") if l.strip()]
if error_lines:
    counts = {}
    for l in error_lines:
        m = re.search(r'" (5\d\d) ', l)
        if m:
            code = m.group(1)
            counts[code] = counts.get(code, 0) + 1
    count_str = ", ".join([f"{c}: {n}x" for c, n in sorted(counts.items())])
    report_lines.append(section("⚠️ 5xx Errors (last 1h)", [
        f"Total: **{len(error_lines)}** ({count_str})",
        "Recent (last 3):"
    ] + [
        f"`{re.sub(r'^.*gunicorn\\[\\d+\\]: ', '', l)[-120:]}`" for l in error_lines[-3:]
    ]))
else:
    report_lines.append(section("✅ 5xx Errors (last 1h)", ["None detected"]))

# --- DJANGO: App-level errors ---
django_errors = run(
    'journalctl -u gathering-app.service --since "1 hour ago" --no-pager 2>/dev/null'
    ' | grep -iE "\\[ERROR\\]|\\[CRITICAL\\]|Traceback|Internal Server Error" | tail -10'
)
dj_lines = [l for l in django_errors.split("\n") if l.strip()]
if dj_lines:
    report_lines.append(section("🔥 Django App Errors (last 1h)", [
        f"`{l[-120:]}`" for l in dj_lines[:5]
    ]))

# --- QCLUSTER: task failures ---
qcluster_errors = run(
    'journalctl -u gathering-qcluster.service --since "1 hour ago" --no-pager 2>/dev/null'
    ' | grep -iE "failed|error|critical" | tail -5'
)
qc_lines = [l for l in qcluster_errors.split("\n") if l.strip()]
if qc_lines:
    report_lines.append(section("⚠️ Q-Cluster Issues (last 1h)", [
        f"`{l[-120:]}`" for l in qc_lines[:5]
    ]))
else:
    report_lines.append(section("✅ Q-Cluster (last 1h)", ["No failures detected"]))

# --- REQUEST RATE (last 1h) ---
req_count = run(
    'journalctl -u gathering-app.service --since "1 hour ago" --no-pager 2>/dev/null'
    ' | grep -c "HTTP/1" 2>/dev/null || echo 0'
)
top_paths = run(
    r"""journalctl -u gathering-app.service --since "1 hour ago" --no-pager 2>/dev/null | grep -oP '"(GET|POST|HEAD|PUT|DELETE) \K[^ ]+' | sort | uniq -c | sort -rn | head -5"""
)
traffic_lines = [f"Requests: **{req_count.strip()}**"]
if top_paths:
    traffic_lines.append("Top paths:")
    for line in top_paths.split("\n")[:5]:
        traffic_lines.append(f"  `{line.strip()}`")
report_lines.append(section("📈 Traffic (last 1h)", traffic_lines))

# --- OUTPUT ---
print("\n".join(report_lines))
