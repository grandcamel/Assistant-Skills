"""
Pytest fixtures for assistant-builder tests.

Note: Common fixtures (temp_dir, temp_path, sample_template, sample_context)
are provided by the root conftest.py.
"""

import pytest
from pathlib import Path


@pytest.fixture
def sample_project(temp_path):
    """Create a sample project with OLD structure for backward compatibility testing.

    Uses temp_path from root conftest.py.
    """
    project_path = temp_path / "Test-Skills"
    project_path.mkdir()

    # Create OLD structure (.claude/skills/)
    claude_dir = project_path / ".claude"
    skills_dir = claude_dir / "skills"
    shared_dir = skills_dir / "shared" / "scripts" / "lib"

    shared_dir.mkdir(parents=True)

    # Create settings.json (old format)
    settings = claude_dir / "settings.json"
    settings.write_text('{"test": {"default_profile": "production"}}')

    # Create a sample skill
    skill_dir = skills_dir / "test-sample"
    (skill_dir / "scripts").mkdir(parents=True)
    (skill_dir / "tests").mkdir(parents=True)

    skill_md = skill_dir / "SKILL.md"
    skill_md.write_text("""---
name: "test-sample"
description: "Sample skill for testing"
---

# Sample Skill

A sample skill for testing.
""")

    return str(project_path)


@pytest.fixture
def sample_project_new(temp_path):
    """Create a sample project with NEW structure (.claude-plugin/).

    Uses temp_path from root conftest.py.
    """
    project_path = temp_path / "Test-Skills"
    project_path.mkdir()

    # Create NEW structure (.claude-plugin/ + skills/)
    plugin_dir = project_path / ".claude-plugin"
    commands_dir = plugin_dir / "commands"
    commands_dir.mkdir(parents=True)

    skills_dir = project_path / "skills"
    shared_docs = skills_dir / "shared" / "docs"
    shared_docs.mkdir(parents=True)

    # Create plugin.json
    plugin_json = plugin_dir / "plugin.json"
    plugin_json.write_text("""{
  "name": "test-skills",
  "version": "1.0.0",
  "skills": ["../skills/test-assistant/SKILL.md", "../skills/test-sample/SKILL.md"]
}""")

    # Create VERSION file
    (project_path / "VERSION").write_text("1.0.0")

    # Create conftest.py
    (project_path / "conftest.py").write_text('''"""Root fixtures."""
import pytest

@pytest.fixture
def temp_fixture():
    pass
''')

    # Create pytest.ini
    (project_path / "pytest.ini").write_text("""[pytest]
testpaths = skills
markers =
    unit: Unit tests
""")

    # Create hub/router skill
    assistant_dir = skills_dir / "test-assistant"
    (assistant_dir / "docs").mkdir(parents=True)

    assistant_md = assistant_dir / "SKILL.md"
    assistant_md.write_text("""---
name: "test-assistant"
description: "Test hub skill for routing requests."
---

# Test Assistant

## Quick Reference

| I want to... | Use this skill | Risk |
|--------------|----------------|:----:|
| Search | test-search | - |

## Routing Rules

Route requests to appropriate skill.
""")

    # Create DECISION_TREE.md
    (assistant_dir / "docs" / "DECISION_TREE.md").write_text("""# Decision Tree
Route based on user intent.
""")

    # Create a sample skill
    skill_dir = skills_dir / "test-sample"
    (skill_dir / "docs").mkdir(parents=True)

    skill_md = skill_dir / "SKILL.md"
    skill_md.write_text("""---
name: "test-sample"
description: "Sample skill for testing. ALWAYS use when working with samples."
---

# Sample Skill

## Quick Reference

| Operation | Command | Risk |
|-----------|---------|:----:|
| List samples | `test sample list` | - |
| Create sample | `test sample create` | ⚠️ |

A sample skill for testing.
""")

    # Create shared docs
    (shared_docs / "SAFEGUARDS.md").write_text("""# Safeguards
Risk documentation.
""")

    (shared_docs / "QUICK_REFERENCE.md").write_text("""# Quick Reference
Common commands.
""")

    return str(project_path)
