"""Pytest configuration and fixtures for landing-page tests.

Note: Common fixtures (temp_dir, temp_path) are provided by root conftest.py.
"""

import pytest
from pathlib import Path


@pytest.fixture
def sample_project(temp_path):
    """Create a sample Assistant Skills project structure.

    Uses temp_path from root conftest.py.
    """
    project_dir = temp_path / "Test-Assistant-Skills"
    project_dir.mkdir()

    # Create .claude/skills structure
    skills_dir = project_dir / ".claude" / "skills"
    skills_dir.mkdir(parents=True)

    # Create sample skill
    skill_dir = skills_dir / "test-skill"
    skill_dir.mkdir()

    scripts_dir = skill_dir / "scripts"
    scripts_dir.mkdir()

    # Create SKILL.md
    (skill_dir / "SKILL.md").write_text('''---
name: test-skill
description: A test skill for unit testing
---

# Test Skill

What this skill does: Tests the landing page skill.

## Quick Start

```bash
python test.py
```
''')

    # Create sample scripts
    (scripts_dir / "test_script.py").write_text('def test(): pass')
    (scripts_dir / "another_script.py").write_text('def another(): pass')

    # Create tests
    tests_dir = skill_dir / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_sample.py").write_text('''
def test_one(): pass
def test_two(): pass
def test_three(): pass
''')

    # Create README.md
    (project_dir / "README.md").write_text('# Test Assistant Skills\n')

    return project_dir


@pytest.fixture
def project_without_skills(temp_path):
    """Create a project without .claude/skills directory.

    Uses temp_path from root conftest.py.
    """
    project_dir = temp_path / "No-Skills-Project"
    project_dir.mkdir()
    (project_dir / "README.md").write_text('# No Skills\n')
    return project_dir
