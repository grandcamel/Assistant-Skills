---
name: demo-scaffolding
version: 1.0.0
description: Create production-ready demo platforms for Assistant Skills plugins. Use when you want to "create a demo", "scaffold demo infrastructure", "set up demo for plugin", "generate demo project", or need to create queue-managed demo environments like jira-demo, confluence-demo, or splunk-demo.
category: infrastructure
tags: [demo, scaffolding, docker, queue-manager, observability, infrastructure]
author: grandcamel
license: MIT
---

# Demo Scaffolding Skill

Generate complete, security-hardened demo platforms for Assistant Skills plugins in minutes instead of days.

## What This Skill Does

Creates production-ready demo infrastructure similar to jira-demo, confluence-demo, and splunk-demo with:

| Component | Description |
|-----------|-------------|
| Queue Manager | Node.js WebSocket server with session management |
| Landing Page | Responsive HTML/CSS/JS with queue UI |
| Demo Container | Claude Code terminal with plugin pre-installed |
| Observability | LGTM stack (Grafana, Loki, Tempo, Prometheus) |
| Nginx | Reverse proxy with SSL support |
| Security | 12 security features enabled by default |

---

## Quick Start

### Interactive Mode (Recommended)

```bash
python scripts/create_demo.py
# Interactive wizard guides you through configuration
```

### Command Line Mode

```bash
python scripts/create_demo.py \
  --name github-demo \
  --product GitHub \
  --plugin github-assistant-skills \
  --plugin-source pypi \
  --api-url-var GITHUB_API_URL \
  --api-token-var GITHUB_TOKEN \
  --scenarios search,issues,repos,admin \
  --output ./github-demo
```

### Dry Run

```bash
python scripts/create_demo.py --dry-run
# Shows what would be generated without creating files
```

---

## Usage Examples

```
"Create a demo for my new GitHub Assistant Skills plugin"
"Scaffold a demo infrastructure for Slack plugin"
"Generate a demo project with mock API support"
"Set up demo environment similar to confluence-demo"
```

---

## Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| `--name` | Demo project name (kebab-case) | Required |
| `--product` | Product/brand name | Required |
| `--plugin` | Plugin identifier | Optional |
| `--plugin-source` | `pypi`, `github`, or `none` | `none` |
| `--api-url-var` | Base URL env var name | `{PRODUCT}_API_URL` |
| `--api-token-var` | Auth token env var name | `{PRODUCT}_API_TOKEN` |
| `--scenarios` | Comma-separated scenario names | `search,admin` |
| `--output` | Output directory | `./{name}` |
| `--session-timeout` | Session timeout minutes | `60` |
| `--max-queue` | Max queue size | `10` |
| `--enable-ci` | Generate GitHub Actions workflow | `false` |
| `--enable-precommit` | Generate pre-commit config | `false` |
| `--dry-run` | Show what would be created | `false` |

---

## Generated Structure

```
{demo-name}/
├── docker-compose.yml          # Production orchestration
├── docker-compose.dev.yml      # Development overrides
├── Makefile                    # 50+ dev/deploy targets
├── CLAUDE.md                   # Claude Code instructions
├── README.md                   # Project documentation
├── .gitignore
├── pyproject.toml              # Python linting config
│
├── queue-manager/              # Node.js WebSocket server
│   ├── server.js               # Main entry (modular)
│   ├── package.json
│   ├── Dockerfile
│   ├── config/                 # Configuration modules
│   ├── services/               # Business logic
│   ├── routes/                 # HTTP endpoints
│   └── handlers/               # WebSocket handlers
│
├── demo-container/             # Claude + plugin container
│   ├── Dockerfile
│   ├── entrypoint.sh
│   └── scenarios/              # Test scenarios
│
├── landing-page/               # Static web frontend
│   ├── index.html
│   ├── queue-client.js
│   └── styles.css
│
├── nginx/                      # Reverse proxy
├── observability/              # LGTM stack config
├── scripts/                    # Utility scripts
├── secrets/                    # Credentials template
└── .claude/                    # Claude Code commands
```

---

## Security Features (Always Enabled)

All generated demos include these security measures:

1. **Input Validation** - Regex validation, whitelist enforcement
2. **Rate Limiting** - Connection and invite brute-force protection
3. **Session Security** - HMAC-SHA256 tokens, HttpOnly cookies
4. **Container Security** - Memory/CPU/PID limits, capability dropping
5. **Credential Protection** - Env-file secrets, cleanup on session end
6. **HTTP Headers** - Helmet.js with strict CSP
7. **XSS Prevention** - DOMPurify, HTML escaping
8. **Path Traversal** - Resolved path validation
9. **WebSocket Security** - Origin validation, rate limiting
10. **Redis Security** - Error handling, TTL enforcement
11. **Docker Socket** - Minimal privileges
12. **Production Validation** - SESSION_SECRET enforcement

---

## Post-Generation Steps

After running the scaffolder:

```bash
cd {demo-name}

# 1. Configure credentials
cp secrets/example.env secrets/.env
# Edit secrets/.env with your API credentials

# 2. Start development environment
make dev

# 3. Generate invite URL
make invite-local

# 4. Access the demo
open http://localhost:8080
```

---

## Related Skills

| Skill | Purpose |
|-------|---------|
| `assistant-builder` | Create the plugin itself |
| `landing-page` | Generate README and branding |
| `e2e-testing` | Add comprehensive tests |
| `skills-optimizer` | Optimize skill token usage |

---

## Reference Implementations

| Demo | Repository | Skills |
|------|------------|--------|
| jira-demo | grandcamel/jira-demo | 14 |
| confluence-demo | grandcamel/confluence-demo | 14 |
| splunk-demo | grandcamel/splunk-demo | 13 |

Templates are extracted from these production demos.
