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

    def test_validates_valid_project(self, sample_project_new):
        """Test that a valid project (new structure) passes validation."""
        from validate_project import run_validation

        result = run_validation(sample_project_new)

        # Should have no errors (structure exists)
        assert len(result['errors']) == 0
        assert result['valid'] is True

    def test_detects_missing_plugin_json(self, temp_dir):
        """Test that missing plugin.json is detected."""
        from validate_project import run_validation

        # Create minimal structure without plugin.json
        project = Path(temp_dir) / "BadProject"
        plugin_dir = project / ".claude-plugin"
        plugin_dir.mkdir(parents=True)

        result = run_validation(str(project))

        assert "plugin.json" in str(result['errors'])
        assert result['valid'] is False

    def test_validates_skill_md(self, sample_project_new):
        """Test SKILL.md validation."""
        from validate_project import validate_skill_md

        skill_path = Path(sample_project_new) / "skills" / "test-sample"
        issues = validate_skill_md(skill_path)

        # Should have no errors for valid SKILL.md
        errors = [i for level, i in issues if level == 'error']
        assert len(errors) == 0

    def test_detects_missing_skill_md(self, sample_project_new):
        """Test that missing SKILL.md is detected."""
        from validate_project import validate_skill_md

        # Create skill without SKILL.md
        skill_path = Path(sample_project_new) / "skills" / "test-empty"
        skill_path.mkdir(parents=True)

        issues = validate_skill_md(skill_path)

        errors = [i for level, i in issues if level == 'error']
        assert any("Missing SKILL.md" in e for e in errors)

    def test_validates_plugin_structure(self, sample_project_new):
        """Test plugin structure validation."""
        from validate_project import validate_plugin_structure

        issues = validate_plugin_structure(Path(sample_project_new))

        # Should have no errors
        errors = [msg for level, msg in issues if level == 'error']
        assert len(errors) == 0

    def test_detects_embedded_scripts(self, sample_project_new):
        """Test detection of embedded scripts in skill directories."""
        from validate_project import validate_no_embedded_scripts

        # Create skill with scripts directory
        skill_path = Path(sample_project_new) / "skills" / "test-sample"
        scripts_dir = skill_path / "scripts"
        scripts_dir.mkdir(exist_ok=True)

        script = scripts_dir / "some_script.py"
        script.write_text("print('hello')")

        issues = validate_no_embedded_scripts(skill_path)

        # Should have info message about scripts
        info_messages = [msg for level, msg in issues if level == 'info']
        assert len(info_messages) > 0
        assert any("script" in msg.lower() for msg in info_messages)

    def test_validates_version_management(self, sample_project_new):
        """Test VERSION file validation."""
        from validate_project import validate_version_management

        issues = validate_version_management(Path(sample_project_new))

        # Should have no errors
        errors = [msg for level, msg in issues if level == 'error']
        assert len(errors) == 0

    def test_validates_hub_router_skill(self, sample_project_new):
        """Test hub/router skill validation."""
        from validate_project import validate_hub_router_skill

        issues = validate_hub_router_skill(Path(sample_project_new), 'test')

        # Should have no errors
        errors = [msg for level, msg in issues if level == 'error']
        assert len(errors) == 0


class TestValidationOutput:
    """Tests for validation output formatting."""

    def test_json_output(self, sample_project_new):
        """Test JSON output format."""
        from validate_project import run_validation
        import json

        result = run_validation(sample_project_new)

        # Should be valid JSON
        json_str = json.dumps(result)
        parsed = json.loads(json_str)

        assert 'valid' in parsed
        assert 'errors' in parsed
        assert 'warnings' in parsed
        assert 'info' in parsed

    def test_strict_mode(self, sample_project_new):
        """Test that strict mode treats warnings as errors."""
        from validate_project import run_validation

        # Normal mode - warnings don't fail
        normal_result = run_validation(sample_project_new, strict=False)

        # Strict mode - warnings fail
        strict_result = run_validation(sample_project_new, strict=True)

        # If there are warnings, strict should fail
        if normal_result['warnings']:
            assert strict_result['valid'] is False

    def test_detects_old_structure(self, sample_project):
        """Test that old structure is detected and flagged."""
        from validate_project import run_validation

        result = run_validation(sample_project)

        # Should detect old structure
        project_type = result['project_type']
        assert project_type['structure'] == 'old'

        # Should have info suggesting migration
        all_messages = result['errors'] + result['warnings'] + result['info']
        assert any('migrate' in msg.lower() or 'old' in msg.lower()
                   for msg in all_messages)


class TestProjectTypeDetection:
    """Tests for project type detection."""

    def test_detects_new_structure(self, sample_project_new):
        """Test detection of new structure."""
        from validate_project import detect_project_type

        result = detect_project_type(Path(sample_project_new))

        assert result['structure'] == 'new'
        assert result['topic'] == 'test'

    def test_detects_old_structure(self, sample_project):
        """Test detection of old structure."""
        from validate_project import detect_project_type

        result = detect_project_type(Path(sample_project))

        assert result['structure'] == 'old'

    def test_detects_version(self, sample_project_new):
        """Test detection of VERSION file."""
        from validate_project import detect_project_type

        result = detect_project_type(Path(sample_project_new))

        assert result['version'] == '1.0.0'
