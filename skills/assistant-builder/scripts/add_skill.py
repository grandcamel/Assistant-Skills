#!/usr/bin/env python3
"""
Add a new skill to an existing Assistant Skills project.

Creates the skill directory structure with SKILL.md and documentation
following the production pattern (CLI-reference style, no embedded scripts).

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
        --operations "list,get,create,update,delete"

    # Standard CRUD operations
    python add_skill.py --name "users" --description "User management" --operations crud
"""

import argparse
import json
import sys
from pathlib import Path

from assistant_skills_lib import (
    detect_project, get_topic_prefix,
    validate_required, validate_name, validate_path, validate_list,
    InputValidationError as ValidationError,
    print_success, print_error, print_info, print_warning
)


# Operation presets
OPERATION_PRESETS = {
    'crud': ['list', 'get', 'create', 'update', 'delete'],
    'readonly': ['list', 'get', 'search'],
    'all': ['list', 'get', 'create', 'update', 'delete', 'search', 'export', 'import']
}


def detect_project_type(project_path: Path) -> dict:
    """Detect project type and CLI tool from project structure."""
    result = {
        'type': 'cli-wrapper',
        'cli_tool': None,
        'topic': None
    }

    # Check for .claude-plugin directory (new structure)
    plugin_json = project_path / '.claude-plugin' / 'plugin.json'
    if plugin_json.exists():
        try:
            plugin = json.loads(plugin_json.read_text())
            result['name'] = plugin.get('name', '')
        except Exception:
            pass

    # Check for library directory (custom-library or hybrid)
    lib_dirs = list(project_path.glob('*-assistant-skills-lib'))
    if lib_dirs:
        result['type'] = 'custom-library'

    # Try to detect topic from skills directory
    skills_dir = project_path / 'skills'
    if skills_dir.exists():
        for skill_dir in skills_dir.iterdir():
            if skill_dir.is_dir() and skill_dir.name.endswith('-assistant'):
                # Extract topic from {topic}-assistant
                result['topic'] = skill_dir.name.replace('-assistant', '')
                break

    # Check for CLI tool in setup command
    setup_commands = list((project_path / '.claude-plugin' / 'commands').glob('*-setup.md'))
    if setup_commands:
        try:
            content = setup_commands[0].read_text()
            # Try to extract CLI tool from content
            if 'brew install' in content:
                for line in content.split('\n'):
                    if 'brew install' in line:
                        parts = line.strip().split()
                        if len(parts) >= 3:
                            result['cli_tool'] = parts[-1]
                            break
        except Exception:
            pass

    # Default CLI tool to topic-as for custom libraries
    if not result['cli_tool'] and result['topic']:
        if result['type'] == 'custom-library':
            result['cli_tool'] = f"{result['topic']}-as"
        else:
            result['cli_tool'] = result['topic']

    return result


