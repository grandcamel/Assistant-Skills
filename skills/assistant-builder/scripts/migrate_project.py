#!/usr/bin/env python3
"""
Migrate existing Assistant Skills projects to the new structure.

Transforms projects from the old .claude/skills/ structure to the new
.claude-plugin/ + skills/ structure following production patterns.

Usage:
    python migrate_project.py /path/to/old/project

Examples:
    # Migrate in place (creates backup)
    python migrate_project.py ~/projects/MySkills

    # Migrate to new location
    python migrate_project.py ~/projects/MySkills --output ~/projects/MySkills-New

    # Dry run to preview changes
    python migrate_project.py ~/projects/MySkills --dry-run

    # Generate migration report only
    python migrate_project.py ~/projects/MySkills --report-only
"""

import argparse
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

from assistant_skills_lib import (
    validate_required, validate_path,
    InputValidationError as ValidationError,
    print_success, print_error, print_info, print_warning, print_header
)


def analyze_project(project_path: Path) -> dict:
    """Analyze existing project structure."""
    analysis = {
        'path': str(project_path),
        'structure': 'unknown',
        'topic': None,
        'skills': [],
        'has_shared_lib': False,
        'has_scripts': False,
        'scripts': [],
        'has_tests': False,
        'tests': [],
        'files_to_migrate': [],
        'warnings': [],
        'errors': []
    }

    # Check for old structure
    old_skills_dir = project_path / '.claude' / 'skills'
    new_skills_dir = project_path / 'skills'

    if old_skills_dir.exists():
        analysis['structure'] = 'old'
        skills_dir = old_skills_dir
    elif new_skills_dir.exists():
        analysis['structure'] = 'new'
        skills_dir = new_skills_dir
    else:
        analysis['errors'].append('No skills directory found')
        return analysis

    # Detect topic from assistant skill
    for skill_dir in skills_dir.iterdir():
        if skill_dir.is_dir() and skill_dir.name.endswith('-assistant'):
            analysis['topic'] = skill_dir.name.replace('-assistant', '')
            break

    # Analyze skills
    for skill_dir in skills_dir.iterdir():
        if skill_dir.is_dir() and skill_dir.name != 'shared':
            skill_info = {
                'name': skill_dir.name,
                'has_skill_md': (skill_dir / 'SKILL.md').exists(),
                'has_scripts': (skill_dir / 'scripts').exists(),
                'scripts': [],
                'has_tests': (skill_dir / 'tests').exists(),
                'tests': []
            }

            # Count scripts
            if skill_info['has_scripts']:
                scripts_dir = skill_dir / 'scripts'
                py_files = [f.name for f in scripts_dir.glob('*.py') if f.name != '__init__.py']
                skill_info['scripts'] = py_files
                analysis['has_scripts'] = True
                analysis['scripts'].extend(py_files)

            # Count tests
            if skill_info['has_tests']:
                tests_dir = skill_dir / 'tests'
                test_files = [f.name for f in tests_dir.glob('test_*.py')]
                skill_info['tests'] = test_files
                analysis['has_tests'] = True
                analysis['tests'].extend(test_files)

            analysis['skills'].append(skill_info)

    # Check for shared library
    shared_dir = skills_dir / 'shared'
    if shared_dir.exists():
        shared_lib = shared_dir / 'scripts' / 'lib'
        if shared_lib.exists():
            analysis['has_shared_lib'] = True

    # Check for existing new structure elements
    if (project_path / '.claude-plugin').exists():
        analysis['warnings'].append('Project already has .claude-plugin/ directory')

    if (project_path / 'VERSION').exists():
        analysis['warnings'].append('Project already has VERSION file')

    return analysis


