"""
Template Engine for Assistant Builder

Provides template loading and placeholder replacement functionality.
Uses {{PLACEHOLDER}} syntax for variable substitution.

Usage:
    from template_engine import load_template, render_template, list_placeholders

    template = load_template("path/to/template.md")
    placeholders = list_placeholders(template)
    rendered = render_template(template, {"API_NAME": "GitHub", "TOPIC": "github"})
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Set


# Regex pattern for {{PLACEHOLDER}} syntax
PLACEHOLDER_PATTERN = re.compile(r'\{\{(\w+)\}\}')


def load_template(path: str) -> str:
    """
    Load a template file from disk.

    Args:
        path: Path to the template file (absolute or relative)

    Returns:
        Template content as string

    Raises:
        FileNotFoundError: If template file doesn't exist
        IOError: If file cannot be read
    """
    template_path = Path(path).expanduser().resolve()

    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")

    if not template_path.is_file():
        raise ValueError(f"Path is not a file: {template_path}")

    return template_path.read_text(encoding='utf-8')


def list_placeholders(template: str) -> List[str]:
    """
    Extract all unique placeholders from a template.

    Args:
        template: Template content string

    Returns:
        Sorted list of unique placeholder names (without braces)

    Example:
        >>> list_placeholders("Hello {{NAME}}, welcome to {{PLACE}}!")
        ['NAME', 'PLACE']
    """
    matches = PLACEHOLDER_PATTERN.findall(template)
    return sorted(set(matches))


def render_template(template: str, context: Dict[str, str], strict: bool = True) -> str:
    """
    Replace placeholders in template with values from context.

    Args:
        template: Template content string
        context: Dictionary mapping placeholder names to values
        strict: If True, raise error for missing placeholders

    Returns:
        Rendered template with placeholders replaced

    Raises:
        ValueError: If strict=True and placeholders are missing from context

    Example:
        >>> render_template("Hello {{NAME}}!", {"NAME": "World"})
        'Hello World!'
    """
    if strict:
        required = set(list_placeholders(template))
        provided = set(context.keys())
        missing = required - provided

        if missing:
            raise ValueError(f"Missing placeholder values: {', '.join(sorted(missing))}")

    def replace(match):
        key = match.group(1)
        return context.get(key, match.group(0))

    return PLACEHOLDER_PATTERN.sub(replace, template)


def validate_context(template: str, context: Dict[str, str]) -> Dict[str, any]:
    """
    Validate that context provides all required placeholders.

    Args:
        template: Template content string
        context: Dictionary of placeholder values

    Returns:
        Dictionary with:
            - valid: bool - True if all placeholders have values
            - missing: list - Placeholder names missing from context
            - extra: list - Context keys not used in template
            - used: list - Placeholders that will be replaced
    """
    required = set(list_placeholders(template))
    provided = set(context.keys())

    return {
        'valid': required <= provided,
        'missing': sorted(required - provided),
        'extra': sorted(provided - required),
        'used': sorted(required & provided)
    }


def get_template_dir() -> Path:
    """
    Get the templates directory (parent of .claude folder).

    Returns:
        Path to templates directory
    """
    # Navigate from this file up to the project root
    current = Path(__file__).resolve()
    # .claude/skills/shared/scripts/lib/template_engine.py -> project root
    project_root = current.parent.parent.parent.parent.parent.parent
    return project_root


def list_template_files(category: Optional[str] = None) -> List[Dict[str, str]]:
    """
    List available template files.

    Args:
        category: Optional category filter (e.g., "01-project-scaffolding")

    Returns:
        List of dicts with 'name', 'path', 'category' keys
    """
    template_dir = get_template_dir()
    templates = []

    # Template categories
    categories = [
        "00-project-lifecycle",
        "01-project-scaffolding",
        "02-shared-library",
        "03-skill-templates",
        "04-testing",
        "05-documentation",
        "06-git-and-ci"
    ]

    if category:
        categories = [c for c in categories if category in c]

    for cat in categories:
        cat_path = template_dir / cat
        if cat_path.exists():
            for file in cat_path.rglob("*.md"):
                templates.append({
                    'name': file.name,
                    'path': str(file),
                    'category': cat
                })
            for file in cat_path.rglob("*.template"):
                templates.append({
                    'name': file.name,
                    'path': str(file),
                    'category': cat
                })

    return sorted(templates, key=lambda x: (x['category'], x['name']))


# Common placeholder descriptions for documentation
PLACEHOLDER_DESCRIPTIONS = {
    'API_NAME': 'Friendly API name (e.g., GitHub, Stripe, Twilio)',
    'TOPIC': 'Lowercase topic prefix for skills (e.g., github, stripe)',
    'SKILL_NAME': 'Skill name without prefix (e.g., issues, payments)',
    'SKILL_DESCRIPTION': 'One-line description of the skill',
    'API_RESOURCE': 'Primary API resource name (e.g., issues, users)',
    'ENDPOINT': 'API endpoint path (e.g., /repos/{owner}/{repo}/issues)',
    'BASE_URL': 'API base URL (e.g., https://api.github.com)',
    'PROJECT_NAME': 'Full project name (e.g., GitHub-Assistant-Skills)',
    'DATE': 'Current date timestamp',
    'WHEN_TO_USE': 'List of trigger scenarios for the skill',
    'SCRIPTS_TABLE': 'Markdown table of available scripts',
    'EXAMPLES': 'Example commands and usage patterns',
}