def generate_skill_md(
    topic: str,
    skill_name: str,
    description: str,
    operations: list,
    cli_tool: str,
    project_name: str = None
) -> str:
    """Generate SKILL.md content with CLI command references."""

    # Build operations table
    operations_table = ""
    for op in operations:
        risk = "-"
        if op in ('create', 'update'):
            risk = "⚠️"
        elif op in ('delete',):
            risk = "⚠️⚠️"

        if op == 'list':
            operations_table += f"| List {skill_name}s | `{cli_tool} {skill_name} list` | {risk} |\n"
        elif op == 'get':
            operations_table += f"| Get {skill_name} | `{cli_tool} {skill_name} get <id>` | {risk} |\n"
        elif op == 'create':
            operations_table += f"| Create {skill_name} | `{cli_tool} {skill_name} create [options]` | {risk} |\n"
        elif op == 'update':
            operations_table += f"| Update {skill_name} | `{cli_tool} {skill_name} update <id> [options]` | {risk} |\n"
        elif op == 'delete':
            operations_table += f"| Delete {skill_name} | `{cli_tool} {skill_name} delete <id>` | {risk} |\n"
        elif op == 'search':
            operations_table += f"| Search {skill_name}s | `{cli_tool} {skill_name} search <query>` | {risk} |\n"
        elif op == 'export':
            operations_table += f"| Export {skill_name}s | `{cli_tool} {skill_name} export [options]` | {risk} |\n"
        elif op == 'import':
            operations_table += f"| Import {skill_name}s | `{cli_tool} {skill_name} import <file>` | ⚠️ |\n"
        else:
            operations_table += f"| {op.title()} | `{cli_tool} {skill_name} {op}` | {risk} |\n"

    # Build trigger phrases
    trigger_list = ', '.join([f'({i+1}) {op} {skill_name}s' for i, op in enumerate(operations[:5])])

    # Build command sections
    command_sections = ""

    if 'list' in operations:
        command_sections += f"""
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
"""

    if 'get' in operations:
        command_sections += f"""
### Get {skill_name.title()} Details

```bash
{cli_tool} {skill_name} get <id> [--output json|table]
```

**Examples:**
```bash
# Get by ID
{cli_tool} {skill_name} get ITEM-123

# JSON output
{cli_tool} {skill_name} get ITEM-123 --output json
```
"""

    if 'create' in operations:
        command_sections += f"""
### Create {skill_name.title()}

```bash
{cli_tool} {skill_name} create --name <name> [--description <desc>]
```

**Examples:**
```bash
# Create with name
{cli_tool} {skill_name} create --name "New {skill_name.title()}"

# Create with full details
{cli_tool} {skill_name} create --name "New {skill_name.title()}" --description "Description"
```
"""

    if 'update' in operations:
        command_sections += f"""
### Update {skill_name.title()}

```bash
{cli_tool} {skill_name} update <id> [--name <name>] [--description <desc>]
```

**Examples:**
```bash
# Update name
{cli_tool} {skill_name} update ITEM-123 --name "Updated Name"

# Update multiple fields
{cli_tool} {skill_name} update ITEM-123 --name "New Name" --status "active"
```
"""

    if 'delete' in operations:
        command_sections += f"""
### Delete {skill_name.title()}

```bash
{cli_tool} {skill_name} delete <id> [--force]
```

**Examples:**
```bash
# Delete with confirmation
{cli_tool} {skill_name} delete ITEM-123

# Delete without confirmation
{cli_tool} {skill_name} delete ITEM-123 --force
```
"""

    if 'search' in operations:
        command_sections += f"""
### Search {skill_name.title()}s

```bash
{cli_tool} {skill_name} search <query> [--limit <n>] [--output json|table]
```

**Examples:**
```bash
# Search by keyword
{cli_tool} {skill_name} search "keyword"

# Search with limit
{cli_tool} {skill_name} search "keyword" --limit 10
```
"""

    return f"""---
name: "{topic}-{skill_name}"
description: "{description}. ALWAYS use this skill when user wants to: {trigger_list}."
version: "1.0.0"
author: "{project_name or topic}"
license: "MIT"
allowed-tools: ["Bash", "Read", "Glob", "Grep"]
---

# {skill_name.title()} Skill

{description}

## Quick Reference

| Operation | Command | Risk |
|-----------|---------|:----:|
{operations_table}
**Risk Legend**: - Safe | ⚠️ Caution | ⚠️⚠️ Warning | ⚠️⚠️⚠️ Danger

## When to Use This Skill

**ALWAYS use when:**
- User wants to work with {skill_name}s
- User mentions "{skill_name}", "{skill_name}s", or related terms

**NEVER use when:**
- User wants bulk operations on 10+ items (use {topic}-bulk instead)
- User is doing general search/query (use {topic}-search instead)

## Available Commands
{command_sections}
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

### Pattern 2: Create and Verify

```bash
# Step 1: Create new item
{cli_tool} {skill_name} create --name "New Item"

# Step 2: Verify creation
{cli_tool} {skill_name} list --filter "name=New Item"
```

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| Authentication failed | Invalid token | Run `{cli_tool} auth login` |
| Resource not found | Invalid ID | Verify ID with `{cli_tool} {skill_name} list` |
| Permission denied | Insufficient rights | Check your permissions |

## Related Documentation

- [Best Practices](./docs/BEST_PRACTICES.md)
- [Safeguards](../shared/docs/SAFEGUARDS.md)
"""


