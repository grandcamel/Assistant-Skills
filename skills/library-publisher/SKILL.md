---
name: library-publisher
description: Extract shared libraries from Assistant Skills projects and publish them as PyPI packages. Use when user wants to "publish shared library", "create PyPI package", "extract library to package", "migrate to pip install", or needs to convert vendored code into an installable package with CI/CD.
---

# Library Publisher

Extract and publish shared libraries from Assistant Skills projects as PyPI packages with automated CI/CD.

## Quick Start

```bash
# Analyze existing shared library
python skills/library-publisher/scripts/analyze_library.py /path/to/project

# Scaffold PyPI package
python skills/library-publisher/scripts/scaffold_package.py \
  --name "myproject-assistant-skills-lib" \
  --source /path/to/project/skills/shared/scripts/lib \
  --output ~/IdeaProjects/myproject-assistant-skills-lib

# Migrate imports in original project
python skills/library-publisher/scripts/migrate_imports.py \
  --project /path/to/project \
  --package "myproject_assistant_skills_lib"

# Update documentation
python skills/library-publisher/scripts/update_docs.py /path/to/project \
  --package-name "myproject-assistant-skills-lib" \
  --package-url "https://pypi.org/project/myproject-assistant-skills-lib/"
```

## Workflow Overview

### Phase 1: Analyze & Plan
```
analyze_library.py
├── Scan shared library directory
├── Identify Python modules and dependencies
├── Detect existing imports across project
└── Generate migration report
```

### Phase 2: Create Package
```
scaffold_package.py
├── Create GitHub repository (optional)
├── Generate src/ layout package structure
├── Copy and adapt library modules
├── Generate pyproject.toml with hatchling
├── Generate comprehensive tests
├── Create GitHub Actions workflows
│   ├── test.yml (PR testing)
│   └── publish.yml (PyPI release)
└── Create README, LICENSE, .gitignore
```

### Phase 3: Publish
```
Manual steps:
1. Review generated package
2. git init && git add . && git commit
3. git remote add origin <repo-url>
4. git push -u origin main
5. Configure PyPI trusted publisher
6. Create GitHub release v0.1.0
```

### Phase 4: Migrate Project
```
migrate_imports.py
├── Update all script imports
├── Remove vendored library files
├── Add requirements.txt
└── Update Docker configs (remove PYTHONPATH)

update_docs.py
├── Add PyPI badge to README
├── Update Shared Library section
├── Update test commands
├── Update project structure
└── Update CLAUDE.md
```

## Scripts Reference

| Script | Purpose |
|--------|---------|
| `analyze_library.py` | Analyze shared library structure and usage |
| `scaffold_package.py` | Generate complete PyPI package |
| `migrate_imports.py` | Update project to use new package |
| `update_docs.py` | Update project documentation |

## Package Naming Convention

| Project | Package Name | Import Name |
|---------|--------------|-------------|
| Jira-Assistant-Skills | `jira-assistant-skills-lib` | `jira_assistant_skills_lib` |
| Confluence-Assistant-Skills | `confluence-assistant-skills-lib` | `confluence_assistant_skills_lib` |
| Splunk-Assistant-Skills | `splunk-assistant-skills-lib` | `splunk_assistant_skills_lib` |
| Generic | `{topic}-assistant-skills-lib` | `{topic}_assistant_skills_lib` |

## PyPI Trusted Publisher Setup

After creating the GitHub repository and before the first release:

1. Go to https://pypi.org/manage/account/publishing/
2. Add new pending publisher:

| Field | Value |
|-------|-------|
| PyPI Project | `{package-name}` |
| Owner | `{github-username}` |
| Repository | `{repo-name}` |
| Workflow | `publish.yml` |
| Environment | *(leave blank)* |

## Generated Package Structure

```
{package-name}/
├── src/
│   └── {import_name}/
│       ├── __init__.py      # Public API exports
│       ├── formatters.py    # Output formatting
│       ├── validators.py    # Input validation
│       ├── cache.py         # Response caching
│       ├── error_handler.py # Exception handling
│       ├── template_engine.py
│       └── project_detector.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_formatters.py
│   ├── test_validators.py
│   └── ...
├── .github/
│   └── workflows/
│       ├── test.yml
│       └── publish.yml
├── pyproject.toml
├── README.md
├── LICENSE
└── .gitignore
```

## Example: Full Migration

```bash
# 1. Analyze current state
python skills/library-publisher/scripts/analyze_library.py \
  ~/IdeaProjects/Jira-Assistant-Skills

# 2. Create package repository
gh repo create jira-assistant-skills-lib --public

# 3. Scaffold package
python skills/library-publisher/scripts/scaffold_package.py \
  --name "jira-assistant-skills-lib" \
  --source ~/IdeaProjects/Jira-Assistant-Skills/skills/shared/scripts/lib \
  --output ~/IdeaProjects/jira-assistant-skills-lib \
  --description "Shared Python utilities for Jira Assistant Skills"

# 4. Initialize and push
cd ~/IdeaProjects/jira-assistant-skills-lib
git init && git add . && git commit -m "feat: initial package structure"
git remote add origin git@github.com:grandcamel/jira-assistant-skills-lib.git
git push -u origin main

# 5. Configure PyPI trusted publisher (manual step)
# 6. Create release
gh release create v0.1.0 --title "v0.1.0" --notes "Initial release"

# 7. Wait for PyPI publish, then migrate project
cd ~/IdeaProjects/Jira-Assistant-Skills
python ~/IdeaProjects/Assistant-Skills/skills/library-publisher/scripts/migrate_imports.py \
  --project . \
  --package "jira_assistant_skills_lib"

# 8. Update docs
python ~/IdeaProjects/Assistant-Skills/skills/library-publisher/scripts/update_docs.py . \
  --package-name "jira-assistant-skills-lib"

# 9. Test and commit
pip install -r requirements.txt
pytest skills/*/tests/ -v
git add . && git commit -m "feat(lib): migrate to jira-assistant-skills-lib PyPI package"
```
