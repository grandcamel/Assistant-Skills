"""Tests for analyze_library.py."""

import sys
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from analyze_library import (
    find_library_dir,
    analyze_module,
    suggest_package_name,
    analyze_library,
)


class TestFindLibraryDir:
    """Tests for find_library_dir function."""

    def test_finds_skills_shared_lib(self, sample_library):
        """Test finding library in skills/shared/scripts/lib."""
        lib_dir = find_library_dir(sample_library)
        assert lib_dir is not None
        assert lib_dir.exists()
        assert "shared/scripts/lib" in str(lib_dir)

    def test_returns_none_for_nonexistent(self, temp_path):
        """Test returns None when library doesn't exist."""
        lib_dir = find_library_dir(temp_path)
        assert lib_dir is None


class TestAnalyzeModule:
    """Tests for analyze_module function."""

    def test_extracts_functions(self, sample_library):
        """Test that functions are extracted from module."""
        lib_dir = sample_library / "skills" / "shared" / "scripts" / "lib"
        result = analyze_module(lib_dir / "formatters.py")

        assert result["name"] == "formatters"
        assert "format_table" in result["functions"]
        assert "format_tree" in result["functions"]

    def test_extracts_classes(self, sample_library):
        """Test that classes are extracted from module."""
        lib_dir = sample_library / "skills" / "shared" / "scripts" / "lib"
        result = analyze_module(lib_dir / "formatters.py")

        assert "TableFormatter" in result["classes"]

    def test_counts_lines(self, sample_library):
        """Test that line count is calculated."""
        lib_dir = sample_library / "skills" / "shared" / "scripts" / "lib"
        result = analyze_module(lib_dir / "formatters.py")

        assert result["lines"] > 0


class TestSuggestPackageName:
    """Tests for suggest_package_name function."""

    def test_extracts_topic_from_name(self, temp_path):
        """Test extracting topic from project name."""
        project = temp_path / "Jira-Assistant-Skills"
        project.mkdir()

        name = suggest_package_name(project)
        assert name == "jira-assistant-skills-lib"

    def test_handles_simple_name(self, temp_path):
        """Test handling simple project name."""
        project = temp_path / "my-project"
        project.mkdir()

        name = suggest_package_name(project)
        assert "my_project" in name


class TestAnalyzeLibrary:
    """Tests for analyze_library function."""

    def test_analyzes_complete_library(self, sample_library):
        """Test analyzing a complete library."""
        result = analyze_library(sample_library)

        assert result["library_found"] is True
        assert len(result["modules"]) >= 2
        assert result["total_lines"] > 0

    def test_finds_usage_in_project(self, sample_project):
        """Test finding library usage in project scripts."""
        result = analyze_library(sample_project)

        assert result["usage"]["files_using_library"] >= 1
        assert result["usage"]["total_imports"] >= 1

    def test_handles_missing_library(self, temp_path):
        """Test handling project without library."""
        result = analyze_library(temp_path)

        assert result["library_found"] is False
        assert "error" in result
