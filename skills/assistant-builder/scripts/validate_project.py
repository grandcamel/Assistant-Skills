#!/usr/bin/env python3
"""
Validate project structure against Assistant Skills production patterns.

Checks that a project follows the expected directory structure, file naming
conventions, and best practices based on production implementations.

Usage:
    python validate_project.py /path/to/project

Examples:
    # Validate current directory
    python validate_project.py .

    # Validate with strict mode (warnings as errors)
    python validate_project.py ~/projects/MySkills --strict

    # Output as JSON
    python validate_project.py . --format json
"""

import argparse
import json
import sys
from pathlib import Path

from assistant_skills_lib import (
    detect_project, validate_structure, list_skills, get_project_stats,
    print_success, print_error, print_warning, print_info,
    print_header, format_json, format_table
)


def detect_project_type(project_path: Path) -> dict:
    """Detect project type from structure."""
    result = {
        'type': 'unknown',
        'structure': 'unknown',
        'topic': None,
        'version': None
    }

    # Check for new structure (.claude-plugin/)
    if (project_path / '.claude-plugin' / 'plugin.json').exists():
        result['structure'] = 'new'
        try:
            plugin = json.loads((project_path / '.claude-plugin' / 'plugin.json').read_text())
            result['name'] = plugin.get('name')
            result['version'] = plugin.get('version')
        except Exception:
            pass

    # Check for old structure (.claude/skills/)
    elif (project_path / '.claude' / 'skills').exists():
        result['structure'] = 'old'

    # Determine project type
    lib_dirs = list(project_path.glob('*-assistant-skills-lib'))
    if lib_dirs:
        result['type'] = 'custom-library'
    elif result['structure'] != 'unknown':
        result['type'] = 'cli-wrapper'

    # Detect topic
    skills_dir = project_path / 'skills'
    if not skills_dir.exists():
        skills_dir = project_path / '.claude' / 'skills'

    if skills_dir.exists():
        for skill_dir in skills_dir.iterdir():
            if skill_dir.is_dir() and skill_dir.name.endswith('-assistant'):
                result['topic'] = skill_dir.name.replace('-assistant', '')
                break

    # Check VERSION file
    version_file = project_path / 'VERSION'
    if version_file.exists():
        result['version'] = version_file.read_text().strip()

    return result


def validate_plugin_structure(project_path: Path) -> list:
    """Validate .claude-plugin/ structure."""
    issues = []
    plugin_dir = project_path / '.claude-plugin'

    if not plugin_dir.exists():
        # Check for old structure
        if (project_path / '.claude' / 'skills').exists():
            issues.append(('info', 'Using old structure (.claude/skills/) - consider migrating to .claude-plugin/'))
        else:
            issues.append(('error', 'Missing .claude-plugin/ directory'))
        return issues

    # Check plugin.json
    plugin_json = plugin_dir / 'plugin.json'
    if not plugin_json.exists():
        issues.append(('error', 'Missing .claude-plugin/plugin.json'))
    else:
        try:
            plugin = json.loads(plugin_json.read_text())
            if 'name' not in plugin:
                issues.append(('warning', 'plugin.json missing "name" field'))
            if 'version' not in plugin:
                issues.append(('warning', 'plugin.json missing "version" field'))
            if 'skills' not in plugin:
                issues.append(('warning', 'plugin.json missing "skills" field'))
        except json.JSONDecodeError as e:
            issues.append(('error', f'plugin.json is invalid JSON: {e}'))

    # Check marketplace.json
    marketplace_json = plugin_dir / 'marketplace.json'
    if not marketplace_json.exists():
        issues.append(('info', 'Missing .claude-plugin/marketplace.json'))

    # Check commands directory
    commands_dir = plugin_dir / 'commands'
    if not commands_dir.exists():
        issues.append(('info', 'Missing .claude-plugin/commands/ directory'))
    else:
        setup_cmds = list(commands_dir.glob('*-setup.md'))
        if not setup_cmds:
            issues.append(('info', 'Missing setup command (e.g., topic-assistant-setup.md)'))

    return issues


