"""
Tests for scaffold_project.py
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add scripts to path for importing script modules
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))


class TestScaffoldProject:
    """Tests for project scaffolding functionality."""

    def test_create_directory_structure(self, temp_dir):
        """Test that directory structure is created correctly (new structure)."""
        from scaffold_project import create_directory_structure

        base_path = Path(temp_dir) / "TestProject"
        base_path.mkdir()

        dirs = create_directory_structure(base_path, "test", ["issues", "users"])

        # Check NEW structure (.claude-plugin/)
        assert ".claude-plugin" in dirs
        assert ".claude-plugin/commands" in dirs
        assert "skills" in dirs
        assert "skills/test-assistant" in dirs

        # Check skill directories
        assert "skills/test-issues" in dirs
        assert "skills/test-users" in dirs

    def test_create_directory_structure_custom_library(self, temp_dir):
        """Test directory structure for custom-library projects."""
        from scaffold_project import create_directory_structure

        base_path = Path(temp_dir) / "TestProject"
        base_path.mkdir()

        dirs = create_directory_structure(
            base_path, "myapi", ["resource"],
            project_type='custom-library'
        )

        # Should have library directory
        assert any('myapi-assistant-skills-lib' in d for d in dirs)

    def test_generate_gitignore(self):
        """Test gitignore generation."""
        from scaffold_project import generate_gitignore

        content = generate_gitignore({})

        assert "__pycache__" in content
        assert ".env" in content
        assert ".pytest_cache" in content
        # New pattern uses *.local.json and *.local.md
        assert "*.local.json" in content
        assert "*.local.md" in content

    def test_generate_plugin_json(self):
        """Test plugin.json generation."""
        from scaffold_project import generate_plugin_json
        import json

        context = {
            "TOPIC": "github",
            "PROJECT_NAME": "GitHub-Assistant-Skills",
            "API_NAME": "GitHub",
            "SKILLS": ["issues", "repos"]
        }

        content = generate_plugin_json(context)
        plugin = json.loads(content)

        assert plugin["name"] == "github-assistant-skills"
        assert "skills" in plugin
        assert "commands" in plugin

    def test_generate_skill_md(self):
        """Test SKILL.md generation for a skill."""
        from scaffold_project import generate_skill_md

        context = {
            "TOPIC": "github",
            "PROJECT_NAME": "GitHub-Assistant-Skills",
            "API_NAME": "GitHub",
            "PROJECT_TYPE": "cli-wrapper",
            "CLI_TOOL": "gh"
        }

        content = generate_skill_md(context, "issues")

        assert "github-issues" in content
        assert "Issues" in content
        # Should have CLI command references
        assert "gh issues" in content or "gh issue" in content
        # Should have risk levels
        assert "Risk" in content

    def test_generate_router_skill_md(self):
        """Test router/hub SKILL.md generation."""
        from scaffold_project import generate_router_skill_md

        context = {
            "TOPIC": "github",
            "PROJECT_NAME": "GitHub-Assistant-Skills",
            "API_NAME": "GitHub",
            "PROJECT_TYPE": "cli-wrapper",
            "CLI_TOOL": "gh",
            "SKILLS": ["issues", "repos"]
        }

        content = generate_router_skill_md(context)

        assert "github-assistant" in content
        assert "Routing" in content or "routing" in content
        # Should have quick reference table
        assert "Quick Reference" in content
        # Should reference skills
        assert "github-issues" in content or "Issues" in content

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
        """Test that scaffold creates a complete project (new structure)."""
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

        # Check key files exist (NEW structure)
        assert (project_path / ".gitignore").exists()
        assert (project_path / "README.md").exists()
        assert (project_path / "CLAUDE.md").exists()
        assert (project_path / "VERSION").exists()
        assert (project_path / "conftest.py").exists()
        assert (project_path / "pytest.ini").exists()

        # Check plugin structure
        assert (project_path / ".claude-plugin" / "plugin.json").exists()

        # Check skill structure (new pattern)
        assert (project_path / "skills" / "my-items" / "SKILL.md").exists()

        # Check router skill
        assert (project_path / "skills" / "my-assistant" / "SKILL.md").exists()

    def test_scaffold_cli_wrapper_project(self, temp_dir):
        """Test scaffolding a CLI wrapper project."""
        from scaffold_project import scaffold_project

        result = scaffold_project(
            name="GitLab-Skills",
            topic="gitlab",
            api_name="GitLab",
            project_type="cli-wrapper",
            cli_tool="glab",
            cli_install="brew install glab",
            output_dir=temp_dir,
            dry_run=False
        )

        project_path = Path(result['path'])

        # Should have setup command
        commands_dir = project_path / ".claude-plugin" / "commands"
        setup_cmds = list(commands_dir.glob("*-setup.md"))
        assert len(setup_cmds) > 0

        # Setup should reference glab
        setup_content = setup_cmds[0].read_text()
        assert "glab" in setup_content

    def test_scaffold_custom_library_project(self, temp_dir):
        """Test scaffolding a custom library project."""
        from scaffold_project import scaffold_project

        result = scaffold_project(
            name="MyAPI-Skills",
            topic="myapi",
            api_name="My API",
            project_type="custom-library",
            base_url="https://api.example.com",
            output_dir=temp_dir,
            dry_run=False
        )

        project_path = Path(result['path'])

        # Should have library directory stub
        lib_dirs = list(project_path.glob("*-assistant-skills-lib"))
        assert len(lib_dirs) > 0


class TestValidation:
    """Tests for input validation in scaffold_project."""

    def test_validates_project_name(self):
        """Test that invalid project names are rejected."""
        from assistant_skills_lib import validate_name, InputValidationError as ValidationError

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
        from assistant_skills_lib import validate_topic_prefix, InputValidationError as ValidationError

        # Valid prefixes (note: uppercase gets normalized to lowercase)
        assert validate_topic_prefix("github") == "github"
        assert validate_topic_prefix("my2") == "my2"
        assert validate_topic_prefix("UPPERCASE") == "uppercase"  # Normalized

        # Invalid prefixes
        with pytest.raises(ValidationError):
            validate_topic_prefix("has-dashes")

        with pytest.raises(ValidationError):
            validate_topic_prefix("123startswithnumber")


class TestGenerators:
    """Tests for file content generators."""

    def test_generate_conftest_py(self):
        """Test root conftest.py generation."""
        from scaffold_project import generate_conftest_py

        context = {
            "TOPIC": "test",
            "PROJECT_NAME": "Test-Skills",
            "API_NAME": "Test"
        }

        content = generate_conftest_py(context)

        assert "@pytest.fixture" in content
        assert "temp_path" in content
        assert "mock_test_client" in content

    def test_generate_pytest_ini(self):
        """Test pytest.ini generation."""
        from scaffold_project import generate_pytest_ini

        context = {
            "TOPIC": "test",
            "PROJECT_NAME": "Test-Skills"
        }

        content = generate_pytest_ini(context)

        assert "markers" in content
        assert "testpaths" in content
        assert "unit" in content
        assert "live" in content

    def test_generate_safeguards_md(self):
        """Test SAFEGUARDS.md generation."""
        from scaffold_project import generate_safeguards_md

        context = {
            "TOPIC": "test",
            "API_NAME": "Test",
            "PROJECT_TYPE": "cli-wrapper",
            "CLI_TOOL": "test-cli"
        }

        content = generate_safeguards_md(context)

        assert "Risk Level" in content
        assert "⚠️" in content
        assert "Recovery" in content

    def test_generate_quick_reference_md(self):
        """Test QUICK_REFERENCE.md generation."""
        from scaffold_project import generate_quick_reference_md

        context = {
            "TOPIC": "test",
            "API_NAME": "Test",
            "PROJECT_TYPE": "cli-wrapper",
            "CLI_TOOL": "test-cli"
        }

        content = generate_quick_reference_md(context)

        assert "Quick Reference" in content
        assert "test-cli" in content
        assert "Common Operations" in content
