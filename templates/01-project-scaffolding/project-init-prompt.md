# Project Initialization Prompt

## Purpose

Initialize a new Assistant Skills project with proper directory structure, configuration files, and documentation scaffolding.

## Prerequisites

- Completed architecture design
- Chosen project name and topic prefix
- List of planned skills

## Placeholders

- `{{PROJECT_NAME}}` - Full project name (e.g., "GitHub-Assistant-Skills")
- `{{TOPIC}}` - Lowercase skill prefix (e.g., "github")
- `{{API_NAME}}` - Friendly API name (e.g., "GitHub")
- `{{API_BASE_URL}}` - Base URL for API
- `{{SKILL_LIST}}` - Comma-separated list of planned skills

---

## Prompt

```
Create a new Claude Code Assistant Skills project with the following specifications:

**Project Name:** {{PROJECT_NAME}}
**Topic Prefix:** {{TOPIC}}
**API:** {{API_NAME}} ({{API_BASE_URL}})
**Planned Skills:** {{SKILL_LIST}}

Please create the complete project structure:

## 1. Directory Structure

Create this structure:
```
{{PROJECT_NAME}}/
├── .claude/
│   ├── settings.json
│   └── skills/
│       ├── {{TOPIC}}-assistant/
│       │   ├── SKILL.md
│       │   └── docs/
│       ├── {{TOPIC}}-{skill1}/
│       │   ├── SKILL.md
│       │   ├── scripts/
│       │   │   └── __init__.py
│       │   ├── tests/
│       │   │   ├── __init__.py
│       │   │   ├── conftest.py
│       │   │   └── live_integration/
│       │   └── docs/
│       └── shared/
│           ├── scripts/
│           │   └── lib/
│           │       ├── __init__.py
│           │       └── requirements.txt
│           ├── config/
│           │   └── config.schema.json
│           └── tests/
│               ├── __init__.py
│               ├── conftest.py
│               └── live_integration/
├── .github/
│   └── workflows/
├── docs/
├── .gitignore
├── CLAUDE.md
├── README.md
├── LICENSE
└── pyproject.toml
```

## 2. Configuration Files

### .gitignore
Include patterns for:
- Python: __pycache__, *.pyc, .pytest_cache, htmlcov, .coverage
- IDE: .idea, .vscode
- Virtual environments: venv, .venv
- Credentials: .claude/settings.local.json, .env, *.env
- OS: .DS_Store, Thumbs.db

### pyproject.toml
Configure for:
- Python 3.8+ minimum
- pytest with coverage
- Project metadata

### settings.json
Basic structure with:
- Profile support (default, development, production)
- API configuration section
- Skill-specific settings section

## 3. Documentation Files

### CLAUDE.md
Scaffold with sections for:
- Project overview
- Available skills (placeholder table)
- Architecture (shared library pattern)
- Configuration system
- Error handling strategy
- Testing approach
- Git commit guidelines
- Adding new scripts
- Adding new skills

### README.md
User-facing scaffold with:
- Project title and badges
- Quick start (install, configure, use)
- Skills overview table
- Example commands
- Configuration guide
- Contributing section
- License

## 4. Shared Library Scaffolds

Create empty module files with docstrings:
- __init__.py with version
- requirements.txt with: requests, tabulate, pytest, pytest-cov

## 5. Initial Skill Scaffolds

For each planned skill, create:
- Empty SKILL.md with frontmatter template
- scripts/__init__.py
- tests/__init__.py
- tests/conftest.py with pytest fixture imports

Generate all files with appropriate content. Use the templates from the reference projects as patterns.
```

---

## Expected Outputs

Running this prompt should create:

1. **Complete directory tree** as specified
2. **All configuration files** ready for customization
3. **Documentation scaffolds** with section headers
4. **Empty skill directories** with correct structure
5. **Shared library foundation** ready for implementation

---

## Post-Initialization Steps

1. Customize CLAUDE.md with project-specific details
2. Fill in settings.json with API configuration
3. Begin shared library implementation
4. Follow implementation plan for skill development

---

## Verification

After initialization, verify:

```bash
cd {{PROJECT_NAME}}

# Check structure exists
ls -la .claude/skills/

# Verify Python setup
python -c "import sys; print(sys.version)"

# Install dependencies
pip install -r .claude/skills/shared/scripts/lib/requirements.txt

# Run empty test suite
pytest .claude/skills/ -v
```
