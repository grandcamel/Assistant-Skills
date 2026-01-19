#!/usr/bin/env python3
"""
Scaffold a new Assistant Skills project.

Creates a complete project structure following production patterns from
Jira-Assistant-Skills, Confluence-Assistant-Skills, and Splunk-Assistant-Skills.

Supports three project types:
- CLI Wrapper: Wrap an existing CLI tool (glab, gh, aws, kubectl)
- Custom Library: Build new CLI for an API (like Jira, Confluence, Splunk)
- Hybrid: Wrap CLI and extend with custom library

Usage:
    python scaffold_project.py --type cli-wrapper --name "GitLab-Assistant-Skills"
    python scaffold_project.py --type custom-library --name "MyAPI-Assistant-Skills"

Examples:
    # Interactive mode
    python scaffold_project.py

    # CLI Wrapper project
    python scaffold_project.py \\
        --type cli-wrapper \\
        --name "GitLab-Assistant-Skills" \\
        --topic "gitlab" \\
        --cli-tool "glab" \\
        --cli-install "brew install glab"

    # Custom Library project
    python scaffold_project.py \\
        --type custom-library \\
        --name "MyAPI-Assistant-Skills" \\
        --topic "myapi" \\
        --api "My API" \\
        --api-url "https://api.example.com" \\
        --auth api_key

    # Dry run to preview
    python scaffold_project.py --name "Test-Skills" --topic "test" --dry-run
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


# Project types
PROJECT_TYPES = ['cli-wrapper', 'custom-library', 'hybrid']

# Authentication methods
AUTH_METHODS = ['api_key', 'oauth', 'jwt', 'basic']

# Pagination styles
PAGINATION_STYLES = ['offset', 'cursor', 'page', 'link']


def create_directory_structure(
    base_path: Path,
    topic: str,
    skills: list,
    project_type: str = 'cli-wrapper',
    dry_run: bool = False
) -> list:
    """Create the project directory structure."""
    created = []

    # Core directories (new structure)
    dirs = [
        '.claude-plugin',
        '.claude-plugin/commands',
        'skills',
        f'skills/{topic}-assistant',
        f'skills/{topic}-assistant/docs',
        'skills/shared',
        'skills/shared/docs',
        'skills/shared/config',
        'skills/shared/tests',
        'skills/shared/tests/live_integration',
        '.github',
        '.github/workflows',
        'docs',
    ]

    # Add skill directories
    for skill in skills:
        skill_dir = f'skills/{topic}-{skill}'
        dirs.extend([
            skill_dir,
            f'{skill_dir}/docs',
        ])

    # Add library directory for custom-library and hybrid projects
    if project_type in ('custom-library', 'hybrid'):
        lib_name = f'{topic}-assistant-skills-lib'
        dirs.extend([
            lib_name,
            f'{lib_name}/src',
            f'{lib_name}/src/{topic.replace("-", "_")}_assistant_skills_lib',
            f'{lib_name}/src/{topic.replace("-", "_")}_assistant_skills_lib/cli',
            f'{lib_name}/src/{topic.replace("-", "_")}_assistant_skills_lib/cli/commands',
            f'{lib_name}/tests',
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
.env
*.env
*.pem
*.key
credentials.json
*.local.json
*.local.md

# Logs
*.log
logs/

# Cache
.cache/
"""


def generate_version_file(context: dict) -> str:
    """Generate VERSION file."""
    return "1.0.0"


def generate_plugin_json(context: dict) -> str:
    """Generate .claude-plugin/plugin.json content."""
    topic = context['TOPIC']
    project_name = context['PROJECT_NAME']

    plugin = {
        "name": project_name.lower(),
        "version": "1.0.0",
        "description": f"Claude Code skills for {context['API_NAME']} automation",
        "skills": [
            f"../skills/{topic}-assistant/SKILL.md"
        ],
        "commands": [
            "./commands/*.md"
        ]
    }

    # Add skills
    for skill in context.get('SKILLS', []):
        plugin['skills'].append(f"../skills/{topic}-{skill}/SKILL.md")

    return json.dumps(plugin, indent=2)


def generate_marketplace_json(context: dict) -> str:
    """Generate .claude-plugin/marketplace.json content."""
    project_name = context['PROJECT_NAME']
    topic = context['TOPIC']

    marketplace = {
        "name": project_name.lower(),
        "version": "1.0.0",
        "plugins": [
            {
                "name": project_name.lower(),
                "source": "./",
                "description": f"{context['API_NAME']} automation skills for Claude Code"
            }
        ]
    }

    return json.dumps(marketplace, indent=2)


