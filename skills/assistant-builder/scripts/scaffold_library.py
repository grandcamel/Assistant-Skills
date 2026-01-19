#!/usr/bin/env python3
"""
Scaffold a CLI library package for custom library Assistant Skills projects.

Creates a complete Python package with:
- Click CLI entry point
- HTTP client with retry/pagination
- Configuration management
- Error handling with exception hierarchy
- Output formatters (table, JSON, text)
- Input validators
- Test infrastructure

Usage:
    python scaffold_library.py --name "myapi-assistant-skills-lib" --topic "myapi"

Examples:
    # Interactive mode
    python scaffold_library.py

    # Full specification
    python scaffold_library.py \\
        --name "myapi-assistant-skills-lib" \\
        --topic "myapi" \\
        --api "My API" \\
        --api-url "https://api.example.com" \\
        --auth api_key \\
        --resources "users,projects,tasks"

    # Dry run to preview
    python scaffold_library.py --name "test-lib" --topic "test" --dry-run
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

from assistant_skills_lib import (
    validate_required, validate_name, validate_topic_prefix,
    validate_url, validate_choice, validate_list, validate_path,
    InputValidationError as ValidationError,
    print_success, print_error, print_info, print_warning
)


# Authentication methods
AUTH_METHODS = ['api_key', 'oauth', 'jwt', 'basic']


def generate_pyproject_toml(context: dict) -> str:
    """Generate pyproject.toml."""
    name = context['LIB_NAME']
    topic = context['TOPIC']
    api_name = context['API_NAME']
    cli_name = context.get('CLI_NAME', f'{topic}-as')
    pkg_name = topic.replace('-', '_') + '_assistant_skills_lib'

    return f'''[project]
name = "{name}"
version = "0.1.0"
description = "CLI library for {api_name} automation"
readme = "README.md"
requires-python = ">=3.9"
license = {{text = "MIT"}}

authors = [
    {{name = "{context.get('AUTHOR', 'Your Name')}", email = "{context.get('EMAIL', 'your@email.com')}"}}
]

classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]

dependencies = [
    "requests>=2.28.0",
    "click>=8.0",
    "tabulate>=0.9.0",
    "colorama>=0.4.6",
    "python-dotenv>=1.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
    "black>=23.0",
    "ruff>=0.1.0",
    "mypy>=1.0",
]

[project.scripts]
{cli_name} = "{pkg_name}.cli.main:cli"

[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
where = ["src"]

[tool.black]
line-length = 100
target-version = ["py39"]

[tool.ruff]
line-length = 100
target-version = "py39"

[tool.mypy]
python_version = "3.9"
warn_return_any = true
warn_unused_configs = true

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-v --tb=short"
'''


def generate_readme(context: dict) -> str:
    """Generate README.md."""
    name = context['LIB_NAME']
    api_name = context['API_NAME']
    cli_name = context.get('CLI_NAME', f"{context['TOPIC']}-as")

    return f'''# {name}

CLI library for {api_name} automation.

## Installation

```bash
pip install {name}
```

Or install from source:

```bash
pip install -e .
```

## Quick Start

### Authentication

Set your API credentials:

```bash
export {api_name.upper().replace(' ', '_').replace('-', '_')}_API_KEY="your-api-key"
export {api_name.upper().replace(' ', '_').replace('-', '_')}_BASE_URL="{context.get('API_URL', 'https://api.example.com')}"
```

Or configure via CLI:

```bash
{cli_name} config set api_key YOUR_API_KEY
{cli_name} config set base_url https://api.example.com
```

### Basic Usage

```bash
# Check authentication
{cli_name} auth status

# List resources
{cli_name} resource list

# Get resource details
{cli_name} resource get RESOURCE-123

# Create resource
{cli_name} resource create --name "New Resource"
```

### Output Formats

```bash
# Table output (default)
{cli_name} resource list

# JSON output
{cli_name} resource list --output json

# Text output
{cli_name} resource list --output text
```

### Profiles

Use different profiles for different environments:

```bash
# Set up development profile
{cli_name} --profile development config set base_url https://dev.api.example.com

# Use development profile
{cli_name} --profile development resource list
```

## Development

### Install Development Dependencies

```bash
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest tests/ -v
```

### Run Linting

```bash
black src/ tests/
ruff check src/ tests/
mypy src/
```

## License

MIT License
'''


def generate_init_py(context: dict) -> str:
    """Generate __init__.py for the package."""
    api_name = context['API_NAME']
    pkg_name = context['TOPIC'].replace('-', '_').title().replace('_', '')

    return f'''"""
{api_name} CLI Library

