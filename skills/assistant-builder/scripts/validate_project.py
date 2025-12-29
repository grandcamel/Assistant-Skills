#!/usr/bin/env python3
"""
Validate project structure against Assistant Skills patterns.

Checks that a project follows the expected directory structure,
file naming conventions, and best practices.

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
        if 'when_to_use:' not in content:
            issues.append(('warning', 'SKILL.md frontmatter missing "when_to_use"'))

    # Check for key sections
    if '## What This Skill Does' not in content and '## Quick Start' not in content:
        issues.append(('warning', 'SKILL.md missing standard sections'))

    return issues


def validate_scripts(skill_path: Path) -> list:
    """Validate script files in a skill."""
    issues = []
    scripts_dir = skill_path / 'scripts'

    if not scripts_dir.exists():
        issues.append(('warning', 'Missing scripts directory'))
        return issues

    scripts = list(scripts_dir.glob('*.py'))
    scripts = [s for s in scripts if s.name != '__init__.py']

    if not scripts:
        issues.append(('warning', 'No scripts found'))
        return issues

    for script in scripts:
        content = script.read_text()

        # Check for shebang
        if not content.startswith('#!/usr/bin/env python'):
            issues.append(('warning', f'{script.name}: Missing shebang'))

        # Check for argparse
        if 'argparse' not in content:
            issues.append(('warning', f'{script.name}: Missing argparse (no --help support)'))

        # Check for --profile support
        if '--profile' not in content and "'--profile'" not in content:
            issues.append(('info', f'{script.name}: Missing --profile option'))

        # Check for shared lib imports
        if 'sys.path.insert' not in content:
            issues.append(('info', f'{script.name}: Not using shared library path pattern'))

    return issues


def validate_tests(skill_path: Path) -> list:
    """Validate test files in a skill."""
    issues = []
    tests_dir = skill_path / 'tests'

    if not tests_dir.exists():
        issues.append(('warning', 'Missing tests directory'))
        return issues

    test_files = list(tests_dir.glob('test_*.py'))

    if not test_files:
        issues.append(('warning', 'No test files found'))

    # Check for conftest.py
    if not (tests_dir / 'conftest.py').exists():
        issues.append(('info', 'Missing conftest.py (shared fixtures)'))

    return issues


def run_validation(project_path: str, strict: bool = False) -> dict:
    """Run full validation on a project."""
    path = Path(project_path).expanduser().resolve()

    result = {
        'path': str(path),
        'valid': True,
        'errors': [],
        'warnings': [],
        'info': [],
        'skills': {}
    }

    # Basic structure validation
    structure = validate_structure(str(path))

    result['errors'].extend(structure['errors'])
    result['warnings'].extend(structure['warnings'])

    if structure['errors']:
        result['valid'] = False

    # Validate each skill
    project = detect_project(str(path))
    if project:
        skills_dir = path / '.claude' / 'skills'

        for skill_dir in skills_dir.iterdir():
            if skill_dir.is_dir() and skill_dir.name != 'shared':
                skill_issues = {
                    'errors': [],
                    'warnings': [],
                    'infos': []
                }

                # Validate SKILL.md
                for level, msg in validate_skill_md(skill_dir):
                    skill_issues[level + 's'].append(msg)

                # Validate scripts
                for level, msg in validate_scripts(skill_dir):
                    skill_issues[level + 's'].append(msg)

                # Validate tests
                for level, msg in validate_tests(skill_dir):
                    skill_issues[level + 's'].append(msg)

                result['skills'][skill_dir.name] = skill_issues

                if skill_issues['errors']:
                    result['valid'] = False

    # In strict mode, warnings also fail
    if strict and result['warnings']:
        result['valid'] = False

    return result


def print_validation_result(result: dict, format_type: str = 'text'):
    """Print validation results."""
    if format_type == 'json':
        print(format_json(result))
        return

    print_header(f"Validation: {result['path']}")
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
            print_error(f"  {err}")

    # Warnings
    if result['warnings']:
        print(f"\nWarnings ({len(result['warnings'])}):")
        for warn in result['warnings']:
            print_warning(f"  {warn}")

    # Info
    if result['info']:
        print(f"\nInfo ({len(result['info'])}):")
        for info in result['info']:
            print_info(f"  {info}")

    # Per-skill results
    if result['skills']:
        print("\nSkill Validation:")
        print("-" * 40)

        for skill_name, issues in result['skills'].items():
            total_issues = len(issues['errors']) + len(issues['warnings'])

            if total_issues == 0:
                print_success(f"  {skill_name}")
            else:
                status = "errors" if issues['errors'] else "warnings"
                print(f"  {skill_name} ({total_issues} {status})")

                for err in issues['errors']:
                    print_error(f"    {err}")
                for warn in issues['warnings']:
                    print_warning(f"    {warn}")

    # Stats
    path = Path(result['path'])
    if path.exists():
        stats = get_project_stats(str(path))
        print("\nProject Statistics:")
        print(f"  Skills: {stats['skills']}")
        print(f"  Scripts: {stats['scripts']}")
        print(f"  Tests: {stats['tests']}")
        print(f"  Docs: {stats['docs']}")


def main():
    parser = argparse.ArgumentParser(
        description='Validate project structure against patterns',
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