def validate_version_management(project_path: Path) -> list:
    """Validate VERSION file and version sync."""
    issues = []

    version_file = project_path / 'VERSION'
    if not version_file.exists():
        issues.append(('warning', 'Missing VERSION file - add for single source of truth'))
        return issues

    version = version_file.read_text().strip()

    # Check version format
    import re
    if not re.match(r'^\d+\.\d+\.\d+', version):
        issues.append(('warning', f'VERSION format should be semver (got: {version})'))

    # Check sync with plugin.json
    plugin_json = project_path / '.claude-plugin' / 'plugin.json'
    if plugin_json.exists():
        try:
            plugin = json.loads(plugin_json.read_text())
            plugin_version = plugin.get('version')
            if plugin_version and plugin_version != version:
                issues.append(('warning', f'VERSION ({version}) != plugin.json ({plugin_version})'))
        except Exception:
            pass

    return issues


def validate_testing_infrastructure(project_path: Path) -> list:
    """Validate root conftest.py and pytest.ini."""
    issues = []

    # Check root conftest.py
    conftest = project_path / 'conftest.py'
    if not conftest.exists():
        issues.append(('warning', 'Missing root conftest.py - add for shared fixtures'))

    # Check pytest.ini
    pytest_ini = project_path / 'pytest.ini'
    if not pytest_ini.exists():
        issues.append(('warning', 'Missing pytest.ini - add for test configuration'))
    else:
        content = pytest_ini.read_text()
        if 'markers' not in content:
            issues.append(('info', 'pytest.ini missing markers section'))
        if 'testpaths' not in content:
            issues.append(('info', 'pytest.ini missing testpaths setting'))

    return issues


def validate_shared_documentation(project_path: Path) -> list:
    """Validate shared documentation."""
    issues = []

    # Check skills/shared/docs
    shared_docs = project_path / 'skills' / 'shared' / 'docs'
    if not shared_docs.exists():
        shared_docs = project_path / '.claude' / 'skills' / 'shared' / 'docs'

    if not shared_docs.exists():
        issues.append(('info', 'Missing skills/shared/docs/ directory'))
        return issues

    # Check for standard documentation
    required_docs = ['SAFEGUARDS.md', 'QUICK_REFERENCE.md']
    optional_docs = ['DECISION_TREE.md', 'ERROR_HANDLING.md']

    for doc in required_docs:
        if not (shared_docs / doc).exists():
            issues.append(('info', f'Missing {doc} in shared docs'))

    return issues


def validate_hub_router_skill(project_path: Path, topic: str) -> list:
    """Validate hub/router skill exists and is properly configured."""
    issues = []

    if not topic:
        return issues

    # Check for hub skill
    hub_skill = project_path / 'skills' / f'{topic}-assistant'
    if not hub_skill.exists():
        hub_skill = project_path / '.claude' / 'skills' / f'{topic}-assistant'

    if not hub_skill.exists():
        issues.append(('warning', f'Missing hub/router skill: {topic}-assistant'))
        return issues

    # Check SKILL.md
    skill_md = hub_skill / 'SKILL.md'
    if not skill_md.exists():
        issues.append(('error', f'{topic}-assistant missing SKILL.md'))
        return issues

    content = skill_md.read_text()

    # Check for routing content
    if 'Routing' not in content and 'routing' not in content:
        issues.append(('info', f'{topic}-assistant SKILL.md missing routing rules'))

    # Check for risk levels
    if '⚠️' not in content and 'Risk' not in content:
        issues.append(('info', f'{topic}-assistant SKILL.md missing risk level indicators'))

    # Check for decision tree link
    if 'DECISION_TREE' not in content:
        issues.append(('info', f'{topic}-assistant missing link to DECISION_TREE.md'))

    return issues