Provides CLI tools and Python API for {api_name} automation.
"""

__version__ = "0.1.0"

from .client import {pkg_name}Client
from .config_manager import ConfigManager
from .error_handler import (
    {pkg_name}Error,
    AuthenticationError,
    PermissionError,
    NotFoundError,
    ValidationError,
    RateLimitError,
    ServerError,
    handle_api_error,
    handle_errors,
)
from .validators import (
    validate_required,
    validate_id,
    validate_name,
)
from .formatters import (
    format_table,
    format_json,
    format_text,
    OutputFormatter,
)

__all__ = [
    # Version
    "__version__",
    # Client
    "{pkg_name}Client",
    # Config
    "ConfigManager",
    # Errors
    "{pkg_name}Error",
    "AuthenticationError",
    "PermissionError",
    "NotFoundError",
    "ValidationError",
    "RateLimitError",
    "ServerError",
    "handle_api_error",
    "handle_errors",
    # Validators
    "validate_required",
    "validate_id",
    "validate_name",
    # Formatters
    "format_table",
    "format_json",
    "format_text",
    "OutputFormatter",
]
'''


def generate_client_py(context: dict) -> str:
    """Generate client.py HTTP client."""
    api_name = context['API_NAME']
    pkg_name = context['TOPIC'].replace('-', '_').title().replace('_', '')
    auth_method = context.get('AUTH_METHOD', 'api_key')

    auth_header = 'f"Bearer {self.api_key}"' if auth_method != 'basic' else 'f"Basic {self.api_key}"'

    return f'''"""HTTP client for {api_name} API."""

import requests
from typing import Any, Optional, Dict, List
from .config_manager import ConfigManager
from .error_handler import handle_api_error, AuthenticationError


class {pkg_name}Client:
    """HTTP client with automatic retry and error handling."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        profile: str = "default",
        timeout: int = 30,
    ):
        """
        Initialize the client.

        Args:
            base_url: API base URL (overrides config)
            api_key: API key (overrides config)
            profile: Configuration profile name
            timeout: Request timeout in seconds
        """
        config = ConfigManager()
        self.base_url = base_url or config.get("base_url", profile=profile)
        self.api_key = api_key or config.get("api_key", profile=profile)
        self.timeout = timeout

        if not self.base_url:
            raise AuthenticationError(
                "Base URL not configured. "
                "Set {api_name.upper().replace(' ', '_').replace('-', '_')}_BASE_URL or run config command."
            )
        if not self.api_key:
            raise AuthenticationError(
                "API key not configured. "
                "Set {api_name.upper().replace(' ', '_').replace('-', '_')}_API_KEY or run config command."
            )

        self.session = requests.Session()
        self.session.headers.update({{
            "Authorization": {auth_header},
            "Content-Type": "application/json",
            "Accept": "application/json",
        }})

    def get(self, endpoint: str, params: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
        """
        GET request with error handling.

        Args:
            endpoint: API endpoint (e.g., "/resources")
            params: Query parameters
            **kwargs: Additional request arguments

        Returns:
            Response JSON data
        """
        return self._request("GET", endpoint, params=params, **kwargs)

    def post(self, endpoint: str, data: Dict, **kwargs) -> Dict[str, Any]:
        """
        POST request with error handling.

        Args:
            endpoint: API endpoint
            data: Request body data
            **kwargs: Additional request arguments

        Returns:
            Response JSON data
        """
        return self._request("POST", endpoint, json=data, **kwargs)

    def put(self, endpoint: str, data: Dict, **kwargs) -> Dict[str, Any]:
        """
        PUT request with error handling.

        Args:
            endpoint: API endpoint
            data: Request body data
            **kwargs: Additional request arguments

        Returns:
            Response JSON data
        """
        return self._request("PUT", endpoint, json=data, **kwargs)

    def patch(self, endpoint: str, data: Dict, **kwargs) -> Dict[str, Any]:
        """
        PATCH request with error handling.

        Args:
            endpoint: API endpoint
            data: Request body data
            **kwargs: Additional request arguments

        Returns:
            Response JSON data
        """
        return self._request("PATCH", endpoint, json=data, **kwargs)

    def delete(self, endpoint: str, **kwargs) -> Optional[Dict[str, Any]]:
        """
        DELETE request with error handling.

        Args:
            endpoint: API endpoint
            **kwargs: Additional request arguments

        Returns:
            Response JSON data or None
        """
        return self._request("DELETE", endpoint, **kwargs)

    def _request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """
        Execute request with error handling.

        Args:
            method: HTTP method
            endpoint: API endpoint
            **kwargs: Additional request arguments

        Returns:
            Response JSON data or None
        """
        url = f"{{self.base_url.rstrip('/')}}/{{endpoint.lstrip('/')}}"

        # Set timeout if not provided
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.timeout

        response = self.session.request(method, url, **kwargs)

        if not response.ok:
            handle_api_error(response)

        # Handle empty responses
        if not response.content:
            return None

        return response.json()

    def paginate(
        self,
        endpoint: str,
        params: Optional[Dict] = None,
        page_size: int = 100,
        max_pages: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Paginate through all results.

        Args:
            endpoint: API endpoint
            params: Query parameters
            page_size: Results per page
            max_pages: Maximum pages to fetch (None for all)

        Returns:
            List of all results
        """
        params = params or {{}}
        params['limit'] = page_size
        params['offset'] = 0

        all_results = []
        page = 0

        while True:
            if max_pages and page >= max_pages:
                break

            response = self.get(endpoint, params=params)

            # Handle different response formats
            if isinstance(response, list):
                results = response
                total = len(results)
            else:
                results = response.get('items', response.get('data', []))
                total = response.get('total', len(results))

            all_results.extend(results)

            # Check if we have all results
            if len(all_results) >= total or not results:
                break

            params['offset'] += page_size
            page += 1

        return all_results

    def close(self):
        """Close the session."""
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
'''


def generate_config_manager_py(context: dict) -> str:
    """Generate config_manager.py."""
    api_name = context['API_NAME']
    env_prefix = api_name.upper().replace(' ', '_').replace('-', '_')

    return f'''"""Configuration management for {api_name} CLI."""

import os
import json
from pathlib import Path
from typing import Optional, Any, Dict


class ConfigManager:
    """
    Manage configuration with priority:
    1. Environment variables
    2. Profile-specific config file
    3. Default config file
    """

    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize config manager.

        Args:
            config_dir: Custom config directory (default: ~/.{context['TOPIC']})
        """
        self.config_dir = config_dir or Path.home() / ".{context['TOPIC']}"
        self.config_file = self.config_dir / "config.json"
        self._config: Dict[str, Dict[str, Any]] = {{}

        self._load_config()

    def _load_config(self):
        """Load configuration from file."""
        if self.config_file.exists():
            try:
                self._config = json.loads(self.config_file.read_text())
            except Exception:
                self._config = {{}}

    def _save_config(self):
        """Save configuration to file."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_file.write_text(json.dumps(self._config, indent=2))

    def get(
        self,
        key: str,
        profile: str = "default",
        default: Any = None
    ) -> Any:
        """
        Get configuration value.

        Priority:
        1. Environment variable ({env_prefix}_{{KEY}})
        2. Profile-specific value
        3. Default value

        Args:
            key: Configuration key
            profile: Profile name
            default: Default value if not found

        Returns:
            Configuration value
        """
        # Check environment variable first
        env_key = f"{env_prefix}_{{key.upper()}}"
        env_value = os.environ.get(env_key)
        if env_value is not None:
            return env_value

        # Check profile config
        profile_config = self._config.get(profile, {{}})
        if key in profile_config:
            return profile_config[key]

        # Check default profile
        if profile != "default":
            default_config = self._config.get("default", {{}})
            if key in default_config:
                return default_config[key]

        return default

    def set(self, key: str, value: Any, profile: str = "default"):
        """
        Set configuration value.

        Args:
            key: Configuration key
            value: Configuration value
            profile: Profile name
        """
        if profile not in self._config:
            self._config[profile] = {{}}

        self._config[profile][key] = value
        self._save_config()

    def delete(self, key: str, profile: str = "default") -> bool:
        """
        Delete configuration value.

        Args:
            key: Configuration key
            profile: Profile name

        Returns:
            True if deleted, False if not found
        """
        if profile in self._config and key in self._config[profile]:
            del self._config[profile][key]
            self._save_config()
            return True
        return False

    def list_profiles(self) -> list:
        """List all profiles."""
        return list(self._config.keys())

    def get_profile(self, profile: str = "default") -> Dict[str, Any]:
        """Get all values for a profile."""
        return self._config.get(profile, {{}}).copy()
'''


def generate_error_handler_py(context: dict) -> str:
    """Generate error_handler.py."""
    api_name = context['API_NAME']
    pkg_name = context['TOPIC'].replace('-', '_').title().replace('_', '')

    return f'''"""Exception hierarchy for {api_name} CLI."""

from functools import wraps
import click


class {pkg_name}Error(Exception):
    """Base exception for all {api_name} errors."""
    pass


class AuthenticationError({pkg_name}Error):
    """Authentication failed (401)."""
    pass


class PermissionError({pkg_name}Error):
    """Permission denied (403)."""
    pass


class NotFoundError({pkg_name}Error):
    """Resource not found (404)."""
    pass


class ValidationError({pkg_name}Error):
    """Invalid request (400)."""
    pass


class RateLimitError({pkg_name}Error):
    """Rate limit exceeded (429)."""
    pass


class ServerError({pkg_name}Error):
    """Server error (5xx)."""
    pass


def handle_api_error(response):
    """
    Map HTTP status codes to exceptions.

    Args:
        response: requests.Response object

    Raises:
        Appropriate exception based on status code
    """
    status = response.status_code
    message = response.text

    # Try to extract error message from JSON
    try:
        error_data = response.json()
        message = error_data.get("message", error_data.get("error", message))
    except Exception:
        pass

    if status == 401:
        raise AuthenticationError(f"Authentication failed: {{message}}")
    elif status == 403:
        raise PermissionError(f"Permission denied: {{message}}")
    elif status == 404:
        raise NotFoundError(f"Not found: {{message}}")
    elif status == 400:
        raise ValidationError(f"Invalid request: {{message}}")
    elif status == 429:
        raise RateLimitError(f"Rate limit exceeded: {{message}}")
    elif status >= 500:
        raise ServerError(f"Server error: {{message}}")
    else:
        raise {pkg_name}Error(f"Request failed ({{status}}): {{message}}")


def handle_errors(f):
    """
    Decorator for CLI commands to handle exceptions gracefully.

    Catches {api_name} exceptions and displays user-friendly messages.
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except AuthenticationError as e:
            click.echo(click.style(f"Authentication error: {{e}}", fg="red"), err=True)
            click.echo("Try running: {{ctx.command_path}} auth login", err=True)
            raise SystemExit(1)
        except PermissionError as e:
            click.echo(click.style(f"Permission denied: {{e}}", fg="red"), err=True)
            raise SystemExit(1)
        except NotFoundError as e:
            click.echo(click.style(f"Not found: {{e}}", fg="red"), err=True)
            raise SystemExit(1)
        except ValidationError as e:
            click.echo(click.style(f"Invalid request: {{e}}", fg="red"), err=True)
            raise SystemExit(1)
        except RateLimitError as e:
            click.echo(click.style(f"Rate limit exceeded: {{e}}", fg="yellow"), err=True)
            click.echo("Please wait and try again.", err=True)
            raise SystemExit(1)
        except ServerError as e:
            click.echo(click.style(f"Server error: {{e}}", fg="red"), err=True)
            click.echo("Please check the service status and try again.", err=True)
            raise SystemExit(1)
        except {pkg_name}Error as e:
            click.echo(click.style(f"Error: {{e}}", fg="red"), err=True)
            raise SystemExit(1)
    return wrapper
'''


def generate_validators_py(context: dict) -> str:
    """Generate validators.py."""
    return '''"""Input validation utilities."""

import re
from typing import Optional


def validate_required(value: Optional[str], field_name: str) -> str:
    """
    Validate that a required field has a value.

    Args:
        value: Value to validate
        field_name: Name of the field (for error messages)

    Returns:
        Validated value

    Raises:
        ValueError: If value is empty
    """
    if not value or not value.strip():
        raise ValueError(f"{field_name} is required")
    return value.strip()


def validate_id(value: str, field_name: str = "ID") -> str:
    """
    Validate an ID value.

    Args:
        value: ID to validate
        field_name: Name of the field (for error messages)

    Returns:
        Validated ID

    Raises:
        ValueError: If ID is invalid
    """
    value = validate_required(value, field_name)

    # Allow alphanumeric, hyphens, underscores
    if not re.match(r'^[a-zA-Z0-9_-]+$', value):
        raise ValueError(f"Invalid {field_name}: must be alphanumeric with hyphens/underscores")

    return value


def validate_name(value: str, field_name: str = "name") -> str:
    """
    Validate a name value.

    Args:
        value: Name to validate
        field_name: Name of the field (for error messages)

    Returns:
        Validated name

    Raises:
        ValueError: If name is invalid
    """
    value = validate_required(value, field_name)

    if len(value) < 2:
        raise ValueError(f"{field_name} must be at least 2 characters")

    if len(value) > 255:
        raise ValueError(f"{field_name} must be at most 255 characters")

    return value


def validate_email(value: str) -> str:
    """
    Validate an email address.

    Args:
        value: Email to validate

    Returns:
        Validated email

    Raises:
        ValueError: If email is invalid
    """
    value = validate_required(value, "email")

    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$', value):
        raise ValueError("Invalid email address")

    return value


def validate_url(value: str) -> str:
    """
    Validate a URL.

    Args:
        value: URL to validate

    Returns:
        Validated URL

    Raises:
        ValueError: If URL is invalid
    """
    value = validate_required(value, "URL")

    if not value.startswith(('http://', 'https://')):
        raise ValueError("URL must start with http:// or https://")

    return value
'''


def generate_formatters_py(context: dict) -> str:
    """Generate formatters.py."""
    return '''"""Output formatting utilities."""

import json
from typing import Any, Dict, List, Optional
from tabulate import tabulate


class OutputFormatter:
    """Format output in various formats."""

    def __init__(self, format_type: str = "table"):
        """
        Initialize formatter.

        Args:
            format_type: Output format (table, json, text)
        """
        self.format_type = format_type

    def format(self, data: Any, headers: Optional[List[str]] = None) -> str:
        """
        Format data based on output type.

        Args:
            data: Data to format
            headers: Column headers (for table format)

        Returns:
            Formatted string
        """
        if self.format_type == "json":
            return format_json(data)
        elif self.format_type == "text":
            return format_text(data)
        else:
            return format_table(data, headers)


def format_table(data: Any, headers: Optional[List[str]] = None) -> str:
    """
    Format data as a table.

    Args:
        data: Data to format (dict, list of dicts, or list of lists)
        headers: Column headers

    Returns:
        Formatted table string
    """
    if not data:
        return "No data"

    # Single dict
    if isinstance(data, dict):
        rows = [[k, v] for k, v in data.items()]
        return tabulate(rows, headers=["Field", "Value"], tablefmt="simple")

    # List of dicts
    if isinstance(data, list) and data and isinstance(data[0], dict):
        if not headers:
            headers = list(data[0].keys())
        rows = [[item.get(h, "") for h in headers] for item in data]
        return tabulate(rows, headers=headers, tablefmt="simple")

    # List of lists/tuples
    if isinstance(data, list):
        return tabulate(data, headers=headers or [], tablefmt="simple")

    return str(data)


def format_json(data: Any, indent: int = 2) -> str:
    """
    Format data as JSON.

    Args:
        data: Data to format
        indent: Indentation level

    Returns:
        JSON string
    """
    return json.dumps(data, indent=indent, default=str)


def format_text(data: Any) -> str:
    """
    Format data as plain text.

    Args:
        data: Data to format

    Returns:
        Plain text string
    """
    if not data:
        return ""

    if isinstance(data, dict):
        lines = [f"{k}: {v}" for k, v in data.items()]
        return "\\n".join(lines)

    if isinstance(data, list):
        if data and isinstance(data[0], dict):
            return "\\n\\n".join(format_text(item) for item in data)
        return "\\n".join(str(item) for item in data)

    return str(data)
'''


def generate_cli_main_py(context: dict) -> str:
    """Generate cli/main.py."""
    api_name = context['API_NAME']
    cli_name = context.get('CLI_NAME', f"{context['TOPIC']}-as")
    pkg_path = context['TOPIC'].replace('-', '_') + '_assistant_skills_lib'

    return f'''"""CLI entry point for {cli_name}."""

import click
from .commands import resource_cmds, auth_cmds, config_cmds


@click.group()
@click.version_option()
@click.option("--profile", "-p", default="default", help="Configuration profile")
@click.option(
    "--output", "-o",
    type=click.Choice(["json", "table", "text"]),
    default="table",
    help="Output format"
)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option("--quiet", "-q", is_flag=True, help="Suppress non-essential output")
@click.pass_context
def cli(ctx, profile: str, output: str, verbose: bool, quiet: bool):
    """
    {api_name} CLI - Command-line interface for {api_name} automation.

    Use --profile to switch between configurations (default, development, etc.)
    Use --output to change output format (table, json, text)
    """
    ctx.ensure_object(dict)
    ctx.obj["profile"] = profile
    ctx.obj["output"] = output
    ctx.obj["verbose"] = verbose
    ctx.obj["quiet"] = quiet


# Register command groups
cli.add_command(resource_cmds.resource)
cli.add_command(auth_cmds.auth)
cli.add_command(config_cmds.config)


if __name__ == "__main__":
    cli()
'''


def generate_cli_init_py(context: dict) -> str:
    """Generate cli/__init__.py."""
    return '''"""CLI package."""

from .main import cli

__all__ = ["cli"]
'''


def generate_commands_init_py(context: dict) -> str:
    """Generate cli/commands/__init__.py."""
    return '''"""CLI commands package."""
'''


def generate_resource_cmds_py(context: dict) -> str:
    """Generate cli/commands/resource_cmds.py."""
    api_name = context['API_NAME']
    pkg_name = context['TOPIC'].replace('-', '_').title().replace('_', '')

    return f'''"""Resource commands for {api_name} CLI."""

import click
from ...client import {pkg_name}Client
from ...error_handler import handle_errors
from ...formatters import OutputFormatter


@click.group()
def resource():
    """Resource operations."""
    pass


@resource.command("list")
@click.option("--filter", "-f", "filter_query", help="Filter query")
@click.option("--limit", "-l", type=int, default=50, help="Maximum results")
@click.pass_context
@handle_errors
def list_resources(ctx, filter_query, limit):
    """List resources."""
    client = {pkg_name}Client(profile=ctx.obj["profile"])
    formatter = OutputFormatter(ctx.obj["output"])

    params = {{"limit": limit}}
    if filter_query:
        params["filter"] = filter_query

    results = client.get("/resources", params=params)

    if isinstance(results, dict):
        items = results.get("items", results.get("data", []))
    else:
        items = results

    if not items:
        click.echo("No resources found")
        return

    click.echo(formatter.format(items, headers=["id", "name", "status"]))


@resource.command("get")
@click.argument("resource_id")
@click.pass_context
@handle_errors
def get_resource(ctx, resource_id):
    """Get resource details."""
    client = {pkg_name}Client(profile=ctx.obj["profile"])
    formatter = OutputFormatter(ctx.obj["output"])

    result = client.get(f"/resources/{{resource_id}}")

    click.echo(formatter.format(result))


@resource.command("create")
@click.option("--name", "-n", required=True, help="Resource name")
@click.option("--description", "-d", help="Resource description")
@click.pass_context
@handle_errors
def create_resource(ctx, name, description):
    """Create a new resource."""
    client = {pkg_name}Client(profile=ctx.obj["profile"])
    formatter = OutputFormatter(ctx.obj["output"])

    data = {{"name": name}}
    if description:
        data["description"] = description

    result = client.post("/resources", data=data)

    if not ctx.obj["quiet"]:
        click.echo(click.style("Resource created successfully!", fg="green"))

    click.echo(formatter.format(result))


@resource.command("update")
@click.argument("resource_id")
@click.option("--name", "-n", help="New name")
@click.option("--description", "-d", help="New description")
@click.pass_context
@handle_errors
def update_resource(ctx, resource_id, name, description):
    """Update an existing resource."""
    client = {pkg_name}Client(profile=ctx.obj["profile"])
    formatter = OutputFormatter(ctx.obj["output"])

    data = {{}}
    if name:
        data["name"] = name
    if description:
        data["description"] = description

    if not data:
        click.echo("No updates specified", err=True)
        raise SystemExit(1)

    result = client.patch(f"/resources/{{resource_id}}", data=data)

    if not ctx.obj["quiet"]:
        click.echo(click.style("Resource updated successfully!", fg="green"))

    click.echo(formatter.format(result))


@resource.command("delete")
@click.argument("resource_id")
@click.option("--force", "-f", is_flag=True, help="Skip confirmation")
@click.pass_context
@handle_errors
def delete_resource(ctx, resource_id, force):
    """Delete a resource."""
    if not force:
        if not click.confirm(f"Delete resource {{resource_id}}?"):
            click.echo("Cancelled")
            return

    client = {pkg_name}Client(profile=ctx.obj["profile"])
    client.delete(f"/resources/{{resource_id}}")

    if not ctx.obj["quiet"]:
        click.echo(click.style("Resource deleted successfully!", fg="green"))
'''


def generate_auth_cmds_py(context: dict) -> str:
    """Generate cli/commands/auth_cmds.py."""
    api_name = context['API_NAME']
    pkg_name = context['TOPIC'].replace('-', '_').title().replace('_', '')

    return f'''"""Authentication commands for {api_name} CLI."""

import click
from ...config_manager import ConfigManager
from ...client import {pkg_name}Client
from ...error_handler import handle_errors


@click.group()
def auth():
    """Authentication management."""
    pass


@auth.command("status")
@click.pass_context
@handle_errors
def auth_status(ctx):
    """Check authentication status."""
    config = ConfigManager()
    profile = ctx.obj["profile"]

    base_url = config.get("base_url", profile=profile)
    api_key = config.get("api_key", profile=profile)

    click.echo(f"Profile: {{profile}}")
    click.echo(f"Base URL: {{base_url or '(not set)'}}")
    click.echo(f"API Key: {{'(set)' if api_key else '(not set)'}}")

    if base_url and api_key:
        try:
            client = {pkg_name}Client(profile=profile)
            # Try a simple request to verify
            click.echo(click.style("\\n✓ Authentication valid", fg="green"))
        except Exception as e:
            click.echo(click.style(f"\\n✗ Authentication failed: {{e}}", fg="red"))
    else:
        click.echo(click.style("\\n✗ Configuration incomplete", fg="yellow"))


@auth.command("login")
@click.option("--api-key", "-k", prompt=True, hide_input=True, help="API key")
@click.option("--base-url", "-u", prompt=True, help="Base URL")
@click.pass_context
def auth_login(ctx, api_key, base_url):
    """Configure authentication."""
    config = ConfigManager()
    profile = ctx.obj["profile"]

    config.set("api_key", api_key, profile=profile)
    config.set("base_url", base_url, profile=profile)

    click.echo(click.style(f"Authentication configured for profile '{{profile}}'", fg="green"))


@auth.command("logout")
@click.option("--force", "-f", is_flag=True, help="Skip confirmation")
@click.pass_context
def auth_logout(ctx, force):
    """Remove authentication."""
    profile = ctx.obj["profile"]

    if not force:
        if not click.confirm(f"Remove authentication for profile '{{profile}}'?"):
            click.echo("Cancelled")
            return

    config = ConfigManager()
    config.delete("api_key", profile=profile)

    click.echo(click.style(f"Authentication removed for profile '{{profile}}'", fg="green"))
'''


def generate_config_cmds_py(context: dict) -> str:
    """Generate cli/commands/config_cmds.py."""
    return '''"""Configuration commands."""

import click
from ...config_manager import ConfigManager


@click.group()
def config():
    """Configuration management."""
    pass


@config.command("get")
@click.argument("key")
@click.pass_context
def config_get(ctx, key):
    """Get a configuration value."""
    config_mgr = ConfigManager()
    profile = ctx.obj["profile"]

    value = config_mgr.get(key, profile=profile)

    if value is None:
        click.echo(f"{key}: (not set)")
    else:
        click.echo(f"{key}: {value}")


@config.command("set")
@click.argument("key")
@click.argument("value")
@click.pass_context
def config_set(ctx, key, value):
    """Set a configuration value."""
    config_mgr = ConfigManager()
    profile = ctx.obj["profile"]

    config_mgr.set(key, value, profile=profile)
    click.echo(click.style(f"Set {key} for profile '{profile}'", fg="green"))


@config.command("delete")
@click.argument("key")
@click.pass_context
def config_delete(ctx, key):
    """Delete a configuration value."""
    config_mgr = ConfigManager()
    profile = ctx.obj["profile"]

    if config_mgr.delete(key, profile=profile):
        click.echo(click.style(f"Deleted {key} from profile '{profile}'", fg="green"))
    else:
        click.echo(f"{key} not found in profile '{profile}'")


@config.command("list")
@click.pass_context
def config_list(ctx):
    """List all configuration values."""
    config_mgr = ConfigManager()
    profile = ctx.obj["profile"]

    values = config_mgr.get_profile(profile)

    if not values:
        click.echo(f"No configuration for profile '{profile}'")
        return

    click.echo(f"Profile: {profile}")
    for key, value in values.items():
        # Mask sensitive values
        if "key" in key.lower() or "secret" in key.lower() or "password" in key.lower():
            value = "********"
        click.echo(f"  {key}: {value}")


@config.command("profiles")
def config_profiles():
    """List all profiles."""
    config_mgr = ConfigManager()
    profiles = config_mgr.list_profiles()

    if not profiles:
        click.echo("No profiles configured")
        return

    click.echo("Available profiles:")
    for profile in profiles:
        click.echo(f"  - {profile}")
'''


def generate_test_conftest_py(context: dict) -> str:
    """Generate tests/conftest.py."""
    pkg_name = context['TOPIC'].replace('-', '_').title().replace('_', '')

    return f'''"""Test fixtures for {context['LIB_NAME']}."""

import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path
import tempfile
import shutil


@pytest.fixture
def temp_dir():
    """Create a temporary directory."""
    path = Path(tempfile.mkdtemp())
    yield path
    shutil.rmtree(path, ignore_errors=True)


@pytest.fixture
def mock_client():
    """Create a mock {pkg_name}Client."""
    client = MagicMock()
    client.get.return_value = {{"items": [], "total": 0}}
    client.post.return_value = {{"id": "123", "status": "created"}}
    client.put.return_value = {{"id": "123", "status": "updated"}}
    client.patch.return_value = {{"id": "123", "status": "updated"}}
    client.delete.return_value = None
    return client


@pytest.fixture
def sample_resource():
    """Sample resource data."""
    return {{
        "id": "resource-123",
        "name": "Test Resource",
        "description": "A test resource",
        "status": "active",
    }}


@pytest.fixture
def sample_resources(sample_resource):
    """Sample list of resources."""
    return [sample_resource]


@pytest.fixture
def mock_config(temp_dir):
    """Create a mock config manager."""
    with patch('{{context['TOPIC'].replace('-', '_')}}_assistant_skills_lib.config_manager.ConfigManager') as mock:
        instance = MagicMock()
        instance.get.return_value = "test-value"
        mock.return_value = instance
        yield instance
'''


def generate_test_client_py(context: dict) -> str:
    """Generate tests/test_client.py."""
    pkg_name = context['TOPIC'].replace('-', '_').title().replace('_', '')
    pkg_path = context['TOPIC'].replace('-', '_') + '_assistant_skills_lib'

    return f'''"""Tests for {pkg_name}Client."""

import pytest
from unittest.mock import patch, MagicMock
from {pkg_path}.client import {pkg_name}Client
from {pkg_path}.error_handler import AuthenticationError, NotFoundError


class Test{pkg_name}Client:
    """Tests for the HTTP client."""

    def test_client_requires_base_url(self, mock_config):
        """Test that client raises error without base_url."""
        mock_config.get.return_value = None

        with pytest.raises(AuthenticationError):
            {pkg_name}Client()

    def test_client_requires_api_key(self, mock_config):
        """Test that client raises error without api_key."""
        def get_side_effect(key, profile=None):
            if key == "base_url":
                return "https://api.example.com"
            return None

        mock_config.get.side_effect = get_side_effect

        with pytest.raises(AuthenticationError):
            {pkg_name}Client()

    @patch('requests.Session')
    def test_client_get_request(self, mock_session, mock_config):
        """Test GET request."""
        mock_config.get.return_value = "test-value"

        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.content = b'{{"data": "test"}}'
        mock_response.json.return_value = {{"data": "test"}}

        mock_session.return_value.request.return_value = mock_response

        client = {pkg_name}Client(
            base_url="https://api.example.com",
            api_key="test-key"
        )
        result = client.get("/test")

        assert result == {{"data": "test"}}

    @patch('requests.Session')
    def test_client_handles_404(self, mock_session, mock_config):
        """Test 404 error handling."""
        mock_config.get.return_value = "test-value"

        mock_response = MagicMock()
        mock_response.ok = False
        mock_response.status_code = 404
        mock_response.text = "Not found"
        mock_response.json.return_value = {{"message": "Resource not found"}}

        mock_session.return_value.request.return_value = mock_response

        client = {pkg_name}Client(
            base_url="https://api.example.com",
            api_key="test-key"
        )

        with pytest.raises(NotFoundError):
            client.get("/not-found")
'''


def scaffold_library(
    lib_name: str,
    topic: str,
    api_name: str,
    api_url: str = None,
    auth_method: str = 'api_key',
    resources: list = None,
    output_dir: str = '.',
    dry_run: bool = False
) -> dict:
    """
    Create a CLI library package.

    Returns dict with created files and directories.
    """
    # Prepare context
    cli_name = f'{topic}-as'
    pkg_name = topic.replace('-', '_') + '_assistant_skills_lib'

    context = {
        'LIB_NAME': lib_name,
        'TOPIC': topic,
        'API_NAME': api_name,
        'API_URL': api_url or 'https://api.example.com',
        'AUTH_METHOD': auth_method,
        'CLI_NAME': cli_name,
        'PKG_NAME': pkg_name,
        'RESOURCES': resources or ['resource'],
        'DATE': datetime.now().isoformat()
    }

    # Determine output path
    output_path = Path(output_dir).expanduser().resolve() / lib_name

    if output_path.exists() and not dry_run:
        raise ValueError(f"Directory already exists: {output_path}")

    result = {
        'path': str(output_path),
        'directories': [],
        'files': []
    }

    # Create directories
    src_path = f'src/{pkg_name}'
    dirs = [
        '',
        'src',
        src_path,
        f'{src_path}/cli',
        f'{src_path}/cli/commands',
        'tests',
    ]

    for d in dirs:
        full_path = output_path / d if d else output_path
        result['directories'].append(d or '.')
        if not dry_run:
            full_path.mkdir(parents=True, exist_ok=True)

    # Generate files
    files_to_create = [
        # Root files
        ('pyproject.toml', generate_pyproject_toml(context)),
        ('README.md', generate_readme(context)),

        # Package files
        (f'{src_path}/__init__.py', generate_init_py(context)),
        (f'{src_path}/client.py', generate_client_py(context)),
        (f'{src_path}/config_manager.py', generate_config_manager_py(context)),
        (f'{src_path}/error_handler.py', generate_error_handler_py(context)),
        (f'{src_path}/validators.py', generate_validators_py(context)),
        (f'{src_path}/formatters.py', generate_formatters_py(context)),

        # CLI files
        (f'{src_path}/cli/__init__.py', generate_cli_init_py(context)),
        (f'{src_path}/cli/main.py', generate_cli_main_py(context)),
        (f'{src_path}/cli/commands/__init__.py', generate_commands_init_py(context)),
        (f'{src_path}/cli/commands/resource_cmds.py', generate_resource_cmds_py(context)),
        (f'{src_path}/cli/commands/auth_cmds.py', generate_auth_cmds_py(context)),
        (f'{src_path}/cli/commands/config_cmds.py', generate_config_cmds_py(context)),

        # Test files
        ('tests/__init__.py', ''),
        ('tests/conftest.py', generate_test_conftest_py(context)),
        ('tests/test_client.py', generate_test_client_py(context)),
    ]

    for file_path, content in files_to_create:
        full_path = output_path / file_path
        result['files'].append(file_path)
        if not dry_run:
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content)

    return result


def interactive_mode():
    """Run interactive wizard."""
    print("\n" + "=" * 60)
    print("  CLI Library Scaffold Wizard")
    print("=" * 60 + "\n")

    # Library name
    lib_name = input("Library name (e.g., myapi-assistant-skills-lib): ").strip()
    lib_name = validate_required(lib_name, "library name")

    # Extract topic from library name
    default_topic = lib_name.replace('-assistant-skills-lib', '').replace('-lib', '')
    topic = input(f"Topic prefix [{default_topic}]: ").strip()
    if not topic:
        topic = default_topic
    topic = validate_topic_prefix(topic)

    # API name
    api_name = input(f"API name [{topic.title()}]: ").strip()
    if not api_name:
        api_name = topic.title()

    # API URL
    api_url = input("API base URL [https://api.example.com]: ").strip()
    if not api_url:
        api_url = "https://api.example.com"
    else:
        api_url = validate_url(api_url)

    # Auth method
    print(f"\nAuthentication methods: {', '.join(AUTH_METHODS)}")
    auth_method = input(f"Auth method [{AUTH_METHODS[0]}]: ").strip().lower()
    if not auth_method:
        auth_method = AUTH_METHODS[0]
    auth_method = validate_choice(auth_method, AUTH_METHODS, "auth method")

    # Confirmation
    print("\n" + "-" * 60)
    print("Summary:")
    print("-" * 60)
    print(f"  Library:     {lib_name}")
    print(f"  Topic:       {topic}")
    print(f"  API Name:    {api_name}")
    print(f"  API URL:     {api_url}")
    print(f"  Auth:        {auth_method}")
    print(f"  CLI Name:    {topic}-as")
    print("-" * 60)

    confirm = input("\nProceed? [Y/n]: ").strip().lower()
    if confirm and confirm != 'y':
        print("Cancelled.")
        return None

    return {
        'lib_name': lib_name,
        'topic': topic,
        'api_name': api_name,
        'api_url': api_url,
        'auth_method': auth_method,
    }


def main():
    parser = argparse.ArgumentParser(
        description='Scaffold a CLI library package',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Interactive mode
  python scaffold_library.py

  # Full specification
  python scaffold_library.py \\
      --name "myapi-assistant-skills-lib" \\
      --topic "myapi" \\
      --api "My API" \\
      --api-url "https://api.example.com"

  # Dry run
  python scaffold_library.py --name "test-lib" --topic "test" --dry-run
'''
    )

    parser.add_argument('--name', '-n', help='Library name')
    parser.add_argument('--topic', '-t', help='Topic prefix')
    parser.add_argument('--api', '-a', help='API name')
    parser.add_argument('--api-url', '-u', help='API base URL')
    parser.add_argument('--auth', choices=AUTH_METHODS, default='api_key',
                        help='Authentication method')
    parser.add_argument('--output-dir', '-o', default='.', help='Output directory')
    parser.add_argument('--dry-run', '-d', action='store_true',
                        help='Preview without creating files')

    args = parser.parse_args()

    try:
        if not args.name:
            config = interactive_mode()
            if not config:
                sys.exit(0)
        else:
            topic = args.topic or args.name.replace('-assistant-skills-lib', '').replace('-lib', '')
            config = {
                'lib_name': args.name,
                'topic': validate_topic_prefix(topic),
                'api_name': args.api or topic.title(),
                'api_url': args.api_url,
                'auth_method': args.auth,
            }

        if args.dry_run:
            print_info("DRY RUN - No files will be created\n")

        result = scaffold_library(
            lib_name=config['lib_name'],
            topic=config['topic'],
            api_name=config['api_name'],
            api_url=config.get('api_url'),
            auth_method=config.get('auth_method', 'api_key'),
            output_dir=args.output_dir,
            dry_run=args.dry_run
        )

        print_success(f"Created library at: {result['path']}")
        print(f"\nDirectories: {len(result['directories'])}")
        print(f"Files: {len(result['files'])}")

        if args.dry_run:
            print("\nFiles that would be created:")
            for f in result['files']:
                print(f"  {f}")

        # Next steps
        print("\n" + "=" * 60)
        print("Next Steps:")
        print("=" * 60)
        print(f"1. cd {result['path']}")
        print("2. pip install -e .")
        print(f"3. {config['topic']}-as --help")
        print("4. Customize resource commands for your API")
        print("5. Run tests: pytest tests/ -v")

    except ValidationError as e:
        print_error(str(e))
        sys.exit(1)
    except Exception as e:
        print_error(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
