#!/usr/bin/env python3
"""
List available template files.

Shows all templates organized by category with their purposes.

Usage:
    python list_templates.py

Examples:
    # List all templates
    python list_templates.py

    # Filter by category
    python list_templates.py --category 01-project-scaffolding

    # Output as JSON
    python list_templates.py --format json

    # Show as tree
    python list_templates.py --format tree
"""

import argparse
import json
import sys
from pathlib import Path

# Add shared lib to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'shared' / 'scripts' / 'lib'))

from template_engine import list_template_files, get_template_dir
from formatters import print_header, format_table, format_tree, format_json


# Category descriptions
CATEGORIES = {
    '00-project-lifecycle': 'Full project lifecycle guidance (research, planning, completion)',
    '01-project-scaffolding': 'Initial project setup (structure, configs, docs)',
    '02-shared-library': 'Common utilities (client, config, error handling)',
    '03-skill-templates': 'Individual skill creation (SKILL.md, scripts)',
    '04-testing': 'TDD workflow and test templates',
    '05-documentation': 'User documentation patterns',
    '06-git-and-ci': 'Version control and CI/CD setup'
}


def list_categories():
    """List all template categories with descriptions."""
    print_header("Template Categories")
    print()
    for cat, desc in CATEGORIES.items():
        print(f"  {cat}")
        print(f"    {desc}")
        print()


def list_all_templates(category: str = None, format_type: str = 'text'):
    """List templates with various output formats."""
    templates = list_template_files(category)

    if not templates:
        print("No templates found.")
        return

    if format_type == 'json':
        print(format_json(templates))
        return

    if format_type == 'tree':
        # Group by category
        by_category = {}
        for t in templates:
            cat = t['category']
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append({'name': t['name']})

        root_items = []
        for cat in sorted(by_category.keys()):
            root_items.append({
                'name': cat,
                'children': by_category[cat]
            })

        print(format_tree('Templates', root_items))
        return

    # Default: text table
    if category:
        print_header(f"Templates in {category}")
        print(f"{CATEGORIES.get(category, '')}\n")
    else:
        print_header("All Templates")
        print()

    # Group by category for display
    current_cat = None
    for t in templates:
        if t['category'] != current_cat:
            current_cat = t['category']
            print(f"\n{current_cat}/")
            print(f"  {CATEGORIES.get(current_cat, '')}")
            print()

        print(f"  - {t['name']}")


def show_template_details(template_name: str):
    """Show details about a specific template."""
    templates = list_template_files()
    matches = [t for t in templates if template_name in t['name']]

    if not matches:
        print(f"No template matching '{template_name}' found.")
        return

    for t in matches:
        print_header(t['name'])
        print(f"Category: {t['category']}")
        print(f"Path: {t['path']}")

        # Show file size
        path = Path(t['path'])
        if path.exists():
            size = path.stat().st_size
            print(f"Size: {size} bytes")

            # Show first few lines as preview
            content = path.read_text()
            lines = content.split('\n')[:10]
            print("\nPreview:")
            print("-" * 40)
            for line in lines:
                print(f"  {line[:70]}")
            if len(content.split('\n')) > 10:
                print("  ...")
        print()


def main():
    parser = argparse.ArgumentParser(
        description='List available template files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # List all templates
  python list_templates.py

  # Filter by category
  python list_templates.py --category 03-skill-templates

  # Show as JSON
  python list_templates.py --format json

  # Show specific template
  python list_templates.py --show SKILL.md.template
'''
    )

    parser.add_argument('--category', '-c',
                        help='Filter by category (e.g., 01-project-scaffolding)')
    parser.add_argument('--format', '-f', choices=['text', 'json', 'tree'],
                        default='text', help='Output format')
    parser.add_argument('--show', '-s', help='Show details for a specific template')
    parser.add_argument('--categories', action='store_true',
                        help='List category descriptions')

    args = parser.parse_args()

    if args.categories:
        list_categories()
        return

    if args.show:
        show_template_details(args.show)
        return

    list_all_templates(args.category, args.format)


if __name__ == '__main__':
    main()