def generate_setup_command(context: dict) -> str:
    """Generate setup command markdown."""
    topic = context['TOPIC']
    api_name = context['API_NAME']
    project_type = context.get('PROJECT_TYPE', 'cli-wrapper')

    if project_type == 'cli-wrapper':
        cli_tool = context.get('CLI_TOOL', topic)
        cli_install = context.get('CLI_INSTALL', f'brew install {cli_tool}')

        return f"""---
description: "Set up {api_name} Assistant Skills with credentials and configuration"
user_invocable: true
arguments:
  - name: profile
    description: "Configuration profile name"
    required: false
    default: "default"
---

# {api_name} Assistant Setup

Set up {api_name} Assistant Skills for Claude Code.

## Prerequisites

Install the {cli_tool} CLI:

```bash
{cli_install}
```

## Authentication

Authenticate with {api_name}:

```bash
{cli_tool} auth login
```

## Verification

Verify your setup:

```bash
{cli_tool} auth status
```

## Configuration

Configuration is stored in your {cli_tool} CLI config.

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Auth failed | Run `{cli_tool} auth login` again |
| CLI not found | Verify installation: `which {cli_tool}` |
| Permission denied | Check your {api_name} permissions |
"""
    else:
        # Custom library setup
        cli_name = f'{topic}-as'
        return f"""---
description: "Set up {api_name} Assistant Skills with credentials and configuration"
user_invocable: true
arguments:
  - name: profile
    description: "Configuration profile name"
    required: false
    default: "default"
---

# {api_name} Assistant Setup

Set up {api_name} Assistant Skills for Claude Code.

## Installation

Install the CLI library:

```bash
pip install {topic}-assistant-skills-lib
```

Or install from source:

```bash
cd {topic}-assistant-skills-lib
pip install -e .
```

## Authentication

Configure your API credentials:

```bash
# Set environment variables
export {api_name.upper().replace(' ', '_').replace('-', '_')}_API_KEY="your-api-key"
export {api_name.upper().replace(' ', '_').replace('-', '_')}_BASE_URL="{context.get('API_URL', 'https://api.example.com')}"

# Or use the config command
{cli_name} config set api_key YOUR_API_KEY
{cli_name} config set base_url {context.get('API_URL', 'https://api.example.com')}
```

## Verification

Verify your setup:

```bash
{cli_name} auth status
```

## Profiles

Use different profiles for different environments:

```bash
# Use development profile
{cli_name} --profile development config set base_url https://dev.api.example.com

# Use profile in commands
{cli_name} --profile development resource list
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Auth failed | Verify API key: `{cli_name} auth status` |
| CLI not found | Verify installation: `pip show {topic}-assistant-skills-lib` |
| Connection error | Check BASE_URL and network connectivity |
"""


def generate_browse_skills_command(context: dict) -> str:
    """Generate browse-skills command markdown."""
    topic = context['TOPIC']
    api_name = context['API_NAME']
    skills = context.get('SKILLS', [])

    skills_table = ""
    for skill in skills:
        skills_table += f"| {topic}-{skill} | {skill.title()} operations |\n"

    return f"""---
description: "Browse all available {api_name} skills with descriptions and examples"
user_invocable: true
---

# Browse {api_name} Skills

List all available {api_name} automation skills.

## Available Skills

| Skill | Description |
|-------|-------------|
| {topic}-assistant | Hub skill - routes to specialized skills |
{skills_table}

## Usage

To use a skill, simply describe what you want to do:

- "List all resources" - Routes to appropriate skill
- "Create a new item" - Routes to resource skill
- "Search for X" - Routes to search skill

## Getting Started

1. Run `/{topic}-assistant-setup` to configure authentication
2. Describe your task naturally
3. The assistant will route to the appropriate skill
"""


def generate_skill_info_command(context: dict) -> str:
    """Generate skill-info command markdown."""
    topic = context['TOPIC']
    api_name = context['API_NAME']

    return f"""---
description: "Get detailed information about a specific {api_name} skill"
user_invocable: true
arguments:
  - name: skill_name
    description: "Name of the skill to get info about"
    required: true
---

# Skill Information

Get detailed information about a specific {api_name} skill.

## Usage

```
/skill-info {topic}-issue
```

## Information Provided

- Skill description and purpose
- Available operations with risk levels
- CLI commands and options
- Common patterns and examples
- Related skills and documentation

## Example Output

For `{topic}-resource`:
- **Operations**: list, get, create, update, delete
- **Risk Level**: ⚠️ (modifiable)
- **Related**: {topic}-search, {topic}-bulk
"""


