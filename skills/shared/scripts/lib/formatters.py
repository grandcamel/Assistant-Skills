"""
Formatters for Assistant Builder

Provides output formatting utilities for consistent CLI output.

Usage:
    from formatters import format_table, format_tree, print_success, print_error

    print(format_table(data, headers=['Name', 'Status']))
    print_success("Operation completed")
"""

import json
import sys
from typing import Any, Dict, List, Optional, Sequence


# ANSI color codes
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    RESET = '\033[0m'


def _supports_color() -> bool:
    """Check if terminal supports color."""
    return hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()


def _colorize(text: str, color: str) -> str:
    """Apply color to text if terminal supports it."""
    if _supports_color():
        return f"{color}{text}{Colors.RESET}"
    return text


def format_table(
    data: Sequence[Dict[str, Any]],
    headers: Optional[List[str]] = None,
    keys: Optional[List[str]] = None
) -> str:
    """
    Format data as a simple ASCII table.

    Args:
        data: List of dictionaries to format
        headers: Optional list of header labels
        keys: Keys to include (if None, uses all keys from first item)

    Returns:
        Formatted table string
    """
    if not data:
        return "(no data)"

    # Determine columns
    if keys is None:
        keys = list(data[0].keys())

    if headers is None:
        headers = keys

    # Calculate column widths
    widths = [len(str(h)) for h in headers]
    for row in data:
        for i, key in enumerate(keys):
            val = str(row.get(key, ''))
            widths[i] = max(widths[i], len(val))

    # Build table
    lines = []

    # Header row
    header_row = ' | '.join(str(h).ljust(widths[i]) for i, h in enumerate(headers))
    lines.append(header_row)

    # Separator
    separator = '-+-'.join('-' * w for w in widths)
    lines.append(separator)

    # Data rows
    for row in data:
        row_str = ' | '.join(
            str(row.get(key, '')).ljust(widths[i])
            for i, key in enumerate(keys)
        )
        lines.append(row_str)

    return '\n'.join(lines)


def format_tree(
    root: str,
    items: List[Dict[str, Any]],
    name_key: str = 'name',
    children_key: str = 'children'
) -> str:
    """
    Format data as a tree structure.

    Args:
        root: Root node name
        items: List of items (can be nested with children_key)
        name_key: Key for item name
        children_key: Key for nested children

    Returns:
        Formatted tree string
    """
    lines = [root]

    def add_items(items: List, prefix: str = '', is_last_parent: bool = True):
        for i, item in enumerate(items):
            is_last = i == len(items) - 1

            # Determine branch character
            if is_last:
                branch = '└── '
                next_prefix = prefix + '    '
            else:
                branch = '├── '
                next_prefix = prefix + '│   '

            # Get name
            name = item.get(name_key, str(item)) if isinstance(item, dict) else str(item)
            lines.append(f"{prefix}{branch}{name}")

            # Process children
            if isinstance(item, dict) and children_key in item:
                add_items(item[children_key], next_prefix, is_last)

    add_items(items)
    return '\n'.join(lines)


def format_json(data: Any, indent: int = 2) -> str:
    """
    Format data as pretty-printed JSON.

    Args:
        data: Data to format
        indent: Indentation level

    Returns:
        JSON string
    """
    return json.dumps(data, indent=indent, default=str)


def format_list(items: List[str], bullet: str = '-') -> str:
    """
    Format items as a bulleted list.

    Args:
        items: List of strings
        bullet: Bullet character

    Returns:
        Formatted list string
    """
    return '\n'.join(f"{bullet} {item}" for item in items)


def print_success(message: str) -> None:
    """Print a success message in green."""
    prefix = _colorize("✓", Colors.GREEN)
    print(f"{prefix} {message}")


def print_error(message: str) -> None:
    """Print an error message in red."""
    prefix = _colorize("✗", Colors.RED)
    print(f"{prefix} {message}", file=sys.stderr)


def print_warning(message: str) -> None:
    """Print a warning message in yellow."""
    prefix = _colorize("!", Colors.YELLOW)
    print(f"{prefix} {message}")


def print_info(message: str) -> None:
    """Print an info message in blue."""
    prefix = _colorize("→", Colors.BLUE)
    print(f"{prefix} {message}")


def print_header(title: str) -> None:
    """Print a section header."""
    if _supports_color():
        print(f"\n{Colors.BOLD}{title}{Colors.RESET}")
        print('=' * len(title))
    else:
        print(f"\n{title}")
        print('=' * len(title))


def format_path(path: str, relative_to: Optional[str] = None) -> str:
    """
    Format a path for display.

    Args:
        path: Absolute path
        relative_to: Optional base path to make relative

    Returns:
        Formatted path string
    """
    from pathlib import Path

    p = Path(path)

    if relative_to:
        try:
            return str(p.relative_to(relative_to))
        except ValueError:
            pass

    # Use ~ for home directory
    home = Path.home()
    try:
        return '~/' + str(p.relative_to(home))
    except ValueError:
        return str(p)


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def format_count(count: int, singular: str, plural: Optional[str] = None) -> str:
    """
    Format a count with proper pluralization.

    Args:
        count: Number to format
        singular: Singular form of word
        plural: Plural form (defaults to singular + 's')

    Returns:
        Formatted string like "1 file" or "5 files"
    """
    if plural is None:
        plural = singular + 's'

    word = singular if count == 1 else plural
    return f"{count} {word}"
