# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Claude Code plugin marketplace providing templates, wizards, and tools for building Assistant Skills projects. It contains 6 production-ready skills and serves as both an installable plugin and a reference implementation.

## Commands

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run Setup Wizard
```
/assistant-skills-setup
```
Configures shared venv at `~/.assistant-skills-venv/` and adds `claude-as` shell function.

### Run Tests
```bash
# Run all skill tests
pytest skills/*/tests/ -v

# Run specific skill tests
pytest skills/assistant-builder/tests/ -v
```

### Run Single Test
```bash
pytest skills/assistant-builder/tests/test_validate_project.py::test_validates_existing_project -v
```

### Analyze Skill Token Efficiency
```bash
./skills/skills-optimizer/scripts/analyze-skill.sh /path/to/skill
```

### Validate Skill Structure
```bash
./skills/skills-optimizer/scripts/validate-skill.sh /path/to/skill
```

### Run Tests in Docker
```bash
# Unit tests
./scripts/run-tests-docker.sh

# Unit tests with coverage
./scripts/run-tests-docker.sh --coverage

# Live integration tests
./scripts/run-live-tests-docker.sh

# All tests
./scripts/test.sh all

# Test across Python versions (3.8-3.12)
./scripts/test.sh matrix
```

### Docker Compose (Testing)
```bash
# Run unit tests
docker-compose -f docker/docker-compose.yml run --rm unit-tests

# Run with parallel execution
docker-compose -f docker/docker-compose.yml run --rm unit-tests-parallel

# Run live integration tests (requires .env)
docker-compose -f docker/docker-compose.yml run --rm live-tests
```

### Docker Runtime (Claude Code)
```bash
# Run Claude with Assistant Skills in Docker
./scripts/claude-as-docker.sh

# Or pull from GitHub Container Registry
docker run -it -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \
  -v $(pwd):/workspace ghcr.io/grandcamel/assistant-skills:latest

# With plugins and marketplaces
CLAUDE_PLUGINS="owner/plugin" CLAUDE_MARKETPLACES="owner/marketplace" \
  ./scripts/claude-as-docker.sh

# Build locally
docker build -t assistant-skills -f docker/runtime/Dockerfile .
```

### Run E2E Tests
```bash
# Run in Docker (recommended)
./scripts/run-e2e-tests.sh

# Run locally
./scripts/run-e2e-tests.sh --local

# With verbose output
./scripts/run-e2e-tests.sh --verbose
```

Authentication: Local runs prefer OAuth (`~/.claude.json`), Docker runs require `ANTHROPIC_API_KEY`. See `skills/e2e-testing/SKILL.md` for configuration options.

## Architecture

### Directory Structure

Skills and tests are in a single location:
- `skills/` - All skills with their scripts, docs, and tests
- `.claude-plugin/` - Plugin manifest, commands, and agents
- `hooks/` - Plugin hooks (SessionStart health checks)

The plugin.json references `../skills/` to load skills from the repo root.

### Test Infrastructure

- `pytest.ini` - Root config with `--import-mode=importlib` to avoid conftest conflicts
- `conftest.py` - Root fixtures (`temp_path`, `temp_dir`, `claude_project_structure`)
- `skills/*/tests/conftest.py` - Skill-specific fixtures (use root fixtures as dependencies)

### Shared Library

All Python scripts use the `assistant-skills-lib` package from PyPI:

```bash
pip install assistant-skills-lib
```

```python
from assistant_skills_lib import (
    format_table, validate_url, Cache, handle_errors,
    load_template, detect_project
)
```

The package provides:
- `formatters` - Output formatting (tables, trees, colors)
- `validators` - Input validation (names, URLs, paths)
- `cache` - Response caching with TTL
- `error_handler` - Exception hierarchy and `@handle_errors` decorator
- `template_engine` - Template loading and placeholder replacement
- `project_detector` - Find existing Assistant Skills projects

Package source: https://github.com/grandcamel/assistant-skills-lib

### Plugin Manifest Files

