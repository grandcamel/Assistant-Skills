---
name: "assistant-builder"
description: "Interactive wizard for creating new Assistant Skills projects or adding skills to existing ones"
when_to_use: |
  - Starting a new Assistant Skills project from scratch
  - Adding a new skill to an existing project
  - Looking for patterns from reference implementations (Jira, Confluence, Splunk)
  - Validating project structure against templates
  - Exploring available templates and examples
---

# Assistant Builder

Interactive wizard for creating and extending Claude Code Assistant Skills projects using proven templates and patterns.

---

## What This Skill Does

| Operation | Script | Description |
|-----------|--------|-------------|
| Create Project | `scaffold_project.py` | Initialize a new Assistant Skills project with full structure |
| Add Skill | `add_skill.py` | Add a new skill to an existing project |
| Show Reference | `show_reference.py` | Display patterns from Jira/Confluence/Splunk projects |
| List Templates | `list_templates.py` | List available template files |
| Show Template | `show_template.py` | Display a specific template's content |
| Validate | `validate_project.py` | Check project structure against patterns |

---

## Quick Start

### Create a New Project

```bash
# Interactive mode (recommended)
python scaffold_project.py

# Or with all options
python scaffold_project.py \
  --name "GitHub-Assistant-Skills" \
  --topic "github" \
  --api "GitHub" \
  --base-url "https://api.github.com" \
  --skills "issues,repos,users,search" \
  --auth api_key
```

### Add a Skill to Existing Project

```bash
# Interactive mode
python add_skill.py

# Or with options
python add_skill.py \
  --name "search" \
  --description "Search and query operations" \
  --resource "queries" \
  --scripts "search,list_saved,create_saved"
```

### Show Reference Patterns

```bash
# List topics
python show_reference.py --list-topics

# Show shared library pattern from Jira
python show_reference.py --topic shared-library --project jira

# Compare router skills across projects
python show_reference.py --topic router-skill --project all
```

---

## Available Scripts

All scripts support `--help` for detailed usage information.

### scaffold_project.py

Create a new Assistant Skills project with complete structure.

```bash
python scaffold_project.py [OPTIONS]

Options:
  --name NAME           Project name (e.g., "GitHub-Assistant-Skills")
  --topic TOPIC         Lowercase topic prefix (e.g., "github")
  --api API_NAME        Friendly API name (e.g., "GitHub")
  --base-url URL        API base URL
  --skills LIST         Comma-separated skill names
  --auth METHOD         Authentication: api_key, oauth, jwt, basic
  --pagination STYLE    Pagination: offset, cursor, page, link
  --output-dir PATH     Output directory (default: current)
  --dry-run             Preview without creating files
  --help                Show this help message
```

### add_skill.py

Add a new skill to an existing project.

```bash
python add_skill.py [OPTIONS]

Options:
  --name NAME           Skill name (without topic prefix)
  --description DESC    One-line description
  --resource RESOURCE   Primary API resource name
  --scripts LIST        Comma-separated script names (or: crud, list-get, all)
  --with-tests          Generate test stubs (default: true)
  --project-dir PATH    Project directory (default: auto-detect)
  --help                Show this help message
```

### show_reference.py

Show patterns from reference implementations.

```bash
python show_reference.py [OPTIONS]

Options:
  --topic TOPIC         Pattern topic (see --list-topics)
  --project PROJECT     Reference: jira, confluence, splunk, all
  --list-topics         List available pattern topics
  --help                Show this help message

Topics:
  - project-structure   Directory layout patterns
  - shared-library      Shared lib organization
  - skill-organization  How skills are structured
  - testing-patterns    Test organization and patterns
  - skill-md            SKILL.md format examples
  - router-skill        Hub/router skill patterns
  - configuration       settings.json patterns
```

### list_templates.py

List available template files.

```bash
python list_templates.py [OPTIONS]

Options:
  --category CAT        Filter by category (e.g., "01-project-scaffolding")
  --format FORMAT       Output: text, json, tree
  --help                Show this help message
```

### validate_project.py

Validate project structure.

```bash
python validate_project.py [OPTIONS]

Arguments:
  PROJECT_DIR           Project to validate (default: current)

Options:
  --strict              Treat warnings as errors
  --format FORMAT       Output: text, json
  --help                Show this help message
```

---

## Interactive Wizard

The skill can be invoked interactively through the `/assistant-builder-setup` command:

```
/assistant-builder-setup
```

This launches a guided wizard that:
1. Asks what you want to do (create project, add skill, show examples)
2. Collects required information step by step
3. Confirms before making changes
4. Provides next-steps guidance

---

## Templates Used

| Template | Purpose |
|----------|---------|
| `01-project-scaffolding/project-init-prompt.md` | Project initialization pattern |
| `01-project-scaffolding/*.template` | Config file templates |
| `02-shared-library/*.template` | Shared library templates |
| `03-skill-templates/skill-creation-prompt.md` | Skill creation pattern |
| `03-skill-templates/SKILL.md.template` | SKILL.md format |
| `04-testing/*.template` | Test file templates |

---

## Reference Projects

Patterns are extracted from production implementations:

| Project | Skills | Scripts | Tests | Specialty |
|---------|--------|---------|-------|-----------|
| Jira-Assistant-Skills | 14 | 100+ | 560+ | Most comprehensive |
| Confluence-Assistant-Skills | 14 | 60+ | 200+ | Content-focused |
| Splunk-Assistant-Skills | 13 | 50+ | 150+ | Data/search-focused |

---

## Configuration

Settings in `.claude/settings.json`:

```json
{
  "assistant-builder": {
    "template_dir": "../",
    "reference_projects": {
      "jira": "~/IdeaProjects/Jira-Assistant-Skills",
      "confluence": "~/IdeaProjects/Confluence-Assistant-Skills",
      "splunk": "~/IdeaProjects/Splunk-Assistant-Skills"
    },
    "defaults": {
      "auth_method": "api_key",
      "pagination_style": "offset"
    }
  }
}
```

---

## Related Documentation

- [QUICK-REFERENCE.md](docs/QUICK-REFERENCE.md) - Command quick reference
- [WORKFLOWS.md](docs/WORKFLOWS.md) - Common workflow patterns
- [EXAMPLES.md](docs/EXAMPLES.md) - Example projects walkthrough
