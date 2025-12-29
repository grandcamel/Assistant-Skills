#!/usr/bin/env python3
"""
Show patterns from reference implementations.

Displays patterns, code examples, and best practices from the Jira,
Confluence, and Splunk Assistant Skills projects.

Usage:
    python show_reference.py --topic shared-library --project jira

Examples:
    # List available topics
    python show_reference.py --list-topics

    # Show shared library pattern from Jira
    python show_reference.py --topic shared-library --project jira

    # Compare patterns across all projects
    python show_reference.py --topic router-skill --project all
"""

import argparse
import json
import sys
from pathlib import Path

# Add shared lib to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'shared' / 'scripts' / 'lib'))

from project_detector import detect_project, get_project_stats
from formatters import print_success, print_error, print_info, print_header, format_table


# Available topics
TOPICS = {
    'project-structure': 'Directory layout and organization',
    'shared-library': 'Shared library modules and patterns',
    'skill-organization': 'How skills are structured (SKILL.md, scripts, tests)',
    'testing-patterns': 'Unit tests, integration tests, fixtures',
    'skill-md': 'SKILL.md format with progressive disclosure',
    'router-skill': 'Hub/router skill pattern',
    'configuration': 'settings.json patterns and profiles',
    'error-handling': 'Exception hierarchy and error handling',
    'client-pattern': 'HTTP client with retry, pagination'
}

# Reference projects (from settings, with fallbacks)
DEFAULT_PROJECTS = {
    'jira': '~/IdeaProjects/Jira-Assistant-Skills',
    'confluence': '~/IdeaProjects/Confluence-Assistant-Skills',
    'splunk': '~/IdeaProjects/Splunk-Assistant-Skills'
}


def load_settings():
    """Load settings.json to get reference project paths."""
    settings_path = Path(__file__).parent.parent.parent.parent / 'settings.json'
    if settings_path.exists():
        try:
            settings = json.loads(settings_path.read_text())
            return settings.get('assistant-builder', {}).get('reference_projects', DEFAULT_PROJECTS)
        except json.JSONDecodeError:
            pass
    return DEFAULT_PROJECTS


def get_reference_doc(project_name: str) -> str:
    """Get the reference documentation for a project."""
    refs_dir = Path(__file__).parent.parent / 'references'
    ref_file = refs_dir / f'{project_name}-patterns.md'

    if ref_file.exists():
        return ref_file.read_text()
    return None


def show_project_stats(project_path: str, project_name: str):
    """Show statistics for a reference project."""
    project = detect_project(project_path)
    if not project:
        print_error(f"  {project_name}: Project not found at {project_path}")
        return

    stats = get_project_stats(project_path)

    print(f"\n  {project_name.title()}-Assistant-Skills:")
    print(f"    Skills: {stats['skills']}")
    print(f"    Scripts: {stats['scripts']}")
    print(f"    Tests: {stats['tests']}")
    print(f"    Docs: {stats['docs']}")


def show_topic(topic: str, project: str, projects: dict):
    """Show a specific topic from reference projects."""
    print_header(f"Topic: {topic}")
    print(f"Description: {TOPICS.get(topic, 'Unknown topic')}\n")

    if project == 'all':
        project_list = list(projects.keys())
    else:
        project_list = [project]

    for proj_name in project_list:
        print_header(f"{proj_name.title()} Project")

        # Show from reference doc
        ref_content = get_reference_doc(proj_name)
        if ref_content:
            # Extract relevant section
            section = extract_section(ref_content, topic)
            if section:
                print(section)
            else:
                print(f"  (No specific section for '{topic}' in {proj_name} patterns)")
        else:
            print(f"  (Reference document not found for {proj_name})")

        # Show live stats if project exists
        proj_path = projects.get(proj_name, '')
        expanded_path = Path(proj_path).expanduser()
        if expanded_path.exists():
            show_project_stats(str(expanded_path), proj_name)

        print()


def extract_section(content: str, topic: str) -> str:
    """Extract a section from markdown content based on topic."""
    # Map topics to section headers
    section_map = {
        'project-structure': ['Project Structure', 'Structure'],
        'shared-library': ['Shared Library', 'Shared Lib'],
        'skill-organization': ['Skill', 'Organization'],
        'testing-patterns': ['Testing', 'Test'],
        'skill-md': ['SKILL.md', 'SKILL'],
        'router-skill': ['Router', 'Hub'],
        'configuration': ['Configuration', 'Config', 'settings'],
        'error-handling': ['Error', 'Exception'],
        'client-pattern': ['Client', 'HTTP']
    }

    keywords = section_map.get(topic, [topic])

    lines = content.split('\n')
    in_section = False
    section_lines = []
    section_level = 0

    for line in lines:
        # Check for section header
        if line.startswith('#'):
            header_level = len(line) - len(line.lstrip('#'))
            header_text = line.lstrip('#').strip()

            # Check if this header matches our topic
            if any(kw.lower() in header_text.lower() for kw in keywords):
                in_section = True
                section_level = header_level
                section_lines = [line]
                continue

            # Check if we've hit a same-level or higher header (end of section)
            if in_section and header_level <= section_level:
                break

        if in_section:
            section_lines.append(line)

    return '\n'.join(section_lines) if section_lines else None


def list_topics():
    """List all available topics."""
    print_header("Available Topics")
    print()
    for topic, description in TOPICS.items():
        print(f"  {topic:20} - {description}")
    print()


def main():
    parser = argparse.ArgumentParser(
        description='Show patterns from reference implementations',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # List topics
  python show_reference.py --list-topics

  # Show specific topic
  python show_reference.py --topic shared-library --project jira

  # Compare across all projects
  python show_reference.py --topic testing-patterns --project all
'''
    )

    parser.add_argument('--topic', '-t', help='Pattern topic to show')
    parser.add_argument('--project', '-p', default='jira',
                        choices=['jira', 'confluence', 'splunk', 'all'],
                        help='Reference project (default: jira)')
    parser.add_argument('--list-topics', '-l', action='store_true',
                        help='List available topics')
    parser.add_argument('--stats', '-s', action='store_true',
                        help='Show project statistics')

    args = parser.parse_args()

    projects = load_settings()

    if args.list_topics:
        list_topics()
        return

    if args.stats:
        print_header("Reference Project Statistics")
        for name, path in projects.items():
            expanded = Path(path).expanduser()
            if expanded.exists():
                show_project_stats(str(expanded), name)
            else:
                print(f"\n  {name}: Not found at {path}")
        return

    if not args.topic:
        print_error("Please specify a topic with --topic or use --list-topics")
        sys.exit(1)

    if args.topic not in TOPICS:
        print_error(f"Unknown topic: {args.topic}")
        print("Use --list-topics to see available topics")
        sys.exit(1)

    show_topic(args.topic, args.project, projects)


if __name__ == '__main__':
    main()
