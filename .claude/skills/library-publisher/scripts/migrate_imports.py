#!/usr/bin/env python3
"""
Migrate imports in an Assistant Skills project to use a PyPI package.

Usage:
    python migrate_imports.py --project /path/to/project --package mypackage_lib
    python migrate_imports.py --project /path/to/project --package mypackage_lib --dry-run
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple


# Standard library modules to recognize (not to migrate)
STDLIB_MODULES = {
    "os", "sys", "re", "json", "datetime", "time", "pathlib", "typing",
    "collections", "functools", "itertools", "operator", "contextlib",
    "abc", "dataclasses", "enum", "copy", "hashlib", "base64", "uuid",
    "urllib", "http", "email", "logging", "argparse", "textwrap",
    "shutil", "tempfile", "glob", "fnmatch", "io", "pickle", "csv",
    "configparser", "ast", "inspect", "traceback", "warnings", "unittest",
}

# Common shared library module names
LIBRARY_MODULES = {
    "formatters", "validators", "cache", "error_handler",
    "template_engine", "project_detector",
}


def find_library_modules(project_path: Path) -> Set[str]:
    """Find actual library modules in the project."""
    modules = set()

    lib_paths = [
        project_path / "skills" / "shared" / "scripts" / "lib",
        project_path / ".claude" / "skills" / "shared" / "scripts" / "lib",
    ]

    for lib_path in lib_paths:
        if lib_path.exists():
            for py_file in lib_path.glob("*.py"):
                if py_file.name != "__init__.py":
                    modules.add(py_file.stem)

    return modules if modules else LIBRARY_MODULES


def migrate_file_imports(
    file_path: Path,
    package_name: str,
    library_modules: Set[str],
) -> Tuple[str, List[Dict]]:
    """Migrate imports in a single file."""
    content = file_path.read_text()
    changes = []

    # Pattern 1: from module import x, y, z
    def replace_from_import(match):
        module = match.group(1)
        imports = match.group(2)
        if module in library_modules:
            changes.append({
                "type": "from_import",
                "old": match.group(0),
                "new": f"from {package_name} import {imports}",
                "module": module,
            })
            return f"from {package_name} import {imports}"
        return match.group(0)

    from_pattern = r"from\s+(" + "|".join(re.escape(m) for m in library_modules) + r")\s+import\s+(.+)"
    content = re.sub(from_pattern, replace_from_import, content)

    # Pattern 2: import module
    def replace_import(match):
        module = match.group(1)
        if module in library_modules:
            changes.append({
                "type": "import",
                "old": match.group(0),
                "new": f"from {package_name} import {module}",
                "module": module,
            })
            return f"from {package_name} import {module}"
        return match.group(0)

    import_pattern = r"^import\s+(" + "|".join(re.escape(m) for m in library_modules) + r")\s*$"
    content = re.sub(import_pattern, replace_import, content, flags=re.MULTILINE)

    # Pattern 3: sys.path manipulation for lib imports
    # Remove lines like: sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts' / 'lib'))
    syspath_pattern = r"^.*sys\.path\.insert.*(?:lib|shared).*$\n?"
    syspath_matches = re.findall(syspath_pattern, content, re.MULTILINE)
    for match in syspath_matches:
        changes.append({
            "type": "syspath_removal",
            "old": match.strip(),
            "new": "(removed)",
        })
    content = re.sub(syspath_pattern, "", content, flags=re.MULTILINE)

    return content, changes


def find_python_files(project_path: Path) -> List[Path]:
    """Find all Python files to migrate."""
    files = []

    for py_file in project_path.rglob("*.py"):
        # Skip library itself
        if "shared/scripts/lib" in str(py_file):
            continue
        # Skip virtual environments
        if any(d in str(py_file) for d in ["venv", ".venv", "env", "__pycache__"]):
            continue
        # Skip test cache
        if ".pytest_cache" in str(py_file):
            continue

        files.append(py_file)

    return files


def create_requirements_txt(
    project_path: Path,
    package_name: str,
    package_version: str = "0.1.0",
) -> str:
    """Generate requirements.txt content."""
    # Check for existing requirements
    existing_deps = []
    req_file = project_path / "requirements.txt"
    if req_file.exists():
        for line in req_file.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                # Don't include the old package if it's there
                if package_name.replace("_", "-") not in line:
                    existing_deps.append(line)

    # Build new requirements
    deps = [
        f"{package_name.replace('_', '-')}>={package_version}",
        "pytest>=7.0.0",
        "pytest-cov>=4.0.0",
    ]

    # Add existing deps that aren't duplicates
    for dep in existing_deps:
        dep_name = dep.split(">=")[0].split("==")[0].split("<")[0].strip()
        if not any(dep_name in d for d in deps):
            deps.append(dep)

    return "\n".join(sorted(set(deps))) + "\n"


def update_docker_files(project_path: Path) -> List[Dict]:
    """Update Docker files to remove PYTHONPATH."""
    changes = []

    docker_files = [
        project_path / "docker" / "Dockerfile",
        project_path / "Dockerfile",
        project_path / "docker" / "docker-compose.yml",
        project_path / "docker-compose.yml",
    ]

    for docker_file in docker_files:
        if not docker_file.exists():
            continue

        content = docker_file.read_text()
        original = content

        # Remove PYTHONPATH env vars
        pythonpath_pattern = r'^\s*PYTHONPATH[=:].*$\n?'
        content = re.sub(pythonpath_pattern, "", content, flags=re.MULTILINE)

        # Remove PYTHONPATH from ENV statements
        env_pythonpath = r'\s*PYTHONPATH="[^"]*"\s*\\?\n?'
        content = re.sub(env_pythonpath, "", content)

        if content != original:
            changes.append({
                "file": str(docker_file),
                "type": "docker_pythonpath_removal",
            })
            docker_file.write_text(content)

    return changes


def remove_vendored_library(project_path: Path, dry_run: bool = False) -> List[str]:
    """Remove vendored library files."""
    removed = []

    lib_paths = [
        project_path / "skills" / "shared" / "scripts" / "lib",
        project_path / ".claude" / "skills" / "shared" / "scripts" / "lib",
    ]

    for lib_path in lib_paths:
        if not lib_path.exists():
            continue

        for py_file in lib_path.glob("*.py"):
            if not dry_run:
                py_file.unlink()
            removed.append(str(py_file.relative_to(project_path)))

        # Leave README explaining migration
        readme_path = lib_path / "README.md"
        if not dry_run:
            readme_path.write_text(f"""# Shared Library

