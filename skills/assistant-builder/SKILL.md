---
name: "assistant-builder"
description: "Interactive wizard for creating new Assistant Skills projects or adding skills to existing ones"
when_to_use: |
  - Starting a new Assistant Skills project from scratch
  - Adding a new skill to an existing project
  - Looking for patterns from reference implementations (Jira, Confluence, Splunk)
  - Validating project structure against templates
---

# Assistant Builder

Create and extend Claude Code Assistant Skills projects using proven templates and patterns.

## What This Skill Does

| Operation | Script | Description |
|-----------|--------|-------------|
| Create Project | `scaffold_project.py` | Initialize new project with full structure |
| Add Skill | `add_skill.py` | Add skill to existing project |
| Show Reference | `show_reference.py` | Display patterns from reference projects |
| List Templates | `list_templates.py` | List available templates |
| Show Template | `show_template.py` | Display template content |
| Validate | `validate_project.py` | Check project structure |

---

## Quick Start

### Create a New Project

```bash
python scaffold_project.py
# Interactive wizard guides you through setup

# Or specify all options:
python scaffold_project.py --name "GitHub-Assistant-Skills" --topic "github" --api "GitHub" --skills "issues,repos"
```

### Add a Skill

```bash
python add_skill.py --name "search" --description "Search operations" --scripts crud
```

### Show Reference Patterns

```bash
python show_reference.py --list-topics
python show_reference.py --topic shared-library --project jira
```

### Validate Project

```bash
python validate_project.py /path/to/project
```

---

## Scripts Reference

All scripts support `--help` for full options.

| Script | Primary Use | Key Options |
|--------|-------------|-------------|
| `scaffold_project.py` | Create project | `--name`, `--topic`, `--skills`, `--dry-run` |
| `add_skill.py` | Add skill | `--name`, `--description`, `--scripts` |
| `show_reference.py` | View patterns | `--topic`, `--project`, `--list-topics` |
| `list_templates.py` | Browse templates | `--category`, `--format` |
| `validate_project.py` | Check structure | `--strict`, `--format` |

---

## Interactive Wizard

```
/assistant-builder-setup
```

Launches guided wizard for project creation, skill addition, or viewing examples.

---

## Reference Projects

| Project | Skills | Tests | Focus |
|---------|--------|-------|-------|
| Jira-Assistant-Skills | 14 | 560+ | Issue tracking |
| Confluence-Assistant-Skills | 14 | 200+ | Content management |
| Splunk-Assistant-Skills | 13 | 150+ | Search/analytics |

---

## Related Documentation

- [QUICK-REFERENCE.md](docs/QUICK-REFERENCE.md) - Command reference
- [WORKFLOWS.md](docs/WORKFLOWS.md) - Workflow patterns
- [EXAMPLES.md](docs/EXAMPLES.md) - Example projects
- [Configuration](docs/QUICK-REFERENCE.md#configuration) - Settings reference