def generate_migration_plan(analysis: dict) -> dict:
    """Generate a migration plan based on analysis."""
    plan = {
        'create_directories': [],
        'create_files': [],
        'move_files': [],
        'update_files': [],
        'delete_files': [],
        'manual_steps': []
    }

    topic = analysis['topic']
    if not topic:
        return plan

    # Directories to create
    plan['create_directories'] = [
        '.claude-plugin',
        '.claude-plugin/commands',
        'skills',
        f'skills/{topic}-assistant',
        f'skills/{topic}-assistant/docs',
        'skills/shared',
        'skills/shared/docs',
        'skills/shared/config',
    ]

    # Files to create
    plan['create_files'] = [
        ('VERSION', '1.0.0'),
        ('.claude-plugin/plugin.json', None),  # Will be generated
        ('.claude-plugin/marketplace.json', None),
        (f'.claude-plugin/commands/{topic}-assistant-setup.md', None),
        ('.claude-plugin/commands/browse-skills.md', None),
        ('.claude-plugin/commands/skill-info.md', None),
        ('skills/shared/docs/SAFEGUARDS.md', None),
        ('skills/shared/docs/QUICK_REFERENCE.md', None),
        ('conftest.py', None),
        ('pytest.ini', None),
    ]

    # Files/directories to move (if old structure)
    if analysis['structure'] == 'old':
        for skill in analysis['skills']:
            old_path = f".claude/skills/{skill['name']}"
            new_path = f"skills/{skill['name']}"
            plan['move_files'].append((old_path, new_path))

        # Move shared
        plan['move_files'].append(('.claude/skills/shared', 'skills/shared'))

    # Manual steps
    if analysis['has_scripts']:
        plan['manual_steps'].append(
            f"Extract {len(analysis['scripts'])} scripts to a separate library package"
        )
        plan['manual_steps'].append(
            "Update SKILL.md files to reference CLI commands instead of scripts"
        )

    if analysis['has_tests']:
        plan['manual_steps'].append(
            f"Review and update {len(analysis['tests'])} test files for new structure"
        )

    return plan


def execute_migration(
    project_path: Path,
    output_path: Path,
    analysis: dict,
    plan: dict,
    dry_run: bool = False
) -> dict:
    """Execute the migration plan."""
    result = {
        'success': True,
        'created_directories': [],
        'created_files': [],
        'moved_files': [],
        'errors': [],
        'warnings': []
    }

    topic = analysis['topic']
    if not topic:
        result['success'] = False
        result['errors'].append('Could not detect topic prefix')
        return result

    # Create backup if migrating in place
    if project_path == output_path and not dry_run:
        backup_path = project_path.parent / f"{project_path.name}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        try:
            shutil.copytree(project_path, backup_path)
            result['backup_path'] = str(backup_path)
        except Exception as e:
            result['warnings'].append(f"Could not create backup: {e}")

    # Create output directory if different
    if project_path != output_path and not dry_run:
        if output_path.exists():
            result['success'] = False
            result['errors'].append(f"Output directory already exists: {output_path}")
            return result
        shutil.copytree(project_path, output_path)

    target_path = output_path

    # Create directories
    for dir_path in plan['create_directories']:
        full_path = target_path / dir_path
        if not full_path.exists():
            if not dry_run:
                full_path.mkdir(parents=True, exist_ok=True)
            result['created_directories'].append(dir_path)

    # Move files (for old structure)
    for old_path, new_path in plan['move_files']:
        old_full = target_path / old_path
        new_full = target_path / new_path

        if old_full.exists() and not new_full.exists():
            if not dry_run:
                shutil.move(str(old_full), str(new_full))
            result['moved_files'].append((old_path, new_path))

    # Create files
    for file_path, content in plan['create_files']:
        full_path = target_path / file_path

        if full_path.exists():
            result['warnings'].append(f"Skipping existing file: {file_path}")
            continue

        if content is None:
            # Generate content based on file type
            if file_path == '.claude-plugin/plugin.json':
                content = generate_plugin_json(topic, analysis)
            elif file_path == '.claude-plugin/marketplace.json':
                content = generate_marketplace_json(topic, analysis)
            elif file_path.endswith('-setup.md'):
                content = generate_setup_command(topic)
            elif file_path == '.claude-plugin/commands/browse-skills.md':
                content = generate_browse_skills(topic, analysis)
            elif file_path == '.claude-plugin/commands/skill-info.md':
                content = generate_skill_info(topic)
            elif file_path == 'skills/shared/docs/SAFEGUARDS.md':
                content = generate_safeguards(topic)
            elif file_path == 'skills/shared/docs/QUICK_REFERENCE.md':
                content = generate_quick_reference(topic)
            elif file_path == 'conftest.py':
                content = generate_conftest(topic)
            elif file_path == 'pytest.ini':
                content = generate_pytest_ini(topic)

        if content is not None:
            if not dry_run:
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.write_text(content)
            result['created_files'].append(file_path)

    # Clean up old structure if migrating in place
    if analysis['structure'] == 'old' and project_path == output_path:
        old_claude_dir = target_path / '.claude'
        if old_claude_dir.exists() and not (old_claude_dir / 'skills').exists():
            if not dry_run:
                # Only remove if empty or just has settings
                remaining = list(old_claude_dir.iterdir())
                if len(remaining) <= 1:  # settings.json
                    pass  # Keep for now

    return result


def generate_plugin_json(topic: str, analysis: dict) -> str:
    """Generate plugin.json content."""
    skills = [f"../skills/{s['name']}/SKILL.md" for s in analysis['skills']]

    plugin = {
        "name": f"{topic}-assistant-skills",
        "version": "1.0.0",
        "description": f"Claude Code skills for {topic.title()} automation",
        "skills": skills,
        "commands": ["./commands/*.md"]
    }

    return json.dumps(plugin, indent=2)


