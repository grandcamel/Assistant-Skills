"""
Validators for Assistant Builder

Provides input validation utilities for user inputs and paths.

Usage:
    from validators import validate_required, validate_path, validate_name

    name = validate_name(user_input)  # Raises ValueError if invalid
    path = validate_path(path_input)  # Returns validated Path
"""

import re
from pathlib import Path
from typing import List, Optional, Union


class ValidationError(ValueError):
    """Custom exception for validation errors with helpful messages."""

    def __init__(self, message: str, field: str = None, suggestion: str = None):
        self.field = field
        self.suggestion = suggestion
        full_message = message
        if suggestion:
            full_message += f"\nSuggestion: {suggestion}"
        super().__init__(full_message)


def validate_required(value: Optional[str], field_name: str = "value") -> str:
    """
    Validate that a value is provided and not empty.

    Args:
        value: Value to validate
        field_name: Name of field for error message

    Returns:
        Stripped value string

    Raises:
        ValidationError: If value is None or empty
    """
    if value is None:
        raise ValidationError(f"{field_name} is required", field=field_name)

    stripped = str(value).strip()
    if not stripped:
        raise ValidationError(f"{field_name} cannot be empty", field=field_name)

    return stripped


def validate_name(
    name: str,
    field_name: str = "name",
    allow_dashes: bool = True,
    allow_underscores: bool = True,
    min_length: int = 1,
    max_length: int = 64
) -> str:
    """
    Validate a name (project name, skill name, etc).

    Args:
        name: Name to validate
        field_name: Field name for error messages
        allow_dashes: Allow hyphens in name
        allow_underscores: Allow underscores in name
        min_length: Minimum name length
        max_length: Maximum name length

    Returns:
        Validated name string

    Raises:
        ValidationError: If name is invalid
    """
    name = validate_required(name, field_name)

    # Check length
    if len(name) < min_length:
        raise ValidationError(
            f"{field_name} must be at least {min_length} characters",
            field=field_name
        )

    if len(name) > max_length:
        raise ValidationError(
            f"{field_name} must be at most {max_length} characters",
            field=field_name
        )

    # Build allowed pattern
    allowed = r'a-zA-Z0-9'
    if allow_dashes:
        allowed += r'\-'
    if allow_underscores:
        allowed += r'_'

    pattern = f'^[{allowed}]+$'

    if not re.match(pattern, name):
        allowed_desc = "letters, numbers"
        if allow_dashes:
            allowed_desc += ", dashes"
        if allow_underscores:
            allowed_desc += ", underscores"

        raise ValidationError(
            f"{field_name} can only contain {allowed_desc}",
            field=field_name,
            suggestion=f"Try: {re.sub(r'[^a-zA-Z0-9_-]', '-', name)}"
        )

    # Must start with letter
    if not name[0].isalpha():
        raise ValidationError(
            f"{field_name} must start with a letter",
            field=field_name
        )

    return name


def validate_topic_prefix(prefix: str) -> str:
    """
    Validate a topic prefix (lowercase, no special chars).

    Args:
        prefix: Prefix to validate

    Returns:
        Validated lowercase prefix

    Raises:
        ValidationError: If prefix is invalid
    """
    prefix = validate_required(prefix, "topic prefix")
    prefix = prefix.lower()

    if not re.match(r'^[a-z][a-z0-9]*$', prefix):
        raise ValidationError(
            "Topic prefix must be lowercase letters/numbers, starting with a letter",
            field="topic prefix",
            suggestion=f"Try: {re.sub(r'[^a-z0-9]', '', prefix.lower())}"
        )

    if len(prefix) > 20:
        raise ValidationError(
            "Topic prefix should be concise (max 20 characters)",
            field="topic prefix"
        )

    return prefix


def validate_path(
    path: Union[str, Path],
    must_exist: bool = False,
    must_be_dir: bool = False,
    must_be_file: bool = False,
    create_parents: bool = False
) -> Path:
    """
    Validate a file system path.

    Args:
        path: Path to validate
        must_exist: Require path to exist
        must_be_dir: Require path to be a directory
        must_be_file: Require path to be a file
        create_parents: Create parent directories if needed

    Returns:
        Resolved Path object

    Raises:
        ValidationError: If path is invalid
    """
    if not path:
        raise ValidationError("Path is required", field="path")

    resolved = Path(path).expanduser().resolve()

    if must_exist and not resolved.exists():
        raise ValidationError(
            f"Path does not exist: {resolved}",
            field="path"
        )

    if must_be_dir:
        if resolved.exists() and not resolved.is_dir():
            raise ValidationError(
                f"Path is not a directory: {resolved}",
                field="path"
            )

    if must_be_file:
        if resolved.exists() and not resolved.is_file():
            raise ValidationError(
                f"Path is not a file: {resolved}",
                field="path"
            )

    if create_parents and not resolved.parent.exists():
        resolved.parent.mkdir(parents=True, exist_ok=True)

    return resolved


def validate_url(url: str, field_name: str = "URL") -> str:
    """
    Validate a URL format.

    Args:
        url: URL to validate
        field_name: Field name for error messages

    Returns:
        Validated URL string

    Raises:
        ValidationError: If URL is invalid
    """
    url = validate_required(url, field_name)

    # Basic URL pattern
    pattern = r'^https?://[a-zA-Z0-9][-a-zA-Z0-9.]*[a-zA-Z0-9](:[0-9]+)?(/.*)?$'

    if not re.match(pattern, url):
        raise ValidationError(
            f"Invalid {field_name} format",
            field=field_name,
            suggestion="URL should start with http:// or https://"
        )

    return url


def validate_choice(
    value: str,
    choices: List[str],
    field_name: str = "value"
) -> str:
    """
    Validate that value is one of allowed choices.

    Args:
        value: Value to validate
        choices: List of allowed values
        field_name: Field name for error messages

    Returns:
        Validated value (case-normalized to match choice)

    Raises:
        ValidationError: If value not in choices
    """
    value = validate_required(value, field_name)

    # Try exact match first
    if value in choices:
        return value

    # Try case-insensitive match
    lower_value = value.lower()
    for choice in choices:
        if choice.lower() == lower_value:
            return choice

    raise ValidationError(
        f"Invalid {field_name}: '{value}'",
        field=field_name,
        suggestion=f"Choose from: {', '.join(choices)}"
    )


def validate_list(
    value: str,
    field_name: str = "list",
    separator: str = ",",
    min_items: int = 0,
    max_items: Optional[int] = None
) -> List[str]:
    """
    Validate and parse a comma-separated list.

    Args:
        value: Comma-separated string
        field_name: Field name for error messages
        separator: List separator character
        min_items: Minimum number of items required
        max_items: Maximum number of items allowed

    Returns:
        List of stripped strings

    Raises:
        ValidationError: If list is invalid
    """
    if not value or not value.strip():
        if min_items > 0:
            raise ValidationError(
                f"{field_name} requires at least {min_items} items",
                field=field_name
            )
        return []

    items = [item.strip() for item in value.split(separator)]
    items = [item for item in items if item]  # Remove empty

    if len(items) < min_items:
        raise ValidationError(
            f"{field_name} requires at least {min_items} items, got {len(items)}",
            field=field_name
        )

    if max_items and len(items) > max_items:
        raise ValidationError(
            f"{field_name} allows at most {max_items} items, got {len(items)}",
            field=field_name
        )

    return items
