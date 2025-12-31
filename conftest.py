"""
Shared pytest fixtures for all Assistant Skills tests.

This root conftest.py provides common fixtures used across multiple skill tests.
Skill-specific fixtures remain in their respective conftest.py files.
"""

import json
import pytest
import tempfile
import shutil
from pathlib import Path


# =============================================================================
# TEMPORARY DIRECTORY FIXTURES
# =============================================================================

@pytest.fixture
def temp_path():
    """Create a temporary directory as Path object.

    Preferred over temp_dir for new tests.
    Automatically cleaned up after test.

    Returns:
        Path: Temporary directory path
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def temp_dir(temp_path):
    """Create a temporary directory as string.

    Legacy compatibility fixture. Prefer temp_path for new tests.

    Returns:
        str: Temporary directory path as string
    """
    return str(temp_path)


# =============================================================================
# PROJECT STRUCTURE FIXTURES
# =============================================================================

@pytest.fixture
def claude_project_structure(temp_path):
    """Create a standard .claude project structure.

    Creates:
        project/
        ├── .claude/
        │   ├── settings.json
        │   └── skills/
        │       └── shared/
        │           └── scripts/
        │               └── lib/
        └── README.md

    Returns:
        dict: Paths to key directories and files
            - root: Project root Path
            - claude_dir: .claude directory Path
            - skills_dir: .claude/skills directory Path
            - shared_lib: .claude/skills/shared/scripts/lib Path
            - settings: .claude/settings.json Path
    """
    project = temp_path / "Test-Project"
    project.mkdir()

    claude_dir = project / ".claude"
    skills_dir = claude_dir / "skills"
    shared_lib = skills_dir / "shared" / "scripts" / "lib"
    shared_lib.mkdir(parents=True)

    settings = claude_dir / "settings.json"
    settings.write_text('{"test": {"default_profile": "production"}}')

    readme = project / "README.md"
    readme.write_text("# Test Project\n")

    return {
        "root": project,
        "claude_dir": claude_dir,
        "skills_dir": skills_dir,
        "shared_lib": shared_lib,
        "settings": settings,
    }


@pytest.fixture
def plugin_project_structure(temp_path):
    """Create a standard .claude-plugin project structure.

    Creates:
        project/
        ├── .claude-plugin/
        │   └── plugin.json
        ├── skills/
        └── README.md

    Returns:
        dict: Paths to key directories and files
            - root: Project root Path
            - plugin_dir: .claude-plugin directory Path
            - plugin_json: plugin.json Path
            - skills_dir: skills directory Path
    """
    project = temp_path / "Test-Plugin"
    project.mkdir()

    plugin_dir = project / ".claude-plugin"
    plugin_dir.mkdir()

    plugin_json = plugin_dir / "plugin.json"
    plugin_json.write_text(json.dumps({
        "name": "test-plugin",
        "version": "1.0.0",
        "description": "Test plugin for unit testing"
    }, indent=2))

    skills_dir = project / "skills"
    skills_dir.mkdir()

    readme = project / "README.md"
    readme.write_text("# Test Plugin\n")

    return {
        "root": project,
        "plugin_dir": plugin_dir,
        "plugin_json": plugin_json,
        "skills_dir": skills_dir,
    }


# =============================================================================
# SKILL CONTENT FIXTURES
# =============================================================================

@pytest.fixture
def sample_skill_md():
    """Return sample SKILL.md content.

    Returns:
        str: Valid SKILL.md content with frontmatter
    """
    return '''---
name: sample-skill
description: A sample skill for testing. Use when user asks to "test something".
---

# Sample Skill

This is a sample skill for unit testing.

## Quick Start

```bash
echo "Hello from sample skill"
```

## Usage Examples

- "Test something"
- "Run a sample"
'''


@pytest.fixture
def sample_skill(claude_project_structure, sample_skill_md):
    """Create a sample skill in the project structure.

    Returns:
        dict: Skill paths
            - skill_dir: Skill directory Path
            - skill_md: SKILL.md Path
            - scripts_dir: scripts directory Path
            - tests_dir: tests directory Path
    """
    skills_dir = claude_project_structure["skills_dir"]

    skill_dir = skills_dir / "sample-skill"
    skill_dir.mkdir()

    skill_md = skill_dir / "SKILL.md"
    skill_md.write_text(sample_skill_md)

    scripts_dir = skill_dir / "scripts"
    scripts_dir.mkdir()

    tests_dir = skill_dir / "tests"
    tests_dir.mkdir()

    return {
        "skill_dir": skill_dir,
        "skill_md": skill_md,
        "scripts_dir": scripts_dir,
        "tests_dir": tests_dir,
        **claude_project_structure,  # Include parent structure
    }


# =============================================================================
# TEMPLATE FIXTURES
# =============================================================================

@pytest.fixture
def sample_template():
    """Sample template content with placeholders.

    Returns:
        str: Template with {{PLACEHOLDER}} markers
    """
    return """# {{PROJECT_NAME}}

This is a template for {{API_NAME}}.

Topic: {{TOPIC}}
"""


@pytest.fixture
def sample_context():
    """Sample context for template rendering.

    Returns:
        dict: Key-value pairs for template placeholders
    """
    return {
        "PROJECT_NAME": "Test-Skills",
        "API_NAME": "Test API",
        "TOPIC": "test"
    }


# =============================================================================
# PYTEST HOOKS
# =============================================================================

def pytest_configure(config):
    """Configure pytest with custom markers."""
    # Markers are already defined in pytest.ini, but this ensures
    # they're available even if pytest.ini is not found
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "live: marks tests requiring live API access"
    )
    config.addinivalue_line(
        "markers", "e2e: marks end-to-end tests requiring Claude CLI"
    )
