"""Tests for generate_test_cases.py script."""

import pytest
import sys
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from generate_test_cases import (
    parse_skill_md,
    analyze_plugin,
    generate_skill_tests,
    generate_plugin_tests,
    generate_test_cases_yaml,
    generate_test_cases,
)


class TestParseSkillMd:
    """Tests for SKILL.md parsing."""

    def test_parses_yaml_frontmatter(self, temp_project):
        """Should parse YAML frontmatter from SKILL.md."""
        skill_md = temp_project / "skills" / "sample-skill" / "SKILL.md"
        result = parse_skill_md(skill_md)

        assert result["name"] == "sample-skill"
        assert result["has_frontmatter"] is True
        assert "sample skill for testing" in result["description"].lower()

    def test_extracts_trigger_phrases(self, temp_project):
        """Should extract trigger phrases from description."""
        skill_md = temp_project / "skills" / "sample-skill" / "SKILL.md"
        result = parse_skill_md(skill_md)

        # Should find quoted phrases
        assert len(result["trigger_phrases"]) > 0
        phrases_lower = [p.lower() for p in result["trigger_phrases"]]
        assert any("test" in p for p in phrases_lower)

    def test_finds_scripts(self, temp_project):
        """Should find Python scripts in skill."""
        skill_md = temp_project / "skills" / "sample-skill" / "SKILL.md"
        result = parse_skill_md(skill_md)

        assert "sample_script.py" in result["scripts"]

    def test_handles_missing_frontmatter(self, tmp_path):
        """Should handle SKILL.md without frontmatter."""
        skill_dir = tmp_path / "skill"
        skill_dir.mkdir()
        skill_md = skill_dir / "SKILL.md"
        skill_md.write_text("# Simple Skill\n\nNo frontmatter here.")

        result = parse_skill_md(skill_md)

        assert result["has_frontmatter"] is False
        assert result["name"] == "skill"  # Uses directory name


class TestAnalyzePlugin:
    """Tests for plugin analysis."""

    def test_extracts_plugin_info(self, temp_project):
        """Should extract info from plugin.json."""
        result = analyze_plugin(temp_project)

        assert result["plugin_name"] == "test-plugin"
        assert result["plugin_version"] == "1.0.0"

    def test_finds_all_skills(self, temp_project):
        """Should find all skills in project."""
        result = analyze_plugin(temp_project)

        assert len(result["skills"]) == 2
        skill_names = [s["name"] for s in result["skills"]]
        assert "sample-skill" in skill_names
        assert "another-skill" in skill_names

    def test_handles_missing_plugin_json(self, empty_project):
        """Should handle projects without plugin.json."""
        result = analyze_plugin(empty_project)

        assert result["plugin_name"] is None
        assert len(result["skills"]) == 0


class TestGenerateSkillTests:
    """Tests for skill test generation."""

    def test_generates_discovery_test(self, temp_project):
        """Should generate skill discovery test."""
        skill_md = temp_project / "skills" / "sample-skill" / "SKILL.md"
        skill = parse_skill_md(skill_md)
        tests = generate_skill_tests(skill)

        discovery_tests = [t for t in tests if "discoverable" in t["id"]]
        assert len(discovery_tests) >= 1

    def test_generates_trigger_tests(self, temp_project):
        """Should generate tests from trigger phrases."""
        skill_md = temp_project / "skills" / "sample-skill" / "SKILL.md"
        skill = parse_skill_md(skill_md)
        tests = generate_skill_tests(skill)

        trigger_tests = [t for t in tests if "trigger" in t["id"]]
        # Should have at least one trigger test if phrases found
        if skill["trigger_phrases"]:
            assert len(trigger_tests) >= 1

    def test_generates_error_handling_test(self, temp_project):
        """Should generate error handling test."""
        skill_md = temp_project / "skills" / "sample-skill" / "SKILL.md"
        skill = parse_skill_md(skill_md)
        tests = generate_skill_tests(skill)

        error_tests = [t for t in tests if "error" in t["id"]]
        assert len(error_tests) >= 1


class TestGeneratePluginTests:
    """Tests for plugin-level test generation."""

    def test_generates_install_test(self, temp_project):
        """Should generate plugin installation test."""
        analysis = analyze_plugin(temp_project)
        tests = generate_plugin_tests(analysis)

        install_tests = [t for t in tests if "install" in t["id"]]
        assert len(install_tests) >= 1

    def test_generates_skills_verification(self, temp_project):
        """Should generate test to verify all skills loaded."""
        analysis = analyze_plugin(temp_project)
        tests = generate_plugin_tests(analysis)

        verify_tests = [t for t in tests if "verify" in t["id"]]
        assert len(verify_tests) >= 1


class TestGenerateTestCasesYaml:
    """Tests for YAML test cases generation."""

    def test_generates_valid_structure(self, temp_project):
        """Should generate valid YAML structure."""
        analysis = analyze_plugin(temp_project)
        result = generate_test_cases_yaml(analysis)

        assert "metadata" in result
        assert "settings" in result
        assert "suites" in result

    def test_includes_metadata(self, temp_project):
        """Should include metadata section."""
        analysis = analyze_plugin(temp_project)
        result = generate_test_cases_yaml(analysis)

        assert result["metadata"]["name"] == "test-plugin-e2e"
        assert "version" in result["metadata"]

    def test_includes_plugin_suite(self, temp_project):
        """Should include plugin installation suite."""
        analysis = analyze_plugin(temp_project)
        result = generate_test_cases_yaml(analysis)

        assert "plugin_installation" in result["suites"]

    def test_includes_skill_suites(self, temp_project):
        """Should include suite for each skill."""
        analysis = analyze_plugin(temp_project)
        result = generate_test_cases_yaml(analysis)

        assert "sample_skill" in result["suites"]
        assert "another_skill" in result["suites"]

    def test_includes_error_handling_suite(self, temp_project):
        """Should include error handling suite."""
        analysis = analyze_plugin(temp_project)
        result = generate_test_cases_yaml(analysis)

        assert "error_handling" in result["suites"]


class TestGenerateTestCases:
    """Tests for full test case generation."""

    def test_generates_yaml_file(self, temp_project):
        """Should generate test_cases.yaml file."""
        result = generate_test_cases(temp_project)

        yaml_file = temp_project / "tests" / "e2e" / "test_cases.yaml"
        assert yaml_file.exists()
        assert "tests/e2e/test_cases.yaml" in result["files_generated"]

    def test_generates_pytest_file(self, temp_project):
        """Should generate pytest test file."""
        result = generate_test_cases(temp_project)

        pytest_file = temp_project / "tests" / "e2e" / "test_plugin_e2e.py"
        assert pytest_file.exists()
        assert "tests/e2e/test_plugin_e2e.py" in result["files_generated"]

    def test_returns_analysis_summary(self, temp_project):
        """Should return analysis summary."""
        result = generate_test_cases(temp_project)

        assert result["analysis"]["plugin_name"] == "test-plugin"
        assert result["analysis"]["skills_found"] == 2

    def test_counts_generated_tests(self, temp_project):
        """Should count total generated tests."""
        result = generate_test_cases(temp_project)

        assert result["tests_generated"] > 0

    def test_uses_custom_output_path(self, temp_project):
        """Should use custom output path when provided."""
        custom_path = temp_project / "custom" / "tests.yaml"
        result = generate_test_cases(temp_project, output_path=custom_path)

        assert custom_path.exists()
