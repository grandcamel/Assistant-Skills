#!/usr/bin/env python3
"""
Scaffold a PyPI package from an existing shared library.

Usage:
    python scaffold_package.py --name "myproject-lib" --source /path/to/lib --output /path/to/output
"""

import argparse
import re
import shutil
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set
from datetime import datetime


def to_import_name(package_name: str) -> str:
    """Convert package name to valid Python import name."""
    return package_name.replace("-", "_")


def extract_exports_from_module(module_path: Path) -> List[str]:
    """Extract public exports from a module."""
    exports = []
    try:
        content = module_path.read_text()

        # Look for __all__
        import ast
        tree = ast.parse(content)

        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "__all__":
                        if isinstance(node.value, ast.List):
                            for elt in node.value.elts:
                                if isinstance(elt, ast.Constant):
                                    exports.append(elt.value)

        # If no __all__, find public functions and classes
        if not exports:
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and not node.name.startswith("_"):
                    exports.append(node.name)
                elif isinstance(node, ast.ClassDef) and not node.name.startswith("_"):
                    exports.append(node.name)

    except Exception:
        pass

    return exports


def detect_dependencies(source_dir: Path) -> Set[str]:
    """Detect external dependencies from library source."""
    stdlib = {
        "os", "sys", "re", "json", "datetime", "time", "pathlib", "typing",
        "collections", "functools", "itertools", "operator", "contextlib",
        "abc", "dataclasses", "enum", "copy", "hashlib", "base64", "uuid",
        "urllib", "http", "email", "logging", "argparse", "textwrap",
        "shutil", "tempfile", "glob", "fnmatch", "io", "pickle", "csv",
        "configparser", "ast", "inspect", "traceback", "warnings",
    }

    deps = set()
    import_pattern = r"^(?:from|import)\s+(\w+)"

    for py_file in source_dir.glob("*.py"):
        try:
            content = py_file.read_text()
            for match in re.finditer(import_pattern, content, re.MULTILINE):
                module = match.group(1)
                if module not in stdlib:
                    deps.add(module)
        except Exception:
            pass

    # Map common imports to PyPI package names
    dep_mapping = {
        "tabulate": "tabulate>=0.9.0",
        "requests": "requests>=2.28.0",
        "yaml": "PyYAML>=6.0",
        "dateutil": "python-dateutil>=2.8.0",
    }

    result = set()
    for dep in deps:
        if dep in dep_mapping:
            result.add(dep_mapping[dep])
        elif dep not in {"formatters", "validators", "cache", "error_handler",
                         "template_engine", "project_detector"}:
            # Skip internal modules
            pass

    return result


def generate_pyproject_toml(
    package_name: str,
    import_name: str,
    description: str,
    author: str,
    dependencies: Set[str],
    github_owner: str,
) -> str:
    """Generate pyproject.toml content."""
    deps_str = ",\n    ".join(f'"{d}"' for d in sorted(dependencies)) if dependencies else ""
    deps_section = f"""dependencies = [
    {deps_str}
]""" if dependencies else "dependencies = []"

    return f'''[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "{package_name}"
version = "0.1.0"
description = "{description}"
readme = "README.md"
license = "MIT"
requires-python = ">=3.8"
authors = [
    {{ name = "{author}" }}
]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]
{deps_section}

[project.urls]
Homepage = "https://github.com/{github_owner}/{package_name}"
Repository = "https://github.com/{github_owner}/{package_name}"
Issues = "https://github.com/{github_owner}/{package_name}/issues"

[tool.hatch.build.targets.sdist]
include = [
    "/src",
]

[tool.hatch.build.targets.wheel]
packages = ["src/{import_name}"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_functions = ["test_*"]
addopts = "-v --tb=short"
'''


def generate_init_py(modules: List[Dict], import_name: str) -> str:
    """Generate __init__.py with all exports."""
    lines = [
        '"""',
        f'{import_name} - Shared Python utilities for Assistant Skills.',
        '"""',
        '',
        '__version__ = "0.1.0"',
        '',
    ]

    # Import from each module
    for module in modules:
        if module["exports"]:
            exports = ", ".join(module["exports"])
            lines.append(f'from .{module["name"]} import {exports}')

    # Import modules themselves
    lines.append('')
    lines.append('# Module imports for direct access')
    for module in modules:
        lines.append(f'from . import {module["name"]}')

    # Build __all__
    lines.append('')
    lines.append('__all__ = [')
    lines.append('    "__version__",')
    for module in modules:
        lines.append(f'    "{module["name"]}",')
        for export in module["exports"]:
            lines.append(f'    "{export}",')
    lines.append(']')

    return '\n'.join(lines)


