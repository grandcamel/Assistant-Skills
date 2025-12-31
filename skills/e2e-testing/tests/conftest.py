"""Pytest fixtures for e2e-testing skill tests.

Note: Common fixtures (temp_dir, temp_path) are provided by root conftest.py.
"""

import json
import pytest
from pathlib import Path


@pytest.fixture
def temp_project(temp_path):
    """Create a temporary project structure for testing.

    Uses temp_path from root conftest.py.
    """
    project = temp_path / "test-project"
    project.mkdir()

    # Create .claude-plugin directory
    plugin_dir = project / ".claude-plugin"
    plugin_dir.mkdir()

    # Create plugin.json
    plugin_json = {
        "name": "test-plugin",
        "version": "1.0.0",
        "description": "Test plugin for E2E testing"
    }
    (plugin_dir / "plugin.json").write_text(json.dumps(plugin_json, indent=2))

    # Create skills directory with sample skills
    skills_dir = project / "skills"
    skills_dir.mkdir()

    # Create sample skill 1
    skill1 = skills_dir / "sample-skill"
    skill1.mkdir()
    (skill1 / "SKILL.md").write_text('''---
name: sample-skill
description: A sample skill for testing. Use when user wants to "test something" or "run sample".
when_to_use:
  - User wants to test functionality
  - User asks to run a sample
---

# Sample Skill

This is a sample skill for testing.

## Quick Start

```bash
echo "Hello from sample skill"
```
''')

    # Create scripts directory for skill
    scripts_dir = skill1 / "scripts"
    scripts_dir.mkdir()
    (scripts_dir / "sample_script.py").write_text('''#!/usr/bin/env python3
"""Sample script."""
print("Hello from sample script")
''')

    # Create sample skill 2
    skill2 = skills_dir / "another-skill"
    skill2.mkdir()
    (skill2 / "SKILL.md").write_text('''---
name: another-skill
description: Another skill for testing. Helps with "creating things" and "building stuff".
---

# Another Skill

Another skill for testing purposes.
''')

    # Create README.md
    (project / "README.md").write_text('''# Test Project

A test project for E2E testing.

## Development

### Run Tests
```bash
pytest tests/ -v
```

## Contributing

Contributions welcome!
''')

    # Create CLAUDE.md
    (project / "CLAUDE.md").write_text('''# CLAUDE.md

## Commands

### Run Tests
```bash
pytest tests/ -v
```
''')

    return project


@pytest.fixture
def project_with_e2e(temp_project):
    """Create a project with E2E testing already set up."""
    # Create tests/e2e directory
    e2e_dir = temp_project / "tests" / "e2e"
    e2e_dir.mkdir(parents=True)

    # Create minimal files
    (e2e_dir / "__init__.py").write_text('"""E2E tests."""\n')
    (e2e_dir / "test_cases.yaml").write_text('''metadata:
  name: test-e2e
  version: "1.0.0"

settings:
  default_timeout: 120
  default_model: claude-sonnet-4-20250514

suites:
  basic:
    description: Basic tests
    tests:
      - id: sample_test
        name: Sample test
        prompt: "Hello"
        expect:
          success: true
''')

    return temp_project


@pytest.fixture
def empty_project(temp_path):
    """Create an empty project without plugin structure.

    Uses temp_path from root conftest.py.
    """
    project = temp_path / "empty-project"
    project.mkdir()
    (project / "README.md").write_text("# Empty Project\n")
    return project