def generate_conftest_py(context: dict) -> str:
    """Generate root conftest.py with standard fixtures."""
    topic = context['TOPIC']
    api_name = context['API_NAME']

    return f'''"""
Root test fixtures for {context['PROJECT_NAME']}.

This file contains shared fixtures used across all skill tests.
"""

import pytest
from pathlib import Path
from typing import Generator
import tempfile
import shutil


@pytest.fixture
def temp_path() -> Generator[Path, None, None]:
    """Create a temporary directory as Path object."""
    path = Path(tempfile.mkdtemp())
    yield path
    shutil.rmtree(path, ignore_errors=True)


@pytest.fixture
def temp_dir(temp_path: Path) -> str:
    """Create a temporary directory as string."""
    return str(temp_path)


@pytest.fixture
def mock_{topic}_client():
    """Mock {topic} client for offline testing."""
    from unittest.mock import MagicMock

    client = MagicMock()
    client.get.return_value = {{"items": [], "total": 0}}
    client.post.return_value = {{"id": "123", "status": "created"}}
    client.put.return_value = {{"id": "123", "status": "updated"}}
    client.delete.return_value = None

    return client


@pytest.fixture
def sample_resource():
    """Sample resource data for testing."""
    return {{
        "id": "RESOURCE-123",
        "name": "Test Resource",
        "description": "A test resource",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
    }}


@pytest.fixture
def sample_resource_list(sample_resource):
    """Sample list of resources for testing."""
    return [sample_resource]


@pytest.fixture
def claude_project_structure(temp_path: Path) -> Path:
    """Create a minimal Claude plugin project structure."""
    # Create .claude-plugin directory
    plugin_dir = temp_path / ".claude-plugin"
    plugin_dir.mkdir()

    # Create plugin.json
    (plugin_dir / "plugin.json").write_text(\'\'\'{{
        "name": "test-plugin",
        "version": "1.0.0",
        "skills": ["../skills/test-skill/SKILL.md"]
    }}\'\'\')

    # Create skills directory
    skills_dir = temp_path / "skills" / "test-skill"
    skills_dir.mkdir(parents=True)

    # Create SKILL.md
    (skills_dir / "SKILL.md").write_text(\'\'\'---
name: test-skill
description: Test skill for testing.
---

# Test Skill

Test content.
\'\'\')

    return temp_path
'''


def generate_pytest_ini(context: dict) -> str:
    """Generate pytest.ini with markers."""
    topic = context['TOPIC']

    return f"""[pytest]
testpaths = skills tests
pythonpath = . skills/shared/tests/live_integration
addopts = -v --tb=short --import-mode=importlib

markers =
    # Environment markers
    unit: Unit tests (fast, no external dependencies)
    integration: Integration tests (may require setup)
    live: Live tests against real {topic} instance
    e2e: End-to-end tests with Claude Code
    docker_required: Requires Docker

    # Characteristic markers
    slow: Slow tests (>10s)
    fast: Fast tests (<1s)
    flaky: Tests that may fail intermittently
    destructive: Tests that modify state
    readonly: Tests that only read data

    # Feature markers
    search: Search functionality tests
    crud: Create/Read/Update/Delete tests
    bulk: Bulk operation tests
    auth: Authentication tests

    # Priority markers
    critical: Critical path tests
    smoke: Smoke tests for quick validation

    # Risk markers
    safe: Safe operations (no side effects)
    caution: Operations that modify single items
    warning: Bulk/destructive operations

    # Skill markers
    {topic}_assistant: Hub/router skill tests
"""


def generate_requirements_txt(context: dict) -> str:
    """Generate requirements.txt."""
    project_type = context.get('PROJECT_TYPE', 'cli-wrapper')

    base_requirements = """# Core dependencies
requests>=2.28.0

# Output formatting
tabulate>=0.9.0
colorama>=0.4.6

# Configuration
python-dotenv>=1.0.0

# Testing
pytest>=7.0.0
pytest-cov>=4.0.0

# Assistant Skills library
assistant-skills-lib>=0.3.0
"""

    if project_type in ('custom-library', 'hybrid'):
        topic = context['TOPIC']
        base_requirements += f"""
# Project CLI library (install in editable mode during development)
# pip install -e ./{topic}-assistant-skills-lib/
"""

    return base_requirements


