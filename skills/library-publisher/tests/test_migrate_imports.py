"""Tests for migrate_imports.py."""

import sys
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from migrate_imports import (
    find_library_modules,
    migrate_file_imports,
    find_python_files,
    create_requirements_txt,
    migrate_project,
)


class TestFindLibraryModules:
    """Tests for find_library_modules function."""

    def test_finds_modules_in_library(self, sample_library):
        """Test finding modules in library directory."""
        modules = find_library_modules(sample_library)

        assert "formatters" in modules
        assert "validators" in modules

    def test_returns_default_for_missing_library(self, temp_path):
        """Test returns default modules when library not found."""
        modules = find_library_modules(temp_path)

        # Should return common module names
        assert len(modules) > 0


class TestMigrateFileImports:
    """Tests for migrate_file_imports function."""

    def test_migrates_from_imports(self, temp_path):
        """Test migrating 'from module import' statements."""
        script = temp_path / "test_script.py"
        script.write_text('''from formatters import format_table
from validators import validate_url
''')

        content, changes = migrate_file_imports(
            script,
            "mypackage_lib",
            {"formatters", "validators"},
        )

        assert "from mypackage_lib import format_table" in content
        assert "from mypackage_lib import validate_url" in content
        assert len(changes) == 2

    def test_migrates_import_statements(self, temp_path):
        """Test migrating 'import module' statements."""
        script = temp_path / "test_script.py"
        script.write_text('''import formatters
import validators
''')

        content, changes = migrate_file_imports(
            script,
            "mypackage_lib",
            {"formatters", "validators"},
        )

        assert "from mypackage_lib import formatters" in content
        assert len(changes) == 2

    def test_removes_syspath_manipulation(self, temp_path):
        """Test removing sys.path manipulation."""
        script = temp_path / "test_script.py"
        script.write_text('''import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'lib'))
from formatters import format_table
''')

        content, changes = migrate_file_imports(
            script,
            "mypackage_lib",
            {"formatters"},
        )

        assert "sys.path.insert" not in content
        assert "from mypackage_lib import format_table" in content


class TestFindPythonFiles:
    """Tests for find_python_files function."""

    def test_finds_python_files(self, sample_project):
        """Test finding Python files in project."""
        files = find_python_files(sample_project)

        assert len(files) >= 1
        assert all(f.suffix == ".py" for f in files)

    def test_excludes_library_files(self, sample_project):
        """Test excluding library files from results."""
        files = find_python_files(sample_project)

        for f in files:
            assert "shared/scripts/lib" not in str(f)


class TestCreateRequirementsTxt:
    """Tests for create_requirements_txt function."""

    def test_includes_package(self, temp_path):
        """Test including the package in requirements."""
        content = create_requirements_txt(temp_path, "mypackage_lib")

        assert "mypackage-lib>=0.1.0" in content

    def test_includes_pytest(self, temp_path):
        """Test including pytest in requirements."""
        content = create_requirements_txt(temp_path, "mypackage_lib")

        assert "pytest" in content


class TestMigrateProject:
    """Tests for migrate_project function."""

    def test_dry_run_makes_no_changes(self, sample_project):
        """Test dry run doesn't modify files."""
        script = sample_project / "skills" / "myskill" / "scripts" / "my_script.py"
        original_content = script.read_text()

        result = migrate_project(
            sample_project,
            "mypackage_lib",
            dry_run=True,
            remove_library=False,
        )

        assert script.read_text() == original_content
        assert result["imports_changed"] > 0

    def test_migrates_imports(self, sample_project):
        """Test migrating imports in project."""
        result = migrate_project(
            sample_project,
            "mypackage_lib",
            dry_run=False,
            remove_library=False,
        )

        script = sample_project / "skills" / "myskill" / "scripts" / "my_script.py"
        content = script.read_text()

        assert "from mypackage_lib import" in content
        assert result["requirements_created"] is True

    def test_creates_requirements_txt(self, sample_project):
        """Test creating requirements.txt."""
        migrate_project(
            sample_project,
            "mypackage_lib",
            dry_run=False,
            remove_library=False,
        )

        req_file = sample_project / "requirements.txt"
        assert req_file.exists()
        assert "mypackage-lib" in req_file.read_text()
