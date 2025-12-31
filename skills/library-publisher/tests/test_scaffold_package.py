"""Tests for scaffold_package.py."""

import sys
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from scaffold_package import (
    to_import_name,
    extract_exports_from_module,
    detect_dependencies,
    generate_pyproject_toml,
    generate_init_py,
    scaffold_package,
)


class TestToImportName:
    """Tests for to_import_name function."""

    def test_converts_dashes_to_underscores(self):
        """Test converting package name to import name."""
        assert to_import_name("my-package-lib") == "my_package_lib"
        assert to_import_name("jira-assistant-skills-lib") == "jira_assistant_skills_lib"

    def test_preserves_underscores(self):
        """Test that underscores are preserved."""
        assert to_import_name("my_package") == "my_package"


class TestExtractExportsFromModule:
    """Tests for extract_exports_from_module function."""

    def test_extracts_functions(self, sample_library):
        """Test extracting public functions."""
        lib_dir = sample_library / "skills" / "shared" / "scripts" / "lib"
        exports = extract_exports_from_module(lib_dir / "formatters.py")

        assert "format_table" in exports
        assert "format_tree" in exports
        assert "TableFormatter" in exports

    def test_ignores_private_functions(self, temp_path):
        """Test that private functions are ignored."""
        module = temp_path / "test_module.py"
        module.write_text('''
def public_func():
    pass

def _private_func():
    pass

class PublicClass:
    pass

class _PrivateClass:
    pass
''')
        exports = extract_exports_from_module(module)

        assert "public_func" in exports
        assert "_private_func" not in exports
        assert "PublicClass" in exports
        assert "_PrivateClass" not in exports


class TestGeneratePyprojectToml:
    """Tests for generate_pyproject_toml function."""

    def test_generates_valid_toml(self):
        """Test generating pyproject.toml content."""
        content = generate_pyproject_toml(
            package_name="test-lib",
            import_name="test_lib",
            description="Test library",
            author="Test Author",
            dependencies={"tabulate>=0.9.0"},
            github_owner="testowner",
        )

        assert 'name = "test-lib"' in content
        assert 'version = "0.1.0"' in content
        assert "hatchling" in content
        assert "tabulate" in content


class TestGenerateInitPy:
    """Tests for generate_init_py function."""

    def test_generates_imports(self):
        """Test generating __init__.py with imports."""
        modules = [
            {"name": "formatters", "exports": ["format_table", "format_tree"]},
            {"name": "validators", "exports": ["validate_url"]},
        ]
        content = generate_init_py(modules, "test_lib")

        assert "from .formatters import format_table, format_tree" in content
        assert "from .validators import validate_url" in content
        assert "__version__" in content
        assert "__all__" in content


class TestScaffoldPackage:
    """Tests for scaffold_package function."""

    def test_dry_run_returns_info(self, sample_library, temp_path):
        """Test dry run returns package info without creating files."""
        lib_dir = sample_library / "skills" / "shared" / "scripts" / "lib"
        output_dir = temp_path / "output"

        result = scaffold_package(
            package_name="test-lib",
            source_dir=lib_dir,
            output_dir=output_dir,
            dry_run=True,
        )

        assert result["package_name"] == "test-lib"
        assert result["import_name"] == "test_lib"
        assert not output_dir.exists()

    def test_creates_package_structure(self, sample_library, temp_path):
        """Test creating complete package structure."""
        lib_dir = sample_library / "skills" / "shared" / "scripts" / "lib"
        output_dir = temp_path / "test-lib"

        result = scaffold_package(
            package_name="test-lib",
            source_dir=lib_dir,
            output_dir=output_dir,
            dry_run=False,
        )

        # Check directories
        assert output_dir.exists()
        assert (output_dir / "src" / "test_lib").exists()
        assert (output_dir / "tests").exists()
        assert (output_dir / ".github" / "workflows").exists()

        # Check files
        assert (output_dir / "pyproject.toml").exists()
        assert (output_dir / "README.md").exists()
        assert (output_dir / "LICENSE").exists()
        assert (output_dir / ".gitignore").exists()
        assert (output_dir / "src" / "test_lib" / "__init__.py").exists()
        assert (output_dir / "src" / "test_lib" / "formatters.py").exists()