- `.claude-plugin/plugin.json` - Plugin definition (references `../skills/` and `../hooks/`)
- `.claude-plugin/marketplace.json` - Marketplace registry with installable plugins
- `.claude-plugin/commands/` - Slash commands (assistant-skills-setup, assistant-builder-setup)
- `.claude-plugin/agents/` - Skill reviewer agents

## Skill Development Patterns

### Progressive Disclosure Model

Skills use 3 levels to minimize token usage:

| Level | Target | Contains |
|-------|--------|----------|
| L1: Metadata | ~200 chars | YAML frontmatter in SKILL.md |
| L2: SKILL.md | <500 lines | Quick start, workflow overview |
| L3: docs/ | Variable | Detailed references, examples |

### SKILL.md Structure

```yaml
---
name: skill-name
description: Third-person description with trigger phrases (under 1024 chars). Use "This skill should be used when..." or include phrases like "add E2E tests", "test my plugin".
---

# Skill Name

Brief intro (1-2 sentences).

## Quick Start
## Usage Examples
## [Core sections]
```

Note: The `when_to_use` field is deprecated. Include trigger phrases directly in `description`.

### Router/Hub Skills

For projects with multiple specialized skills, create a router skill that routes requests to the appropriate skill. See `templates/03-skill-templates/router-skill/` for templates.

**Key components**:
- Quick Reference table with risk levels
- Keyword-based routing rules
- Negative triggers (what each skill does NOT handle)
- Disambiguation examples for ambiguous requests
- Context awareness (pronoun resolution, scope persistence)

**Core insight**: "The LLM IS the Router" - SKILL.md provides instructions for Claude, not configuration for code.

Example Quick Reference:
```markdown
| I want to... | Use this skill | Risk |
|--------------|----------------|:----:|
| Search with queries | topic-search | - |
| Create a single item | topic-issue | ⚠️ |
| Update 10+ items | topic-bulk | ⚠️⚠️ |
```

### Risk-Level Marking

Mark operations by risk in skill documentation:

| Risk | Meaning | Operations | Safeguards |
|:----:|---------|------------|------------|
| `-` | Safe | search, list, get, export | None |
| `⚠️` | Destructive | create, update, delete (single) | Confirm |
| `⚠️⚠️` | High-risk | bulk ops, admin changes | Confirm + dry-run |

Always include the legend: `**Risk Legend**: - Read-only | ⚠️ Destructive | ⚠️⚠️ High-risk`

See `templates/03-skill-templates/router-skill/RISK-LEVELS.md` for implementation patterns.

### Commit Convention

Use conventional commits with TDD pattern:
```
test(scope): add failing tests for feature
feat(scope): implement feature (N/N tests passing)
```

Types: `feat`, `fix`, `docs`, `test`, `refactor`, `style`, `perf`, `build`, `ci`, `chore`

## Template Folders

- `templates/00-project-lifecycle/` - API research, GAP analysis, architecture
- `templates/01-project-scaffolding/` - Project initialization
- `templates/02-shared-library/` - HTTP client, error handling patterns
- `templates/03-skill-templates/` - SKILL.md, scripts, router skills, bulk operations, discovery commands
- `templates/04-testing/` - TDD workflow, pytest patterns, sandboxed profiles
- `templates/05-documentation/` - Workflow guides, parallel subagents
- `templates/06-git-and-ci/` - Commit conventions, GitHub Actions

## Additional Patterns

| Pattern | Template | Key Flags/Options |
|---------|----------|-------------------|
| Bulk Operations | `templates/03-skill-templates/BULK-OPERATIONS.md` | `--dry-run`, `--batch-size`, `--enable-checkpoint`, `--resume` |
| Sandboxed Testing | `templates/04-testing/SANDBOXED-PROFILES.md` | `SANDBOX_PROFILE=read-only\|create-only\|full-access` |
| Parallel Subagents | `templates/05-documentation/PARALLEL_SUBAGENTS.md` | Worktrees, file-persisted results |

## Version Management

Single source of truth in `VERSION` file, synced across:
- `.claude-plugin/plugin.json`
- `.claude-plugin/marketplace.json`

```bash
./scripts/sync-version.sh --check     # Check if in sync
./scripts/sync-version.sh             # Sync all to VERSION
./scripts/sync-version.sh --set 2.0.0 # Set new version
```
