# metis.the-gathering.earth — Server Stack Reference

**OS:** AlmaLinux 10.1 (Heliotrope Lion)
**Hardware:** Intel Xeon E3-1270 v6 @ 3.80GHz, 8 cores, 32GB RAM, 417GB RAID disk

## Key Services

| Service | Unit | User | Notes |
|---|---|---|---|
| Django app | `gathering-app.service` | `gatheringprd` | Gunicorn, workdir `/srv/www/the-gathering.earth` |
| Async tasks | `gathering-qcluster.service` | `gatheringprd` | Django-Q2 cluster |
| Database | `postgresql-18.service` | postgres | PostgreSQL 18 |
| Web proxy | `nginx.service` | nginx | Reverse proxy on 80/443 |
| Agent | `hermes-gateway.service` | hermes | Hermes Agent gateway |
| Monitoring | `zabbix-agent.service` | zabbix | Zabbix agent (check for alert overlap) |
| Containers | `docker.service` / `containerd.service` | — | Docker available |

## Django App Config
- Settings module: `config.settings.prod`
- Gunicorn config: `deploy/gunicorn.conf.py`
- Env file: `/srv/www/the-gathering.earth/.env`
- Workers: 4 (arbiter + 4 workers observed)
- Memory: ~467MB RSS (peak 476MB)

## Django-Q2 Scheduled Tasks (observed)
- `agents.metis_telegram_update.metis_telegram_update` — [METIS Telegram Updates]
- `coherence.iris_realtimekit.realtimekit_downloader` — [IRIS: RealtimeKit downloader]

## Log Access Matrix (as `hermes` user)
- `journalctl -u <service>` — ✅ full access, use `--since`, `--no-pager`
- `/var/log/nginx/` — ❌ permission denied
- `/srv/www/the-gathering.earth/` — ❌ permission denied (owned by `gatheringprd`)
- `/opt/hermes/.hermes/` — ✅ full read/write

## Baseline Health (2026-04-29)
- Uptime: 26+ days
- Load avg: 0.07–0.08 (very low)
- Disk: 84G / 417G (21%)
- Memory: 5.2Gi used / 31Gi total (25Gi available)
- All 5 key services: active

## Noise to Filter
- Frequent 500s on `GET /` from scanners: PROPFIND, `.env` probes, old/fake browser UAs
- Cloudflare security center HEAD requests (301 redirects, normal)
- AI bots: `Claude-SearchBot`, `OAI-SearchBot` hitting `/robots.txt` (404, add robots.txt)
