---
name: assistant-builder
description: "Build and scaffold Assistant Skills plugin projects. This skill should be used when: (1) create new Claude Code plugin project, (2) add skill to existing project, (3) scaffold CLI library for API, (4) wrap existing CLI tool, (5) validate project structure, (6) migrate existing project to new structure, (7) show reference patterns from production implementations (Jira, Confluence, Splunk)."
---

# Assistant Builder

Build production-ready Claude Code plugin projects that wrap CLIs or APIs.

## Quick Reference

| I want to... | Script | Type |
|--------------|--------|------|
| Create new project | `scaffold_project.py` | Interactive |
| Add skill to project | `add_skill.py` | Interactive |
| Generate CLI library | `scaffold_library.py` | Interactive |
| Validate structure | `validate_project.py` | Check |
| Migrate old project | `migrate_project.py` | Transform |
| Show reference patterns | `show_reference.py` | Info |
| List templates | `list_templates.py` | Info |
| Show template | `show_template.py` | Info |

---

## Project Types

### 1. CLI Wrapper Projects

Wrap an existing CLI tool (like `glab`, `gh`, `aws`, `kubectl`):

```bash
python scaffold_project.py \
  --type cli-wrapper \
  --name "GitLab-Assistant-Skills" \
  --topic "gitlab" \
  --cli-tool "glab" \
  --cli-install "brew install glab"
```

**Generated structure:**
- `.claude-plugin/` with plugin.json
- `skills/gitlab-assistant/` (hub router)
- `skills/gitlab-{resource}/` per skill
- `skills/shared/docs/` (SAFEGUARDS, QUICK_REFERENCE)
- No library package (uses existing CLI)

### 2. Custom Library Projects

Build new CLI for an API (like Jira, Confluence, Splunk):

```bash
python scaffold_project.py \
  --type custom-library \
  --name "MyAPI-Assistant-Skills" \
  --topic "myapi" \
  --api "My API" \
  --api-url "https://api.example.com" \
  --auth api_key
```

**Generated structure:**
- `myapi-assistant-skills-lib/` with:
  - `pyproject.toml` with CLI entry point
  - HTTP client, error handler, validators
  - Click CLI commands structure
- `.claude-plugin/` with plugin.json
- `skills/` (pure documentation)
- `requirements.txt` referencing library

### 3. Hybrid Projects

Wrap CLI and extend with custom functionality:

```bash
python scaffold_project.py \
  --type hybrid \
  --name "GitHub-Assistant-Skills" \
  --topic "github" \
  --cli-tool "gh" \
  --api-url "https://api.github.com"
```

---

## Adding Skills

```bash
cd /path/to/project
python add_skill.py \
  --name "merge-request" \
  --description "Merge request operations" \
  --operations "list,get,create,update,delete"
```

**Generated:**
- `skills/{topic}-{name}/SKILL.md` with CLI command references
- `skills/{topic}-{name}/docs/` subdirectory
- Updates to plugin.json

---

## Generating CLI Libraries

For custom library projects, scaffold a complete Python package:

```bash
python scaffold_library.py \
  --name "myapi-assistant-skills-lib" \
  --topic "myapi" \
  --api "My API" \
  --api-url "https://api.example.com"
```

**Generated:**
- Complete Click CLI with commands
- HTTP client with retry/pagination
- Configuration management
- Error handling hierarchy
- Output formatters
- Input validators
- Test infrastructure

---

## Validating Projects

```bash
python validate_project.py /path/to/project
```

**Checks:**
- `.claude-plugin/plugin.json` exists
- VERSION file present
- Root conftest.py exists
- No scripts in skills/ directories
- Hub/router skill present
- Risk levels documented
- Shared documentation complete

---

## Migrating Existing Projects

Transform old `.claude/skills/` structure to new `.claude-plugin/` pattern:

```bash
# Analyze and preview
python migrate_project.py /path/to/old/project --dry-run

# Migrate in place (creates backup)
python migrate_project.py /path/to/old/project

# Migrate to new location
python migrate_project.py /path/to/old/project --output /path/to/new/project
```

**Transforms:**
- Moves skills from `.claude/skills/` to `skills/`
- Creates `.claude-plugin/` with plugin.json
- Generates VERSION, conftest.py, pytest.ini
- Creates shared documentation

---

## Reference Projects

Learn from production implementations:

| Project | Skills | Type | Strength |
|---------|--------|------|----------|
| Jira-Assistant-Skills | 14 | Custom Library | Mock architecture |
| Confluence-Assistant-Skills | 17 | Custom Library | Risk documentation |
| Splunk-Assistant-Skills | 14 | Custom Library | Test infrastructure |

```bash
# Show patterns from specific project
python show_reference.py --project jira --topic client-pattern

# Compare patterns across projects
python show_reference.py --topic testing-patterns --compare-all

# List available topics
python show_reference.py --list-topics
```

---

## Production Architecture

The production pattern is **thin documentation wrappers around a publishable CLI library**:

```
my-project/
├── .claude-plugin/           # Plugin manifest
│   ├── plugin.json
│   ├── marketplace.json
│   └── commands/             # Slash commands
├── skills/                    # Pure documentation
│   ├── {topic}-assistant/    # Hub/router skill
│   ├── {topic}-{skill}/      # Feature skills (SKILL.md only)
│   └── shared/docs/          # SAFEGUARDS, QUICK_REFERENCE
├── {topic}-assistant-skills-lib/  # Optional: CLI library
├── conftest.py               # Root test fixtures
├── pytest.ini                # Test configuration
├── VERSION                   # Single version source
└── CLAUDE.md                # Project guidance
```

**Key principles:**
- Skills are documentation, not code
- Scripts live in separate library packages
- Hub/router skill routes requests
- Risk levels documented everywhere
- VERSION is single source of truth

---

## Risk Level System

All operations marked with risk indicators:

| Risk | Symbol | Description |
|------|:------:|-------------|
| Safe | `-` | Read-only operations |
| Caution | `⚠️` | Single-item modifications |
| Warning | `⚠️⚠️` | Bulk/destructive operations |
| Danger | `⚠️⚠️⚠️` | Irreversible operations |

---

## Related Documentation

- [Quick Reference](./docs/QUICK-REFERENCE.md)
- [Workflows](./docs/WORKFLOWS.md)
- [Examples](./docs/EXAMPLES.md)
- [Migration Guide](./docs/MIGRATION.md)