def generate_claude_md(context: dict) -> str:
    """Generate CLAUDE.md content."""
    project_name = context['PROJECT_NAME']
    topic = context['TOPIC']
    api_name = context['API_NAME']
    skills = context.get('SKILLS', [])
    project_type = context.get('PROJECT_TYPE', 'cli-wrapper')

    skills_table = ""
    for skill in skills:
        skills_table += f"| `{topic}-{skill}` | {skill.title()} operations | `skills/{topic}-{skill}/` |\n"

    cli_section = ""
    if project_type == 'cli-wrapper':
        cli_tool = context.get('CLI_TOOL', topic)
        cli_section = f"""
## CLI Tool

This project wraps the `{cli_tool}` CLI tool. Skills document `{cli_tool}` commands
rather than implementing custom scripts.

### Installation

See `/{topic}-assistant-setup` for installation instructions.
"""
    else:
        cli_name = f'{topic}-as'
        cli_section = f"""
## CLI Library

This project includes a custom CLI library: `{topic}-assistant-skills-lib/`

### Installation

```bash
pip install -e ./{topic}-assistant-skills-lib/
```

### Usage

```bash
{cli_name} --help
{cli_name} resource list
{cli_name} resource get RESOURCE-123
```
"""

    return f"""# {project_name}

Claude Code guidance for the {project_name} project.

## Overview

This project provides Claude Code skills for interacting with {api_name}.
{cli_section}

## Available Skills

| Skill | Purpose | Location |
|-------|---------|----------|
| `{topic}-assistant` | Hub skill - routes to specialized skills | `skills/{topic}-assistant/` |
{skills_table}

## Project Structure

```
{project_name}/
├── .claude-plugin/           # Plugin manifest and commands
│   ├── plugin.json          # Plugin definition
│   ├── marketplace.json     # Marketplace registry
│   └── commands/            # Slash commands
├── skills/                   # Skill documentation
│   ├── {topic}-assistant/   # Hub/router skill
│   ├── {topic}-*/           # Feature skills
│   └── shared/              # Shared docs and config
├── conftest.py              # Root test fixtures
├── pytest.ini               # Test configuration
├── VERSION                  # Single version source
└── CLAUDE.md               # This file
```

## Configuration

Configuration priority:
1. Environment variables
2. CLI configuration
3. Project defaults

## Testing

### Run Tests

```bash
# All tests
pytest skills/ -v

# Specific skill
pytest skills/{topic}-issue/tests/ -v

# Skip destructive tests
pytest skills/ -v -m "not destructive"

# Only smoke tests
pytest skills/ -v -m "smoke"
```

### Test Markers

| Marker | Description |
|--------|-------------|
| `@pytest.mark.unit` | Unit tests (fast, no deps) |
| `@pytest.mark.live` | Live API tests |
| `@pytest.mark.destructive` | Modifies state |
| `@pytest.mark.readonly` | Read-only operations |

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

## Risk Levels

All operations are marked with risk levels:

| Risk | Symbol | Description |
|------|:------:|-------------|
| Safe | `-` | Read-only operations |
| Caution | `⚠️` | Single-item modifications |
| Warning | `⚠️⚠️` | Bulk/destructive operations |
| Danger | `⚠️⚠️⚠️` | Irreversible operations |

## Version Management

Single source of truth: `VERSION` file

To update version:
```bash
echo "2.0.0" > VERSION
```
"""


def generate_readme(context: dict) -> str:
    """Generate README.md content."""
    project_name = context['PROJECT_NAME']
    topic = context['TOPIC']
    api_name = context['API_NAME']
    project_type = context.get('PROJECT_TYPE', 'cli-wrapper')

    install_section = ""
    if project_type == 'cli-wrapper':
        cli_tool = context.get('CLI_TOOL', topic)
        cli_install = context.get('CLI_INSTALL', f'brew install {cli_tool}')
        install_section = f"""
### 1. Install CLI

```bash
{cli_install}
```

### 2. Authenticate

```bash
{cli_tool} auth login
```
"""
    else:
        cli_name = f'{topic}-as'
        install_section = f"""
### 1. Install Library

```bash
pip install {topic}-assistant-skills-lib
```

Or from source:

```bash
pip install -e ./{topic}-assistant-skills-lib/
```

### 2. Configure

```bash
export {api_name.upper().replace(' ', '_').replace('-', '_')}_API_KEY="your-api-key"
```
"""

    return f"""# {project_name}

Claude Code Assistant Skills for {api_name}.

## Quick Start
{install_section}
### 3. Load in Claude Code

```
/load {topic}
```

## Available Skills

| Skill | Description |
|-------|-------------|
| `{topic}-assistant` | Hub skill for routing to specialized skills |

## Configuration

See [CLAUDE.md](CLAUDE.md) for configuration options and development guidelines.

## Development

### Run Tests

```bash
pytest skills/ -v
```

### Validate Project

```bash
python -m assistant_builder.validate_project .
```

## License

MIT License
"""