def generate_readme(
    package_name: str,
    import_name: str,
    description: str,
    modules: List[Dict],
    github_owner: str,
) -> str:
    """Generate README.md content."""
    module_table = "\n".join(
        f"| `{m['name']}` | {len(m['exports'])} exports |"
        for m in modules
    )

    example_exports = []
    for m in modules[:3]:
        example_exports.extend(m["exports"][:2])
    example_imports = ", ".join(example_exports[:6])

    return f'''# {package_name}

{description}

## Installation

```bash
pip install {package_name}
```

## Quick Start

```python
from {import_name} import {example_imports}
```

## Modules

| Module | Contents |
|--------|----------|
{module_table}

## Usage Examples

```python
from {import_name} import format_table, validate_url, handle_errors

# Format data as table
data = [{{"name": "Item 1", "value": 100}}]
print(format_table(data))

# Validate input
url = validate_url("https://example.com")

# Error handling decorator
@handle_errors
def my_function():
    pass
```

## Development

```bash
# Clone repository
git clone https://github.com/{github_owner}/{package_name}.git
cd {package_name}

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

## License

MIT License - see [LICENSE](LICENSE) for details.

## Links

- [PyPI Package](https://pypi.org/project/{package_name}/)
- [GitHub Repository](https://github.com/{github_owner}/{package_name})
'''


def generate_test_workflow() -> str:
    """Generate GitHub Actions test workflow."""
    return '''name: Tests

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.8", "3.9", "3.10", "3.11", "3.12"]

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e ".[dev]"

      - name: Run tests
        run: pytest --cov=src --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        if: matrix.python-version == '3.11'
        with:
          file: ./coverage.xml
'''


def generate_publish_workflow(package_name: str) -> str:
    """Generate GitHub Actions publish workflow."""
    return f'''name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install build tools
        run: pip install build

      - name: Build package
        run: python -m build

      - name: Upload artifacts
        uses: actions/upload-artifact@v4
        with:
          name: dist
          path: dist/

  publish-testpypi:
    needs: build
    runs-on: ubuntu-latest
    environment: testpypi
    permissions:
      id-token: write
    steps:
      - name: Download artifacts
        uses: actions/download-artifact@v4
        with:
          name: dist
          path: dist/

      - name: Publish to TestPyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          repository-url: https://test.pypi.org/legacy/
        continue-on-error: true

  publish-pypi:
    needs: build
    runs-on: ubuntu-latest
    environment: pypi
    permissions:
      id-token: write
    steps:
      - name: Download artifacts
        uses: actions/download-artifact@v4
        with:
          name: dist
          path: dist/

      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
'''


def generate_gitignore() -> str:
    """Generate .gitignore content."""
    return '''# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# Distribution / packaging
dist/
build/
*.egg-info/
*.egg

# Virtual environments
venv/
.venv/
env/

# Testing
.pytest_cache/
.coverage
htmlcov/
coverage.xml

# IDE
.idea/
.vscode/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
'''


def generate_license(author: str) -> str:
    """Generate MIT LICENSE content."""
    year = datetime.now().year
    return f'''MIT License

Copyright (c) {year} {author}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''


def generate_test_file(module_name: str, exports: List[str], import_name: str) -> str:
    """Generate a test file for a module."""
    lines = [
        '"""',
        f'Tests for {module_name} module.',
        '"""',
        '',
        'import pytest',
        f'from {import_name} import {module_name}',
        '',
        '',
    ]

    # Generate basic existence tests
    for export in exports[:10]:  # Limit to first 10 exports
        lines.append(f'def test_{export}_exists():')
        lines.append(f'    """Test that {export} is exported."""')
        lines.append(f'    assert hasattr({module_name}, "{export}")')
        lines.append('')

    return '\n'.join(lines)


def generate_conftest(import_name: str) -> str:
    """Generate conftest.py for tests."""
    return f'''"""
Pytest configuration and fixtures.
"""

import pytest
import tempfile
from pathlib import Path


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_data():
    """Sample data for testing formatters."""
    return [
        {{"name": "Item 1", "value": 100, "status": "active"}},
        {{"name": "Item 2", "value": 200, "status": "inactive"}},
        {{"name": "Item 3", "value": 300, "status": "active"}},
    ]
