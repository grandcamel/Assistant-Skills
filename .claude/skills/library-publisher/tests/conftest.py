"""Pytest configuration and fixtures for library-publisher tests."""

import pytest
import tempfile
import shutil
from pathlib import Path


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_library(temp_dir):
    """Create a sample shared library structure."""
    lib_dir = temp_dir / "skills" / "shared" / "scripts" / "lib"
    lib_dir.mkdir(parents=True)

    # Create formatters.py
    (lib_dir / "formatters.py").write_text('''"""Output formatting utilities."""

def format_table(data, headers=None):
    """Format data as a table."""
    return str(data)

def format_tree(root, items):
    """Format data as a tree."""
    return f"{root}: {items}"

class TableFormatter:
    """Table formatting class."""
    pass
''')

    # Create validators.py
    (lib_dir / "validators.py").write_text('''"""Input validation utilities."""

def validate_url(url):
    """Validate a URL."""
    return url

def validate_email(email):
    """Validate an email address."""
    return email
''')

    # Create __init__.py
    (lib_dir / "__init__.py").write_text('')

    return temp_dir


@pytest.fixture
def sample_project(sample_library):
    """Create a sample project with scripts using the library."""
    project_dir = sample_library

    # Create a script that imports from the library
    scripts_dir = project_dir / "skills" / "myskill" / "scripts"
    scripts_dir.mkdir(parents=True)

    (scripts_dir / "my_script.py").write_text('''"""Sample script."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'shared' / 'scripts' / 'lib'))

from formatters import format_table, TableFormatter
from validators import validate_url

def main():
    data = [{"name": "test"}]
    print(format_table(data))

if __name__ == "__main__":
    main()
''')

    # Create README.md
    (project_dir / "README.md").write_text('''# Test Project

## Shared Library

Production-ready Python modules in `skills/shared/scripts/lib/`:

| Module | Purpose |
|--------|---------|
| `formatters.py` | Output formatting |

```python
from formatters import format_table
```

## Development

### Run Tests

```bash
PYTHONPATH="skills/shared/scripts/lib" pytest tests/ -v
```
''')

    # Create CLAUDE.md
    (project_dir / "CLAUDE.md").write_text('''# CLAUDE.md

## Run Tests

```bash
PYTHONPATH="skills/shared/scripts/lib" pytest tests/ -v
```

All Python scripts import from `skills/shared/scripts/lib/`:

Scripts require `PYTHONPATH` to be set for imports to work.
''')

    return project_dir
