# CLAUDE.md

This file provides guidance to Claude Code when working with the {{DEMO_NAME}} project.

## Project Overview

This is a production demo platform for **{{PRODUCT}} Assistant Skills** - a Claude Code plugin that enables natural language automation of {{PRODUCT}} operations.

### Architecture

```
{{DEMO_NAME}}/
├── docker-compose.yml          # Production orchestration
├── docker-compose.dev.yml      # Development overrides
├── Makefile                    # Dev/deploy/test targets
├── queue-manager/              # Node.js WebSocket server
│   ├── server.js               # Main server with session management
│   ├── templates/              # HTML templates
│   └── static/                 # CSS files
├── demo-container/             # Claude + plugin container
├── landing-page/               # Static HTML frontend
├── nginx/                      # Reverse proxy configuration
├── observability/              # LGTM stack (Grafana, Loki, Tempo)
├── scripts/                    # Python maintenance scripts
└── secrets/                    # Credentials (.gitignored)
```

### Key Services

| Service | Port | Purpose |
|---------|------|---------|
| nginx | 80, 443 | Reverse proxy, SSL, static content |
| queue-manager | 3000 | WebSocket, session management, invites |
| demo-container | 7681 | Claude terminal (ttyd, spawned per session) |
| redis | 6379 | Session state, queue, invite tokens |
| lgtm | 3001 (Grafana), 4317, 4318 | Grafana, Loki, Tempo (LGTM stack) |

## Development Commands

### Quick Start

```bash
# Start local development
make dev

# Access at http://localhost:8080
# Grafana at http://localhost:3001

# Stop environment
make dev-down
```

### Code Quality

```bash
# Run all linters
make lint

# JavaScript only (ESLint)
make lint-js

# Python only (Ruff)
make lint-py

# Auto-fix issues
make lint-fix
```

### Invite Management

```bash
# Generate invite (local dev)
make invite-local

# Generate with custom expiration and label
make invite EXPIRES=7d LABEL="Workshop Demo"

# List/revoke invites
make invite-list
make invite-revoke TOKEN=abc123
```

## Configuration

### Environment Variables

Set in `secrets/.env`:

```bash
# {{PRODUCT}} API
{{API_TOKEN_VAR}}=your-api-token
{{#IF HAS_PLUGIN}}
{{API_URL_VAR}}=https://api.example.com
{{/IF}}

# Claude Authentication (one required)
CLAUDE_CODE_OAUTH_TOKEN=...  # or
ANTHROPIC_API_KEY=...
```

## Security Considerations

### Session Management

- `SESSION_SECRET` must be set in production (server exits if default value detected with `NODE_ENV=production`)
- Session tokens use HMAC-SHA256 signatures
- Reconnection logic has race condition protection via `reconnectionInProgress` lock

### Input Validation

- Invite tokens validated via regex: `[A-Za-z0-9_-]{4,64}`
- HTML template substitution uses `escapeHtml()` to prevent XSS
- Scenario names validated against whitelist (`SCENARIO_NAMES` object)

## Troubleshooting

### Common Issues

**Container fails to start:**
```bash
# Check Docker is running
docker info

# Check for port conflicts
lsof -i :3000 -i :3001 -i :8080

# View container logs
make logs
```

**Claude authentication fails:**
```bash
# Verify token is set
echo $CLAUDE_CODE_OAUTH_TOKEN | head -c 20
```

**Redis connection issues:**
```bash
# Check Redis is running
docker compose ps redis

# Connect to Redis CLI
docker compose exec redis redis-cli ping
```

### Debug Mode

Enable verbose logging:

```bash
# All services
DEBUG=* make dev

# Specific service
make logs-queue
```

### Reset Everything

```bash
# Remove all containers and volumes
make clean-all
make dev
```
