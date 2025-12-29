# Assistant Skills

A Claude Code plugin with templates and tools for building Assistant Skills projects.

## Installation

### As Claude Code Plugin

```bash
# Clone the repository
git clone https://github.com/jasonkrueger/Assistant-Skills.git

# Install as plugin (from Claude Code)
/install-plugin /path/to/Assistant-Skills
```

Or install directly from GitHub:
```bash
/install-plugin https://github.com/jasonkrueger/Assistant-Skills
```

### Manual Installation

Copy the skills to your user skills directory:
```bash
cp -r skills/* ~/.claude/skills/
```

---

## Included Skills

| Skill | Description |
|-------|-------------|
| `assistant-builder` | Interactive wizard for creating new Assistant Skills projects |
| `skills-optimizer` | Audit and optimize skills for token efficiency |

### assistant-builder

Create and extend Claude Code Assistant Skills projects using proven templates.

```bash
# Create new project
python skills/assistant-builder/scripts/scaffold_project.py

# Add skill to existing project
python skills/assistant-builder/scripts/add_skill.py --name "search"

# Or use the interactive wizard
/assistant-builder-setup
```

### skills-optimizer

Audit skills for token efficiency and progressive disclosure compliance.

```bash
# Analyze a skill
./skills/skills-optimizer/scripts/analyze-skill.sh ~/.claude/skills/my-skill

# Audit all skills
./skills/skills-optimizer/scripts/audit-all-skills.sh ~/.claude/skills
```

---

## Templates

This project includes comprehensive templates for building Assistant Skills:

| Folder | Purpose |
|--------|---------|
| `00-project-lifecycle/` | API research, GAP analysis, architecture |
| `01-project-scaffolding/` | Project initialization, configs |
| `02-shared-library/` | HTTP client, error handling templates |
| `03-skill-templates/` | SKILL.md, script templates |
| `04-testing/` | TDD workflow, test templates |
| `05-documentation/` | Workflow, reference docs |
| `06-git-and-ci/` | Commits, GitHub Actions |

---

## Progressive Disclosure Model

Skills use 3 levels to minimize token usage:

| Level | Target | Loaded When |
|-------|--------|-------------|
| L1: Metadata | ~200 chars | Startup (all skills) |
| L2: SKILL.md | <500 lines | Skill triggered |
| L3: Nested docs | Variable | Explicitly accessed |

---

## Reference Projects

Templates derived from production implementations:

| Project | Skills | Tests |
|---------|--------|-------|
| Jira-Assistant-Skills | 14 | 560+ |
| Confluence-Assistant-Skills | 14 | 200+ |
| Splunk-Assistant-Skills | 13 | 150+ |

---

## Development

### Run Tests

```bash
PYTHONPATH="skills/shared/scripts/lib" pytest skills/assistant-builder/tests/ -v
```

### Project Structure

```
Assistant-Skills/
├── .claude-plugin/
│   └── plugin.json          # Plugin manifest
├── skills/
│   ├── assistant-builder/   # Project scaffolding skill
│   ├── skills-optimizer/    # Optimization skill
│   └── shared/              # Shared library
├── 00-project-lifecycle/    # Templates
├── 01-project-scaffolding/
├── ...
└── README.md
```

---

## License

MIT License