def validate_skill_md(skill_path: Path) -> list:
    """Validate SKILL.md file format."""
    issues = []
    skill_md = skill_path / 'SKILL.md'

    if not skill_md.exists():
        issues.append(('error', 'Missing SKILL.md'))
        return issues

    content = skill_md.read_text()

    # Check for frontmatter
    if not content.startswith('---'):
        issues.append(('warning', 'SKILL.md missing YAML frontmatter'))
    else:
        # Check required frontmatter fields
        if 'name:' not in content:
            issues.append(('warning', 'SKILL.md frontmatter missing "name"'))
        if 'description:' not in content:
            issues.append(('warning', 'SKILL.md frontmatter missing "description"'))

    # Check for risk levels
    if '⚠️' in content or 'Risk' in content:
        pass  # Has risk levels
    else:
        issues.append(('info', 'SKILL.md missing risk level indicators'))

    # Check for Quick Reference section
    if '## Quick Reference' not in content:
        issues.append(('info', 'SKILL.md missing "Quick Reference" section'))

    return issues


def validate_no_embedded_scripts(skill_path: Path) -> list:
    """Check that skills don't have embedded scripts (new pattern)."""
    issues = []
    scripts_dir = skill_path / 'scripts'

    if scripts_dir.exists():
        py_files = list(scripts_dir.glob('*.py'))
        # Exclude __init__.py
        py_files = [f for f in py_files if f.name != '__init__.py']

        if py_files:
            issues.append(('info', f'Found {len(py_files)} scripts in skill directory - consider moving to library'))

    return issues


def run_validation(project_path: str, strict: bool = False) -> dict:
    """Run full validation on a project."""
    path = Path(project_path).expanduser().resolve()

    result = {
        'path': str(path),
        'valid': True,
        'project_type': None,
        'errors': [],
        'warnings': [],
        'info': [],
        'skills': {},
        'stats': {}
    }

    # Detect project type
    project_info = detect_project_type(path)
    result['project_type'] = project_info

    # Validate plugin structure
    for level, msg in validate_plugin_structure(path):
        if level == 'error':
            result['errors'].append(msg)
            result['valid'] = False
        elif level == 'warning':
            result['warnings'].append(msg)
        else:
            result['info'].append(msg)

    # Validate version management
    for level, msg in validate_version_management(path):
        if level == 'error':
            result['errors'].append(msg)
            result['valid'] = False
        elif level == 'warning':
            result['warnings'].append(msg)
        else:
            result['info'].append(msg)

    # Validate testing infrastructure
    for level, msg in validate_testing_infrastructure(path):
        if level == 'error':
            result['errors'].append(msg)
            result['valid'] = False
        elif level == 'warning':
            result['warnings'].append(msg)
        else:
            result['info'].append(msg)

    # Validate shared documentation
    for level, msg in validate_shared_documentation(path):
        if level == 'error':
            result['errors'].append(msg)
            result['valid'] = False
        elif level == 'warning':
            result['warnings'].append(msg)
        else:
            result['info'].append(msg)

    # Validate hub/router skill
    topic = project_info.get('topic')
    for level, msg in validate_hub_router_skill(path, topic):
        if level == 'error':
            result['errors'].append(msg)
            result['valid'] = False
        elif level == 'warning':
            result['warnings'].append(msg)
        else:
            result['info'].append(msg)

    # Validate each skill
    skills_dir = path / 'skills'
    if not skills_dir.exists():
        skills_dir = path / '.claude' / 'skills'

    # Map level names to result keys
    level_map = {'error': 'errors', 'warning': 'warnings', 'info': 'info'}

    if skills_dir.exists():
        for skill_dir in skills_dir.iterdir():
            if skill_dir.is_dir() and skill_dir.name != 'shared' and not skill_dir.name.startswith('.'):
                skill_issues = {
                    'errors': [],
                    'warnings': [],
                    'info': []
                }

                # Validate SKILL.md
                for level, msg in validate_skill_md(skill_dir):
                    skill_issues[level_map[level]].append(msg)

                # Check for embedded scripts
                for level, msg in validate_no_embedded_scripts(skill_dir):
                    skill_issues[level_map[level]].append(msg)

                result['skills'][skill_dir.name] = skill_issues

                if skill_issues['errors']:
                    result['valid'] = False

    # Calculate stats
    result['stats'] = calculate_stats(path, result)

    # In strict mode, warnings also fail
    if strict and result['warnings']:
        result['valid'] = False

    return result


