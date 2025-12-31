"""Tests for skills-optimizer shell scripts."""

import os
import subprocess
import pytest
from pathlib import Path


SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"


class TestScriptStructure:
    """Tests for shell script structure and validity."""

    def test_analyze_skill_exists(self):
        """analyze-skill.sh should exist."""
        script = SCRIPTS_DIR / "analyze-skill.sh"
        assert script.exists(), "analyze-skill.sh not found"

    def test_audit_all_skills_exists(self):
        """audit-all-skills.sh should exist."""
        script = SCRIPTS_DIR / "audit-all-skills.sh"
        assert script.exists(), "audit-all-skills.sh not found"

    def test_validate_skill_exists(self):
        """validate-skill.sh should exist."""
        script = SCRIPTS_DIR / "validate-skill.sh"
        assert script.exists(), "validate-skill.sh not found"

    def test_scripts_are_executable(self):
        """All shell scripts should be executable."""
        for script in SCRIPTS_DIR.glob("*.sh"):
            assert os.access(script, os.X_OK), f"{script.name} is not executable"

    def test_scripts_have_shebang(self):
        """All shell scripts should have proper shebang."""
        for script in SCRIPTS_DIR.glob("*.sh"):
            content = script.read_text()
            assert content.startswith("#!/"), f"{script.name} missing shebang"


class TestAnalyzeSkill:
    """Tests for analyze-skill.sh functionality."""

    def test_no_args_exits_with_error(self):
        """Running without args should exit with error."""
        script = SCRIPTS_DIR / "analyze-skill.sh"
        result = subprocess.run(
            [str(script)],
            capture_output=True,
            text=True
        )
        # Script should exit with error when no path provided
        assert result.returncode != 0

    def test_invalid_path_exits_with_error(self):
        """Invalid path should show error message."""
        script = SCRIPTS_DIR / "analyze-skill.sh"
        result = subprocess.run(
            [str(script), "/nonexistent/path"],
            capture_output=True,
            text=True
        )
        output = result.stdout + result.stderr
        assert result.returncode != 0
        assert "not found" in output.lower() or "error" in output.lower()


class TestValidateSkill:
    """Tests for validate-skill.sh functionality."""

    def test_no_args_exits_with_error(self):
        """Running without args should exit with error."""
        script = SCRIPTS_DIR / "validate-skill.sh"
        result = subprocess.run(
            [str(script)],
            capture_output=True,
            text=True
        )
        assert result.returncode != 0

    def test_invalid_path_exits_with_error(self):
        """Invalid path should show error message."""
        script = SCRIPTS_DIR / "validate-skill.sh"
        result = subprocess.run(
            [str(script), "/nonexistent/path"],
            capture_output=True,
            text=True
        )
        assert result.returncode != 0


class TestAuditAllSkills:
    """Tests for audit-all-skills.sh functionality."""

    def test_invalid_path_exits_with_error(self):
        """Invalid path should exit with error."""
        script = SCRIPTS_DIR / "audit-all-skills.sh"
        result = subprocess.run(
            [str(script), "/nonexistent/path"],
            capture_output=True,
            text=True
        )
        assert result.returncode != 0
