#!/usr/bin/env python3
"""
Analyze shared library structure and usage in an Assistant Skills project.

Usage:
    python analyze_library.py /path/to/project
    python analyze_library.py /path/to/project --output json
"""

import argparse
import ast
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Any, Optional


def find_library_dir(project_path: Path) -> Optional[Path]:
    """Find the shared library directory in a project."""
    candidates = [
        project_path / "skills" / "shared" / "scripts" / "lib",
        project_path / ".claude" / "skills" / "shared" / "scripts" / "lib",
    ]

    for candidate in candidates:
        if candidate.exists() and candidate.is_dir():
            return candidate

    return None


def analyze_module(module_path: Path) -> Dict[str, Any]:
    """Analyze a Python module for exports and dependencies."""
    result = {
        "name": module_path.stem,
        "path": str(module_path),
        "size_bytes": module_path.stat().st_size,
        "lines": 0,
        "functions": [],
        "classes": [],
        "imports": [],
        "exports": [],
    }

    try:
        content = module_path.read_text()
        result["lines"] = len(content.splitlines())

        tree = ast.parse(content)

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if not node.name.startswith("_"):
                    result["functions"].append(node.name)
            elif isinstance(node, ast.ClassDef):
                if not node.name.startswith("_"):
                    result["classes"].append(node.name)
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    result["imports"].append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    result["imports"].append(node.module)

        # Find __all__ if defined
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "__all__":
                        if isinstance(node.value, ast.List):
                            for elt in node.value.elts:
                                if isinstance(elt, ast.Constant):
                                    result["exports"].append(elt.value)

        # If no __all__, exports are public functions and classes
        if not result["exports"]:
            result["exports"] = result["functions"] + result["classes"]

    except Exception as e:
        result["error"] = str(e)

    return result


def find_imports_in_file(file_path: Path, module_names: Set[str]) -> List[Dict[str, Any]]:
    """Find imports of library modules in a Python file."""
    imports = []

    try:
        content = file_path.read_text()

        # Pattern for: from module import ...
        from_pattern = r"from\s+(" + "|".join(re.escape(m) for m in module_names) + r")\s+import\s+(.+)"
        for match in re.finditer(from_pattern, content):
            imports.append({
                "file": str(file_path),
                "type": "from",
                "module": match.group(1),
                "imports": match.group(2).strip(),
            })

        # Pattern for: import module
        import_pattern = r"^import\s+(" + "|".join(re.escape(m) for m in module_names) + r")\b"
        for match in re.finditer(import_pattern, content, re.MULTILINE):
            imports.append({
                "file": str(file_path),
                "type": "import",
                "module": match.group(1),
            })

    except Exception:
        pass

    return imports


def scan_project_imports(project_path: Path, module_names: Set[str]) -> List[Dict[str, Any]]:
    """Scan entire project for imports of library modules."""
    all_imports = []

    # Find all Python files
    for py_file in project_path.rglob("*.py"):
        # Skip the library itself
        if "shared/scripts/lib" in str(py_file):
            continue
        # Skip virtual environments
        if "venv" in str(py_file) or ".venv" in str(py_file):
            continue
        # Skip __pycache__
        if "__pycache__" in str(py_file):
            continue

        imports = find_imports_in_file(py_file, module_names)
        all_imports.extend(imports)

    return all_imports


def detect_dependencies(modules: List[Dict[str, Any]]) -> Set[str]:
    """Detect external dependencies from module imports."""
    stdlib_modules = {
        "os", "sys", "re", "json", "datetime", "time", "pathlib", "typing",
        "collections", "functools", "itertools", "operator", "contextlib",
        "abc", "dataclasses", "enum", "copy", "hashlib", "base64", "uuid",
        "urllib", "http", "email", "logging", "argparse", "textwrap",
        "shutil", "tempfile", "glob", "fnmatch", "io", "pickle", "csv",
        "configparser", "ast", "inspect", "traceback", "warnings",
    }

    internal_modules = {m["name"] for m in modules}

    external_deps = set()
    for module in modules:
        for imp in module.get("imports", []):
            base_module = imp.split(".")[0]
            if base_module not in stdlib_modules and base_module not in internal_modules:
                external_deps.add(base_module)

    return external_deps


def suggest_package_name(project_path: Path) -> str:
    """Suggest a package name based on project name."""
    project_name = project_path.name.lower()

    # Extract topic from common patterns
    patterns = [
        r"^(.+)-assistant-skills$",
        r"^(.+)-skills$",
        r"^(.+)_assistant_skills$",
    ]

    for pattern in patterns:
        match = re.match(pattern, project_name)
        if match:
            topic = match.group(1).replace("-", "_").replace(" ", "_")
            return f"{topic}-assistant-skills-lib"

    return f"{project_name.replace('-', '_')}-lib"


