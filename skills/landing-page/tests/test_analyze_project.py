"""Tests for analyze_project.py module."""

import pytest
from pathlib import Path

# Import functions from analyze_project
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from analyze_project import (
    find_skills_directory,
    extract_product_name,
    count_skills,
    count_scripts,
    count_tests,
    extract_skill_info,
    detect_query_language,
    get_color_palette,
    analyze_project,
)


class TestFindSkillsDirectory:
    """Tests for find_skills_directory function."""

    def test_finds_skills_directory(self, sample_project):
        """Test finding .claude/skills directory."""
        result = find_skills_directory(sample_project)
        assert result is not None
        assert result.name == "skills"
        assert (result.parent.name == ".claude")

    def test_returns_none_when_missing(self, project_without_skills):
        """Test returning None when no skills directory."""
        result = find_skills_directory(project_without_skills)
        assert result is None


class TestExtractProductName:
    """Tests for extract_product_name function."""

    def test_extracts_from_directory_name(self, temp_path):
        """Test extracting product name from directory name."""
        project = temp_path / "Jira-Assistant-Skills"
        project.mkdir()
        result = extract_product_name(project)
        assert result == "Jira"

    def test_extracts_from_readme(self, temp_path):
        """Test extracting product name from README title."""
        project = temp_path / "some-project"
        project.mkdir()
        (project / "README.md").write_text("# Confluence Assistant Skills\n")
        result = extract_product_name(project)
        assert result == "Confluence"

    def test_falls_back_to_directory_name(self, temp_path):
        """Test fallback to cleaned directory name."""
        project = temp_path / "my-custom-project"
        project.mkdir()
        result = extract_product_name(project)
        assert "My" in result or "Custom" in result


class TestCountSkills:
    """Tests for count_skills function."""

    def test_counts_skills(self, sample_project):
        """Test counting skills in a project."""
        skills_path = sample_project / ".claude" / "skills"
        count, names = count_skills(skills_path)
        assert count == 1
        assert "test-skill" in names

    def test_excludes_shared_directory(self, sample_project):
        """Test that shared directory is excluded."""
        skills_path = sample_project / ".claude" / "skills"
        (skills_path / "shared").mkdir()
        count, names = count_skills(skills_path)
        assert "shared" not in names

    def test_excludes_hidden_directories(self, sample_project):
        """Test that hidden directories are excluded."""
        skills_path = sample_project / ".claude" / "skills"
        (skills_path / ".hidden").mkdir()
        count, names = count_skills(skills_path)
        assert ".hidden" not in names


class TestCountScripts:
    """Tests for count_scripts function."""

    def test_counts_scripts(self, sample_project):
        """Test counting Python scripts."""
        skills_path = sample_project / ".claude" / "skills"
        count = count_scripts(skills_path)
        assert count == 2  # test_script.py and another_script.py


class TestCountTests:
    """Tests for count_tests function."""

    def test_counts_test_functions(self, sample_project):
        """Test counting test functions."""
        skills_path = sample_project / ".claude" / "skills"
        count = count_tests(skills_path)
        assert count == 3  # test_one, test_two, test_three


class TestExtractSkillInfo:
    """Tests for extract_skill_info function."""

    def test_extracts_skill_name(self, sample_project):
        """Test extracting skill name."""
        skill_path = sample_project / ".claude" / "skills" / "test-skill"
        info = extract_skill_info(skill_path)
        assert info["name"] == "test-skill"

    def test_extracts_purpose(self, sample_project):
        """Test extracting skill purpose."""
        skill_path = sample_project / ".claude" / "skills" / "test-skill"
        info = extract_skill_info(skill_path)
        # Purpose should be extracted from "What this skill does" section
        assert "purpose" in info


class TestDetectQueryLanguage:
    """Tests for detect_query_language function."""

    def test_detects_jql(self, temp_path):
        """Test detecting JQL for Jira."""
        result = detect_query_language(temp_path, "jira")
        assert result == "JQL"

    def test_detects_cql(self, temp_path):
        """Test detecting CQL for Confluence."""
        result = detect_query_language(temp_path, "confluence")
        assert result == "CQL"

    def test_detects_spl(self, temp_path):
        """Test detecting SPL for Splunk."""
        result = detect_query_language(temp_path, "splunk")
        assert result == "SPL"

    def test_returns_default(self, temp_path):
        """Test returning default query language."""
        result = detect_query_language(temp_path, "unknown")
        assert result == "Query Language"


class TestGetColorPalette:
    """Tests for get_color_palette function."""

    def test_returns_jira_palette(self):
        """Test returning Jira color palette."""
        palette = get_color_palette("jira")
        assert palette["primary"] == "#0052CC"

    def test_returns_confluence_palette(self):
        """Test returning Confluence color palette."""
        palette = get_color_palette("confluence")
        assert palette["accent"] == "#36B37E"

    def test_returns_splunk_palette(self):
        """Test returning Splunk color palette."""
        palette = get_color_palette("splunk")
        assert palette["primary"] == "#FF6900"

    def test_returns_default_palette(self):
        """Test returning default palette for unknown product."""
        palette = get_color_palette("unknown")
        assert "primary" in palette
        assert "accent" in palette


class TestAnalyzeProject:
    """Tests for main analyze_project function."""

    def test_analyzes_project(self, sample_project):
        """Test full project analysis."""
        result = analyze_project(sample_project)
        assert result["skill_count"] == 1
        assert result["script_count"] == 2
        assert result["test_count"] == 3
        assert "test-skill" in result["skill_names"]

    def test_raises_for_missing_project(self, temp_path):
        """Test error for non-existent project."""
        with pytest.raises(ValueError, match="does not exist"):
            analyze_project(temp_path / "nonexistent")

    def test_raises_for_missing_skills(self, project_without_skills):
        """Test error when no skills directory."""
        with pytest.raises(ValueError, match="No .claude/skills"):
            analyze_project(project_without_skills)

    def test_includes_colors(self, sample_project):
        """Test that colors are included in result."""
        result = analyze_project(sample_project)
        assert "colors" in result
        assert "primary" in result["colors"]

    def test_includes_query_language(self, sample_project):
        """Test that query language is included."""
        result = analyze_project(sample_project)
        assert "query_language" in result

    def test_includes_github_info(self, sample_project):
        """Test that GitHub info is included."""
        result = analyze_project(sample_project)
        assert "github_org" in result
        assert "github_repo" in result
