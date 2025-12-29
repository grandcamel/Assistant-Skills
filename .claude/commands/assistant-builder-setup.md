---
name: assistant-builder-setup
description: Interactive wizard to create or extend Assistant Skills projects
---

# Assistant Builder Setup

You are helping the user create or modify an Assistant Skills project using proven templates and patterns.

## Determine Intent

First, ask the user what they would like to do:

1. **Create a new project** - Start a fresh Assistant Skills project from scratch
2. **Add a skill** - Add a new skill to an existing project
3. **Show examples** - See patterns from reference implementations (Jira, Confluence, Splunk)
4. **Validate structure** - Check if a project follows the expected patterns

## For Creating a New Project

Guide the user through these steps:

### Step 1: Project Basics
Ask for:
- **Project name**: e.g., "GitHub-Assistant-Skills"
- **Topic prefix**: Lowercase identifier, e.g., "github" (used as skill prefix)
- **API name**: Friendly name, e.g., "GitHub"

### Step 2: API Details
Ask for:
- **Base URL**: e.g., "https://api.github.com"
- **Authentication method**: api_key, oauth, jwt, or basic
- **Pagination style**: offset, cursor, page, or link

### Step 3: Initial Skills
Ask:
- **Skills to create**: Comma-separated list, e.g., "issues, repos, users, search"
- Each skill will get its own directory structure

### Step 4: Confirmation
Show a summary and ask for confirmation before creating files.

### Step 5: Execute
Run the scaffold_project.py script with the collected parameters:

```bash
python .claude/skills/assistant-builder/scripts/scaffold_project.py \
  --name "{{PROJECT_NAME}}" \
  --topic "{{TOPIC}}" \
  --api "{{API_NAME}}" \
  --base-url "{{BASE_URL}}" \
  --skills "{{SKILLS}}" \
  --auth {{AUTH_METHOD}}
```

### Step 6: Next Steps
After creation, guide the user to:
1. Navigate to the new project directory
2. Edit `.claude/settings.json` with API configuration
3. Create `.claude/settings.local.json` with credentials
4. Start implementing the shared library
5. Follow TDD to implement each skill

## For Adding a Skill

### Step 1: Detect Project
Look for an existing project structure:
- Check current directory for `.claude/skills/`
- If not found, ask for the project path

### Step 2: Skill Details
Ask for:
- **Skill name**: Without prefix, e.g., "search" (will become "github-search")
- **Description**: One-line description
- **Primary resource**: API resource name, e.g., "queries"
- **Scripts needed**: list, get, create, update, delete, or custom list

### Step 3: Generate
Run add_skill.py with the collected parameters.

### Step 4: TDD Guidance
Suggest the TDD workflow:
1. Write failing tests first
2. Commit tests: `test(skill-name): add failing tests for X`
3. Implement to pass tests
4. Commit implementation: `feat(skill-name): implement X (N/N tests passing)`

## For Showing Examples

### Topics Available
1. **Project structure** - Directory layout patterns
2. **Shared library** - How to organize shared code
3. **Skill organization** - SKILL.md format, scripts, tests
4. **Testing patterns** - Unit tests, integration tests, fixtures
5. **Router skill** - Hub pattern for routing to specialized skills
6. **Configuration** - settings.json patterns

### Reference Projects
- **Jira-Assistant-Skills** - 14 skills, most comprehensive
- **Confluence-Assistant-Skills** - 14 skills, content-focused
- **Splunk-Assistant-Skills** - 13 skills, data/search-focused

When showing examples, use show_reference.py:

```bash
python .claude/skills/assistant-builder/scripts/show_reference.py \
  --topic "{{TOPIC}}" \
  --project "{{PROJECT}}"
```

## For Validating Structure

Run validate_project.py on the target directory:

```bash
python .claude/skills/assistant-builder/scripts/validate_project.py "{{PATH}}"
```

Report:
- Errors (missing required files/directories)
- Warnings (recommended but optional items)
- Summary of structure compliance

## Templates Reference

When the user asks about templates, point them to:

| Category | Location | Contents |
|----------|----------|----------|
| Project Lifecycle | `00-project-lifecycle/` | API research, gap analysis, architecture |
| Scaffolding | `01-project-scaffolding/` | Project init, config templates |
| Shared Library | `02-shared-library/` | Client, config, error handling templates |
| Skills | `03-skill-templates/` | SKILL.md, script, router templates |
| Testing | `04-testing/` | TDD workflow, test templates |
| Documentation | `05-documentation/` | Workflow, reference, troubleshooting |
| Git/CI | `06-git-and-ci/` | Commits, GitHub Actions |

## Important Reminders

- Always use the topic prefix consistently (e.g., all Jira skills start with "jira-")
- SKILL.md files should use progressive disclosure (3 levels)
- Every script should support --help, --profile, and --output options
- Follow TDD: write tests before implementation
- Use conventional commits with test counts
