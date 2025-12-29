#!/usr/bin/env python3
"""
Scaffold a new Assistant Skills project.

Creates a complete project structure with all necessary files and directories
based on proven templates from the Assistant-Skills template project.

Usage:
    python scaffold_project.py --name "GitHub-Assistant-Skills" --topic "github" --api "GitHub"

Examples:
    # Interactive mode
    python scaffold_project.py

    # Full specification
    python scaffold_project.py \\
        --name "GitHub-Assistant-Skills" \\
        --topic "github" \\
        --api "GitHub" \\
        --base-url "https://api.github.com" \\
        --skills "issues,repos,users,search" \\
        --auth api_key \\
        --pagination link

    # Dry run to preview
    python scaffold_project.py --name "Test-Skills" --topic "test" --api "Test" --dry-run
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

from assistant_skills_lib import (
    load_template, render_template, get_template_dir,
    validate_required, validate_name, validate_topic_prefix,
    validate_url, validate_choice, validate_list, validate_path,
    InputValidationError as ValidationError,
    print_success, print_error, print_info, print_warning, format_tree
)


# Authentication methods
AUTH_METHODS = ['api_key', 'oauth', 'jwt', 'basic']

# Pagination styles
PAGINATION_STYLES = ['offset', 'cursor', 'page', 'link']


def create_directory_structure(base_path: Path, topic: str, skills: list, dry_run: bool = False) -> list:
    """Create the project directory structure."""
    created = []

    # Core directories
    dirs = [
        '.claude',
        '.claude/commands',
        '.claude/skills',
        '.claude/skills/shared',
        '.claude/skills/shared/scripts',
        '.claude/skills/shared/scripts/lib',
        '.claude/skills/shared/config',
        '.claude/skills/shared/tests',
        '.claude/skills/shared/references',
        f'.claude/skills/{topic}-assistant',
        f'.claude/skills/{topic}-assistant/docs',
        '.github',
        '.github/workflows',
        'docs',
    ]

    # Add skill directories
    for skill in skills:
        skill_dir = f'.claude/skills/{topic}-{skill}'
        dirs.extend([
            skill_dir,
            f'{skill_dir}/scripts',
            f'{skill_dir}/tests',
            f'{skill_dir}/tests/live_integration',
            f'{skill_dir}/docs',
        ])

    for dir_path in dirs:
        full_path = base_path / dir_path
        if not dry_run:
            full_path.mkdir(parents=True, exist_ok=True)
        created.append(dir_path)

    return created


def generate_gitignore(context: dict) -> str:
    """Generate .gitignore content."""
    return """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/
.nox/

# Virtual environments
venv/
.venv/
ENV/
env/

# IDE
.idea/
.vscode/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Credentials - NEVER COMMIT
.claude/settings.local.json
.env
*.env
*.pem
*.key
credentials.json

# Logs
*.log
logs/

# Cache
.cache/
"""


def generate_settings_json(context: dict) -> str:
    """Generate settings.json content."""
    topic = context['TOPIC']
    api_name = context['API_NAME']
    base_url = context.get('BASE_URL', 'https://api.example.com')

    settings = {
        "$schema": "./skills/shared/config/config.schema.json",
        topic: {
            "default_profile": "production",
            "profiles": {
                "production": {
                    "url": base_url,
                    "timeout": 30
                },
                "development": {
                    "url": base_url.replace('api.', 'dev-api.') if 'api.' in base_url else base_url,
                    "timeout": 60
                }
            },
            "api": {
                "version": "1",
                "timeout": 30,
                "max_retries": 3,
                "retry_backoff": 2.0
            }
        }
    }

    return json.dumps(settings, indent=2)


def generate_claude_md(context: dict) -> str:
    """Generate CLAUDE.md content."""
    project_name = context['PROJECT_NAME']
    topic = context['TOPIC']
    api_name = context['API_NAME']
    skills = context.get('SKILLS', [])

    skills_table = ""
    for skill in skills:
        skills_table += f"| `{topic}-{skill}` | {skill.title()} operations | `.claude/skills/{topic}-{skill}/` |\n"

    return f"""# {project_name}

Claude Code guidance for the {project_name} project.

## Overview

This project provides Claude Code skills for interacting with the {api_name} API.

## Available Skills

