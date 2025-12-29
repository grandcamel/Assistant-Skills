"""
Tests for validate_project.py
"""

import pytest
import sys
from pathlib import Path

# Add scripts to path for importing script modules
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))


class TestValidateProject:
    """Tests for project validation functionality."""

    def test_validates_valid_project(self, sample_project):
        """Test that a valid project passes validation."""
        from validate_project import run_validation

        result = run_validation(sample_project)

        # Should have no errors (structure exists)
        assert len(result['errors']) == 0
        assert result['valid'] is True

    def test_detects_missing_settings(self, temp_dir):
        """Test that missing settings.json is detected."""
        from validate_project import run_validation

        # Create minimal structure without settings
        project = Path(temp_dir) / "BadProject"
        skills = project / ".claude" / "skills"
        skills.mkdir(parents=True)

        result = run_validation(str(project))

        assert "settings.json" in str(result['errors'])
        assert result['valid'] is False

    def test_validates_skill_md(self, sample_project):
        """Test SKILL.md validation."""
        from validate_project import validate_skill_md

        skill_path = Path(sample_project) / ".claude" / "skills" / "test-sample"
        issues = validate_skill_md(skill_path)

        # Should have no errors for valid SKILL.md
        errors = [i for level, i in issues if level == 'error']
        assert len(errors) == 0

    def test_detects_missing_skill_md(self, sample_project):
        """Test that missing SKILL.md is detected."""
        from validate_project import validate_skill_md

        # Create skill without SKILL.md
        skill_path = Path(sample_project) / ".claude" / "skills" / "test-empty"
        skill_path.mkdir(parents=True)

        issues = validate_skill_md(skill_path)

        errors = [i for level, i in issues if level == 'error']
        assert any("Missing SKILL.md" in e for e in errors)

    def test_validates_scripts(self, sample_project):
        """Test script validation."""
        from validate_project import validate_scripts

        # Create a script
        skill_path = Path(sample_project) / ".claude" / "skills" / "test-sample"
        scripts_dir = skill_path / "scripts"
        scripts_dir.mkdir(exist_ok=True)

        script = scripts_dir / "list_sample.py"
        script.write_text("""#!/usr/bin/env python3
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--profile', '-p')
""")

        issues = validate_scripts(skill_path)

        # Should have no major issues
        errors = [i for level, i in issues if level == 'error']
        assert len(errors) == 0

    def test_detects_script_issues(self, temp_dir):
        """Test that script issues are detected."""
        from validate_project import validate_scripts

        # Create a minimal skill structure directly
        skill_path = Path(temp_dir) / "test-skill"
        scripts_dir = skill_path / "scripts"
        scripts_dir.mkdir(parents=True)

        # Create script without argparse
        script = scripts_dir / "bad_script.py"
        script.write_text("print('no argparse')")

        # Verify the script was created
        assert script.exists()

        issues = validate_scripts(skill_path)

        # Should have warnings about missing shebang and argparse
        warnings = [msg for level, msg in issues if level == 'warning']
        assert len(warnings) >= 1, f"Expected warnings but got: {issues}"
        assert any("argparse" in w or "shebang" in w for w in warnings)


class TestValidationOutput:
    """Tests for validation output formatting."""

    def test_json_output(self, sample_project):
        """Test JSON output format."""
        from validate_project import run_validation
        import json

        result = run_validation(sample_project)

        # Should be valid JSON
        json_str = json.dumps(result)
        parsed = json.loads(json_str)

        assert 'valid' in parsed
        assert 'errors' in parsed
        assert 'warnings' in parsed

    def test_strict_mode(self, sample_project):
        """Test that strict mode treats warnings as errors."""
        from validate_project import run_validation

        # Normal mode - warnings don't fail
        normal_result = run_validation(sample_project, strict=False)

        # Strict mode - warnings fail
        strict_result = run_validation(sample_project, strict=True)

        # If there are warnings, strict should fail
        if normal_result['warnings']:
            assert strict_result['valid'] is False
