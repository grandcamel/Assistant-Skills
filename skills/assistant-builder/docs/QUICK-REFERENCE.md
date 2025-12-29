# Quick Reference

Fast lookup for assistant-builder commands and options.

## Commands

| Command | Purpose |
|---------|---------|
| `/assistant-builder-setup` | Interactive wizard for all operations |

## Scripts

### scaffold_project.py

Create new project:
```bash
python scaffold_project.py \
  --name "GitHub-Assistant-Skills" \
  --topic "github" \
  --api "GitHub" \
  --base-url "https://api.github.com" \
  --skills "issues,repos,users"
```

Options:
- `--name`, `-n`: Project name (required)
- `--topic`, `-t`: Lowercase prefix
- `--api`, `-a`: API friendly name
- `--base-url`, `-u`: API base URL
- `--skills`, `-s`: Comma-separated skills
- `--auth`: api_key, oauth, jwt, basic
- `--pagination`: offset, cursor, page, link
- `--output-dir`, `-o`: Output directory
- `--dry-run`, `-d`: Preview only

### add_skill.py

Add skill to existing project:
```bash
python add_skill.py \
  --name "search" \
  --description "Search operations" \
  --scripts crud
```

Options:
- `--name`, `-n`: Skill name (without prefix)
- `--description`, `-d`: One-line description
- `--resource`, `-r`: API resource name
- `--scripts`, `-s`: crud, list-get, all, or comma-separated
- `--project-dir`, `-p`: Project path
- `--no-tests`: Skip test generation
- `--dry-run`: Preview only

### show_reference.py

Show patterns from reference projects:
```bash
python show_reference.py --topic shared-library --project jira
```

Options:
- `--topic`, `-t`: Pattern topic
- `--project`, `-p`: jira, confluence, splunk, all
- `--list-topics`, `-l`: List available topics
- `--stats`, `-s`: Show project statistics

Topics: project-structure, shared-library, skill-organization, testing-patterns, skill-md, router-skill, configuration

### list_templates.py

List available templates:
```bash
python list_templates.py --category 03-skill-templates
```

Options:
- `--category`, `-c`: Filter by category
- `--format`, `-f`: text, json, tree
- `--show`, `-s`: Show specific template
- `--categories`: List category descriptions

### show_template.py

Show template content:
```bash
python show_template.py SKILL.md.template --show-placeholders
```

Options:
- `--show-placeholders`, `-p`: Highlight placeholders
- `--raw`, `-r`: Raw output

### validate_project.py

Validate project structure:
```bash
python validate_project.py /path/to/project --strict
```

Options:
- `--strict`, `-s`: Treat warnings as errors
- `--format`, `-f`: text, json

## Placeholders

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `{{PROJECT_NAME}}` | Full project name | GitHub-Assistant-Skills |
| `{{TOPIC}}` | Lowercase prefix | github |
| `{{API_NAME}}` | Friendly API name | GitHub |
| `{{BASE_URL}}` | API base URL | https://api.github.com |
| `{{SKILL_NAME}}` | Skill name | issues |
| `{{SKILL_DESCRIPTION}}` | One-line description | Issue CRUD operations |

## Script Presets

| Preset | Scripts Generated |
|--------|-------------------|
| `crud` | list, get, create, update, delete |
| `list-get` | list, get |
| `all` | list, get, create, update, delete, search, export |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Error (validation failed, missing args, etc.) |