| Skill | Purpose | Location |
|-------|---------|----------|
| `{topic}-assistant` | Hub skill - routes to specialized skills | `.claude/skills/{topic}-assistant/` |
{skills_table}

## Architecture

### Shared Library

All skills use a common shared library at `.claude/skills/shared/scripts/lib/`:

- `{topic}_client.py` - HTTP client with retry, backoff, pagination
- `config_manager.py` - Configuration loading from env/settings
- `error_handler.py` - Exception hierarchy with troubleshooting hints
- `validators.py` - Input validation utilities
- `formatters.py` - Output formatting (tables, JSON)

### Configuration

Configuration is loaded in priority order:
1. Environment variables (`{api_name.upper().replace(' ', '_')}_TOKEN`, etc.)
2. `.claude/settings.local.json` (gitignored, for credentials)
3. `.claude/settings.json` (shared team settings)

### Profile Support

Use `--profile` to switch between environments:
```bash
python script.py --profile development
python script.py --profile production
```

## Error Handling

All scripts use the `@handle_errors` decorator which:
- Catches API errors and displays helpful messages
- Maps HTTP status codes to user-friendly explanations
- Provides troubleshooting suggestions

## Testing

### Run Tests

```bash
# All tests
PYTHONPATH=".claude/skills/shared/scripts/lib" pytest .claude/skills/ -v

# Specific skill
PYTHONPATH=".claude/skills/shared/scripts/lib" pytest .claude/skills/{topic}-issue/tests/ -v

# With coverage
PYTHONPATH=".claude/skills/shared/scripts/lib" pytest .claude/skills/ -v --cov --cov-report=html
```

### Test Organization

- `tests/` - Unit tests with mocked API responses
- `tests/live_integration/` - Integration tests against real API

## Git Commit Guidelines

Follow conventional commits:

```
feat(skill-name): add new capability
fix(skill-name): correct bug in X
test(skill-name): add tests for Y (N/N passing)
docs(skill-name): update documentation
refactor(skill-name): restructure without behavior change
```

### TDD Two-Commit Pattern

1. `test(scope): add failing tests for feature` - Tests fail
2. `feat(scope): implement feature (N/N tests passing)` - Tests pass

## Adding New Scripts

1. Create script in `skill-name/scripts/`
2. Use standard pattern:
   ```python
   #!/usr/bin/env python3
   import sys
   from pathlib import Path
   sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'shared' / 'scripts' / 'lib'))

   from config_manager import get_client
   from error_handler import handle_errors
   from validators import validate_required
   from formatters import print_success

   @handle_errors
   def main():
       # Implementation
       pass

   if __name__ == '__main__':
       main()
   ```
3. Add corresponding test in `tests/test_script_name.py`
4. Update SKILL.md with new script

## Adding New Skills

1. Create directory structure:
   ```
   .claude/skills/{topic}-newskill/
   ├── SKILL.md
   ├── scripts/
   ├── tests/
   └── docs/
   ```
2. Create SKILL.md with frontmatter
3. Implement scripts following TDD
4. Update router skill routing table
"""


def generate_readme(context: dict) -> str:
    """Generate README.md content."""
    project_name = context['PROJECT_NAME']
    topic = context['TOPIC']
    api_name = context['API_NAME']

    return f"""# {project_name}

Claude Code Assistant Skills for the {api_name} API.

## Quick Start

### 1. Install

```bash
git clone https://github.com/your-org/{project_name.lower()}.git
cd {project_name}
pip install -r .claude/skills/shared/scripts/lib/requirements.txt
```

### 2. Configure

Set your API credentials:

```bash
# Option 1: Environment variable
export {api_name.upper().replace(' ', '_').replace('-', '_')}_API_TOKEN="your-token"

# Option 2: Local settings file
cat > .claude/settings.local.json << 'EOF'
{{
  "{topic}": {{
    "api_token": "your-token"
  }}
}}
EOF
```

### 3. Use

Load the skill in Claude Code:

```
/load {topic}
```

Or run scripts directly:

```bash
cd .claude/skills/{topic}-issue/scripts
python list_issues.py --help
```

## Available Skills

| Skill | Description |
|-------|-------------|
| `{topic}-assistant` | Hub skill for routing to specialized skills |

## Configuration

Edit `.claude/settings.json` to configure profiles:

