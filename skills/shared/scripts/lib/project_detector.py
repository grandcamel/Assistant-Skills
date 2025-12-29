"""
Project Detector for Assistant Builder

Detects and analyzes existing Assistant Skills project structures.

Usage:
    from project_detector import detect_project, list_skills, get_topic_prefix

    project = detect_project("/path/to/project")
    if project:
        skills = list_skills(project['path'])
        prefix = get_topic_prefix(project['path'])
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Any


def detect_project(path: str) -> Optional[Dict[str, Any]]:
    """
    Detect if a path contains an Assistant Skills project.

    Args:
        path: Path to check for project structure

    Returns:
        Dict with project info if detected, None otherwise:
            - path: Absolute path to project root
            - name: Project name (from directory or README)
            - topic_prefix: Detected topic prefix
            - skills: List of skill names
            - has_shared_lib: Whether shared library exists
            - has_settings: Whether settings.json exists
    """
    project_path = Path(path).expanduser().resolve()

    if not project_path.exists():
        return None

    # Look for .claude/skills directory
    claude_dir = project_path / '.claude'
    skills_dir = claude_dir / 'skills'

    if not skills_dir.exists():
        return None

    # This is likely an Assistant Skills project
    project_info = {
        'path': str(project_path),
        'name': project_path.name,
        'topic_prefix': None,
        'skills': [],
        'has_shared_lib': (skills_dir / 'shared').exists(),
        'has_settings': (claude_dir / 'settings.json').exists()
    }

    # Detect skills
    for item in skills_dir.iterdir():
        if item.is_dir() and item.name != 'shared':
            project_info['skills'].append(item.name)

    # Detect topic prefix from skill names
    if project_info['skills']:
        # Find common prefix (e.g., "jira-" from "jira-issue", "jira-search")
        first_skill = project_info['skills'][0]
        if '-' in first_skill:
            potential_prefix = first_skill.split('-')[0]
            # Verify other skills share this prefix
            if all(s.startswith(potential_prefix + '-') or s == potential_prefix + '-assistant'
                   for s in project_info['skills']):
                project_info['topic_prefix'] = potential_prefix

    # Try to get topic prefix from settings.json
    if not project_info['topic_prefix'] and project_info['has_settings']:
        settings_path = claude_dir / 'settings.json'
        try:
            settings = json.loads(settings_path.read_text())
            # Look for first key that's not a special key
            for key in settings.keys():
                if key not in ('$schema', 'permissions'):
                    project_info['topic_prefix'] = key.replace('-assistant', '')
                    break
        except (json.JSONDecodeError, IOError):
            pass

    return project_info


def list_skills(project_path: str) -> List[Dict[str, Any]]:
    """
    List all skills in a project with their details.

    Args:
        project_path: Path to project root

    Returns:
        List of skill info dicts:
            - name: Skill directory name
            - path: Absolute path to skill
            - has_skill_md: Whether SKILL.md exists
            - scripts: List of script files
            - has_tests: Whether tests directory exists
    """
    path = Path(project_path).expanduser().resolve()
    skills_dir = path / '.claude' / 'skills'

    if not skills_dir.exists():
        return []

    skills = []

    for item in sorted(skills_dir.iterdir()):
        if item.is_dir() and item.name != 'shared':
            skill_info = {
                'name': item.name,
                'path': str(item),
                'has_skill_md': (item / 'SKILL.md').exists(),
                'scripts': [],
                'has_tests': (item / 'tests').exists()
            }

            # List scripts
            scripts_dir = item / 'scripts'
            if scripts_dir.exists():
                skill_info['scripts'] = [
                    f.name for f in scripts_dir.glob('*.py')
                    if f.name != '__init__.py'
                ]

            skills.append(skill_info)

    return skills


def get_topic_prefix(project_path: str) -> Optional[str]:
    """
    Get the topic prefix for a project.

    Args:
        project_path: Path to project root

    Returns:
        Topic prefix string or None if not detected
    """
    project = detect_project(project_path)
    return project['topic_prefix'] if project else None


def get_shared_lib_modules(project_path: str) -> List[str]:
    """
    List modules in the shared library.

    Args:
        project_path: Path to project root

    Returns:
        List of module names (without .py extension)
    """
    path = Path(project_path).expanduser().resolve()
    lib_dir = path / '.claude' / 'skills' / 'shared' / 'scripts' / 'lib'

    if not lib_dir.exists():
        return []

    return [
        f.stem for f in lib_dir.glob('*.py')
        if f.name != '__init__.py'
    ]


def validate_structure(project_path: str) -> Dict[str, Any]:
    """
    Validate project structure against expected patterns.

    Args:
        project_path: Path to project root

    Returns:
        Dict with validation results:
            - valid: bool - Overall validity
            - errors: List of error messages
            - warnings: List of warning messages
            - structure: Dict of structure checks
    """
    path = Path(project_path).expanduser().resolve()

    errors = []
    warnings = []
    structure = {}

    # Check root files
    structure['has_readme'] = (path / 'README.md').exists()
    structure['has_claude_md'] = (path / 'CLAUDE.md').exists()
    structure['has_gitignore'] = (path / '.gitignore').exists()

    if not structure['has_readme']:
        warnings.append("Missing README.md")
    if not structure['has_claude_md']:
        warnings.append("Missing CLAUDE.md")
    if not structure['has_gitignore']:
        warnings.append("Missing .gitignore")

    # Check .claude structure
    claude_dir = path / '.claude'
    if not claude_dir.exists():
        errors.append("Missing .claude directory")
        return {'valid': False, 'errors': errors, 'warnings': warnings, 'structure': structure}

    structure['has_settings'] = (claude_dir / 'settings.json').exists()
    structure['has_skills_dir'] = (claude_dir / 'skills').exists()

    if not structure['has_settings']:
        errors.append("Missing .claude/settings.json")
    if not structure['has_skills_dir']:
        errors.append("Missing .claude/skills directory")

    # Check shared library
    shared_dir = claude_dir / 'skills' / 'shared'
    structure['has_shared_lib'] = (shared_dir / 'scripts' / 'lib').exists()

    if not structure['has_shared_lib']:
        warnings.append("Missing shared library at .claude/skills/shared/scripts/lib")

    # Check each skill
    skills = list_skills(str(path))
    structure['skills'] = {}

    for skill in skills:
        skill_checks = {
            'has_skill_md': skill['has_skill_md'],
            'has_scripts': len(skill['scripts']) > 0,
            'has_tests': skill['has_tests']
        }
        structure['skills'][skill['name']] = skill_checks

        if not skill['has_skill_md']:
            warnings.append(f"Skill '{skill['name']}' missing SKILL.md")
        if not skill['has_tests']:
            warnings.append(f"Skill '{skill['name']}' missing tests directory")

    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'warnings': warnings,
        'structure': structure
    }


def get_project_stats(project_path: str) -> Dict[str, int]:
    """
    Get statistics about a project.

    Args:
        project_path: Path to project root

    Returns:
        Dict with counts:
            - skills: Number of skills
            - scripts: Total script files
            - tests: Total test files
            - docs: Total doc files
    """
    path = Path(project_path).expanduser().resolve()
    skills_dir = path / '.claude' / 'skills'

    stats = {
        'skills': 0,
        'scripts': 0,
        'tests': 0,
        'docs': 0
    }

    if not skills_dir.exists():
        return stats

    for skill_dir in skills_dir.iterdir():
        if skill_dir.is_dir() and skill_dir.name != 'shared':
            stats['skills'] += 1

            # Count scripts
            scripts_dir = skill_dir / 'scripts'
            if scripts_dir.exists():
                stats['scripts'] += len([f for f in scripts_dir.glob('*.py') if f.name != '__init__.py'])

            # Count tests
            tests_dir = skill_dir / 'tests'
            if tests_dir.exists():
                stats['tests'] += len(list(tests_dir.rglob('test_*.py')))

            # Count docs
            docs_dir = skill_dir / 'docs'
            if docs_dir.exists():
                stats['docs'] += len(list(docs_dir.rglob('*.md')))

    return stats
