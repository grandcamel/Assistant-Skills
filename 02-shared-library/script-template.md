# Script Template Pattern

## Purpose

Provides a standardized template for all skill scripts to ensure consistency, proper error handling, and maintainability across the project.

## Standard Script Template

```python
#!/usr/bin/env python3
"""
Brief description of what this script does.

Examples:
    python script_name.py REQUIRED_ARG --option value
    python script_name.py REQUIRED_ARG --output json
"""

import sys
import argparse
from pathlib import Path

# Add shared lib to path - adjust path depth based on location
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'shared' / 'scripts' / 'lib'))

from config_manager import get_client  # Or your API client getter
from error_handler import handle_errors
from validators import validate_required, validate_limit
from formatters import print_success, format_json


@handle_errors
def main():
    parser = argparse.ArgumentParser(
        description='Script description',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s RESOURCE_ID
  %(prog)s RESOURCE_ID --limit 50
  %(prog)s RESOURCE_ID --output json
        """
    )

    # Required positional arguments
    parser.add_argument('resource_id', help='Resource identifier')

    # Optional arguments
    parser.add_argument('--limit', '-l', type=int, default=25,
                        help='Maximum number of results (default: 25)')
    parser.add_argument('--profile', '-p',
                        help='Configuration profile to use')
    parser.add_argument('--output', '-o',
                        choices=['text', 'json'],
                        default='text',
                        help='Output format (default: text)')

    args = parser.parse_args()

    # Validate inputs
    resource_id = validate_required(args.resource_id, "resource_id")
    limit = validate_limit(args.limit)

    # Get API client
    client = get_client(profile=args.profile)

    # Perform operation
    result = client.get(f'/api/resources/{resource_id}', params={'limit': limit})

    # Output results
    if args.output == 'json':
        print(format_json(result))
    else:
        format_and_print_result(result)

    print_success("Operation completed")


def format_and_print_result(result):
    """Format result for text output."""
    print(f"Resource: {result.get('name', 'Unknown')}")
    print(f"  ID: {result.get('id')}")
    print(f"  Status: {result.get('status', 'unknown')}")


if __name__ == '__main__':
    main()
```

## Template Components

### 1. Shebang and Docstring

```python
#!/usr/bin/env python3
"""
Brief description.

Examples:
    python script.py ARG --option value
"""
```

- Always include shebang for executable scripts
- Docstring should describe purpose and show usage examples

### 2. Shared Library Import Pattern

```python
import sys
from pathlib import Path

# Add shared lib to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'shared' / 'scripts' / 'lib'))
```

Adjust the number of `.parent` calls based on script location:
- `scripts/script.py` -> 3 parents to reach `shared/scripts/lib/`
- `scripts/subdir/script.py` -> 4 parents

### 3. @handle_errors Decorator

```python
@handle_errors
def main():
    ...
```

The decorator:
- Catches all API errors (401, 403, 404, 429, 5xx)
- Catches network errors (connection, timeout)
- Prints formatted error messages with hints
- Exits with appropriate status codes
- Handles KeyboardInterrupt gracefully

### 4. Argument Parser Pattern

```python
parser = argparse.ArgumentParser(
    description='Script description',
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog="""
Examples:
  %(prog)s REQUIRED_ARG
  %(prog)s REQUIRED_ARG --option VALUE
    """
)
```

Standard flags all scripts should support:
- `--profile, -p`: Configuration profile
- `--output, -o`: Output format (text/json)
- `--limit, -l`: Pagination limit (where applicable)

### 5. Validation Pattern

```python
# Validate inputs BEFORE making API calls
resource_id = validate_required(args.resource_id, "resource_id")
limit = validate_limit(args.limit, max_value=100)
```

Always validate:
- Required fields are present
- IDs are in correct format
- Limits are within bounds
- Paths exist (if applicable)

### 6. Output Format Pattern

```python
if args.output == 'json':
    print(format_json(result))
else:
    format_and_print_text(result)
```

- JSON output for programmatic consumption
- Text output for human readability
- Success message at the end

## Script Categories

### 1. List/Get Scripts

```python
# Pattern: Retrieve and display resources
def main():
    ...
    results = client.get('/api/resources', params={'limit': limit})

    if args.output == 'json':
        print(format_json(results))
    else:
        if not results:
            print("No resources found.")
            return
        for item in results:
            print(format_resource(item))
```

### 2. Create Scripts

```python
# Pattern: Create a new resource
def main():
    ...
    # Read from file or argument
    if args.file:
        content = Path(args.file).read_text()
    else:
        content = args.content

    result = client.post('/api/resources', json_data={
        'name': args.name,
        'content': content,
    })

    print_success(f"Created resource: {result['id']}")
```

### 3. Update Scripts

```python
# Pattern: Update existing resource with version handling
def main():
    ...
    # Get current version first
    current = client.get(f'/api/resources/{resource_id}')
    current_version = current.get('version', {}).get('number', 1)

    result = client.put(f'/api/resources/{resource_id}', json_data={
        'name': args.name,
        'version': {'number': current_version + 1},
    })

    print_success(f"Updated resource: {result['id']}")
```

### 4. Delete Scripts

```python
# Pattern: Delete with confirmation
def main():
    ...
    if not args.force:
        confirm = input(f"Delete resource {resource_id}? [y/N]: ")
        if confirm.lower() != 'y':
            print("Cancelled.")
            return

    client.delete(f'/api/resources/{resource_id}')
    print_success(f"Deleted resource: {resource_id}")
```

## File Structure

```
.claude/skills/{topic}-{skill}/
├── scripts/
│   ├── __init__.py           # Empty or with __all__
│   ├── list_resources.py     # List/search operations
│   ├── get_resource.py       # Get single resource
│   ├── create_resource.py    # Create new resource
│   ├── update_resource.py    # Update existing
│   └── delete_resource.py    # Delete resource
├── tests/
│   ├── conftest.py           # Shared fixtures
│   ├── test_list_resources.py
│   └── ...
└── SKILL.md
```

## Making Scripts Executable

```bash
chmod +x .claude/skills/{topic}-{skill}/scripts/*.py
```

## Checklist for New Scripts

- [ ] Shebang line present
- [ ] Docstring with description and examples
- [ ] Shared library import pattern
- [ ] `@handle_errors` decorator on `main()`
- [ ] Argument parser with `--profile` and `--output`
- [ ] Input validation before API calls
- [ ] JSON and text output formats
- [ ] Success message on completion
- [ ] Made executable with `chmod +x`
- [ ] Unit tests written