```json
{{
  "{topic}": {{
    "default_profile": "production",
    "profiles": {{
      "production": {{ "url": "https://api.example.com" }},
      "development": {{ "url": "https://dev.api.example.com" }}
    }}
  }}
}}
```

## Development

### Run Tests

```bash
# Run all tests
PYTHONPATH=".claude/skills/shared/scripts/lib" pytest .claude/skills/ -v
```

### Add a New Skill

See [CLAUDE.md](CLAUDE.md) for development guidelines.

## License

MIT License
"""


def generate_pyproject(context: dict) -> str:
    """Generate pyproject.toml content."""
    project_name = context['PROJECT_NAME']

    return f"""[project]
name = "{project_name.lower()}"
version = "0.1.0"
description = "Claude Code Assistant Skills for {context['API_NAME']}"
readme = "README.md"
requires-python = ">=3.8"
license = {{text = "MIT"}}

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
]

[tool.pytest.ini_options]
testpaths = [".claude/skills"]
python_files = ["test_*.py"]
python_functions = ["test_*"]
addopts = "-v --tb=short"

[tool.coverage.run]
source = [".claude/skills"]
omit = ["*/tests/*", "*/__pycache__/*"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "if __name__ == .__main__.:",
    "raise NotImplementedError",
]
"""


def generate_skill_md(context: dict, skill_name: str) -> str:
    """Generate SKILL.md for a skill."""
    topic = context['TOPIC']
    api_name = context['API_NAME']

    return f"""---
name: "{topic}-{skill_name}"
description: "{skill_name.title()} operations for {api_name}"
when_to_use: |
  - Working with {skill_name} in {api_name}
  - CRUD operations on {skill_name}
---

# {skill_name.title()} Skill

{skill_name.title()} operations for {api_name}.

---

## What This Skill Does

| Operation | Script | Description |
|-----------|--------|-------------|
| List | `list_{skill_name}.py` | List all {skill_name} |
| Get | `get_{skill_name}.py` | Get a specific {skill_name} by ID |
| Create | `create_{skill_name}.py` | Create a new {skill_name} |
| Update | `update_{skill_name}.py` | Update an existing {skill_name} |
| Delete | `delete_{skill_name}.py` | Delete a {skill_name} |

---

## Quick Start

```bash
# List all
python list_{skill_name}.py

# Get by ID
python get_{skill_name}.py ID

# Create new
python create_{skill_name}.py --name "Name"
```

---

## Configuration

Uses shared configuration from `.claude/settings.json`.

See [Configuration Guide](../../shared/references/configuration.md) for details.
"""


def generate_router_skill_md(context: dict) -> str:
    """Generate SKILL.md for the router/assistant skill."""
    topic = context['TOPIC']
    api_name = context['API_NAME']
    skills = context.get('SKILLS', [])

    routing_table = ""
    for skill in skills:
        routing_table += f"| {skill.title()} operations | `{topic}-{skill}` | Working with {skill} |\n"

    return f"""---
name: "{topic}-assistant"
description: "Hub skill for {api_name} operations - routes to specialized skills"
when_to_use: |
  - Any {api_name} operation
  - When unsure which skill to use
  - Multi-step {api_name} workflows
---

# {api_name} Assistant

Central hub for all {api_name} operations. This skill routes requests to specialized skills based on the operation type.

---

## Skill Routing

| When you want to... | Use this skill | Triggers |
|---------------------|----------------|----------|
{routing_table}

---

## Quick Start

Simply describe what you want to do with {api_name}, and this skill will route to the appropriate specialized skill.

Examples:
- "List all issues" → `{topic}-issue`
- "Create a new user" → `{topic}-users`
- "Search for X" → `{topic}-search`

---

## Available Skills

| Skill | Purpose | Scripts |
|-------|---------|---------|
"""


def generate_shared_lib_init(context: dict) -> str:
    """Generate shared library __init__.py."""
    topic = context['TOPIC']
    api_name = context['API_NAME']

    return f'''"""
{api_name} Assistant Skills - Shared Library

Common utilities for all {topic}-* skills.
"""

__version__ = "0.1.0"
'''


def generate_requirements(context: dict) -> str:
    """Generate requirements.txt."""
    return """# Core dependencies
requests>=2.28.0

