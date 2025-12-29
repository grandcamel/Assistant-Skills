#!/usr/bin/env python3
"""
Show the content of a specific template.

Displays template content with syntax highlighting and placeholder info.

Usage:
    python show_template.py SKILL.md.template

Examples:
    # Show a template
    python show_template.py SKILL.md.template

    # Show with placeholders highlighted
    python show_template.py project-init-prompt.md --show-placeholders

    # Output raw content
    python show_template.py settings.json.template --raw
"""

import argparse
import re
import sys
from pathlib import Path

from assistant_skills_lib import (
    load_template, list_placeholders, list_template_files,
    print_header, print_info, print_warning
)
from assistant_skills_lib.template_engine import PLACEHOLDER_DESCRIPTIONS


def find_template(name: str) -> str:
    """Find a template file by name."""
    templates = list_template_files()

    # Exact match
    for t in templates:
        if t['name'] == name:
            return t['path']

    # Partial match
    matches = [t for t in templates if name.lower() in t['name'].lower()]
    if len(matches) == 1:
        return matches[0]['path']
    elif len(matches) > 1:
        print_warning(f"Multiple templates match '{name}':")
        for m in matches:
            print(f"  - {m['name']} ({m['category']})")
        return None

    return None


def show_template(path: str, show_placeholders: bool = False, raw: bool = False):
    """Show template content."""
    template_path = Path(path)

    if not template_path.exists():
        # Try to find it
        found_path = find_template(path)
        if found_path:
            template_path = Path(found_path)
        else:
            print(f"Template not found: {path}")
            return

    content = template_path.read_text()

    if raw:
        print(content)
        return

    # Header
    print_header(template_path.name)
    print(f"Location: {template_path}")
    print(f"Size: {len(content)} bytes, {len(content.splitlines())} lines")

    # Show placeholders
    placeholders = list_placeholders(content)
    if placeholders:
        print(f"\nPlaceholders ({len(placeholders)}):")
        for p in placeholders:
            desc = PLACEHOLDER_DESCRIPTIONS.get(p, 'No description')
            print(f"  {{{{{{p}}}}}}: {desc}")

    print("\n" + "=" * 60)
    print("CONTENT")
    print("=" * 60 + "\n")

    if show_placeholders:
        # Highlight placeholders
        def highlight(match):
            return f"\033[93m{match.group(0)}\033[0m"  # Yellow

        content = re.sub(r'\{\{\w+\}\}', highlight, content)

    print(content)


def main():
    parser = argparse.ArgumentParser(
        description='Show template content',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Show a template
  python show_template.py SKILL.md.template

  # Highlight placeholders
  python show_template.py project-init-prompt.md --show-placeholders

  # Raw output (for piping)
  python show_template.py settings.json.template --raw
'''
    )

    parser.add_argument('template', help='Template name or path')
    parser.add_argument('--show-placeholders', '-p', action='store_true',
                        help='Highlight placeholders in output')
    parser.add_argument('--raw', '-r', action='store_true',
                        help='Output raw content without formatting')

    args = parser.parse_args()

    show_template(args.template, args.show_placeholders, args.raw)


if __name__ == '__main__':
    main()