def generate_marketplace_json(topic: str, analysis: dict) -> str:
    """Generate marketplace.json content."""
    marketplace = {
        "name": f"{topic}-assistant-skills",
        "version": "1.0.0",
        "plugins": [{
            "name": f"{topic}-assistant-skills",
            "source": "./",
            "description": f"{topic.title()} automation skills for Claude Code"
        }]
    }

    return json.dumps(marketplace, indent=2)


def generate_setup_command(topic: str) -> str:
    """Generate setup command."""
    return f"""---
description: "Set up {topic.title()} Assistant Skills with credentials and configuration"
user_invocable: true
arguments:
  - name: profile
    description: "Configuration profile name"
    required: false
    default: "default"
---

# {topic.title()} Assistant Setup

Set up {topic.title()} Assistant Skills for Claude Code.

## Prerequisites

Configure your API credentials.

## Authentication

Set environment variables or use configuration file.

## Verification

Verify your setup is working.
"""


def generate_browse_skills(topic: str, analysis: dict) -> str:
    """Generate browse-skills command."""
    skills_table = ""
    for skill in analysis['skills']:
        skills_table += f"| {skill['name']} | {skill['name'].replace(topic + '-', '').title()} operations |\n"

    return f"""---
description: "Browse all available {topic.title()} skills"
user_invocable: true
---

# Browse {topic.title()} Skills

| Skill | Description |
|-------|-------------|
{skills_table}
"""


def generate_skill_info(topic: str) -> str:
    """Generate skill-info command."""
    return f"""---
description: "Get detailed information about a {topic.title()} skill"
user_invocable: true
arguments:
  - name: skill_name
    description: "Name of the skill"
    required: true
---

# Skill Information

Get detailed information about a specific {topic.title()} skill.
"""


def generate_safeguards(topic: str) -> str:
    """Generate SAFEGUARDS.md."""
    return f"""# Safeguards & Recovery Procedures

## Risk Level Matrix

| Risk | Symbol | Description | Safeguards |
|------|:------:|-------------|------------|
| Read-only | - | Safe operations | None |
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

## Recovery Procedures

Document your recovery procedures here.
"""


def generate_quick_reference(topic: str) -> str:
    """Generate QUICK_REFERENCE.md."""
    return f"""# Quick Reference

## Connection

Check your connection and authentication status.

## Common Operations

### Search & List

List and search for resources.

### CRUD Operations

Create, read, update, and delete resources.

## Output Formats

| Format | Flag | Use Case |
|--------|------|----------|
| Table | `--output table` | Human readable |
| JSON | `--output json` | Scripting |
| Text | `--output text` | Simple output |
"""


def generate_conftest(topic: str) -> str:
    """Generate root conftest.py."""
    return f'''"""Root test fixtures for {topic}-assistant-skills."""

import pytest
from pathlib import Path
from typing import Generator
import tempfile
import shutil


@pytest.fixture
def temp_path() -> Generator[Path, None, None]:
    """Create a temporary directory."""
    path = Path(tempfile.mkdtemp())
    yield path
    shutil.rmtree(path, ignore_errors=True)


@pytest.fixture
def temp_dir(temp_path: Path) -> str:
    """Create a temporary directory as string."""
    return str(temp_path)


@pytest.fixture
def sample_resource():
    """Sample resource data."""
    return {{
        "id": "RESOURCE-123",
        "name": "Test Resource",
        "status": "active",
    }}
'''


def generate_pytest_ini(topic: str) -> str:
    """Generate pytest.ini."""
    return f"""[pytest]
testpaths = skills tests
pythonpath = .
addopts = -v --tb=short --import-mode=importlib

markers =
    unit: Unit tests
    integration: Integration tests
    live: Live API tests
    slow: Slow tests
    destructive: Tests that modify state
    readonly: Read-only tests
"""


def print_analysis(analysis: dict):
    """Print analysis results."""
    print_header("Project Analysis")
    print()

    print(f"Path: {analysis['path']}")
    print(f"Structure: {analysis['structure']}")
    print(f"Topic: {analysis['topic'] or '(unknown)'}")
    print(f"Skills: {len(analysis['skills'])}")

    if analysis['skills']:
        print("\nSkills found:")
        for skill in analysis['skills']:
            scripts = f", {len(skill['scripts'])} scripts" if skill['scripts'] else ""
            tests = f", {len(skill['tests'])} tests" if skill['tests'] else ""
            print(f"  - {skill['name']}{scripts}{tests}")

    print(f"\nHas shared library: {'Yes' if analysis['has_shared_lib'] else 'No'}")
    print(f"Has embedded scripts: {'Yes' if analysis['has_scripts'] else 'No'}")
    print(f"Has tests: {'Yes' if analysis['has_tests'] else 'No'}")

    if analysis['warnings']:
        print("\nWarnings:")
        for warn in analysis['warnings']:
            print_warning(f"  {warn}")

    if analysis['errors']:
        print("\nErrors:")
        for err in analysis['errors']:
            print_error(f"  {err}")