# Output formatting
tabulate>=0.9.0

# Testing
pytest>=7.0.0
pytest-cov>=4.0.0

# Development
"""


def scaffold_project(
    name: str,
    topic: str,
    api_name: str,
    base_url: str = None,
    skills: list = None,
    auth_method: str = 'api_key',
    pagination_style: str = 'offset',
    output_dir: str = '.',
    dry_run: bool = False
) -> dict:
    """
    Create a new Assistant Skills project.

    Returns dict with created files and directories.
    """
    # Prepare context
    context = {
        'PROJECT_NAME': name,
        'TOPIC': topic,
        'API_NAME': api_name,
        'BASE_URL': base_url or 'https://api.example.com',
        'AUTH_METHOD': auth_method,
        'PAGINATION_STYLE': pagination_style,
        'SKILLS': skills or [],
        'DATE': datetime.now().isoformat()
    }

    # Determine output path
    output_path = Path(output_dir).expanduser().resolve() / name

    if output_path.exists() and not dry_run:
        raise ValueError(f"Directory already exists: {output_path}")

    result = {
        'path': str(output_path),
        'directories': [],
        'files': []
    }

    # Create directory structure
    if not dry_run:
        output_path.mkdir(parents=True, exist_ok=True)

    result['directories'] = create_directory_structure(output_path, topic, skills or [], dry_run)

    # Generate files
    files_to_create = [
        ('.gitignore', generate_gitignore(context)),
        ('README.md', generate_readme(context)),
        ('CLAUDE.md', generate_claude_md(context)),
        ('pyproject.toml', generate_pyproject(context)),
        ('.claude/settings.json', generate_settings_json(context)),
        (f'.claude/skills/shared/scripts/lib/__init__.py', generate_shared_lib_init(context)),
        (f'.claude/skills/shared/scripts/lib/requirements.txt', generate_requirements(context)),
        (f'.claude/skills/{topic}-assistant/SKILL.md', generate_router_skill_md(context)),
    ]

    # Add skill files
    for skill in (skills or []):
        files_to_create.extend([
            (f'.claude/skills/{topic}-{skill}/SKILL.md', generate_skill_md(context, skill)),
            (f'.claude/skills/{topic}-{skill}/scripts/__init__.py', ''),
            (f'.claude/skills/{topic}-{skill}/tests/__init__.py', ''),
            (f'.claude/skills/{topic}-{skill}/tests/conftest.py', '"""Pytest fixtures."""\n'),
        ])

    for file_path, content in files_to_create:
        full_path = output_path / file_path
        result['files'].append(file_path)
        if not dry_run:
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content)

    return result


def interactive_mode():
    """Run interactive wizard to collect project configuration."""
    print("\n" + "=" * 60)
    print("  Assistant Skills Project Wizard")
    print("=" * 60 + "\n")

    # Step 1: Project basics
    print("Step 1: Project Basics\n")

    name = input("Project name (e.g., GitHub-Assistant-Skills): ").strip()
    name = validate_name(name, "project name")

    topic = input(f"Topic prefix (lowercase, e.g., github) [{name.split('-')[0].lower()}]: ").strip()
    if not topic:
        topic = name.split('-')[0].lower()
    topic = validate_topic_prefix(topic)

    api_name = input(f"API name (e.g., GitHub) [{topic.title()}]: ").strip()
    if not api_name:
        api_name = topic.title()

    # Step 2: API details
    print("\nStep 2: API Details\n")

    base_url = input("Base URL (e.g., https://api.github.com) [https://api.example.com]: ").strip()
    if not base_url:
        base_url = "https://api.example.com"
    else:
        base_url = validate_url(base_url)

    print(f"\nAuthentication methods: {', '.join(AUTH_METHODS)}")
    auth = input(f"Auth method [{AUTH_METHODS[0]}]: ").strip().lower()
    if not auth:
        auth = AUTH_METHODS[0]
    auth = validate_choice(auth, AUTH_METHODS, "auth method")

    print(f"\nPagination styles: {', '.join(PAGINATION_STYLES)}")
    pagination = input(f"Pagination style [{PAGINATION_STYLES[0]}]: ").strip().lower()
    if not pagination:
        pagination = PAGINATION_STYLES[0]
    pagination = validate_choice(pagination, PAGINATION_STYLES, "pagination style")

    # Step 3: Skills
    print("\nStep 3: Initial Skills\n")

    skills_input = input("Initial skills (comma-separated, e.g., issues,repos,users): ").strip()
    skills = validate_list(skills_input, "skills", min_items=0)

    # Step 4: Confirmation
    print("\n" + "-" * 60)
    print("Configuration Summary:")
    print("-" * 60)
    print(f"  Project Name: {name}")
    print(f"  Topic Prefix: {topic}")
    print(f"  API Name:     {api_name}")
    print(f"  Base URL:     {base_url}")
    print(f"  Auth Method:  {auth}")
    print(f"  Pagination:   {pagination}")
    print(f"  Skills:       {', '.join(skills) if skills else '(none)'}")
    print("-" * 60)

    confirm = input("\nProceed with creation? [Y/n]: ").strip().lower()
    if confirm and confirm != 'y':
        print("Cancelled.")
        return None

    return {
        'name': name,
        'topic': topic,
        'api_name': api_name,
        'base_url': base_url,
        'auth_method': auth,
        'pagination_style': pagination,
        'skills': skills
    }


def main():
    parser = argparse.ArgumentParser(
        description='Create a new Assistant Skills project',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Interactive mode
  python scaffold_project.py

  # Full specification
  python scaffold_project.py \\
      --name "GitHub-Assistant-Skills" \\
      --topic "github" \\
      --api "GitHub" \\
      --base-url "https://api.github.com" \\
      --skills "issues,repos,users"

  # Dry run
  python scaffold_project.py --name "Test" --topic "test" --api "Test" --dry-run
'''
    )

    parser.add_argument('--name', '-n', help='Project name')
    parser.add_argument('--topic', '-t', help='Lowercase topic prefix')
    parser.add_argument('--api', '-a', help='Friendly API name')
    parser.add_argument('--base-url', '-u', help='API base URL')
    parser.add_argument('--skills', '-s', help='Comma-separated skill names')
    parser.add_argument('--auth', choices=AUTH_METHODS, default='api_key',
                        help='Authentication method')
    parser.add_argument('--pagination', choices=PAGINATION_STYLES, default='offset',
                        help='Pagination style')
    parser.add_argument('--output-dir', '-o', default='.', help='Output directory')
    parser.add_argument('--dry-run', '-d', action='store_true',
                        help='Preview without creating files')

    args = parser.parse_args()

    try:
        # Interactive mode if no name provided
        if not args.name:
            config = interactive_mode()
            if not config:
                sys.exit(0)
        else:
            # Validate required args
            name = validate_name(args.name, "project name")
            topic = validate_topic_prefix(args.topic or name.split('-')[0].lower())
            api_name = args.api or topic.title()

            config = {
                'name': name,
                'topic': topic,
                'api_name': api_name,
                'base_url': args.base_url,
                'auth_method': args.auth,
                'pagination_style': args.pagination,
                'skills': args.skills.split(',') if args.skills else []
            }

        # Create project
        if args.dry_run:
            print_info("DRY RUN - No files will be created\n")

        result = scaffold_project(
            name=config['name'],
            topic=config['topic'],
            api_name=config['api_name'],
            base_url=config.get('base_url'),
            skills=config.get('skills', []),
            auth_method=config.get('auth_method', 'api_key'),
            pagination_style=config.get('pagination_style', 'offset'),
            output_dir=args.output_dir,
            dry_run=args.dry_run
        )

        # Report results
        print_success(f"Created project at: {result['path']}")
        print(f"\nDirectories: {len(result['directories'])}")
        print(f"Files: {len(result['files'])}")

        if args.dry_run:
            print("\nFiles that would be created:")
            for f in result['files']:
                print(f"  {f}")

        # Next steps
        print("\n" + "=" * 60)
        print("Next Steps:")
        print("=" * 60)
        print(f"1. cd {result['path']}")
        print("2. Edit .claude/settings.json with your API configuration")
        print("3. Create .claude/settings.local.json with credentials")
        print("4. Implement shared library (client, error handling)")
        print("5. Implement skills following TDD")
        print("\nSee CLAUDE.md for development guidelines.")

    except ValidationError as e:
        print_error(str(e))
        sys.exit(1)
    except Exception as e:
        print_error(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
