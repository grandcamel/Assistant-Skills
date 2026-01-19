# {{PRODUCT}} Assistant Skills Demo

A production-ready demo platform for {{PRODUCT}} Assistant Skills, providing interactive demonstrations of natural language {{PRODUCT}} automation with Claude Code.

## Features

- **Live Demo Sessions**: Single-user sessions with queue management
- **Invite System**: Secure access control with expiring invite links
- **Observability**: Built-in Grafana dashboards, Loki logging, Tempo tracing
- **Security**: Rate limiting, CSRF protection, secure session management
- **Responsive UI**: Modern landing page with real-time queue status

## Quick Start

### Prerequisites

- Docker and Docker Compose
- {{PRODUCT}} API credentials
- Claude Code authentication (OAuth token or API key)

### Setup

1. **Clone and configure:**
   ```bash
   cd {{DEMO_NAME}}
   cp secrets/example.env secrets/.env
   # Edit secrets/.env with your credentials
   ```

2. **Start development environment:**
   ```bash
   make dev
   ```

3. **Generate an invite:**
   ```bash
   make invite-local
   ```

4. **Access the demo:**
   Open the invite URL in your browser (e.g., `http://localhost:8080/ABC123`)

## Configuration

### Required Environment Variables

| Variable | Description |
|----------|-------------|
| `{{API_TOKEN_VAR}}` | {{PRODUCT}} API token |
{{#IF HAS_PLUGIN}}
| `{{API_URL_VAR}}` | {{PRODUCT}} API base URL |
{{/IF}}
| `CLAUDE_CODE_OAUTH_TOKEN` | Claude Code OAuth token (or use `ANTHROPIC_API_KEY`) |
| `SESSION_SECRET` | Secret for session signing (generate with `openssl rand -hex 32`) |

### Optional Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `SESSION_TIMEOUT_MINUTES` | {{SESSION_TIMEOUT}} | Session duration |
| `MAX_QUEUE_SIZE` | {{MAX_QUEUE_SIZE}} | Maximum queue length |

## Development

### Available Commands

```bash
make dev           # Start development environment
make dev-down      # Stop development environment
make logs          # View all service logs
make logs-queue    # View queue-manager logs
make lint          # Run linters
make lint-fix      # Auto-fix linting issues
make invite-local  # Generate local invite URL
make health        # Check service health
```

### Project Structure

```
{{DEMO_NAME}}/
├── docker-compose.yml      # Production config
├── docker-compose.dev.yml  # Development overrides
├── Makefile                # Development commands
├── queue-manager/          # Node.js WebSocket server
├── demo-container/         # Claude terminal container
├── landing-page/           # Static frontend
├── nginx/                  # Reverse proxy
├── observability/          # Grafana, Loki, Tempo
├── scripts/                # Maintenance scripts
└── secrets/                # Credentials (gitignored)
```

## Security

This demo includes multiple security features:

- **Input Validation**: Regex validation, whitelist enforcement
- **Rate Limiting**: Connection and brute-force protection
- **Session Security**: HMAC-SHA256 tokens, HttpOnly cookies
- **Container Security**: Memory/CPU limits, capability dropping
- **Credential Protection**: Environment file isolation, cleanup on session end
- **HTTP Headers**: Helmet.js with strict CSP
- **XSS Prevention**: DOMPurify sanitization

## Deployment

### Production

```bash
# Build and deploy
make deploy

# Setup SSL (requires domain)
make ssl-setup DOMAIN=demo.example.com
```

### Health Check

```bash
make health
```

## License

MIT License

---

Built with [Claude Code](https://claude.ai/code)
