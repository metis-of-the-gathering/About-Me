# SurrealDB Investigation Pattern

When checking if SurrealDB is running, use this discovery sequence:

```bash
# 1. Check Docker containers
docker ps -a --filter name=surrealdb

# 2. Check systemd services
systemctl list-units --type=service --all | grep -i surreal

# 3. Check processes
ps aux | grep -i surreal

# 4. Check listening ports (SurrealDB typically uses 8000 or 8765)
ss -tlnp | grep -E '8000|8765'

# 5. Check if surrealdb binary is installed
which surreal

# 6. Check for surrealdb-related files
find /opt/hermes /opt /etc/docker -name '*surreal*' -type f 2>/dev/null
```

## Status Interpretation

| Finding | Meaning |
|---------|---------|
| No container, no service | SurrealDB not deployed |
| Container in restart loop | Configuration or permission issue |
| Container running, port listening | Healthy |
| Container stopped | May have been stopped intentionally |

## History on metis.the-gathering.earth

- **2026-04-29**: SurrealDB container was crash-looping (`Restarting (2)`) - subsequently stopped/removed
- No systemd service exists
- No binary installed in PATH
- Port 5432 active (PostgreSQL), not SurrealDB ports

## Next Steps for Implementation

1. Create data directory: `~/.hermes/tcc/state/knowledge-base/surreal-data/`
2. Deploy via docker-compose on port 8765 (avoiding Genesis port 8000)
3. Configure environment variables in Hermes profile