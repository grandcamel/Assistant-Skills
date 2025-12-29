# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Claude Code plugin marketplace providing templates, wizards, and tools for building Assistant Skills projects. It contains 3 production-ready skills and serves as both an installable plugin and a reference implementation.

## Commands

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run Tests
```bash
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

### Docker Compose
```bash
# Run unit tests
docker-compose -f docker/docker-compose.yml run --rm unit-tests

# Run with parallel execution
docker-compose -f docker/docker-compose.yml run --rm unit-tests-parallel

# Run live integration tests (requires .env)
docker-compose -f docker/docker-compose.yml run --rm live-tests
```

## Architecture

### Dual Directory Structure

Skills exist in two locations that must be kept in sync:
- `.claude/skills/` - Project-level skills (loaded when working in this repo)
- `skills/` - Plugin-installable copies (distributed via marketplace)

When modifying a skill, update both locations.

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

- `.claude-plugin/plugin.json` - Plugin definition
- `.claude-plugin/marketplace.json` - Marketplace registry with installable plugins

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
description: Third-person description with trigger phrases (under 1024 chars)
---

# Skill Name

Brief intro (1-2 sentences).

## Quick Start
## Usage Examples
## [Core sections]
```

### Commit Convention

Use conventional commits with TDD pattern:
```
test(scope): add failing tests for feature
feat(scope): implement feature (N/N tests passing)
```

Types: `feat`, `fix`, `docs`, `test`, `refactor`, `style`, `perf`, `build`, `ci`, `chore`

## Template Folders

- `00-project-lifecycle/` - API research, GAP analysis, architecture
- `01-project-scaffolding/` - Project initialization
- `02-shared-library/` - HTTP client, error handling patterns
- `03-skill-templates/` - SKILL.md format, script templates
- `04-testing/` - TDD workflow, pytest patterns
- `05-documentation/` - Workflow guides
- `06-git-and-ci/` - Commit conventions, GitHub Actions
