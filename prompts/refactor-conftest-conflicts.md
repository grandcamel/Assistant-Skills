# Refactor: Resolve conftest.py Conflicts Across Skills

Apply this refactoring to resolve pytest collection conflicts when running all skill tests together.

## Problem

When running `pytest skills/*/tests/` from the project root, pytest fails with:
- `ImportPathMismatchError: tests.conftest` - Multiple conftest.py files conflict
- `ModuleNotFoundError: No module named 'tests.test_*'` - Module name collisions
- `ValueError: Plugin already registered under a different name` - Duplicate plugin registration

Root causes:
1. Multiple `skills/*/tests/` directories each have `conftest.py` with same module name
2. `__init__.py` files in test directories make pytest treat them as packages
3. Duplicate tests in `.claude/skills/*/tests/` (if present)
4. Same-named scripts across skills (e.g., multiple `update_docs.py`)

## Solution Steps

### Step 1: Create pytest.ini at project root

```ini
[pytest]
# Test discovery paths
testpaths = skills tests

# Directories to ignore during test collection
norecursedirs =
    .claude
    __pycache__
    .git
    .venv
    node_modules
    templates
    docker

# Test file patterns
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# Import mode - use importlib to avoid conflicts with multiple tests/ directories
pythonpath = .
addopts = -v --tb=short --import-mode=importlib

# Filter warnings
filterwarnings =
    ignore::DeprecationWarning
    ignore::PendingDeprecationWarning

# Markers
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    live: marks tests requiring live API access
```

### Step 2: Create root conftest.py with shared fixtures

```python
"""
Shared pytest fixtures for all skill tests.

Provides common fixtures used across multiple skill tests.
Skill-specific fixtures remain in their respective conftest.py files.
"""

import json
import pytest
import tempfile
from pathlib import Path


# =============================================================================
# TEMPORARY DIRECTORY FIXTURES
# =============================================================================

@pytest.fixture
def temp_path():
    """Create a temporary directory as Path object.

    Preferred fixture for new tests. Automatically cleaned up.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def temp_dir(temp_path):
    """Create a temporary directory as string.

    Legacy compatibility. Prefer temp_path for new tests.
    """
    return str(temp_path)


# =============================================================================
# PROJECT STRUCTURE FIXTURES
# =============================================================================

@pytest.fixture
def claude_project_structure(temp_path):
    """Create a standard .claude project structure."""
    project = temp_path / "Test-Project"
    project.mkdir()

    claude_dir = project / ".claude"
    skills_dir = claude_dir / "skills"
    shared_lib = skills_dir / "shared" / "scripts" / "lib"
    shared_lib.mkdir(parents=True)

    settings = claude_dir / "settings.json"
    settings.write_text('{}')

    return {
        "root": project,
        "claude_dir": claude_dir,
        "skills_dir": skills_dir,
        "shared_lib": shared_lib,
        "settings": settings,
    }


@pytest.fixture
def sample_skill_md():
    """Return sample SKILL.md content."""
    return '''---
name: sample-skill
description: A sample skill for testing.
---

# Sample Skill

## Quick Start

```bash
echo "Hello"
```
'''


# =============================================================================
# PYTEST HOOKS
# =============================================================================

def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "slow: marks tests as slow")
    config.addinivalue_line("markers", "integration: marks integration tests")
    config.addinivalue_line("markers", "live: marks tests requiring live API")
```

### Step 3: Remove duplicate test directories

```bash
# Remove tests from .claude/skills/ (keep only skills/*/tests/)
rm -rf .claude/skills/*/tests/
```

### Step 4: Remove __init__.py from test directories

```bash
# Remove __init__.py files that cause module name conflicts
find skills -path "*/tests/__init__.py" -delete
find skills -path "*live_integration/__init__.py" -delete
```

### Step 5: Update skill conftest files

For each `skills/*/tests/conftest.py`:

1. Remove duplicate fixtures now in root conftest (temp_dir, temp_path)
2. Update fixtures to use `temp_path` parameter instead of defining their own
3. Add note about shared fixtures

Example update:
```python
"""
Pytest fixtures for [skill-name] tests.

Note: Common fixtures (temp_dir, temp_path) are provided by root conftest.py.
"""

import pytest
from pathlib import Path


@pytest.fixture
def sample_project(temp_path):  # Changed from temp_dir or custom temp fixture
    """Create a sample project structure.

    Uses temp_path from root conftest.py.
    """
    project = temp_path / "Test-Project"
    project.mkdir()
    # ... rest of fixture
    return project
```

### Step 6: Fix same-named script imports (if needed)

If tests import from scripts that have the same name across skills (e.g., `update_docs.py`), use explicit importlib:

```python
"""Tests for update_docs.py module."""

import pytest
import importlib.util
from pathlib import Path

# Import using explicit path to avoid conflicts with same-named modules
_script_path = Path(__file__).parent.parent / "scripts" / "update_docs.py"
_spec = importlib.util.spec_from_file_location("skill_update_docs", _script_path)
_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_module)

# Extract functions
update_docs = _module.update_docs
# ... other imports
```

### Step 7: Fix path resolution for symlinks (macOS)

If scripts use `Path.relative_to()`, ensure paths are resolved first:

```python
# Before
result = output_path.relative_to(project_path)  # Fails on macOS symlinks

# After
project_path = Path(project_path).resolve()
output_path = Path(output_path).resolve()
result = output_path.relative_to(project_path)  # Works
```

## Verification

Run all tests together:
```bash
pytest skills/*/tests/ -v
```

Expected: All tests pass without import errors or conflicts.

## Summary of Changes

| Change | Purpose |
|--------|---------|
| Create `pytest.ini` | Configure test paths, import mode, markers |
| Create root `conftest.py` | Shared fixtures (temp_path, temp_dir, etc.) |
| Remove `.claude/skills/*/tests/` | Eliminate duplicate test directories |
| Remove `tests/__init__.py` | Prevent module name conflicts |
| Update skill conftest files | Use shared fixtures from root |
| Use importlib for same-named scripts | Explicit imports avoid conflicts |
| Resolve paths for symlinks | Fix macOS `/var` -> `/private/var` issues |
