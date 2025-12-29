"""Tests for update_docs.py script."""

import pytest
import sys
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from update_docs import (
    detect_project_info,
    generate_e2e_readme,
    add_e2e_section_to_readme,
    update_claude_md,
    update_docs,
)


class TestDetectProjectInfo:
    """Tests for project info detection."""

    def test_detects_readme(self, temp_project):
        """Should detect README.md."""
        result = detect_project_info(temp_project)

        assert result["has_readme"] is True

    def test_detects_claude_md(self, temp_project):
        """Should detect CLAUDE.md."""
        result = detect_project_info(temp_project)

        assert result["has_claude_md"] is True

    def test_detects_e2e_tests(self, project_with_e2e):
        """Should detect existing E2E tests."""
        result = detect_project_info(project_with_e2e)

        assert result["has_e2e_tests"] is True

    def test_counts_skills(self, temp_project):
        """Should count skills."""
        result = detect_project_info(temp_project)

        assert result["skills_count"] == 2

    def test_gets_plugin_name(self, temp_project):
        """Should get plugin name from plugin.json."""
        result = detect_project_info(temp_project)

        assert result["name"] == "test-plugin"


class TestGenerateE2EReadme:
    """Tests for E2E README generation."""

    def test_includes_plugin_name(self, temp_project):
        """Should include plugin name in title."""
        info = detect_project_info(temp_project)
        result = generate_e2e_readme(info)

        assert "test-plugin" in result

    def test_includes_prerequisites(self, temp_project):
        """Should include prerequisites section."""
        info = detect_project_info(temp_project)
        result = generate_e2e_readme(info)

        assert "Prerequisites" in result
        assert "ANTHROPIC_API_KEY" in result

    def test_includes_quick_start(self, temp_project):
        """Should include quick start section."""
        info = detect_project_info(temp_project)
        result = generate_e2e_readme(info)

        assert "Quick Start" in result
        assert "run-e2e-tests.sh" in result

    def test_includes_configuration(self, temp_project):
        """Should include configuration section."""
        info = detect_project_info(temp_project)
        result = generate_e2e_readme(info)

        assert "Configuration" in result
        assert "E2E_TEST_TIMEOUT" in result
        assert "E2E_TEST_MODEL" in result


class TestAddE2ESectionToReadme:
    """Tests for adding E2E section to README."""

    def test_adds_e2e_section(self, temp_project):
        """Should add E2E section to README."""
        content = (temp_project / "README.md").read_text()
        info = detect_project_info(temp_project)
        result = add_e2e_section_to_readme(content, info)

        assert "E2E" in result
        assert "run-e2e-tests.sh" in result

    def test_does_not_duplicate_section(self, temp_project):
        """Should not add section if already exists."""
        content = "# Project\n\n## E2E Testing\n\nAlready exists."
        info = detect_project_info(temp_project)
        result = add_e2e_section_to_readme(content, info)

        # Should be unchanged
        assert result == content

    def test_adds_after_run_tests(self, temp_project):
        """Should add after Run Tests section if present."""
        content = """# Project

## Development

### Run Tests
```bash
pytest tests/ -v
```

## Contributing
"""
        info = detect_project_info(temp_project)
        result = add_e2e_section_to_readme(content, info)

        # E2E section should appear after Run Tests
        run_tests_idx = result.find("### Run Tests")
        e2e_idx = result.find("run-e2e-tests.sh")
        assert e2e_idx > run_tests_idx


class TestUpdateClaudeMd:
    """Tests for CLAUDE.md updates."""

    def test_adds_e2e_commands(self, temp_project):
        """Should add E2E test commands."""
        content = (temp_project / "CLAUDE.md").read_text()
        info = detect_project_info(temp_project)
        result = update_claude_md(content, info)

        assert "run-e2e-tests.sh" in result

    def test_does_not_duplicate(self, temp_project):
        """Should not duplicate if already present."""
        content = "# CLAUDE.md\n\n## E2E\n\n```bash\n./scripts/run-e2e-tests.sh\n```"
        info = detect_project_info(temp_project)
        result = update_claude_md(content, info)

        # Should be unchanged
        assert result == content


class TestUpdateDocs:
    """Tests for full documentation update."""

    def test_creates_e2e_readme(self, project_with_e2e):
        """Should create tests/e2e/README.md."""
        result = update_docs(project_with_e2e)

        readme = project_with_e2e / "tests" / "e2e" / "README.md"
        assert readme.exists()

    def test_updates_readme(self, project_with_e2e):
        """Should update README.md with E2E section."""
        # Ensure no E2E section exists first
        readme = project_with_e2e / "README.md"
        original = readme.read_text()
        assert "run-e2e-tests.sh" not in original

        result = update_docs(project_with_e2e)

        updated = readme.read_text()
        assert "run-e2e-tests.sh" in updated

    def test_updates_claude_md(self, project_with_e2e):
        """Should update CLAUDE.md with E2E commands."""
        result = update_docs(project_with_e2e)

        claude_md = project_with_e2e / "CLAUDE.md"
        content = claude_md.read_text()
        assert "run-e2e-tests.sh" in content

    def test_dry_run_does_not_modify(self, project_with_e2e):
        """Dry run should not modify files."""
        readme = project_with_e2e / "README.md"
        original = readme.read_text()

        result = update_docs(project_with_e2e, dry_run=True)

        # Should be unchanged
        assert readme.read_text() == original

    def test_returns_summary(self, project_with_e2e):
        """Should return summary of changes."""
        result = update_docs(project_with_e2e)

        assert "project" in result
        assert "files_updated" in result
        assert "files_created" in result