def generate_best_practices_md(topic: str, skill_name: str, cli_tool: str) -> str:
    """Generate best practices documentation."""
    return f"""# {skill_name.title()} Best Practices

## General Guidelines

1. **Always verify before modifying** - List or get items before updating/deleting
2. **Use filters wisely** - Narrow down results with filters to avoid mistakes
3. **Prefer JSON output for scripting** - Use `--output json` when piping to other tools

## Safety Checklist

Before any destructive operation:

- [ ] Verify the target ID/name is correct
- [ ] Confirm you have the right permissions
- [ ] Consider if this should be a bulk operation
- [ ] Know the rollback procedure

## Common Mistakes

| Mistake | Prevention |
|---------|------------|
| Wrong ID | Always double-check with `{cli_tool} {skill_name} get <id>` |
| Missing confirmation | Don't use `--force` unless certain |
| Wrong filter | Test filters with list before bulk operations |

## Performance Tips

1. Use pagination for large result sets
2. Cache frequently accessed data
3. Use filters to reduce API calls
"""


def add_skill(
    project_dir: str,
    skill_name: str,
    description: str,
    resource: str = None,
    operations: list = None,
    dry_run: bool = False
) -> dict:
    """
    Add a new skill to an existing project.

    Returns dict with created files.
    """
    project_path = Path(project_dir).expanduser().resolve()

    # Detect project structure
    project_info = detect_project_type(project_path)
    topic = project_info.get('topic')
    cli_tool = project_info.get('cli_tool')

    if not topic:
        # Fallback: try to detect from old structure
        project = detect_project(str(project_path))
        if not project:
            raise ValueError(f"No Assistant Skills project found at: {project_path}")
        topic = project.get('topic_prefix')
        if not topic:
            raise ValueError("Could not detect topic prefix. Is this a valid project?")

    if not cli_tool:
        cli_tool = topic

    # Default resource to skill name
    if not resource:
        resource = skill_name

    # Default operations
    if not operations:
        operations = OPERATION_PRESETS['crud']

    # Skill directory - use new structure (skills/)
    skills_dir = project_path / 'skills'

    # Fallback to old structure if new doesn't exist
    if not skills_dir.exists():
        skills_dir = project_path / '.claude' / 'skills'

    skill_dir = skills_dir / f'{topic}-{skill_name}'

    if skill_dir.exists() and not dry_run:
        raise ValueError(f"Skill already exists: {skill_dir}")

    result = {
        'skill_dir': str(skill_dir),
        'files': [],
        'topic': topic,
        'cli_tool': cli_tool
    }

    # Create directories
    dirs = [
        skill_dir,
        skill_dir / 'docs',
    ]

    for d in dirs:
        if not dry_run:
            d.mkdir(parents=True, exist_ok=True)

    # Create SKILL.md (CLI-reference style, no scripts)
    skill_md_path = skill_dir / 'SKILL.md'
    skill_md_content = generate_skill_md(
        topic=topic,
        skill_name=skill_name,
        description=description,
        operations=operations,
        cli_tool=cli_tool,
        project_name=project_info.get('name')
    )
    result['files'].append('SKILL.md')
    if not dry_run:
        skill_md_path.write_text(skill_md_content)

    # Create docs/BEST_PRACTICES.md
    best_practices_path = skill_dir / 'docs' / 'BEST_PRACTICES.md'
    best_practices_content = generate_best_practices_md(topic, skill_name, cli_tool)
    result['files'].append('docs/BEST_PRACTICES.md')
    if not dry_run:
        best_practices_path.write_text(best_practices_content)

    # Update plugin.json to include new skill
    plugin_json_path = project_path / '.claude-plugin' / 'plugin.json'
    if plugin_json_path.exists() and not dry_run:
        try:
            plugin = json.loads(plugin_json_path.read_text())
            skill_path = f"../skills/{topic}-{skill_name}/SKILL.md"
            if 'skills' not in plugin:
                plugin['skills'] = []
            if skill_path not in plugin['skills']:
                plugin['skills'].append(skill_path)
                plugin_json_path.write_text(json.dumps(plugin, indent=2))
                result['files'].append('.claude-plugin/plugin.json (updated)')
        except Exception as e:
            print_warning(f"Could not update plugin.json: {e}")

    return result