def calculate_stats(project_path: Path, result: dict) -> dict:
    """Calculate project statistics."""
    stats = {
        'skills': len(result['skills']),
        'commands': 0,
        'shared_docs': 0,
        'has_version': (project_path / 'VERSION').exists(),
        'has_conftest': (project_path / 'conftest.py').exists(),
        'has_pytest_ini': (project_path / 'pytest.ini').exists(),
        'project_type': result['project_type'].get('type', 'unknown'),
        'structure': result['project_type'].get('structure', 'unknown'),
    }

    # Count commands
    commands_dir = project_path / '.claude-plugin' / 'commands'
    if commands_dir.exists():
        stats['commands'] = len(list(commands_dir.glob('*.md')))

    # Count shared docs
    shared_docs = project_path / 'skills' / 'shared' / 'docs'
    if not shared_docs.exists():
        shared_docs = project_path / '.claude' / 'skills' / 'shared' / 'docs'
    if shared_docs.exists():
        stats['shared_docs'] = len(list(shared_docs.glob('*.md')))

    return stats


def print_validation_result(result: dict, format_type: str = 'text'):
    """Print validation results."""
    if format_type == 'json':
        print(format_json(result))
        return

    print_header(f"Validation: {result['path']}")
    print()

    # Project info
    project_type = result['project_type']
    print(f"Project Type: {project_type.get('type', 'unknown')}")
    print(f"Structure: {project_type.get('structure', 'unknown')}")
    if project_type.get('topic'):
        print(f"Topic: {project_type.get('topic')}")
    if project_type.get('version'):
        print(f"Version: {project_type.get('version')}")
    print()

    # Overall status
    if result['valid']:
        print_success("Project structure is valid!")
    else:
        print_error("Project has validation errors")

    # Errors
    if result['errors']:
        print(f"\nErrors ({len(result['errors'])}):")
        for err in result['errors']:
            print_error(f"  ✗ {err}")

    # Warnings
    if result['warnings']:
        print(f"\nWarnings ({len(result['warnings'])}):")
        for warn in result['warnings']:
            print_warning(f"  ⚠ {warn}")

    # Info
    if result['info']:
        print(f"\nSuggestions ({len(result['info'])}):")
        for info in result['info']:
            print_info(f"  ℹ {info}")

    # Per-skill results
    if result['skills']:
        print("\nSkill Validation:")
        print("-" * 50)

        for skill_name, issues in result['skills'].items():
            total_issues = len(issues['errors']) + len(issues['warnings'])

            if total_issues == 0:
                print_success(f"  ✓ {skill_name}")
            else:
                status = "errors" if issues['errors'] else "warnings"
                print(f"  {skill_name} ({total_issues} {status})")

                for err in issues['errors']:
                    print_error(f"      ✗ {err}")
                for warn in issues['warnings']:
                    print_warning(f"      ⚠ {warn}")

    # Stats
    stats = result['stats']
    print("\nProject Statistics:")
    print(f"  Skills: {stats['skills']}")
    print(f"  Commands: {stats['commands']}")
    print(f"  Shared Docs: {stats['shared_docs']}")
    print(f"  VERSION file: {'✓' if stats['has_version'] else '✗'}")
    print(f"  Root conftest.py: {'✓' if stats['has_conftest'] else '✗'}")
    print(f"  pytest.ini: {'✓' if stats['has_pytest_ini'] else '✗'}")


def main():
    parser = argparse.ArgumentParser(
        description='Validate project structure against production patterns',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Validate current directory
  python validate_project.py .

  # Strict mode
  python validate_project.py ~/MySkills --strict

  # JSON output
  python validate_project.py . --format json
'''
    )

    parser.add_argument('project_dir', nargs='?', default='.',
                        help='Project directory to validate')
    parser.add_argument('--strict', '-s', action='store_true',
                        help='Treat warnings as errors')
    parser.add_argument('--format', '-f', choices=['text', 'json'],
                        default='text', help='Output format')

    args = parser.parse_args()

    result = run_validation(args.project_dir, args.strict)
    print_validation_result(result, args.format)

    # Exit code
    sys.exit(0 if result['valid'] else 1)


if __name__ == '__main__':
    main()
