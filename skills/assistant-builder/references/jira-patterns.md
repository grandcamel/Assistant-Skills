# Jira Assistant Skills Patterns

Patterns extracted from the Jira-Assistant-Skills project (14 skills, 100+ scripts, 560+ tests).

## Project Structure

```
Jira-Assistant-Skills/
├── .claude/
│   ├── settings.json           # Multi-profile configuration
│   ├── settings.local.json     # Credentials (gitignored)
│   ├── commands/               # Slash commands
│   │   ├── jira-assistant-setup.md
│   │   └── jira-discover-project.md
│   └── skills/
│       ├── shared/             # Shared library
│       │   ├── scripts/lib/    # 24 Python modules
│       │   ├── config/         # JSON schemas
│       │   ├── references/     # Shared docs
│       │   └── tests/
│       ├── jira-assistant/     # Hub/router skill
│       ├── jira-issue/         # Issue CRUD
│       ├── jira-search/        # JQL queries
│       ├── jira-bulk/          # Batch operations
│       ├── jira-agile/         # Sprints, epics
│       ├── jira-dev/           # Git integration
│       ├── jira-ops/           # Cache, discovery
│       ├── jira-fields/        # Custom fields
│       ├── jira-collaborate/   # Comments, attachments
│       ├── jira-relationships/ # Issue links
│       ├── jira-time/          # Time tracking
│       ├── jira-lifecycle/     # Workflow transitions
│       ├── jira-jsm/           # Service Management
│       └── jira-admin/         # Admin operations
├── docs/
├── tests/
├── README.md
├── CLAUDE.md
└── pyproject.toml
```

## Shared Library Pattern

Location: `.claude/skills/shared/scripts/lib/`

### Core Modules

| Module | Purpose | Lines |
|--------|---------|-------|
| `jira_client.py` | HTTP client with auth, retry, pagination | ~2000 |
| `cache.py` | SQLite caching with TTL, LRU | ~500 |
| `config_manager.py` | Multi-source config loading | ~300 |
| `credential_manager.py` | Secure credential handling | ~200 |
| `error_handler.py` | Exception hierarchy | ~250 |
| `formatters.py` | Output formatting | ~400 |
| `validators.py` | Input validation | ~300 |

### Client Features

```python
# Automatic retry with exponential backoff
client = JiraClient(profile='production')

# Pagination handling
all_issues = client.paginate('/rest/api/3/search', params={'jql': query})

# Bulk operations with batching
results = client.bulk_create('/rest/api/3/issue/bulk', issues, batch_size=50)
```

## SKILL.md Pattern

```yaml
---
name: "jira-issue"
description: "CRUD operations for Jira issues"
when_to_use: |
  - Creating new issues
  - Reading issue details
  - Updating issue fields
  - Deleting issues
---

# Issue Skill

Level 2 content: Tables, examples, quick reference

---

## What This Skill Does

| Operation | Script | Description |
|-----------|--------|-------------|

---

## Quick Start

Examples...

---

## Related Skills

Links to related skills...
```

## Router Skill Pattern

The jira-assistant skill routes based on intent:

```markdown
## Skill Routing

| When you want to... | Use this skill | Key scripts |
|---------------------|----------------|-------------|
| Create/read/update issues | jira-issue | create, get, update |
| Search with JQL | jira-search | search, jql_builder |
| Bulk operations | jira-bulk | bulk_create, bulk_update |
| Sprint management | jira-agile | list_sprints, move_to_sprint |
```

## Testing Pattern

### Test Organization

```
skill-name/
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Shared fixtures
│   ├── test_list_resource.py
│   ├── test_get_resource.py
│   ├── test_create_resource.py
│   └── live_integration/
│       └── test_resource_lifecycle.py
```

### Fixture Pattern

```python
@pytest.fixture
def mock_jira_client():
    client = MagicMock()
    client.get.return_value = {'issues': []}
    return client

@pytest.fixture
def sample_issue():
    return {
        'key': 'PROJ-123',
        'fields': {
            'summary': 'Test issue',
            'status': {'name': 'Open'}
        }
    }
```

## Configuration Pattern

### settings.json

```json
{
  "jira": {
    "default_profile": "production",
    "profiles": {
      "production": {
        "url": "https://company.atlassian.net",
        "project_keys": ["PROJ", "OPS"],
        "default_project": "PROJ"
      },
      "development": {
        "url": "https://company-dev.atlassian.net"
      }
    },
    "api": {
      "version": "3",
      "timeout": 30,
      "max_retries": 3
    }
  }
}
```

### Profile Usage

```python
# In scripts
parser.add_argument('--profile', '-p', help='Configuration profile')
client = get_client(profile=args.profile)
```

## Key Metrics

| Metric | Value |
|--------|-------|
| Skills | 14 |
| Scripts | 100+ |
| Tests | 560+ |
| Shared lib modules | 24 |
| Test coverage | 85%+ |
