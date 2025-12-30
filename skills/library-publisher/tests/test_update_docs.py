"""Tests for update_docs.py module."""

import pytest
from pathlib import Path

# Import functions from update_docs
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from update_docs import (
    add_pypi_badge,
    update_shared_library_section,
    update_test_commands,
    update_project_structure,
    update_claude_md,
    update_readme,
    update_claude_md_file,
    update_docs,
)


class TestAddPyPiBadge:
    """Tests for add_pypi_badge function."""

    def test_adds_badge_when_missing(self):
        """Test that PyPI badge is added when missing."""
        content = '''# Project
<p align="center">
  <a href="https://github.com/org/repo"><img src="https://img.shields.io/github/stars/org/repo" alt="Stars"></a>
</p>
'''
        result = add_pypi_badge(content, "my-package")
        assert "pypi.org/project/my-package" in result
        assert "img.shields.io/pypi/v/my-package" in result

    def test_does_not_duplicate_badge(self):
        """Test that badge is not added if already present."""
        content = '''# Project
<p align="center">
  <a href="https://pypi.org/project/my-package/"><img src="badge" alt="PyPI"></a>
</p>
'''
        result = add_pypi_badge(content, "my-package")
        assert result == content

    def test_handles_no_badge_section(self):
        """Test handling when no badge section exists."""
        content = "# Project\n\nSome content"
        result = add_pypi_badge(content, "my-package")
        # Should return unchanged if no badge section
        assert result == content


class TestUpdateSharedLibrarySection:
    """Tests for update_shared_library_section function."""

    def test_updates_existing_section(self):
        """Test updating an existing Shared Library section."""
        content = '''# Project

## Shared Library

Old content about shared library.

## Other Section
'''
        result = update_shared_library_section(content, "my-package", "my_package")
        assert "pip install my-package" in result
        assert "from my_package import" in result
        assert "## Other Section" in result

    def test_preserves_content_without_section(self):
        """Test content without Shared Library section is unchanged."""
        content = "# Project\n\n## Other Section\n"
        result = update_shared_library_section(content, "my-package", "my_package")
        assert result == content


class TestUpdateTestCommands:
    """Tests for update_test_commands function."""

    def test_removes_pythonpath_quoted(self):
        """Test removing quoted PYTHONPATH."""
        content = 'PYTHONPATH="skills/lib" pytest tests/'
        result = update_test_commands(content)
        assert "PYTHONPATH" not in result
        assert "pytest tests/" in result

    def test_removes_pythonpath_unquoted(self):
        """Test removing unquoted PYTHONPATH."""
        content = "PYTHONPATH=skills/lib pytest tests/"
        result = update_test_commands(content)
        assert "PYTHONPATH" not in result
        assert "pytest tests/" in result

    def test_adds_pip_install_before_pytest(self):
        """Test adding pip install before pytest command."""
        content = '''```bash
pytest tests/ -v
```'''
        result = update_test_commands(content)
        assert "pip install -r requirements.txt" in result
        assert "pytest" in result


class TestUpdateProjectStructure:
    """Tests for update_project_structure function."""

    def test_removes_lib_files(self):
        """Test removing lib file listings."""
        content = '''## Project Structure

```
├── skills/
│   └── shared/scripts/lib/
│   ├── formatters.py
│   └── validators.py
├── README.md
```
'''
        result = update_project_structure(content, "my-package")
        assert "formatters.py" not in result or "shared/scripts/lib" not in result

    def test_adds_requirements_txt(self):
        """Test adding requirements.txt if missing."""
        content = '''## Project Structure

```
├── README.md
├── CLAUDE.md
```
'''
        result = update_project_structure(content, "my-package")
        assert "requirements.txt" in result


class TestUpdateClaudeMd:
    """Tests for update_claude_md function."""

    def test_removes_pythonpath(self):
        """Test removing PYTHONPATH from CLAUDE.md."""
        content = 'PYTHONPATH="skills/lib" pytest'
        result = update_claude_md(content, "my-package", "my_package")
        assert 'PYTHONPATH="skills/lib"' not in result
        assert "pytest" in result

    def test_updates_import_reference(self):
        """Test updating import reference."""
        content = "All Python scripts import from `skills/shared/scripts/lib/`:"
        result = update_claude_md(content, "my-package", "my_package")
        assert "my-package" in result
        assert "PyPI package" in result

    def test_updates_pythonpath_requirement(self):
        """Test updating PYTHONPATH requirement text."""
        content = "Scripts require `PYTHONPATH` to be set for imports to work."
        result = update_claude_md(content, "my-package", "my_package")
        assert "my-package" in result
        assert "pip install" in result


class TestUpdateReadme:
    """Tests for update_readme function."""

    def test_updates_readme(self, sample_project):
        """Test updating README.md."""
        result = update_readme(sample_project, "test-lib", "test_lib", dry_run=True)
        assert result["updated"] is True

    def test_returns_error_when_missing(self, temp_dir):
        """Test error when README.md missing."""
        result = update_readme(temp_dir, "test-lib", "test_lib")
        assert result["updated"] is False
        assert "not found" in result["error"]


class TestUpdateClaudeMdFile:
    """Tests for update_claude_md_file function."""

    def test_updates_claude_md(self, sample_project):
        """Test updating CLAUDE.md file."""
        result = update_claude_md_file(sample_project, "test-lib", "test_lib", dry_run=True)
        assert result["updated"] is True

    def test_returns_error_when_missing(self, temp_dir):
        """Test error when CLAUDE.md missing."""
        result = update_claude_md_file(temp_dir, "test-lib", "test_lib")
        assert result["updated"] is False
        assert "not found" in result["error"]


class TestUpdateDocs:
    """Tests for main update_docs function."""

    def test_updates_all_docs(self, sample_project):
        """Test updating all documentation files."""
        result = update_docs(
            project_path=sample_project,
            package_name="test-lib",
            dry_run=True,
        )
        assert result["package_name"] == "test-lib"
        assert result["import_name"] == "test_lib"
        assert len(result["files"]) == 2

    def test_generates_package_url(self, sample_project):
        """Test auto-generating package URL."""
        result = update_docs(
            project_path=sample_project,
            package_name="test-lib",
            dry_run=True,
        )
        assert "pypi.org/project/test-lib" in result["package_url"]

    def test_uses_provided_url(self, sample_project):
        """Test using provided package URL."""
        result = update_docs(
            project_path=sample_project,
            package_name="test-lib",
            package_url="https://custom.url/",
            dry_run=True,
        )
        assert result["package_url"] == "https://custom.url/"

    def test_dry_run_does_not_modify(self, sample_project):
        """Test dry run doesn't modify files."""
        original_readme = (sample_project / "README.md").read_text()

        update_docs(
            project_path=sample_project,
            package_name="test-lib",
            dry_run=True,
        )

        assert (sample_project / "README.md").read_text() == original_readme

    def test_actual_run_modifies_files(self, sample_project):
        """Test actual run modifies files."""
        original_readme = (sample_project / "README.md").read_text()

        update_docs(
            project_path=sample_project,
            package_name="test-lib",
            dry_run=False,
        )

        new_readme = (sample_project / "README.md").read_text()
        assert new_readme != original_readme
        assert "test-lib" in new_readme
