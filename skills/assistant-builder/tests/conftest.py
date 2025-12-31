"""
Pytest fixtures for assistant-builder tests.

Note: Common fixtures (temp_dir, temp_path, sample_template, sample_context)
are provided by the root conftest.py.
"""

import pytest
from pathlib import Path


@pytest.fixture
def sample_project(temp_path):
    """Create a sample project structure for assistant-builder testing.

    This fixture creates a complete project structure suitable for
    testing project validation and skill addition.

    Uses temp_path from root conftest.py.
    """
    project_path = temp_path / "Test-Skills"
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
---

# Sample Skill

A sample skill for testing.
""")

    return str(project_path)
