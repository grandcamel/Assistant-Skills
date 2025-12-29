# Shared Library Creation Prompt

## Purpose

Create the shared library components that all skills will depend on.

## Prerequisites

- Project scaffolding complete
- GAP analysis with API details (auth, pagination, rate limits)
- Architecture design with shared component list

## Placeholders

- `{{API_NAME}}` - Friendly API name
- `{{TOPIC}}` - Lowercase prefix
- `{{BASE_URL}}` - API base URL
- `{{AUTH_METHOD}}` - Authentication method (api_key, oauth, jwt)
- `{{AUTH_HEADER}}` - Header name for auth (Authorization, X-API-Key, etc.)
- `{{PAGINATION_STYLE}}` - Pagination type (offset, cursor, page, link)

---

## Prompt

```
Create the shared library for {{PROJECT_NAME}} at `.claude/skills/shared/scripts/lib/`.

**API Details:**
- Base URL: {{BASE_URL}}
- Authentication: {{AUTH_METHOD}}
- Auth Header: {{AUTH_HEADER}}
- Pagination: {{PAGINATION_STYLE}}

Create the following modules with full implementation:

## 1. __init__.py

Export version and key classes:
```python
__version__ = "0.1.0"
from .client import {{API_NAME}}Client, get_client
from .config_manager import get_config, get_profile
from .error_handler import {{API_NAME}}Error, handle_errors
from .validators import validate_id, validate_required
from .formatters import print_success, print_error, format_table
```

## 2. client.py

HTTP client with:
- Session management (reuse connections)
- Base URL configuration
- Authentication ({{AUTH_METHOD}})
- Automatic retry on [429, 500, 502, 503, 504]
- Exponential backoff (2s, 4s, 8s)
- Rate limit header parsing
- Request/response logging (debug mode)
- Pagination helper method
- Methods: get(), post(), put(), patch(), delete()

## 3. config_manager.py

Configuration with:
- Environment variable loading ({{API_NAME}}_URL, {{API_NAME}}_TOKEN, etc.)
- settings.local.json loading (gitignored)
- settings.json loading (committed)
- Default values
- Config merging (priority: env > local > settings > defaults)
- Profile support (--profile flag)
- get_client() function that returns configured client

## 4. error_handler.py

Error handling with:
- Base exception class: {{API_NAME}}Error
- Subclasses: AuthenticationError, PermissionError, NotFoundError,
  ValidationError, RateLimitError, ConflictError, ServerError
- HTTP status code to exception mapping
- @handle_errors decorator for scripts
- print_error() for user-friendly output
- Troubleshooting hints per exception type

## 5. validators.py

Input validation for:
- Required fields (validate_required)
- ID formats (validate_id)
- URL formats (validate_url)
- Email formats (validate_email)
- API-specific patterns
- Return cleaned/normalized values
- Raise ValidationError with helpful message

## 6. formatters.py

Output formatting for:
- print_success(message) - green checkmark
- print_error(message, exception=None) - red X with details
- print_warning(message) - yellow warning
- format_table(data, headers) - tabulate table
- format_json(data, indent=2) - pretty JSON
- format_date(date) - consistent date format
- truncate(text, max_length) - with ellipsis

## 7. requirements.txt

Dependencies:
- requests>=2.28.0
- tabulate>=0.9.0
- python-dateutil>=2.8.0

Dev dependencies (separate or in pyproject.toml):
- pytest>=7.0.0
- pytest-cov>=4.0.0
- pytest-mock>=3.10.0
- responses>=0.22.0

Implement each module with:
- Comprehensive docstrings
- Type hints
- Error handling
- Unit testability (dependency injection where needed)
```

---

## Expected Outputs

After running this prompt:

1. **client.py** - Full HTTP client implementation
2. **config_manager.py** - Configuration loading/merging
3. **error_handler.py** - Exception hierarchy and handlers
4. **validators.py** - Input validation utilities
5. **formatters.py** - Output formatting helpers
6. **requirements.txt** - Project dependencies

---

## Verification

After creation:

```bash
# Test imports
python -c "from client import get_client; print('Client OK')"
python -c "from config_manager import get_config; print('Config OK')"
python -c "from error_handler import handle_errors; print('Errors OK')"
python -c "from validators import validate_required; print('Validators OK')"
python -c "from formatters import print_success; print('Formatters OK')"

# Run unit tests
pytest .claude/skills/shared/tests/ -v
```

---

## Next Steps

1. Write unit tests for each module
2. Test with real API credentials
3. Begin implementing first skill