The shared library modules have been migrated to a PyPI package.

## Installation

```bash
pip install {project_path.name.lower().replace('-', '_')}_lib
```

## Usage

```python
from {project_path.name.lower().replace('-', '_')}_lib import format_table, validate_url
```
""")

    return removed


def migrate_project(
    project_path: Path,
    package_name: str,
    dry_run: bool = False,
    remove_library: bool = True,
) -> Dict:
    """Migrate an entire project to use a PyPI package."""
    project_path = Path(project_path).resolve()

    result = {
        "project": str(project_path),
        "package": package_name,
        "files_modified": [],
        "imports_changed": 0,
        "library_files_removed": [],
        "requirements_created": False,
        "docker_updated": False,
    }

    # Find library modules
    library_modules = find_library_modules(project_path)
    result["library_modules"] = sorted(library_modules)

    # Find and migrate Python files
    py_files = find_python_files(project_path)

    for py_file in py_files:
        new_content, changes = migrate_file_imports(py_file, package_name, library_modules)

        if changes:
            result["files_modified"].append({
                "file": str(py_file.relative_to(project_path)),
                "changes": len(changes),
            })
            result["imports_changed"] += len(changes)

            if not dry_run:
                py_file.write_text(new_content)

    # Create requirements.txt
    req_content = create_requirements_txt(project_path, package_name)
    req_path = project_path / "requirements.txt"
    if not dry_run:
        req_path.write_text(req_content)
    result["requirements_created"] = True

    # Update Docker files
    if not dry_run:
        docker_changes = update_docker_files(project_path)
        result["docker_updated"] = len(docker_changes) > 0

    # Remove vendored library
    if remove_library:
        removed = remove_vendored_library(project_path, dry_run)
        result["library_files_removed"] = removed

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Migrate project imports to use PyPI package"
    )
    parser.add_argument(
        "--project", "-p",
        required=True,
        help="Path to the project to migrate"
    )
    parser.add_argument(
        "--package", "-k",
        required=True,
        help="Package import name (e.g., jira_assistant_skills_lib)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without making changes"
    )
    parser.add_argument(
        "--keep-library",
        action="store_true",
        help="Don't remove vendored library files"
    )

    args = parser.parse_args()

    project_path = Path(args.project)
    if not project_path.exists():
        print(f"Error: Project path does not exist: {project_path}", file=sys.stderr)
        sys.exit(1)

    result = migrate_project(
        project_path=project_path,
        package_name=args.package,
        dry_run=args.dry_run,
        remove_library=not args.keep_library,
    )

    print(f"Project: {result['project']}")
    print(f"Package: {result['package']}")
    print()

    if args.dry_run:
        print("DRY RUN - No changes made")
        print()

    print(f"Library modules detected: {', '.join(result['library_modules'])}")
    print()

    print(f"Files modified: {len(result['files_modified'])}")
    for f in result["files_modified"]:
        print(f"  {f['file']} ({f['changes']} changes)")
    print()

    print(f"Total import changes: {result['imports_changed']}")
    print(f"Requirements.txt: {'created' if result['requirements_created'] else 'unchanged'}")
    print(f"Docker files: {'updated' if result['docker_updated'] else 'unchanged'}")
    print()

    if result["library_files_removed"]:
        print(f"Library files removed: {len(result['library_files_removed'])}")
        for f in result["library_files_removed"]:
            print(f"  {f}")

    if not args.dry_run:
        print()
        print("Next steps:")
        print(f"  pip install -r requirements.txt")
        print(f"  pytest skills/*/tests/ -v")


if __name__ == "__main__":
    main()