def analyze_library(project_path: Path) -> Dict[str, Any]:
    """Analyze the shared library in a project."""
    project_path = Path(project_path).resolve()

    result = {
        "project_name": project_path.name,
        "project_path": str(project_path),
        "library_found": False,
        "library_path": None,
        "suggested_package_name": suggest_package_name(project_path),
        "suggested_import_name": suggest_package_name(project_path).replace("-", "_"),
        "modules": [],
        "total_lines": 0,
        "total_exports": 0,
        "external_dependencies": [],
        "usage": {
            "files_using_library": 0,
            "total_imports": 0,
            "imports": [],
        },
    }

    # Find library directory
    lib_dir = find_library_dir(project_path)
    if not lib_dir:
        result["error"] = "Shared library directory not found"
        return result

    result["library_found"] = True
    result["library_path"] = str(lib_dir)

    # Analyze each module
    module_names = set()
    for py_file in lib_dir.glob("*.py"):
        if py_file.name == "__init__.py":
            continue

        module_info = analyze_module(py_file)
        result["modules"].append(module_info)
        result["total_lines"] += module_info["lines"]
        result["total_exports"] += len(module_info["exports"])
        module_names.add(module_info["name"])

    # Detect dependencies
    result["external_dependencies"] = sorted(detect_dependencies(result["modules"]))

    # Scan for usage
    imports = scan_project_imports(project_path, module_names)
    result["usage"]["imports"] = imports
    result["usage"]["total_imports"] = len(imports)
    result["usage"]["files_using_library"] = len(set(i["file"] for i in imports))

    return result


def format_report(analysis: Dict[str, Any]) -> str:
    """Format analysis as human-readable report."""
    lines = []

    lines.append("=" * 60)
    lines.append(f"Library Analysis: {analysis['project_name']}")
    lines.append("=" * 60)
    lines.append("")

    if not analysis["library_found"]:
        lines.append(f"ERROR: {analysis.get('error', 'Library not found')}")
        return "\n".join(lines)

    lines.append(f"Library Path: {analysis['library_path']}")
    lines.append(f"Suggested Package: {analysis['suggested_package_name']}")
    lines.append(f"Suggested Import: {analysis['suggested_import_name']}")
    lines.append("")

    lines.append("MODULES")
    lines.append("-" * 40)
    for module in analysis["modules"]:
        exports = len(module["exports"])
        lines.append(f"  {module['name']}.py")
        lines.append(f"    Lines: {module['lines']}, Exports: {exports}")
        if module["classes"]:
            lines.append(f"    Classes: {', '.join(module['classes'])}")
        if module["functions"]:
            funcs = module["functions"][:5]
            more = f" (+{len(module['functions']) - 5} more)" if len(module["functions"]) > 5 else ""
            lines.append(f"    Functions: {', '.join(funcs)}{more}")
    lines.append("")

    lines.append("SUMMARY")
    lines.append("-" * 40)
    lines.append(f"  Total Modules: {len(analysis['modules'])}")
    lines.append(f"  Total Lines: {analysis['total_lines']}")
    lines.append(f"  Total Exports: {analysis['total_exports']}")
    lines.append("")

    if analysis["external_dependencies"]:
        lines.append("EXTERNAL DEPENDENCIES")
        lines.append("-" * 40)
        for dep in analysis["external_dependencies"]:
            lines.append(f"  - {dep}")
        lines.append("")

    lines.append("PROJECT USAGE")
    lines.append("-" * 40)
    lines.append(f"  Files using library: {analysis['usage']['files_using_library']}")
    lines.append(f"  Total import statements: {analysis['usage']['total_imports']}")

    if analysis["usage"]["imports"]:
        lines.append("")
        lines.append("  Import locations:")
        # Group by file
        by_file = {}
        for imp in analysis["usage"]["imports"]:
            file_key = imp["file"].replace(analysis["project_path"], ".")
            if file_key not in by_file:
                by_file[file_key] = []
            by_file[file_key].append(imp["module"])

        for file_path, modules in sorted(by_file.items())[:10]:
            lines.append(f"    {file_path}")
            lines.append(f"      imports: {', '.join(sorted(set(modules)))}")

        if len(by_file) > 10:
            lines.append(f"    ... and {len(by_file) - 10} more files")

    lines.append("")
    lines.append("=" * 60)
    lines.append("NEXT STEPS")
    lines.append("=" * 60)
    lines.append(f"""
1. Create package repository:
   gh repo create {analysis['suggested_package_name']} --public

2. Scaffold package:
   python scaffold_package.py \\
     --name "{analysis['suggested_package_name']}" \\
     --source "{analysis['library_path']}" \\
     --output ~/{analysis['suggested_package_name']}

3. Configure PyPI trusted publisher at:
   https://pypi.org/manage/account/publishing/

4. Create release to publish:
   gh release create v0.1.0
""")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze shared library in an Assistant Skills project"
    )
    parser.add_argument(
        "project_path",
        help="Path to the Assistant Skills project"
    )
    parser.add_argument(
        "--output", "-o",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)"
    )

    args = parser.parse_args()

    project_path = Path(args.project_path)
    if not project_path.exists():
        print(f"Error: Project path does not exist: {project_path}", file=sys.stderr)
        sys.exit(1)

    analysis = analyze_library(project_path)

    if args.output == "json":
        print(json.dumps(analysis, indent=2))
    else:
        print(format_report(analysis))


if __name__ == "__main__":
    main()
