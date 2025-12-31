"""Tests for setup-wizard skill structure."""

import pytest
from pathlib import Path


SKILL_PATH = Path(__file__).parent.parent
PROJECT_ROOT = SKILL_PATH.parent.parent
COMMAND_PATH = PROJECT_ROOT / ".claude-plugin" / "commands" / "assistant-skills-setup.md"
HOOKS_PATH = PROJECT_ROOT / "hooks" / "hooks.json"


class TestSkillStructure:
    """Tests for skill file structure."""

    def test_skill_md_exists(self):
        """SKILL.md should exist."""
        assert (SKILL_PATH / "SKILL.md").exists()

    def test_skill_md_has_frontmatter(self):
        """SKILL.md should have YAML frontmatter."""
        content = (SKILL_PATH / "SKILL.md").read_text()
        assert content.startswith("---")
        assert "name:" in content
        assert "description:" in content

    def test_skill_md_has_name(self):
        """SKILL.md frontmatter should have correct name."""
        content = (SKILL_PATH / "SKILL.md").read_text()
        assert "name: setup-wizard" in content

    def test_docs_directory_exists(self):
        """docs/ directory should exist."""
        assert (SKILL_PATH / "docs").is_dir()

    def test_reference_doc_exists(self):
        """docs/reference.md should exist."""
        assert (SKILL_PATH / "docs" / "reference.md").exists()


class TestCommandStructure:
    """Tests for associated command file."""

    def test_command_file_exists(self):
        """assistant-skills-setup.md command should exist."""
        assert COMMAND_PATH.exists()

    def test_command_has_frontmatter(self):
        """Command file should have YAML frontmatter with description."""
        content = COMMAND_PATH.read_text()
        assert content.startswith("---")
        assert "description:" in content

    def test_command_has_steps(self):
        """Command file should contain setup steps."""
        content = COMMAND_PATH.read_text()
        assert "Step 1" in content
        assert "Step 2" in content
        assert "python3" in content.lower()
        assert "venv" in content.lower()


class TestHooksIntegration:
    """Tests for hooks integration."""

    def test_hooks_file_exists(self):
        """hooks.json should exist."""
        assert HOOKS_PATH.exists()

    def test_hooks_has_session_start(self):
        """hooks.json should have SessionStart hook."""
        content = HOOKS_PATH.read_text()
        assert "SessionStart" in content

    def test_hooks_checks_venv(self):
        """SessionStart hook should check for venv."""
        content = HOOKS_PATH.read_text()
        assert "assistant-skills-venv" in content or "assistant_skills" in content


class TestDocumentation:
    """Tests for documentation completeness."""

    def test_skill_md_has_quick_start(self):
        """SKILL.md should have Quick Start section."""
        content = (SKILL_PATH / "SKILL.md").read_text()
        assert "## Quick Start" in content

    def test_skill_md_has_troubleshooting(self):
        """SKILL.md should have Troubleshooting section."""
        content = (SKILL_PATH / "SKILL.md").read_text()
        assert "## Troubleshooting" in content

    def test_reference_has_schema(self):
        """Reference doc should document the config schema."""
        content = (SKILL_PATH / "docs" / "reference.md").read_text()
        assert "config.yaml" in content or "Configuration" in content

    def test_reference_has_shell_function(self):
        """Reference doc should document claude-as function."""
        content = (SKILL_PATH / "docs" / "reference.md").read_text()
        assert "claude-as" in content