'''


def scaffold_package(
    package_name: str,
    source_dir: Path,
    output_dir: Path,
    description: str = "",
    author: str = "Assistant Skills",
    github_owner: str = "grandcamel",
    dry_run: bool = False,
) -> Dict:
    """Scaffold a complete PyPI package."""
    import_name = to_import_name(package_name)

    result = {
        "package_name": package_name,
        "import_name": import_name,
        "output_dir": str(output_dir),
        "files_created": [],
        "modules": [],
    }

    if not description:
        description = f"Shared Python utilities for {package_name.replace('-lib', '').replace('-', ' ').title()}"

    # Analyze source modules
    modules = []
    for py_file in sorted(source_dir.glob("*.py")):
        if py_file.name == "__init__.py":
            continue
        exports = extract_exports_from_module(py_file)
        modules.append({
            "name": py_file.stem,
            "path": py_file,
            "exports": exports,
        })
    result["modules"] = [{"name": m["name"], "exports": m["exports"]} for m in modules]

    # Detect dependencies
    dependencies = detect_dependencies(source_dir)
    # Always include tabulate as it's commonly used
    dependencies.add("tabulate>=0.9.0")

    if dry_run:
        result["dry_run"] = True
        return result

    # Create directories
    output_dir.mkdir(parents=True, exist_ok=True)
    src_dir = output_dir / "src" / import_name
    src_dir.mkdir(parents=True, exist_ok=True)
    tests_dir = output_dir / "tests"
    tests_dir.mkdir(parents=True, exist_ok=True)
    workflows_dir = output_dir / ".github" / "workflows"
    workflows_dir.mkdir(parents=True, exist_ok=True)

    # Copy source modules
    for module in modules:
        dest = src_dir / f"{module['name']}.py"
        shutil.copy2(module["path"], dest)
        result["files_created"].append(str(dest.relative_to(output_dir)))

    # Generate __init__.py
    init_content = generate_init_py(modules, import_name)
    init_path = src_dir / "__init__.py"
    init_path.write_text(init_content)
    result["files_created"].append(str(init_path.relative_to(output_dir)))

    # Generate pyproject.toml
    pyproject_content = generate_pyproject_toml(
        package_name, import_name, description, author, dependencies, github_owner
    )
    pyproject_path = output_dir / "pyproject.toml"
    pyproject_path.write_text(pyproject_content)
    result["files_created"].append("pyproject.toml")

    # Generate README.md
    readme_content = generate_readme(
        package_name, import_name, description, result["modules"], github_owner
    )
    readme_path = output_dir / "README.md"
    readme_path.write_text(readme_content)
    result["files_created"].append("README.md")

    # Generate LICENSE
    license_content = generate_license(author)
    license_path = output_dir / "LICENSE"
    license_path.write_text(license_content)
    result["files_created"].append("LICENSE")

    # Generate .gitignore
    gitignore_content = generate_gitignore()
    gitignore_path = output_dir / ".gitignore"
    gitignore_path.write_text(gitignore_content)
    result["files_created"].append(".gitignore")

    # Generate workflows
    test_workflow = generate_test_workflow()
    test_workflow_path = workflows_dir / "test.yml"
    test_workflow_path.write_text(test_workflow)
    result["files_created"].append(".github/workflows/test.yml")

    publish_workflow = generate_publish_workflow(package_name)
    publish_workflow_path = workflows_dir / "publish.yml"
    publish_workflow_path.write_text(publish_workflow)
    result["files_created"].append(".github/workflows/publish.yml")

    # Generate tests
    conftest_content = generate_conftest(import_name)
    conftest_path = tests_dir / "conftest.py"
    conftest_path.write_text(conftest_content)
    result["files_created"].append("tests/conftest.py")

    tests_init = tests_dir / "__init__.py"
    tests_init.write_text("")
    result["files_created"].append("tests/__init__.py")

    for module in modules:
        test_content = generate_test_file(module["name"], module["exports"], import_name)
        test_path = tests_dir / f"test_{module['name']}.py"
        test_path.write_text(test_content)
        result["files_created"].append(f"tests/test_{module['name']}.py")

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Scaffold a PyPI package from shared library"
    )
    parser.add_argument(
        "--name", "-n",
        required=True,
        help="Package name (e.g., jira-assistant-skills-lib)"
    )
    parser.add_argument(
        "--source", "-s",
        required=True,
        help="Source library directory"
    )
    parser.add_argument(
        "--output", "-o",
        required=True,
        help="Output directory for the package"
    )
    parser.add_argument(
        "--description", "-d",
        default="",
        help="Package description"
    )
    parser.add_argument(
        "--author", "-a",
        default="Assistant Skills",
        help="Package author"
    )
    parser.add_argument(
        "--github-owner", "-g",
        default="grandcamel",
        help="GitHub repository owner"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be created without creating files"
    )

    args = parser.parse_args()

    source_dir = Path(args.source)
    if not source_dir.exists():
        print(f"Error: Source directory does not exist: {source_dir}", file=sys.stderr)
        sys.exit(1)

    output_dir = Path(args.output)
    if output_dir.exists() and not args.dry_run:
        print(f"Error: Output directory already exists: {output_dir}", file=sys.stderr)
        sys.exit(1)

    result = scaffold_package(
        package_name=args.name,
        source_dir=source_dir,
        output_dir=output_dir,
        description=args.description,
        author=args.author,
        github_owner=args.github_owner,
        dry_run=args.dry_run,
    )

    print(f"Package: {result['package_name']}")
    print(f"Import:  {result['import_name']}")
    print(f"Output:  {result['output_dir']}")
    print()

    if result.get("dry_run"):
        print("DRY RUN - No files created")
        print()
        print("Would create:")
    else:
        print("Created files:")

    for f in result["files_created"]:
        print(f"  {f}")

    print()
    print("Modules included:")
    for m in result["modules"]:
        print(f"  {m['name']}: {len(m['exports'])} exports")

    if not result.get("dry_run"):
        print()
        print("Next steps:")
        print(f"  cd {output_dir}")
        print("  git init && git add . && git commit -m 'feat: initial package'")
        print(f"  gh repo create {args.name} --public --source . --push")
        print("  # Configure PyPI trusted publisher")
        print("  gh release create v0.1.0 --title 'v0.1.0' --notes 'Initial release'")


if __name__ == "__main__":
    main()