def print_plan(plan: dict):
    """Print migration plan."""
    print_header("Migration Plan")
    print()

    if plan['create_directories']:
        print("Directories to create:")
        for d in plan['create_directories']:
            print(f"  + {d}/")

    if plan['move_files']:
        print("\nFiles/directories to move:")
        for old, new in plan['move_files']:
            print(f"  {old} → {new}")

    if plan['create_files']:
        print("\nFiles to create:")
        for f, _ in plan['create_files']:
            print(f"  + {f}")

    if plan['manual_steps']:
        print("\nManual steps required:")
        for i, step in enumerate(plan['manual_steps'], 1):
            print(f"  {i}. {step}")


def print_result(result: dict):
    """Print migration result."""
    print_header("Migration Result")
    print()

    if result['success']:
        print_success("Migration completed successfully!")
    else:
        print_error("Migration failed")

    if result.get('backup_path'):
        print(f"\nBackup created: {result['backup_path']}")

    if result['created_directories']:
        print(f"\nDirectories created: {len(result['created_directories'])}")

    if result['created_files']:
        print(f"Files created: {len(result['created_files'])}")

    if result['moved_files']:
        print(f"Files moved: {len(result['moved_files'])}")

    if result['warnings']:
        print("\nWarnings:")
        for warn in result['warnings']:
            print_warning(f"  {warn}")

    if result['errors']:
        print("\nErrors:")
        for err in result['errors']:
            print_error(f"  {err}")


def main():
    parser = argparse.ArgumentParser(
        description='Migrate Assistant Skills projects to new structure',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Migrate in place
  python migrate_project.py ~/projects/MySkills

  # Migrate to new location
  python migrate_project.py ~/projects/MySkills --output ~/projects/MySkills-New

  # Dry run
  python migrate_project.py ~/projects/MySkills --dry-run

  # Report only
  python migrate_project.py ~/projects/MySkills --report-only
'''
    )

    parser.add_argument('project_dir', help='Project directory to migrate')
    parser.add_argument('--output', '-o', help='Output directory (default: in-place)')
    parser.add_argument('--dry-run', '-d', action='store_true',
                        help='Preview without making changes')
    parser.add_argument('--report-only', '-r', action='store_true',
                        help='Generate analysis report only')

    args = parser.parse_args()

    try:
        project_path = Path(args.project_dir).expanduser().resolve()
        output_path = Path(args.output).expanduser().resolve() if args.output else project_path

        if not project_path.exists():
            print_error(f"Project not found: {project_path}")
            sys.exit(1)

        # Analyze
        print_info("Analyzing project...\n")
        analysis = analyze_project(project_path)
        print_analysis(analysis)

        if analysis['errors']:
            print_error("\nCannot proceed due to errors")
            sys.exit(1)

        if args.report_only:
            sys.exit(0)

        # Generate plan
        print()
        plan = generate_migration_plan(analysis)
        print_plan(plan)

        if args.dry_run:
            print_info("\nDRY RUN - No changes made")
            sys.exit(0)

        # Confirm
        print()
        if project_path == output_path:
            confirm = input("Proceed with in-place migration? [y/N]: ").strip().lower()
        else:
            confirm = input(f"Proceed with migration to {output_path}? [y/N]: ").strip().lower()

        if confirm != 'y':
            print("Cancelled.")
            sys.exit(0)

        # Execute
        print_info("\nExecuting migration...\n")
        result = execute_migration(project_path, output_path, analysis, plan)
        print_result(result)

        if plan['manual_steps']:
            print("\n" + "=" * 60)
            print("Manual Steps Required:")
            print("=" * 60)
            for i, step in enumerate(plan['manual_steps'], 1):
                print(f"{i}. {step}")

        print("\n" + "=" * 60)
        print("Next Steps:")
        print("=" * 60)
        print("1. Review generated files")
        print("2. Update SKILL.md files to reference CLI commands")
        print("3. Consider extracting scripts to a library package")
        print("4. Run validation: python validate_project.py .")

    except ValidationError as e:
        print_error(str(e))
        sys.exit(1)
    except Exception as e:
        print_error(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
