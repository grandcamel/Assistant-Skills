#!/usr/bin/env python3
"""
Add a new skill to an existing Assistant Skills project.

Creates the skill directory structure with SKILL.md, scripts, tests,
and documentation following established patterns.

Usage:
    python add_skill.py --name "search" --description "Search operations"

Examples:
    # Interactive mode
    python add_skill.py

    # Full specification
    python add_skill.py \\
        --name "search" \\
        --description "Search and query operations" \\
        --resource "queries" \\
        --scripts "search,list_saved,create_saved,delete_saved"

    # Standard CRUD operations
    python add_skill.py --name "users" --description "User management" --scripts crud
"""

import argparse
import sys
from pathlib import Path

from assistant_skills_lib import (
    detect_project, get_topic_prefix,
    validate_required, validate_name, validate_path, validate_list,
    InputValidationError as ValidationError,
    print_success, print_error, print_info, print_warning
)


# Script presets
SCRIPT_PRESETS = {
    'crud': ['list', 'get', 'create', 'update', 'delete'],
    'list-get': ['list', 'get'],
    'all': ['list', 'get', 'create', 'update', 'delete', 'search', 'export']
}


def generate_skill_md(topic: str, skill_name: str, description: str, scripts: list) -> str:
    """Generate SKILL.md content."""
    scripts_table = ""
    for script in scripts:
        script_desc = script.replace('_', ' ').title()
        scripts_table += f"| {script_desc} | `{script}_{skill_name}.py` | {script_desc} {skill_name} |\n"

    return f"""---
name: "{topic}-{skill_name}"
description: "{description}"
when_to_use: |
  - Working with {skill_name}
  - {description}
---

# {skill_name.title()} Skill

{description}

---

## What This Skill Does

| Operation | Script | Description |
|-----------|--------|-------------|
{scripts_table}

---

## Quick Start

```bash
# List all
python list_{skill_name}.py

# Get by ID
python get_{skill_name}.py ID

# With different profile
python list_{skill_name}.py --profile development
```

---

## Available Scripts

All scripts support:
- `--help` - Show usage and examples
- `--profile` - Use specific configuration profile
- `--output` - Output format (text, json)

---

## Configuration

Uses shared configuration from `.claude/settings.json`.

---

## Related Skills

| Skill | Relationship |
|-------|--------------|
| `{topic}-assistant` | Hub skill for routing |
"""


def generate_script_template(topic: str, skill_name: str, script_name: str) -> str:
    """Generate a script file template."""
    resource = skill_name

    return f'''#!/usr/bin/env python3
"""
{script_name.replace('_', ' ').title()} {skill_name}.

Examples:
    python {script_name}_{skill_name}.py --help
    python {script_name}_{skill_name}.py --output json
"""

import argparse
import sys
from pathlib import Path

# Add shared lib to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'shared' / 'scripts' / 'lib'))

# Uncomment when shared lib is implemented:
# from config_manager import get_client
# from error_handler import handle_errors
# from validators import validate_required
# from formatters import print_success, format_table, format_json


def main():
    parser = argparse.ArgumentParser(
        description='{script_name.replace("_", " ").title()} {skill_name}',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python {script_name}_{skill_name}.py
  python {script_name}_{skill_name}.py --output json
  python {script_name}_{skill_name}.py --profile development
"""
    )

    # Add arguments based on script type
    {"parser.add_argument('id', nargs='?', help='Resource ID')" if script_name in ('get', 'update', 'delete') else "# No positional args for list/create/search"}

    parser.add_argument('--profile', '-p', help='Configuration profile')
    parser.add_argument('--output', '-o', choices=['text', 'json'], default='text',
                        help='Output format')

    args = parser.parse_args()

    # TODO: Implement {script_name} logic
    print(f"TODO: Implement {script_name}_{skill_name}")

    # Example implementation pattern:
    # client = get_client(profile=args.profile)
    # result = client.{script_name}('{resource}')
    #
    # if args.output == 'json':
    #     print(format_json(result))
    # else:
    #     print(format_table(result))


if __name__ == '__main__':
    main()
'''


def generate_test_template(topic: str, skill_name: str, script_name: str) -> str:
    """Generate a test file template."""
    return f'''"""
Tests for {script_name}_{skill_name}.py
"""

import pytest
from unittest.mock import patch, MagicMock


class Test{script_name.title()}{skill_name.title()}:
    """Tests for {script_name}_{skill_name} script."""

    def test_{script_name}_returns_results(self):
        """Test that {script_name} returns expected results."""
        # Arrange
        # mock_client = MagicMock()
        # mock_client.{script_name}.return_value = {{'data': []}}

        # Act
        # with patch('script.get_client', return_value=mock_client):
        #     result = {script_name}_function()

        # Assert
        # assert result is not None
        pass  # TODO: Implement test

    def test_{script_name}_handles_errors(self):
        """Test that {script_name} handles API errors gracefully."""
        # TODO: Implement error handling test
        pass

    def test_{script_name}_validates_input(self):
        """Test that {script_name} validates required inputs."""
        # TODO: Implement validation test
        pass
'''