def generate_router_skill_md(context: dict) -> str:
    """Generate SKILL.md for the router/assistant skill."""
    topic = context['TOPIC']
    api_name = context['API_NAME']
    skills = context.get('SKILLS', [])
    project_type = context.get('PROJECT_TYPE', 'cli-wrapper')
    cli_tool = context.get('CLI_TOOL', topic) if project_type == 'cli-wrapper' else f'{topic}-as'

    # Build routing table
    routing_table = ""
    for skill in skills:
        routing_table += f"| {skill.title()} operations | `{topic}-{skill}` | ⚠️ |\n"

    # Build skills overview
    skills_overview = ""
    for skill in skills:
        skills_overview += f"""
### {topic}-{skill}

- **Purpose**: {skill.title()} operations
- **Risk**: ⚠️ (modifiable)
- **Triggers**: {skill}, {skill}s, manage {skill}
"""

    return f"""---
name: "{topic}-assistant"
description: "{api_name} automation hub. Routes requests to specialized skills. ALWAYS use this skill when: (1) any {api_name} operation, (2) unsure which skill to use, (3) multi-step {api_name} workflows. Start here for any {topic} task."
version: "1.0.0"
author: "{context['PROJECT_NAME']}"
license: "MIT"
allowed-tools: ["Bash", "Read", "Glob", "Grep"]
---

# {api_name} Assistant

Central hub for {api_name} automation. Routes requests to the most appropriate specialized skill.

## Quick Reference

| I want to... | Use this skill | Risk |
|--------------|----------------|:----:|
| Search/list/query | {topic}-search | - |
{routing_table}| Bulk operations on 10+ items | {topic}-bulk | ⚠️⚠️ |

**Risk Legend**: - Safe | ⚠️ Caution | ⚠️⚠️ Warning | ⚠️⚠️⚠️ Danger

## Routing Rules

### Rule 1: Explicit Skill Mention

If user explicitly mentions a skill name, route to that skill.

- "use {topic}-search" → {topic}-search
- "run the bulk skill" → {topic}-bulk

### Rule 2: Entity Signals

| Signal | Route to |
|--------|----------|
| Item ID (e.g., ITEM-123) | {topic}-resource |
| Query/filter expression | {topic}-search |
| "bulk", "batch", "multiple" | {topic}-bulk |

### Rule 3: Operation Type

| Operation | Route to |
|-----------|----------|
| List, search, find, query | {topic}-search |
| Get, show, view details | {topic}-resource |
| Create, new, add | {topic}-resource |
| Update, edit, modify | {topic}-resource |
| Delete, remove | {topic}-resource |
| Bulk create/update/delete | {topic}-bulk |

### Rule 4: Quantity Determines Skill

| Quantity | Route to |
|----------|----------|
| Single item | {topic}-resource |
| 2-10 items | {topic}-resource (loop) |
| 10+ items | {topic}-bulk |

## Skills Overview
{skills_overview}

## Disambiguation

When request is ambiguous, ask for clarification:

| Ambiguous Request | Clarifying Question |
|-------------------|---------------------|
| "Update the items" | "How many items? If more than 10, I'll use bulk operations." |
| "Show me the data" | "Do you want to search/filter, or view a specific item?" |

## Connection Verification

Before any operation, verify {api_name} is configured:

```bash
{cli_tool} auth status
```

If not authenticated:
```bash
{cli_tool} auth login
```

## Related Documentation

- [Decision Tree](./docs/DECISION_TREE.md)
- [Safeguards](../shared/docs/SAFEGUARDS.md)
- [Quick Reference](../shared/docs/QUICK_REFERENCE.md)
"""


def generate_skill_md(context: dict, skill_name: str) -> str:
    """Generate SKILL.md for a specific skill."""
    topic = context['TOPIC']
    api_name = context['API_NAME']
    project_type = context.get('PROJECT_TYPE', 'cli-wrapper')
    cli_tool = context.get('CLI_TOOL', topic) if project_type == 'cli-wrapper' else f'{topic}-as'

    return f"""---
name: "{topic}-{skill_name}"
description: "{api_name} {skill_name} operations. ALWAYS use this skill when user wants to: (1) list {skill_name}s, (2) get {skill_name} details, (3) create new {skill_name}s, (4) update existing {skill_name}s, (5) delete {skill_name}s."
version: "1.0.0"
author: "{context['PROJECT_NAME']}"
license: "MIT"
allowed-tools: ["Bash", "Read", "Glob", "Grep"]
---

# {skill_name.title()} Skill

{skill_name.title()} operations for {api_name}.

## Quick Reference

| Operation | Command | Risk |
|-----------|---------|:----:|
| List {skill_name}s | `{cli_tool} {skill_name} list` | - |
| Get {skill_name} | `{cli_tool} {skill_name} get <id>` | - |
| Create {skill_name} | `{cli_tool} {skill_name} create [options]` | ⚠️ |
| Update {skill_name} | `{cli_tool} {skill_name} update <id> [options]` | ⚠️ |
| Delete {skill_name} | `{cli_tool} {skill_name} delete <id>` | ⚠️⚠️ |

**Risk Legend**: - Safe | ⚠️ Caution | ⚠️⚠️ Warning | ⚠️⚠️⚠️ Danger

## When to Use This Skill

**ALWAYS use when:**
- User wants to work with {skill_name}s
- User mentions "{skill_name}", "{skill_name}s", or related terms

**NEVER use when:**
- User wants bulk operations on 10+ items (use {topic}-bulk instead)
- User is searching/querying (use {topic}-search instead)

## Available Commands

### List {skill_name.title()}s

```bash
{cli_tool} {skill_name} list [--filter <query>] [--output json|table]
```

**Examples:**
```bash
# List all {skill_name}s
{cli_tool} {skill_name} list

# Filter by status
{cli_tool} {skill_name} list --filter "status=active"

# JSON output for scripting
{cli_tool} {skill_name} list --output json
```

### Get {skill_name.title()} Details

```bash
{cli_tool} {skill_name} get <id> [--output json|table]
```

### Create {skill_name.title()}

```bash
{cli_tool} {skill_name} create --name <name> [--description <desc>]
```

### Update {skill_name.title()}

```bash
{cli_tool} {skill_name} update <id> [--name <name>] [--description <desc>]
```

### Delete {skill_name.title()}

```bash
{cli_tool} {skill_name} delete <id> [--force]
```

## Common Patterns

### Pattern 1: View and Update

```bash
# Step 1: List to find the item
{cli_tool} {skill_name} list --filter "name=example"

# Step 2: Get details
{cli_tool} {skill_name} get ITEM-123

# Step 3: Update if needed
{cli_tool} {skill_name} update ITEM-123 --status completed
```

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| Authentication failed | Invalid token | Run `{cli_tool} auth login` |
| Resource not found | Invalid ID | Verify ID with `{cli_tool} {skill_name} list` |
| Permission denied | Insufficient rights | Check your {api_name} permissions |

## Related Documentation

- [Best Practices](./docs/BEST_PRACTICES.md)
- [Safeguards](../shared/docs/SAFEGUARDS.md)
"""


