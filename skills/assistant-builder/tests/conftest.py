"""
Pytest fixtures for assistant-builder tests.
"""

import pytest
import tempfile
import shutil
from pathlib import Path


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    temp = tempfile.mkdtemp()
    yield temp
    shutil.rmtree(temp, ignore_errors=True)


@pytest.fixture
def sample_project(temp_dir):
    """Create a sample project structure for testing."""
    project_path = Path(temp_dir) / "Test-Skills"
    project_path.mkdir()

    # Create basic structure
    claude_dir = project_path / ".claude"
    skills_dir = claude_dir / "skills"
    shared_dir = skills_dir / "shared" / "scripts" / "lib"

    shared_dir.mkdir(parents=True)

    # Create settings.json
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
when_to_use: |
  - Testing
---

# Sample Skill
""")

    return str(project_path)


@pytest.fixture
def sample_template():
    """Sample template content for testing."""
    return """# {{PROJECT_NAME}}

This is a template for {{API_NAME}}.

Topic: {{TOPIC}}
"""


@pytest.fixture
def sample_context():
    """Sample context for template rendering."""
    return {
        "PROJECT_NAME": "Test-Skills",
        "API_NAME": "Test API",
        "TOPIC": "test"
    }