def generate_conftest(topic: str, skill_name: str) -> str:
    """Generate conftest.py with shared fixtures."""
    return f'''"""
Pytest fixtures for {topic}-{skill_name} tests.
"""

import pytest
from unittest.mock import MagicMock


@pytest.fixture
def mock_client():
    """Create a mock API client."""
    client = MagicMock()
    return client


@pytest.fixture
def sample_{skill_name}():
    """Sample {skill_name} data for testing."""
    return {{
        'id': '123',
        'name': 'Test {skill_name.title()}',
        'status': 'active'
    }}


@pytest.fixture
def sample_{skill_name}_list(sample_{skill_name}):
    """Sample list of {skill_name} for testing."""
    return [sample_{skill_name}]
'''


def add_skill(
    project_dir: str,
    skill_name: str,
    description: str,
    resource: str = None,
    scripts: list = None,
    with_tests: bool = True,
    dry_run: bool = False
) -> dict:
    """
    Add a new skill to an existing project.

    Returns dict with created files.
    """
    project_path = Path(project_dir).expanduser().resolve()

    # Detect project
    project = detect_project(str(project_path))
    if not project:
        raise ValueError(f"No Assistant Skills project found at: {project_path}")

    topic = project['topic_prefix']
    if not topic:
        raise ValueError("Could not detect topic prefix. Is this a valid project?")

    # Default resource to skill name
    if not resource:
        resource = skill_name

    # Default scripts
    if not scripts:
        scripts = SCRIPT_PRESETS['crud']

    # Skill directory
    skills_dir = project_path / '.claude' / 'skills'
    skill_dir = skills_dir / f'{topic}-{skill_name}'

    if skill_dir.exists() and not dry_run:
        raise ValueError(f"Skill already exists: {skill_dir}")

    result = {
        'skill_dir': str(skill_dir),
        'files': []
    }

    # Create directories
    dirs = [
        skill_dir,
        skill_dir / 'scripts',
        skill_dir / 'tests',
        skill_dir / 'tests' / 'live_integration',
        skill_dir / 'docs'
    ]

    for d in dirs:
        if not dry_run:
            d.mkdir(parents=True, exist_ok=True)

    # Create SKILL.md
    skill_md_path = skill_dir / 'SKILL.md'
    skill_md_content = generate_skill_md(topic, skill_name, description, scripts)
    result['files'].append('SKILL.md')
    if not dry_run:
        skill_md_path.write_text(skill_md_content)

    # Create scripts
    scripts_init = skill_dir / 'scripts' / '__init__.py'
    result['files'].append('scripts/__init__.py')
    if not dry_run:
        scripts_init.write_text(f'"""{skill_name.title()} scripts."""\n')

    for script in scripts:
        script_path = skill_dir / 'scripts' / f'{script}_{skill_name}.py'
        script_content = generate_script_template(topic, skill_name, script)
        result['files'].append(f'scripts/{script}_{skill_name}.py')
        if not dry_run:
            script_path.write_text(script_content)
            script_path.chmod(0o755)

    # Create tests
    if with_tests:
        tests_init = skill_dir / 'tests' / '__init__.py'
        result['files'].append('tests/__init__.py')
        if not dry_run:
            tests_init.write_text(f'"""{skill_name.title()} tests."""\n')

        conftest_path = skill_dir / 'tests' / 'conftest.py'
        conftest_content = generate_conftest(topic, skill_name)
        result['files'].append('tests/conftest.py')
        if not dry_run:
            conftest_path.write_text(conftest_content)

        for script in scripts:
            test_path = skill_dir / 'tests' / f'test_{script}_{skill_name}.py'
            test_content = generate_test_template(topic, skill_name, script)
            result['files'].append(f'tests/test_{script}_{skill_name}.py')
            if not dry_run:
                test_path.write_text(test_content)

        # Live integration placeholder
        live_init = skill_dir / 'tests' / 'live_integration' / '__init__.py'
        result['files'].append('tests/live_integration/__init__.py')
        if not dry_run:
            live_init.write_text('"""Live integration tests."""\n')

    return result