def generate_safeguards_md(context: dict) -> str:
    """Generate SAFEGUARDS.md template."""
    topic = context['TOPIC']
    api_name = context['API_NAME']
    project_type = context.get('PROJECT_TYPE', 'cli-wrapper')
    cli_tool = context.get('CLI_TOOL', topic) if project_type == 'cli-wrapper' else f'{topic}-as'

    return f"""# Safeguards & Recovery Procedures

## Risk Level Matrix

| Risk | Symbol | Description | Safeguards |
|------|:------:|-------------|------------|
| Read-only | - | Safe operations, no confirmation | None |
| Caution | ⚠️ | Single-item modifications | Optional confirmation |
| Warning | ⚠️⚠️ | Bulk/destructive operations | Required confirmation, dry-run |
| Danger | ⚠️⚠️⚠️ | Irreversible operations | Double confirmation, backup |

## Pre-Operation Checklist

### Before Any Destructive Operation

1. [ ] Verify target (ID, name, filter)
2. [ ] Confirm scope (single vs. bulk)
3. [ ] Check permissions
4. [ ] Consider dry-run first
5. [ ] Note rollback procedure

### Before Bulk Operations

1. [ ] Run with `--dry-run` first
2. [ ] Review affected items
3. [ ] Confirm count is expected
4. [ ] Set reasonable batch size
5. [ ] Enable checkpointing for large batches

## Recovery Procedures

### Accidental Single Delete

1. Check if soft-delete is enabled
2. If yes, restore from trash within retention period
3. If no, restore from backup

### Accidental Bulk Modification

1. Stop immediately if in progress
2. Review checkpoint file for affected items
3. Reverse changes using bulk update
4. Or restore from backup

### Authentication Issues

1. Verify credentials: `{cli_tool} auth status`
2. Re-authenticate: `{cli_tool} auth login`
3. Check token expiration
4. Verify API endpoint connectivity

## Emergency Contacts

| Issue | Contact |
|-------|---------|
| API outage | Check {api_name} status page |
| Security incident | Contact security team |
| Data loss | Contact backup administrator |
"""


def generate_decision_tree_md(context: dict) -> str:
    """Generate DECISION_TREE.md template."""
    topic = context['TOPIC']

    return f"""# Skill Routing Decision Tree

## Primary Decision: What does the user want to do?

```
User Request
    │
    ├─ Mentions specific skill? ──────► Use that skill
    │
    ├─ Search/query/find? ────────────► {topic}-search
    │
    ├─ Single item CRUD? ─────────────► {topic}-resource
    │   ├─ Create
    │   ├─ Read/Get
    │   ├─ Update
    │   └─ Delete
    │
    ├─ Multiple items (10+)? ─────────► {topic}-bulk
    │   └─ "bulk", "batch", "all"
    │
    └─ Ambiguous? ────────────────────► Ask for clarification
```

## Keyword-Based Routing

| Keywords | Route to |
|----------|----------|
| search, find, query, list, filter | {topic}-search |
| create, new, add, make | {topic}-resource |
| get, show, view, display | {topic}-resource |
| update, edit, modify, change | {topic}-resource |
| delete, remove, destroy | {topic}-resource |
| bulk, batch, mass, multiple | {topic}-bulk |

## Context-Based Routing

| Context | Consideration |
|---------|---------------|
| Previous skill used | Continue with same skill if follow-up |
| Item ID mentioned | Route to resource skill |
| Count > 10 | Route to bulk skill |

## Disambiguation Questions

When unclear, ask:

- "How many items are you working with?"
- "Do you want to search or view a specific item?"
- "Should I use bulk operations for this?"
"""