def interactive_mode(project_dir: str = '.'):
    """Run interactive wizard to add a skill."""
    print("\n" + "=" * 60)
    print("  Add Skill Wizard")
    print("=" * 60 + "\n")

    project_path = Path(project_dir).expanduser().resolve()

    # Detect project
    project_info = detect_project_type(project_path)
    topic = project_info.get('topic')
    cli_tool = project_info.get('cli_tool')

    if not topic:
        # Fallback to old detection
        project = detect_project(project_dir)
        if not project:
            print_error(f"No Assistant Skills project found in: {project_dir}")
            alt_path = input("Enter project path (or press Enter to cancel): ").strip()
            if not alt_path:
                return None
            project_path = Path(alt_path).expanduser().resolve()
            project_info = detect_project_type(project_path)
            topic = project_info.get('topic')
            cli_tool = project_info.get('cli_tool')
            if not topic:
                print_error(f"No project found at: {alt_path}")
                return None
            project_dir = alt_path
        else:
            topic = project['topic_prefix']
            cli_tool = topic

    print_info(f"Detected project type: {project_info.get('type', 'unknown')}")
    print_info(f"Topic prefix: {topic}")
    print_info(f"CLI tool: {cli_tool}")

    # List existing skills
    skills_dir = project_path / 'skills'
    if not skills_dir.exists():
        skills_dir = project_path / '.claude' / 'skills'

    if skills_dir.exists():
        existing = [d.name for d in skills_dir.iterdir()
                   if d.is_dir() and d.name != 'shared' and not d.name.startswith('.')]
        if existing:
            print_info(f"Existing skills: {', '.join(existing)}")
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

    # Operations
    print("\nStep 2: Operations\n")
    print("Presets: crud (list/get/create/update/delete), readonly, all")
    print("Or enter comma-separated operation names")

    operations_input = input("Operations [crud]: ").strip().lower()
    if not operations_input:
        operations_input = 'crud'

    if operations_input in OPERATION_PRESETS:
        operations = OPERATION_PRESETS[operations_input]
    else:
        operations = validate_list(operations_input, "operations", min_items=1)

    # Confirmation
    print("\n" + "-" * 60)
    print("Summary:")
    print("-" * 60)
    print(f"  Skill:       {topic}-{name}")
    print(f"  Description: {description}")
    print(f"  Resource:    {resource}")
    print(f"  Operations:  {', '.join(operations)}")
    print(f"  CLI Tool:    {cli_tool}")
    print("-" * 60)

    confirm = input("\nProceed? [Y/n]: ").strip().lower()
    if confirm and confirm != 'y':
        print("Cancelled.")
        return None

    return {
        'project_dir': str(project_path),
        'skill_name': name,
        'description': description,
        'resource': resource,
        'operations': operations
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
  python add_skill.py --name "users" --description "User management" --operations crud

  # Custom operations
  python add_skill.py --name "reports" --operations "list,get,generate,export"
'''
    )

    parser.add_argument('--name', '-n', help='Skill name (without topic prefix)')
    parser.add_argument('--description', '-d', help='One-line description')
    parser.add_argument('--resource', '-r', help='Primary API resource name')
    parser.add_argument('--operations', '-o',
                        help='Operations: crud, readonly, all, or comma-separated list')
    parser.add_argument('--project-dir', '-p', default='.',
                        help='Project directory (default: current)')
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
            # Parse operations
            operations = None
            if args.operations:
                if args.operations in OPERATION_PRESETS:
                    operations = OPERATION_PRESETS[args.operations]
                else:
                    operations = [s.strip() for s in args.operations.split(',')]

            config = {
                'project_dir': args.project_dir,
                'skill_name': validate_name(args.name, "skill name"),
                'description': validate_required(args.description, "description"),
                'resource': args.resource,
                'operations': operations
            }

        # Add skill
        if args.dry_run:
            print_info("DRY RUN - No files will be created\n")

        result = add_skill(
            project_dir=config['project_dir'],
            skill_name=config['skill_name'],
            description=config['description'],
            resource=config.get('resource'),
            operations=config.get('operations'),
            dry_run=args.dry_run
        )

        print_success(f"Created skill at: {result['skill_dir']}")
        print(f"\nFiles created: {len(result['files'])}")

        if args.dry_run:
            print("\nFiles that would be created:")
            for f in result['files']:
                print(f"  {f}")

        # Next steps
        print("\n" + "=" * 60)
        print("Next Steps:")
        print("=" * 60)
        print("1. Review and customize SKILL.md")
        print("2. Add skill-specific documentation to docs/")
        print("3. Update the hub router skill routing table")
        print("4. Test the CLI commands documented in SKILL.md")

    except ValidationError as e:
        print_error(str(e))
        sys.exit(1)
    except Exception as e:
        print_error(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
