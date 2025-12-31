"""Tests for setup_e2e.py script."""

import pytest
import sys
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from setup_e2e import (
    detect_project_info,
    setup_e2e,
)


class TestDetectProjectInfo:
    """Tests for project info detection."""

    def test_detects_assistant_skills_project(self, temp_project):
        """Should detect Assistant Skills project structure."""
        result = detect_project_info(temp_project)

        assert result["has_skills"] is True
        assert result["has_plugin_json"] is True

    def test_detects_empty_project(self, empty_project):
        """Should handle empty projects."""
        result = detect_project_info(empty_project)

        assert result["has_skills"] is False
        assert result["has_plugin_json"] is False

    def test_finds_skills(self, temp_project):
        """Should find skills correctly."""
        result = detect_project_info(temp_project)

        assert len(result["skills"]) == 2
        assert "sample-skill" in result["skills"]
        assert "another-skill" in result["skills"]

    def test_gets_plugin_name(self, temp_project):
        """Should get plugin name from plugin.json."""
        result = detect_project_info(temp_project)

        assert result["name"] == "test-plugin"


class TestSetupE2E:
    """Tests for E2E setup functionality."""

    def test_creates_docker_files(self, temp_project):
        """Should create Docker configuration files."""
        result = setup_e2e(temp_project)

        assert (temp_project / "docker" / "e2e" / "Dockerfile").exists()
        assert (temp_project / "docker" / "e2e" / "docker-compose.yml").exists()
        assert "docker/e2e/Dockerfile" in result["files_created"]

    def test_creates_test_directory(self, temp_project):
        """Should create tests/e2e directory without __init__.py.

        Note: __init__.py is intentionally not created to avoid pytest
        collection conflicts when projects have multiple test directories.
        """
        setup_e2e(temp_project)

        e2e_dir = temp_project / "tests" / "e2e"
        assert e2e_dir.exists()
        assert not (e2e_dir / "__init__.py").exists()  # Avoid pytest conflicts
        assert (e2e_dir / "conftest.py").exists()
        assert (e2e_dir / "runner.py").exists()

    def test_creates_run_script(self, temp_project):
        """Should create run-e2e-tests.sh script."""
        setup_e2e(temp_project)

        script = temp_project / "scripts" / "run-e2e-tests.sh"
        assert script.exists()
        # Check it's executable (has shebang)
        content = script.read_text()
        assert content.startswith("#!/")

    def test_creates_requirements_file(self, temp_project):
        """Should create requirements-e2e.txt."""
        setup_e2e(temp_project)

        req_file = temp_project / "requirements-e2e.txt"
        assert req_file.exists()
        content = req_file.read_text()
        assert "pytest" in content
        assert "pyyaml" in content

    def test_dry_run_does_not_create_files(self, temp_project):
        """Dry run should not create any files."""
        result = setup_e2e(temp_project, dry_run=True)

        assert len(result["files_created"]) > 0
        # Files should NOT exist
        assert not (temp_project / "docker" / "e2e" / "Dockerfile").exists()
        assert not (temp_project / "tests" / "e2e" / "runner.py").exists()

    def test_returns_summary(self, temp_project):
        """Should return summary of created files."""
        result = setup_e2e(temp_project)

        assert "files_created" in result
        assert "project" in result
        assert len(result["files_created"]) > 0


class TestSetupE2EIdempotency:
    """Tests for running setup on existing project."""

    def test_runs_successfully_on_existing_e2e(self, project_with_e2e):
        """Should run without errors on project with existing E2E setup."""
        # Run setup on project that already has tests/e2e
        result = setup_e2e(project_with_e2e)

        # Should still report files created (setup overwrites)
        assert len(result["files_created"]) > 0
        assert (project_with_e2e / "tests" / "e2e" / "runner.py").exists()
        assert (project_with_e2e / "docker" / "e2e" / "Dockerfile").exists()
