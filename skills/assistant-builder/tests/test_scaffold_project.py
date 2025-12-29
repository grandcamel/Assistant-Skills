"""
Tests for scaffold_project.py
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'shared' / 'scripts' / 'lib'))


class TestScaffoldProject:
    """Tests for project scaffolding functionality."""

    def test_create_directory_structure(self, temp_dir):
        """Test that directory structure is created correctly."""
        from scaffold_project import create_directory_structure

        base_path = Path(temp_dir) / "TestProject"
        base_path.mkdir()

        dirs = create_directory_structure(base_path, "test", ["issues", "users"])

        # Check core directories
        assert ".claude" in dirs
        assert ".claude/skills" in dirs
        assert ".claude/skills/shared" in dirs
        assert ".claude/skills/test-assistant" in dirs

        # Check skill directories
        assert ".claude/skills/test-issues" in dirs
        assert ".claude/skills/test-users" in dirs

    def test_generate_gitignore(self):
        """Test gitignore generation."""
        from scaffold_project import generate_gitignore

        content = generate_gitignore({})

        assert "__pycache__" in content
        assert ".env" in content
        assert "settings.local.json" in content
        assert ".pytest_cache" in content

    def test_generate_settings_json(self):
        """Test settings.json generation."""
        from scaffold_project import generate_settings_json
        import json

        context = {
            "TOPIC": "github",
            "API_NAME": "GitHub",
            "BASE_URL": "https://api.github.com"
        }

        content = generate_settings_json(context)
        settings = json.loads(content)

        assert "github" in settings
        assert "profiles" in settings["github"]
        assert "production" in settings["github"]["profiles"]

    def test_generate_skill_md(self):
        """Test SKILL.md generation."""
        from scaffold_project import generate_skill_md

        context = {
            "TOPIC": "github",
            "API_NAME": "GitHub"
        }

        content = generate_skill_md(context, "issues")

        assert "github-issues" in content
        assert "Issues" in content
        assert "when_to_use:" in content

    def test_scaffold_dry_run(self, temp_dir):
        """Test scaffold in dry-run mode doesn't create files."""
        from scaffold_project import scaffold_project

        result = scaffold_project(
            name="Test-Skills",
            topic="test",
            api_name="Test",
            output_dir=temp_dir,
            dry_run=True
        )

        # Should return files but not create them
        assert len(result['files']) > 0
        assert not (Path(temp_dir) / "Test-Skills").exists()

    def test_scaffold_creates_project(self, temp_dir):
        """Test that scaffold creates a complete project."""
        from scaffold_project import scaffold_project

        result = scaffold_project(
            name="My-Skills",
            topic="my",
            api_name="My API",
            skills=["items"],
            output_dir=temp_dir,
            dry_run=False
        )

        project_path = Path(result['path'])

        # Check project was created
        assert project_path.exists()

        # Check key files exist
        assert (project_path / ".gitignore").exists()
        assert (project_path / "README.md").exists()
        assert (project_path / "CLAUDE.md").exists()
        assert (project_path / ".claude" / "settings.json").exists()

        # Check skill structure
        assert (project_path / ".claude" / "skills" / "my-items" / "SKILL.md").exists()


class TestValidation:
    """Tests for input validation in scaffold_project."""

    def test_validates_project_name(self):
        """Test that invalid project names are rejected."""
        from validators import validate_name, ValidationError

        # Valid names
        assert validate_name("Test-Skills") == "Test-Skills"
        assert validate_name("my_project") == "my_project"

        # Invalid names
        with pytest.raises(ValidationError):
            validate_name("has spaces")

        with pytest.raises(ValidationError):
            validate_name("123starts-with-number")

    def test_validates_topic_prefix(self):
        """Test that invalid topic prefixes are rejected."""
        from validators import validate_topic_prefix, ValidationError

        # Valid prefixes (note: uppercase gets normalized to lowercase)
        assert validate_topic_prefix("github") == "github"
        assert validate_topic_prefix("my2") == "my2"
        assert validate_topic_prefix("UPPERCASE") == "uppercase"  # Normalized

        # Invalid prefixes
        with pytest.raises(ValidationError):
            validate_topic_prefix("has-dashes")

        with pytest.raises(ValidationError):
            validate_topic_prefix("123startswithnumber")
