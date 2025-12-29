#!/usr/bin/env python3
"""
Update project documentation after migrating to PyPI package.

Usage:
    python update_docs.py /path/to/project --package-name "myproject-lib"
    python update_docs.py /path/to/project --package-name "myproject-lib" --dry-run
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional


def add_pypi_badge(content: str, package_name: str) -> str:
    """Add PyPI badge to README if not present."""
    if f"pypi.org/project/{package_name}" in content:
        return content  # Already has badge

    # Find badge section (usually after <p align="center"> with badges)
    badge_pattern = r'(<p align="center">.*?)(</p>)'

    def add_badge(match):
        badges = match.group(1)
        # Add PyPI badge after GitHub stars badge if present
        pypi_badge = f'  <a href="https://pypi.org/project/{package_name}/"><img src="https://img.shields.io/pypi/v/{package_name}?color=blue&logo=pypi&logoColor=white" alt="PyPI"></a>\n'

        if "github.com" in badges and "stars" in badges.lower():
            # Add after stars badge
            badges = re.sub(
                r'(.*shields\.io/github/stars.*?</a>)\n',
                r'\1\n' + pypi_badge,
                badges
            )
        else:
            # Add at end of badges
            badges = badges.rstrip() + "\n" + pypi_badge

        return badges + match.group(2)

    return re.sub(badge_pattern, add_badge, content, flags=re.DOTALL)


def update_shared_library_section(
    content: str,
    package_name: str,
    import_name: str,
) -> str:
    """Update Shared Library section in README."""
    # Pattern to find Shared Library section
    section_pattern = r'(## Shared Library\n)(.*?)(\n## |\n---|\Z)'

    def replace_section(match):
        header = match.group(1)
        next_section = match.group(3)

        new_content = f'''
Production-ready Python utilities available via PyPI:

```bash
pip install {package_name}
```

| Module | Purpose |
|--------|---------|
| `formatters` | Output formatting (tables, trees, colors, timestamps) |
| `validators` | Input validation (emails, URLs, dates, pagination) |
| `cache` | Response caching with TTL and LRU eviction |
| `error_handler` | Exception hierarchy and `@handle_errors` decorator |
| `template_engine` | Template loading and placeholder replacement |
| `project_detector` | Find existing Assistant Skills projects |

```python
from {import_name} import (
    format_table, format_tree,
    validate_email, validate_url,
    Cache, handle_errors
)

@handle_errors
def fetch_data(resource_id):
    return api.get(f"/resources/{{resource_id}}")
```

[{package_name} on PyPI](https://pypi.org/project/{package_name}/)
'''
        return header + new_content + next_section

    if "## Shared Library" in content:
        return re.sub(section_pattern, replace_section, content, flags=re.DOTALL)

    return content


def update_test_commands(content: str) -> str:
    """Remove PYTHONPATH from test commands."""
    # Pattern: PYTHONPATH="..." pytest ...
    pythonpath_pattern = r'PYTHONPATH="[^"]*"\s+'
    content = re.sub(pythonpath_pattern, "", content)

    # Also handle PYTHONPATH=... (without quotes)
    pythonpath_pattern2 = r"PYTHONPATH=[^\s]+\s+"
    content = re.sub(pythonpath_pattern2, "", content)

    # Add pip install if pytest commands exist without it
    if "pytest" in content and "pip install" not in content:
        # Find pytest commands and add pip install before first one
        content = re.sub(
            r'(```bash\n)(pytest)',
            r'\1pip install -r requirements.txt\n\2',
            content,
            count=1
        )

    return content


def update_project_structure(content: str, package_name: str) -> str:
    """Update project structure section to remove vendored lib."""
    # Remove detailed shared lib files
    patterns = [
        r'│\s+└── shared/scripts/lib/.*\n(?:│\s+[├└]── \w+\.py\n)*',
        r'│\s+├── shared/scripts/lib/.*\n(?:│\s+[├└]── \w+\.py\n)*',
        r'└── shared/scripts/lib/.*\n(?:\s+[├└]── \w+\.py\n)*',
    ]

    for pattern in patterns:
        content = re.sub(pattern, "", content)

    # Add requirements.txt if not present
    if "requirements.txt" not in content and "Project Structure" in content:
        content = re.sub(
            r'(├── README\.md)',
            r'├── requirements.txt          # Python dependencies\n\1',
            content
        )

    return content


def update_claude_md(content: str, package_name: str, import_name: str) -> str:
    """Update CLAUDE.md documentation."""
    # Update test command
    content = re.sub(
        r'PYTHONPATH="[^"]*"\s+pytest',
        'pytest',
        content
    )

    # Update shared library reference
    if "skills/shared/scripts/lib" in content:
        content = content.replace(
            "All Python scripts import from `skills/shared/scripts/lib/`:",
            f"All Python scripts import from `{package_name}` (PyPI package):"
        )

    # Update example imports
    old_import_patterns = [
        r'from formatters import',
        r'from validators import',
        r'from cache import',
        r'from error_handler import',
    ]
    for pattern in old_import_patterns:
        content = re.sub(
            pattern,
            f'from {import_name} import',
            content
        )

    # Remove PYTHONPATH references
    content = re.sub(
        r'Scripts require `PYTHONPATH` to be set for imports to work\.',
        f'Scripts require `{package_name}` to be installed (`pip install {package_name}`).',
        content
    )

    return content


def update_readme(
    project_path: Path,
    package_name: str,
    import_name: str,
    dry_run: bool = False,
) -> Dict:
    """Update README.md with package information."""
    readme_path = project_path / "README.md"
    if not readme_path.exists():
        return {"updated": False, "error": "README.md not found"}

    content = readme_path.read_text()
    original = content

    # Apply updates
    content = add_pypi_badge(content, package_name)
    content = update_shared_library_section(content, package_name, import_name)
    content = update_test_commands(content)
    content = update_project_structure(content, package_name)

    changes = content != original

    if changes and not dry_run:
        readme_path.write_text(content)

    return {
        "file": "README.md",
        "updated": changes,
    }


def update_claude_md_file(
    project_path: Path,
    package_name: str,
    import_name: str,
    dry_run: bool = False,
) -> Dict:
    """Update CLAUDE.md with package information."""
    claude_path = project_path / "CLAUDE.md"
    if not claude_path.exists():
        return {"updated": False, "error": "CLAUDE.md not found"}

    content = claude_path.read_text()
    original = content

    content = update_claude_md(content, package_name, import_name)

    changes = content != original

    if changes and not dry_run:
        claude_path.write_text(content)

    return {
        "file": "CLAUDE.md",
        "updated": changes,
    }


def update_docs(
    project_path: Path,
    package_name: str,
    package_url: Optional[str] = None,
    dry_run: bool = False,
) -> Dict:
    """Update all documentation files."""
    project_path = Path(project_path).resolve()
    import_name = package_name.replace("-", "_")

    if not package_url:
        package_url = f"https://pypi.org/project/{package_name}/"

    result = {
        "project": str(project_path),
        "package_name": package_name,
        "import_name": import_name,
        "package_url": package_url,
        "files": [],
    }

    # Update README.md
    readme_result = update_readme(project_path, package_name, import_name, dry_run)
    result["files"].append(readme_result)

    # Update CLAUDE.md
    claude_result = update_claude_md_file(project_path, package_name, import_name, dry_run)
    result["files"].append(claude_result)

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Update project documentation after PyPI migration"
    )
    parser.add_argument(
        "project_path",
        help="Path to the project"
    )
    parser.add_argument(
        "--package-name", "-n",
        required=True,
        help="PyPI package name (e.g., jira-assistant-skills-lib)"
    )
    parser.add_argument(
        "--package-url", "-u",
        help="PyPI package URL (auto-generated if not provided)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without making changes"
    )

    args = parser.parse_args()

    project_path = Path(args.project_path)
    if not project_path.exists():
        print(f"Error: Project path does not exist: {project_path}", file=sys.stderr)
        sys.exit(1)

    result = update_docs(
        project_path=project_path,
        package_name=args.package_name,
        package_url=args.package_url,
        dry_run=args.dry_run,
    )

    print(f"Project: {result['project']}")
    print(f"Package: {result['package_name']}")
    print(f"Import:  {result['import_name']}")
    print(f"URL:     {result['package_url']}")
    print()

    if args.dry_run:
        print("DRY RUN - No changes made")
        print()

    print("Documentation updates:")
    for f in result["files"]:
        status = "updated" if f["updated"] else f.get("error", "no changes needed")
        print(f"  {f['file']}: {status}")

    if not args.dry_run and any(f["updated"] for f in result["files"]):
        print()
        print("Documentation updated successfully!")
        print()
        print("Next steps:")
        print("  git add README.md CLAUDE.md")
        print('  git commit -m "docs: update for PyPI package migration"')


if __name__ == "__main__":
    main()
