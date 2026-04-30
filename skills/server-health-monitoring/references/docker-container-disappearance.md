# Docker Container Disappearance Investigation

When Docker containers vanish mysteriously, follow this investigation sequence:

## Discovery Steps

```bash
# 1. Check current state
docker ps -a

# 2. Check for active compose projects
docker compose ls --all

# 3. Check images still exist (proves containers were removed, not images)
docker images | grep -E 'hermes|surreal|n8n'

# 4. Check bash history for destructive commands
cat ~/.bash_history | grep -E 'docker|rm'

# 5. Check systemd services (migration from Docker to systemd?)
systemctl status hermes-gateway  # or relevant service

# 6. Check volumes (data may persist even if containers gone)
docker volume ls

# 7. Check what's actually running
ps aux | grep hermes
```

## Common Causes

| Finding | Likely Cause |
|---------|--------------|
| `rm -rf hermes-data/` in history | Directory containing `docker-compose.yml` was deleted |
| Images exist but no containers | `docker compose down` ran or compose directory removed |
| Service running via systemd | Migration from Docker containers to native systemd service |
| Only some containers affected | Separate compose projects; unaffected ones have their own yaml |

## Key Insight: Separation of Concerns

Docker containers are ephemeral snapshots. The persistent state is:
1. **Images** — rarely disappear unless `docker image prune`
2. **Volumes** — persist unless `docker system prune -v` or explicit `docker volume rm`
3. **Compose configuration** — in yaml files; if deleted, `docker compose up` can't recreate

## Recovery Path

If containers disappeared due to compose directory deletion:
1. Recreate the `docker-compose.yml` from backup or git history
2. `docker compose up -d` will recreate containers from existing images
3. Volumes mount data back in (unless `docker volume rm` also ran)

## Case Study: metis.the-gathering.earth (2026-04-30)

- History showed: `rm -rf hermes-data/`
- `hermes-data/` contained `docker-compose.yml` defining hermes, hermes-dashboard, surrealdb
- Migration completed: Hermes now runs as `hermes-gateway.service` (systemd)
- n8n unaffected: Has its own compose file at `/opt/n8n/docker-compose.yml`