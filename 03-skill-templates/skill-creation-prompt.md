# Skill Creation Prompt

## Purpose

Create a new specialized skill with proper structure, scripts, tests, and documentation.

## Prerequisites

- Project scaffolding complete
- Shared library implemented
- Skill architecture designed (from `03-architecture-prompt.md`)

## Placeholders

- `{{TOPIC}}` - Lowercase prefix (e.g., "github")
- `{{SKILL_NAME}}` - Skill name without prefix (e.g., "issues")
- `{{SKILL_DESCRIPTION}}` - One-line description
- `{{API_RESOURCE}}` - Primary API resource (e.g., "issues", "users")
- `{{SCRIPTS_LIST}}` - List of scripts to create

---

## Prompt

```
Create a new skill: {{TOPIC}}-{{SKILL_NAME}}

**Description:** {{SKILL_DESCRIPTION}}
**Primary Resource:** {{API_RESOURCE}}
**Scripts Needed:** {{SCRIPTS_LIST}}

Create the complete skill structure following TDD principles:

## 1. Directory Structure

```
.claude/skills/{{TOPIC}}-{{SKILL_NAME}}/
├── SKILL.md                    # Progressive disclosure (3 levels)
├── scripts/
│   ├── __init__.py
│   ├── list_{{API_RESOURCE}}.py
│   ├── get_{{API_RESOURCE}}.py
│   ├── create_{{API_RESOURCE}}.py
│   ├── update_{{API_RESOURCE}}.py
│   └── delete_{{API_RESOURCE}}.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_list_{{API_RESOURCE}}.py
│   ├── test_get_{{API_RESOURCE}}.py
│   ├── test_create_{{API_RESOURCE}}.py
│   ├── test_update_{{API_RESOURCE}}.py
│   ├── test_delete_{{API_RESOURCE}}.py
│   └── live_integration/
│       ├── __init__.py
│       └── test_{{API_RESOURCE}}_lifecycle.py
├── docs/
│   └── (optional deep documentation)
└── assets/
    └── templates/
        └── (optional JSON templates)
```

## 2. SKILL.md

Create with 3-level progressive disclosure:

**Level 1 (Frontmatter):**
- name: {{TOPIC}}-{{SKILL_NAME}}
- description: {{SKILL_DESCRIPTION}}
- when_to_use: (list of trigger scenarios)

**Level 2 (Quick Reference):**
- What this skill does (table)
- Available scripts (with one-line descriptions)
- Quick examples
- Common patterns

**Level 3 (Linked Docs):**
- Links to detailed documentation if needed

## 3. Scripts

For each script, implement:
- Proper shebang and docstring
- Shared library imports (path injection pattern)
- argparse with --help, --profile, --output options
- Input validation using validators
- @handle_errors decorator
- Success/error output using formatters
- Make executable (chmod +x)

Use this standard pattern:
```python
#!/usr/bin/env python3
"""
Script description.

Examples:
    python script.py ARG --option VALUE
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'shared' / 'scripts' / 'lib'))

from config_manager import get_client
from error_handler import handle_errors
from validators import validate_required, validate_id
from formatters import print_success, format_table, format_json


@handle_errors
def main():
    parser = argparse.ArgumentParser(
        description='Script description',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python script.py ARG
  python script.py ARG --output json
  python script.py ARG --profile development
'''
    )
    parser.add_argument('id', help='Resource ID')
    parser.add_argument('--profile', '-p', help='Configuration profile')
    parser.add_argument('--output', '-o', choices=['text', 'json'], default='text')
    args = parser.parse_args()

    # Validate inputs
    resource_id = validate_id(args.id)

    # Get client
    client = get_client(profile=args.profile)

    # Perform operation
    result = client.get(f'/api/resource/{resource_id}')

    # Output results
    if args.output == 'json':
        print(format_json(result))
    else:
        print(format_table([result], keys=['id', 'name', 'status']))

    print_success('Operation completed')


if __name__ == '__main__':
    main()
```

## 4. Tests (TDD)

Create unit tests BEFORE implementation (or alongside):
- Test valid inputs
- Test invalid inputs (validation errors)
- Test API success responses
- Test API error responses
- Test output formatting

Use pytest with mocked API responses:
```python
import pytest
from unittest.mock import patch, MagicMock

def test_list_returns_results():
    # Arrange
    mock_client = MagicMock()
    mock_client.get.return_value = {'values': [...]}

    # Act
    with patch('script.get_client', return_value=mock_client):
        result = list_function()

    # Assert
    assert len(result) > 0
```

## 5. Verification

After creation:
- [ ] All scripts have --help
- [ ] All scripts support --profile
- [ ] All tests pass
- [ ] SKILL.md has all 3 levels
- [ ] Scripts are executable
```

---

## Expected Outputs

1. **Complete directory structure** for the skill
2. **SKILL.md** with progressive disclosure
3. **All scripts** with proper patterns
4. **Unit tests** for each script
5. **Test fixtures** in conftest.py

---

## TDD Workflow

1. **Write failing tests first**
   ```bash
   pytest .claude/skills/{{TOPIC}}-{{SKILL_NAME}}/tests/ -v
   # Should fail - no implementation yet
   ```

2. **Commit failing tests**
   ```
   test({{TOPIC}}-{{SKILL_NAME}}): add failing tests for list_{{API_RESOURCE}}
   ```

3. **Implement script**

4. **Verify tests pass**
   ```bash
   pytest .claude/skills/{{TOPIC}}-{{SKILL_NAME}}/tests/ -v
   # Should pass
   ```

5. **Commit implementation**
   ```
   feat({{TOPIC}}-{{SKILL_NAME}}): implement list_{{API_RESOURCE}}.py (N/N tests passing)
   ```

6. **Repeat for each script**

---

## Next Steps

1. Run regression tests on shared library
2. Create next skill
3. After all skills: create router skill