def generate_quick_reference_md(context: dict) -> str:
    """Generate QUICK_REFERENCE.md template."""
    topic = context['TOPIC']
    api_name = context['API_NAME']
    project_type = context.get('PROJECT_TYPE', 'cli-wrapper')
    cli_tool = context.get('CLI_TOOL', topic) if project_type == 'cli-wrapper' else f'{topic}-as'

    return f"""# Quick Reference

## Connection

```bash
# Check connection
{cli_tool} auth status

# Login
{cli_tool} auth login
```

## Common Operations

### Search & List
```bash
{cli_tool} resource list
{cli_tool} resource list --filter "status=active"
{cli_tool} resource list --output json
```

### Get Details
```bash
{cli_tool} resource get <id>
{cli_tool} resource get <id> --output json
```

### Create
```bash
{cli_tool} resource create --name "Name" --description "Desc"
```

### Update
```bash
{cli_tool} resource update <id> --name "New Name"
```

### Delete
```bash
{cli_tool} resource delete <id>
{cli_tool} resource delete <id> --force  # Skip confirmation
```

## Bulk Operations

```bash
# Dry-run first
{cli_tool} bulk update --filter "status=old" --set status=new --dry-run

# Execute with confirmation
{cli_tool} bulk update --filter "status=old" --set status=new

# With checkpoint for large batches
{cli_tool} bulk update --filter "status=old" --set status=new --enable-checkpoint
```

## Output Formats

| Format | Flag | Use Case |
|--------|------|----------|
| Table | `--output table` | Human readable (default) |
| JSON | `--output json` | Scripting, piping |
| Text | `--output text` | Simple output |

## Error Codes

| Code | Meaning | Solution |
|------|---------|----------|
| 401 | Auth failed | Re-run `{cli_tool} auth login` |
| 403 | Permission denied | Check access rights |
| 404 | Not found | Verify resource ID |
| 429 | Rate limited | Wait and retry |
| 5xx | Server error | Check {api_name} status |
"""


