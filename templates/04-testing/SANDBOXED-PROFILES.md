# Sandboxed Testing Profiles

Safe demo and testing profiles that restrict operations to prevent accidental data modification.

---

## Purpose

Sandboxed profiles enable:
- **Safe demos**: Show capabilities without risk
- **Training**: Let users practice without consequences
- **Testing**: Validate read operations without write access
- **Workshops**: Hands-on learning in controlled environments

---

## Profile Types

| Profile | Allowed Operations | Use Case |
|---------|-------------------|----------|
| `read-only` | GET only | Safe demos, read training |
| `search-only` | Search/query only | JQL/query training |
| `create-only` | GET + POST | Issue creation workshops |
| `no-delete` | GET + POST + PUT | Full editing, no deletion |
| `full-access` | All operations | Production use |

---

## Implementation

### Configuration File

Create `.claude/sandbox-profiles.json`:

```json
{
  "profiles": {
    "read-only": {
      "description": "Read-only access for safe demos",
      "allowed_methods": ["GET"],
      "blocked_scripts": ["create_*", "update_*", "delete_*", "bulk_*"],
      "warning_message": "Running in READ-ONLY mode. Write operations are disabled."
    },
    "search-only": {
      "description": "Search and query only",
      "allowed_methods": ["GET"],
      "allowed_scripts": ["search_*", "list_*", "get_*", "export_*"],
      "warning_message": "Running in SEARCH-ONLY mode. Only search operations available."
    },
    "create-only": {
      "description": "Read and create, no updates or deletes",
      "allowed_methods": ["GET", "POST"],
      "blocked_scripts": ["update_*", "delete_*", "bulk_update_*", "bulk_delete_*"],
      "warning_message": "Running in CREATE-ONLY mode. Updates and deletes are disabled."
    },
    "no-delete": {
      "description": "Full access except deletion",
      "allowed_methods": ["GET", "POST", "PUT", "PATCH"],
      "blocked_scripts": ["delete_*", "bulk_delete_*", "purge_*", "remove_*"],
      "warning_message": "Running in NO-DELETE mode. Deletion operations are disabled."
    },
    "full-access": {
      "description": "Full production access",
      "allowed_methods": ["GET", "POST", "PUT", "PATCH", "DELETE"],
      "blocked_scripts": [],
      "warning_message": null
    }
  },
  "default_profile": "full-access"
}
```

### Environment Variable

Set the active profile:

```bash
export SANDBOX_PROFILE=read-only
```

### Script Integration

Add profile checking to scripts:

```python
import os
import sys
from pathlib import Path
import json
import fnmatch

def get_sandbox_profile():
    """Get the active sandbox profile configuration."""
    profile_name = os.environ.get('SANDBOX_PROFILE', 'full-access')

    config_file = Path('.claude/sandbox-profiles.json')
    if not config_file.exists():
        return None

    config = json.loads(config_file.read_text())
    return config['profiles'].get(profile_name)

def check_sandbox_allowed(script_name, method='GET'):
    """Check if operation is allowed in current sandbox profile."""
    profile = get_sandbox_profile()
    if not profile:
        return True  # No sandbox configured

    # Check HTTP method
    if method not in profile.get('allowed_methods', ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']):
        return False

    # Check script name against blocked patterns
    for pattern in profile.get('blocked_scripts', []):
        if fnmatch.fnmatch(script_name, pattern):
            return False

    # Check against allowed patterns (if specified)
    allowed = profile.get('allowed_scripts')
    if allowed:
        for pattern in allowed:
            if fnmatch.fnmatch(script_name, pattern):
                return True
        return False

    return True

def enforce_sandbox():
    """Enforce sandbox restrictions, exit if not allowed."""
    script_name = Path(sys.argv[0]).stem
    profile = get_sandbox_profile()

    if profile and profile.get('warning_message'):
        print(f"⚠️  {profile['warning_message']}", file=sys.stderr)

    if not check_sandbox_allowed(script_name):
        print(f"❌ Operation blocked by sandbox profile", file=sys.stderr)
        print(f"   Script '{script_name}' is not allowed in current profile", file=sys.stderr)
        sys.exit(1)

# Usage in scripts
if __name__ == '__main__':
    enforce_sandbox()  # Add at top of main()
    main()
```

