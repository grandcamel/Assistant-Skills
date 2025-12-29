#!/usr/bin/env python3
"""
Analyze an Assistant Skills project to extract metadata for README generation.

This script examines a Claude Code skills project and extracts:
- Product name and branding
- Skill count and names
- Script count across all skills
- Test count (estimated from test files)
- Key features from SKILL.md files
"""

import argparse
import json
import os
import re
from pathlib import Path
from typing import Any


def find_skills_directory(project_path: Path) -> Path | None:
    """Find the .claude/skills directory in a project."""
    skills_path = project_path / ".claude" / "skills"
    if skills_path.exists():
        return skills_path
    return None


def extract_product_name(project_path: Path) -> str:
    """Extract the product name from the project."""
    # Try to get from directory name
    dir_name = project_path.name.lower()

    # Pattern: xxx-assistant-skills
    match = re.match(r"(.+?)-assistant-skills", dir_name)
    if match:
        return match.group(1).capitalize()

    # Try README.md title
    readme_path = project_path / "README.md"
    if readme_path.exists():
        content = readme_path.read_text()
        # Look for "# Xxx Assistant Skills"
        match = re.search(r"#\s*(\w+)\s+Assistant\s+Skills", content, re.IGNORECASE)
        if match:
            return match.group(1).capitalize()

    # Default to directory name
    return dir_name.replace("-", " ").title()


def count_skills(skills_path: Path) -> tuple[int, list[str]]:
    """Count skills and return their names."""
    skills = []
    for item in skills_path.iterdir():
        if item.is_dir() and not item.name.startswith(".") and item.name != "shared":
            # Check if it has a SKILL.md file
            if (item / "SKILL.md").exists() or (item / "scripts").exists():
                skills.append(item.name)
    return len(skills), sorted(skills)


def count_scripts(skills_path: Path) -> int:
    """Count Python scripts across all skills."""
    count = 0
    for skill_dir in skills_path.iterdir():
        if skill_dir.is_dir():
            scripts_dir = skill_dir / "scripts"
            if scripts_dir.exists():
                count += len(list(scripts_dir.glob("*.py")))
    return count


def count_tests(skills_path: Path) -> int:
    """Estimate test count from test files."""
    test_count = 0
    for test_file in skills_path.rglob("test_*.py"):
        # Rough estimate: count test functions
        content = test_file.read_text()
        test_count += len(re.findall(r"def test_", content))
    return test_count


def extract_skill_info(skill_path: Path) -> dict[str, Any]:
    """Extract information from a skill's SKILL.md."""
    skill_md = skill_path / "SKILL.md"
    info = {
        "name": skill_path.name,
        "purpose": "",
        "features": [],
        "example_commands": [],
    }

    if skill_md.exists():
        content = skill_md.read_text()

        # Extract purpose from first paragraph or "What this skill does"
        purpose_match = re.search(
            r"(?:What this skill does|Purpose)[:\n]+(.+?)(?:\n\n|\n#)",
            content,
            re.IGNORECASE | re.DOTALL,
        )
        if purpose_match:
            info["purpose"] = purpose_match.group(1).strip()[:200]

        # Extract example commands
        code_blocks = re.findall(r'```(?:bash)?\n(.+?)```', content, re.DOTALL)
        for block in code_blocks[:3]:  # Take first 3 examples
            lines = block.strip().split("\n")
            for line in lines:
                if line.startswith("python") or line.startswith('"'):
                    info["example_commands"].append(line.strip())

    return info


def detect_query_language(project_path: Path, product_name: str) -> str:
    """Detect the query language used by the product."""
    product_lower = product_name.lower()

    query_languages = {
        "jira": "JQL",
        "confluence": "CQL",
        "splunk": "SPL",
        "elasticsearch": "Query DSL",
        "datadog": "Query Language",
        "grafana": "PromQL",
        "prometheus": "PromQL",
    }

    return query_languages.get(product_lower, "Query Language")


def get_color_palette(product_name: str) -> dict[str, str]:
    """Get suggested color palette for the product."""
    palettes = {
        "jira": {
            "primary": "#0052CC",
            "accent": "#4a00e0",
            "cursor": "#00C7E6",
            "badge": "FF6B6B",
        },
        "confluence": {
            "primary": "#0052CC",
            "accent": "#36B37E",
            "cursor": "#00C7E6",
            "badge": "36B37E",
        },
        "splunk": {
            "primary": "#FF6900",
            "accent": "#65A637",
            "cursor": "#00C7E6",
            "badge": "FF6900",
        },
        "default": {
            "primary": "#6366F1",
            "accent": "#8B5CF6",
            "cursor": "#00C7E6",
            "badge": "6366F1",
        },
    }

    return palettes.get(product_name.lower(), palettes["default"])


def analyze_project(project_path: str | Path) -> dict[str, Any]:
    """Analyze a project and return metadata."""
    project_path = Path(project_path).resolve()

    if not project_path.exists():
        raise ValueError(f"Project path does not exist: {project_path}")

    skills_path = find_skills_directory(project_path)
    if not skills_path:
        raise ValueError(f"No .claude/skills directory found in: {project_path}")

    product_name = extract_product_name(project_path)
    skill_count, skill_names = count_skills(skills_path)
    script_count = count_scripts(skills_path)
    test_count = count_tests(skills_path)
    query_language = detect_query_language(project_path, product_name)
    colors = get_color_palette(product_name)

    # Extract info from each skill
    skills_info = []
    for skill_name in skill_names:
        skill_path = skills_path / skill_name
        skills_info.append(extract_skill_info(skill_path))

    return {
        "project_path": str(project_path),
        "product_name": product_name,
        "skill_count": skill_count,
        "skill_names": skill_names,
        "script_count": script_count,
        "test_count": test_count,
        "query_language": query_language,
        "colors": colors,
        "skills": skills_info,
        "github_org": "grandcamel",  # Default, can be overridden
        "github_repo": project_path.name.lower(),
    }


def main():
    parser = argparse.ArgumentParser(
        description="Analyze an Assistant Skills project for README generation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Analyze current project
    python analyze_project.py .

    # Analyze specific project
    python analyze_project.py ../Confluence-Assistant-Skills

    # Output as JSON
    python analyze_project.py . --format json
        """,
    )
    parser.add_argument(
        "project_path",
        type=str,
        nargs="?",
        default=".",
        help="Path to the project to analyze (default: current directory)",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )

    args = parser.parse_args()

    try:
        result = analyze_project(args.project_path)

        if args.format == "json":
            print(json.dumps(result, indent=2))
        else:
            print(f"Product: {result['product_name']} Assistant Skills")
            print(f"Skills: {result['skill_count']}")
            print(f"Scripts: {result['script_count']}+")
            print(f"Tests: {result['test_count']}+")
            print(f"Query Language: {result['query_language']}")
            print(f"\nSkills: {', '.join(result['skill_names'])}")
            print(f"\nColors:")
            for key, value in result["colors"].items():
                print(f"  {key}: {value}")

    except Exception as e:
        print(f"Error: {e}")
        exit(1)


if __name__ == "__main__":
    main()