def interactive_mode(project_dir: str = '.'):
    """Run interactive wizard to add a skill."""
    print("\n" + "=" * 60)
    print("  Add Skill Wizard")
    print("=" * 60 + "\n")

    # Detect project
    project = detect_project(project_dir)
    if not project:
        print_error(f"No Assistant Skills project found in: {project_dir}")
        alt_path = input("Enter project path (or press Enter to cancel): ").strip()
        if not alt_path:
            return None
        project = detect_project(alt_path)
        if not project:
            print_error(f"No project found at: {alt_path}")
            return None
        project_dir = alt_path

    topic = project['topic_prefix']
    print_info(f"Detected project: {project['name']}")
    print_info(f"Topic prefix: {topic}")
    print_info(f"Existing skills: {', '.join(project['skills']) if project['skills'] else '(none)'}")
    print()

    # Skill details
    print("Step 1: Skill Details\n")

    name = input("Skill name (without prefix, e.g., 'search'): ").strip()
    name = validate_name(name, "skill name", allow_dashes=False)

    description = input("One-line description: ").strip()
    description = validate_required(description, "description")

    resource = input(f"Primary API resource [{name}]: ").strip()
    if not resource:
        resource = name

    # Scripts
    print("\nStep 2: Scripts\n")
    print("Presets: crud (list/get/create/update/delete), list-get, all")
    print("Or enter comma-separated script names")

    scripts_input = input("Scripts [crud]: ").strip().lower()
    if not scripts_input:
        scripts_input = 'crud'

    if scripts_input in SCRIPT_PRESETS:
        scripts = SCRIPT_PRESETS[scripts_input]
    else:
        scripts = validate_list(scripts_input, "scripts", min_items=1)

    # Confirmation
    print("\n" + "-" * 60)
    print("Summary:")
    print("-" * 60)
    print(f"  Skill:       {topic}-{name}")
    print(f"  Description: {description}")
    print(f"  Resource:    {resource}")
    print(f"  Scripts:     {', '.join(scripts)}")
    print("-" * 60)

    confirm = input("\nProceed? [Y/n]: ").strip().lower()
    if confirm and confirm != 'y':
        print("Cancelled.")
        return None

    return {
        'project_dir': project_dir,
        'skill_name': name,
        'description': description,
        'resource': resource,
        'scripts': scripts
    }


def main():
    parser = argparse.ArgumentParser(
        description='Add a new skill to an Assistant Skills project',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Interactive mode
  python add_skill.py

  # With options
  python add_skill.py --name "search" --description "Search operations"

  # CRUD preset
  python add_skill.py --name "users" --description "User management" --scripts crud

  # Custom scripts
  python add_skill.py --name "reports" --scripts "generate,schedule,export"
'''
    )

    parser.add_argument('--name', '-n', help='Skill name (without topic prefix)')
    parser.add_argument('--description', '-d', help='One-line description')
    parser.add_argument('--resource', '-r', help='Primary API resource name')
    parser.add_argument('--scripts', '-s',
                        help='Script names: crud, list-get, all, or comma-separated')
    parser.add_argument('--project-dir', '-p', default='.',
                        help='Project directory (default: current)')
    parser.add_argument('--no-tests', action='store_true',
                        help='Skip generating test files')
    parser.add_argument('--dry-run', action='store_true',
                        help='Preview without creating files')

    args = parser.parse_args()

    try:
        # Interactive mode if no name provided
        if not args.name:
            config = interactive_mode(args.project_dir)
            if not config:
                sys.exit(0)
        else:
            # Parse scripts
            scripts = None
            if args.scripts:
                if args.scripts in SCRIPT_PRESETS:
                    scripts = SCRIPT_PRESETS[args.scripts]
                else:
                    scripts = [s.strip() for s in args.scripts.split(',')]

            config = {
                'project_dir': args.project_dir,
                'skill_name': validate_name(args.name, "skill name"),
                'description': validate_required(args.description, "description"),
                'resource': args.resource,
                'scripts': scripts
            }

        # Add skill
        if args.dry_run:
            print_info("DRY RUN - No files will be created\n")

        result = add_skill(
            project_dir=config['project_dir'],
            skill_name=config['skill_name'],
            description=config['description'],
            resource=config.get('resource'),
            scripts=config.get('scripts'),
            with_tests=not args.no_tests,
            dry_run=args.dry_run
        )

        print_success(f"Created skill at: {result['skill_dir']}")
        print(f"\nFiles created: {len(result['files'])}")

        if args.dry_run:
            print("\nFiles that would be created:")
            for f in result['files']:
                print(f"  {f}")

        # TDD guidance
        print("\n" + "=" * 60)
        print("TDD Workflow:")
        print("=" * 60)
        print("1. Write failing tests in tests/")
        print("2. Commit: test(skill): add failing tests for X")
        print("3. Implement scripts to pass tests")
        print("4. Commit: feat(skill): implement X (N/N tests passing)")
        print("5. Update router skill with new routing")

    except ValidationError as e:
        print_error(str(e))
        sys.exit(1)
    except Exception as e:
        print_error(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