---

## Docker Integration

### Run Script with Profile

```bash
#!/bin/bash
# run_sandboxed.sh

PROFILE="${1:-read-only}"
shift

echo "Starting with sandbox profile: $PROFILE"
SANDBOX_PROFILE="$PROFILE" claude "$@"
```

### Docker Compose Profiles

```yaml
# docker-compose.sandbox.yml
version: '3.8'

services:
  read-only-demo:
    build: .
    environment:
      - SANDBOX_PROFILE=read-only
    volumes:
      - .:/workspace:ro  # Read-only mount

  training:
    build: .
    environment:
      - SANDBOX_PROFILE=create-only
    volumes:
      - .:/workspace

  full-access:
    build: .
    environment:
      - SANDBOX_PROFILE=full-access
    volumes:
      - .:/workspace
```

### Usage

```bash
# Safe demo
docker-compose -f docker-compose.sandbox.yml run read-only-demo

# Training session
docker-compose -f docker-compose.sandbox.yml run training

# Production
docker-compose -f docker-compose.sandbox.yml run full-access
```

---

## E2E Testing Integration

### Test Configuration

```yaml
# test_cases.yaml
- name: "Search operations in read-only mode"
  sandbox_profile: read-only
  prompt: "Search for all open issues"
  expected_patterns:
    - "Found.*issues"
  expected_success: true

- name: "Create blocked in read-only mode"
  sandbox_profile: read-only
  prompt: "Create a new bug"
  expected_patterns:
    - "Operation blocked by sandbox profile"
  expected_success: false  # Should fail gracefully
```

### Test Runner

```python
def run_sandboxed_test(test_case):
    """Run test with sandbox profile."""
    profile = test_case.get('sandbox_profile', 'full-access')
    env = os.environ.copy()
    env['SANDBOX_PROFILE'] = profile

    result = subprocess.run(
        ['claude', '--print', test_case['prompt']],
        env=env,
        capture_output=True,
        text=True
    )

    return result
```

---

## Use Cases

### 1. Customer Demo

```bash
# Start read-only demo
SANDBOX_PROFILE=read-only claude

# Safe to show:
# - Searching issues
# - Viewing details
# - Exporting data

# Blocked:
# - Creating issues
# - Updating fields
# - Deleting anything
```

### 2. Training Workshop

```bash
# Start create-only training
SANDBOX_PROFILE=create-only claude

# Participants can:
# - View existing data
# - Create new issues (practice)

# Blocked:
# - Modifying existing issues
# - Deleting anything
```

### 3. Query Training

```bash
# Start search-only mode
SANDBOX_PROFILE=search-only claude

# Focus on:
# - JQL/query syntax
# - Search patterns
# - Export formats

# All modifications blocked
```

---

## SKILL.md Documentation

Add sandbox awareness to skill documentation:

```markdown
## Sandbox Profiles

This skill respects sandbox profiles for safe demos and training:

| Profile | Available Operations |
|---------|---------------------|
| `read-only` | search, list, get, export |
| `search-only` | search, list |
| `create-only` | search, list, get, create |
| `no-delete` | All except delete |
| `full-access` | All operations |

Set profile: `export SANDBOX_PROFILE=read-only`

See project documentation for sandbox configuration.
```

---

## Best Practices

1. **Default to restrictive** - Use `read-only` for demos
2. **Clear messaging** - Always show which profile is active
3. **Graceful failures** - Blocked operations should explain why
4. **Document in README** - Explain available profiles
5. **Test profiles** - Include sandbox tests in E2E suite
6. **Training materials** - Create profile-specific guides

---

## Checklist

For projects using sandboxed profiles:

- [ ] Create `.claude/sandbox-profiles.json`
- [ ] Add `enforce_sandbox()` to scripts
- [ ] Document profiles in README
- [ ] Create Docker Compose sandbox config
- [ ] Add sandbox tests to E2E suite
- [ ] Create training materials per profile