def scaffold_project(
    name: str,
    topic: str,
    api_name: str,
    project_type: str = 'cli-wrapper',
    base_url: str = None,
    cli_tool: str = None,
    cli_install: str = None,
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
        'PROJECT_TYPE': project_type,
        'API_URL': base_url or 'https://api.example.com',
        'BASE_URL': base_url or 'https://api.example.com',
        'CLI_TOOL': cli_tool or topic,
        'CLI_INSTALL': cli_install or f'brew install {cli_tool or topic}',
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
        'project_type': project_type,
        'directories': [],
        'files': []
    }

    # Create directory structure
    if not dry_run:
        output_path.mkdir(parents=True, exist_ok=True)

    result['directories'] = create_directory_structure(
        output_path, topic, skills or [], project_type, dry_run
    )

    # Generate files
    files_to_create = [
        # Root files
        ('.gitignore', generate_gitignore(context)),
        ('VERSION', generate_version_file(context)),
        ('README.md', generate_readme(context)),
        ('CLAUDE.md', generate_claude_md(context)),
        ('requirements.txt', generate_requirements_txt(context)),
        ('conftest.py', generate_conftest_py(context)),
        ('pytest.ini', generate_pytest_ini(context)),

        # Plugin files
        ('.claude-plugin/plugin.json', generate_plugin_json(context)),
        ('.claude-plugin/marketplace.json', generate_marketplace_json(context)),
        (f'.claude-plugin/commands/{topic}-assistant-setup.md', generate_setup_command(context)),
        ('.claude-plugin/commands/browse-skills.md', generate_browse_skills_command(context)),
        ('.claude-plugin/commands/skill-info.md', generate_skill_info_command(context)),

        # Router skill
        (f'skills/{topic}-assistant/SKILL.md', generate_router_skill_md(context)),
        (f'skills/{topic}-assistant/docs/DECISION_TREE.md', generate_decision_tree_md(context)),

        # Shared documentation
        ('skills/shared/docs/SAFEGUARDS.md', generate_safeguards_md(context)),
        ('skills/shared/docs/QUICK_REFERENCE.md', generate_quick_reference_md(context)),
    ]

    # Add skill files
    for skill in (skills or []):
        files_to_create.append(
            (f'skills/{topic}-{skill}/SKILL.md', generate_skill_md(context, skill))
        )

    # Create files
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

    # Step 1: Project type
    print("Step 1: Project Type\n")
    print("  [1] CLI Wrapper - Wrap an existing CLI tool (glab, gh, aws, kubectl)")
    print("  [2] Custom Library - Build new CLI for an API (like Jira, Confluence)")
    print("  [3] Hybrid - Wrap CLI and extend with custom library")
    print()

    type_choice = input("Select project type [1]: ").strip()
    if not type_choice or type_choice == '1':
        project_type = 'cli-wrapper'
    elif type_choice == '2':
        project_type = 'custom-library'
    elif type_choice == '3':
        project_type = 'hybrid'
    else:
        project_type = 'cli-wrapper'

    print(f"\nSelected: {project_type}\n")

    # Step 2: Project basics
    print("Step 2: Project Basics\n")

    name = input("Project name (e.g., GitHub-Assistant-Skills): ").strip()
    name = validate_name(name, "project name")

    topic = input(f"Topic prefix (lowercase, e.g., github) [{name.split('-')[0].lower()}]: ").strip()
    if not topic:
        topic = name.split('-')[0].lower()
    topic = validate_topic_prefix(topic)

    api_name = input(f"API/Service name (e.g., GitHub) [{topic.title()}]: ").strip()
    if not api_name:
        api_name = topic.title()

    # Step 3: Project-type specific details
    print(f"\nStep 3: {project_type.title()} Details\n")

    cli_tool = None
    cli_install = None
    base_url = None
    auth_method = 'api_key'

    if project_type == 'cli-wrapper':
        cli_tool = input(f"CLI tool name (e.g., glab, gh) [{topic}]: ").strip()
        if not cli_tool:
            cli_tool = topic

        cli_install = input(f"CLI install command [brew install {cli_tool}]: ").strip()
        if not cli_install:
            cli_install = f'brew install {cli_tool}'

    elif project_type in ('custom-library', 'hybrid'):
        base_url = input("API base URL [https://api.example.com]: ").strip()
        if not base_url:
            base_url = "https://api.example.com"
        else:
            base_url = validate_url(base_url)

        print(f"\nAuthentication methods: {', '.join(AUTH_METHODS)}")
        auth_method = input(f"Auth method [{AUTH_METHODS[0]}]: ").strip().lower()
        if not auth_method:
            auth_method = AUTH_METHODS[0]
        auth_method = validate_choice(auth_method, AUTH_METHODS, "auth method")

        if project_type == 'hybrid':
            cli_tool = input(f"CLI tool to wrap (e.g., glab) [{topic}]: ").strip()
            if not cli_tool:
                cli_tool = topic

    # Step 4: Skills
    print("\nStep 4: Initial Skills\n")

    skills_input = input("Initial skills (comma-separated, e.g., issues,repos,users): ").strip()
    skills = validate_list(skills_input, "skills", min_items=0)

    # Step 5: Confirmation
    print("\n" + "-" * 60)
    print("Configuration Summary:")
    print("-" * 60)
    print(f"  Project Type:  {project_type}")
    print(f"  Project Name:  {name}")
    print(f"  Topic Prefix:  {topic}")
    print(f"  API Name:      {api_name}")
    if project_type == 'cli-wrapper':
        print(f"  CLI Tool:      {cli_tool}")
        print(f"  CLI Install:   {cli_install}")
    elif project_type in ('custom-library', 'hybrid'):
        print(f"  Base URL:      {base_url}")
        print(f"  Auth Method:   {auth_method}")
        if project_type == 'hybrid':
            print(f"  CLI Tool:      {cli_tool}")
    print(f"  Skills:        {', '.join(skills) if skills else '(none)'}")
    print("-" * 60)

    confirm = input("\nProceed with creation? [Y/n]: ").strip().lower()
    if confirm and confirm != 'y':
        print("Cancelled.")
        return None

    return {
        'name': name,
        'topic': topic,
        'api_name': api_name,
        'project_type': project_type,
        'cli_tool': cli_tool,
        'cli_install': cli_install,
        'base_url': base_url,
        'auth_method': auth_method,
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

  # CLI Wrapper project
  python scaffold_project.py \\
      --type cli-wrapper \\
      --name "GitLab-Assistant-Skills" \\
      --topic "gitlab" \\
      --cli-tool "glab" \\
      --cli-install "brew install glab"

  # Custom Library project
  python scaffold_project.py \\
      --type custom-library \\
      --name "MyAPI-Assistant-Skills" \\
      --topic "myapi" \\
      --api "My API" \\
      --api-url "https://api.example.com"

  # Dry run
  python scaffold_project.py --name "Test" --topic "test" --dry-run
'''
    )

    parser.add_argument('--type', '-T', choices=PROJECT_TYPES, default='cli-wrapper',
                        help='Project type: cli-wrapper, custom-library, or hybrid')
    parser.add_argument('--name', '-n', help='Project name')
    parser.add_argument('--topic', '-t', help='Lowercase topic prefix')
    parser.add_argument('--api', '-a', help='Friendly API/service name')
    parser.add_argument('--api-url', '-u', help='API base URL (for custom-library/hybrid)')
    parser.add_argument('--cli-tool', '-c', help='CLI tool name (for cli-wrapper/hybrid)')
    parser.add_argument('--cli-install', help='CLI install command')
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
                'project_type': args.type,
                'base_url': args.api_url,
                'cli_tool': args.cli_tool,
                'cli_install': args.cli_install,
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
            project_type=config.get('project_type', 'cli-wrapper'),
            base_url=config.get('base_url'),
            cli_tool=config.get('cli_tool'),
            cli_install=config.get('cli_install'),
            skills=config.get('skills', []),
            auth_method=config.get('auth_method', 'api_key'),
            pagination_style=config.get('pagination_style', 'offset'),
            output_dir=args.output_dir,
            dry_run=args.dry_run
        )

        # Report results
        print_success(f"Created {result['project_type']} project at: {result['path']}")
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

        if result['project_type'] == 'cli-wrapper':
            print(f"2. Install the CLI tool: {config.get('cli_install', 'see setup command')}")
            print("3. Run authentication: see setup command")
        elif result['project_type'] in ('custom-library', 'hybrid'):
            print(f"2. Implement the library: {config['topic']}-assistant-skills-lib/")
            print("3. Install locally: pip install -e ./{config['topic']}-assistant-skills-lib/")

        print("4. Add more skills with: python add_skill.py")
        print("5. Run validation: python validate_project.py .")
        print("\nSee CLAUDE.md for development guidelines.")

    except ValidationError as e:
        print_error(str(e))
        sys.exit(1)
    except Exception as e:
        print_error(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
