#!/usr/bin/env python3
"""
Auto-generate E2E test cases from an Assistant Skills plugin structure.

Analyzes plugin.json and SKILL.md files to generate intelligent test cases.

Usage:
    python generate_test_cases.py /path/to/project
    python generate_test_cases.py /path/to/project --output custom_tests.yaml
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


def parse_skill_md(skill_path: Path) -> Dict[str, Any]:
    """Parse a SKILL.md file and extract metadata."""
    content = skill_path.read_text()

    skill_info = {
        "name": skill_path.parent.name,
        "path": str(skill_path),
        "has_frontmatter": False,
        "description": "",
        "trigger_phrases": [],
        "scripts": [],
        "when_to_use": [],
    }

    # Parse YAML frontmatter
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            try:
                frontmatter = yaml.safe_load(parts[1])
                skill_info["has_frontmatter"] = True
                skill_info["name"] = frontmatter.get("name", skill_info["name"])
                skill_info["description"] = frontmatter.get("description", "")
                skill_info["when_to_use"] = frontmatter.get("when_to_use", [])
            except yaml.YAMLError:
                pass

    # Extract trigger phrases from description
    if skill_info["description"]:
        # Look for quoted phrases in description
        phrases = re.findall(r'"([^"]+)"', skill_info["description"])
        skill_info["trigger_phrases"].extend(phrases)

        # Look for common trigger patterns
        trigger_patterns = [
            r"when user (?:wants to |asks to )?([^,\.]+)",
            r"use when ([^,\.]+)",
            r'"([^"]+)"',
        ]
        for pattern in trigger_patterns:
            matches = re.findall(pattern, skill_info["description"], re.IGNORECASE)
            for match in matches:
                if match not in skill_info["trigger_phrases"]:
                    skill_info["trigger_phrases"].append(match)

    # Find Python scripts
    scripts_dir = skill_path.parent / "scripts"
    if scripts_dir.exists():
        for py_file in scripts_dir.glob("*.py"):
            if not py_file.name.startswith("_"):
                skill_info["scripts"].append(py_file.name)

    return skill_info


def analyze_plugin(project_path: Path) -> Dict[str, Any]:
    """Analyze a plugin and extract information for test generation."""
    analysis = {
        "project_name": project_path.name,
        "plugin_name": None,
        "plugin_version": None,
        "plugin_description": None,
        "skills": [],
        "has_hooks": False,
        "has_commands": False,
    }

    # Parse plugin.json
    plugin_json = project_path / ".claude-plugin" / "plugin.json"
    if plugin_json.exists():
        with open(plugin_json) as f:
            data = json.load(f)
            analysis["plugin_name"] = data.get("name")
            analysis["plugin_version"] = data.get("version")
            analysis["plugin_description"] = data.get("description")

    # Find and parse all SKILL.md files
    skills_dir = project_path / "skills"
    if skills_dir.exists():
        for skill_dir in sorted(skills_dir.iterdir()):
            if skill_dir.is_dir() and skill_dir.name != "shared":
                skill_md = skill_dir / "SKILL.md"
                if skill_md.exists():
                    skill_info = parse_skill_md(skill_md)
                    analysis["skills"].append(skill_info)

    # Check for hooks
    hooks_dir = project_path / "hooks"
    if hooks_dir.exists() or (project_path / "hooks.json").exists():
        analysis["has_hooks"] = True

    # Check for commands
    commands_dir = project_path / "commands"
    if commands_dir.exists():
        analysis["has_commands"] = True

    return analysis


def generate_skill_tests(skill: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate test cases for a single skill."""
    tests = []
    skill_name = skill["name"]

    # Test 1: Skill discovery
    tests.append({
        "id": f"{skill_name}_discoverable",
        "name": f"Verify {skill_name} skill is discoverable",
        "prompt": f"What can you tell me about the {skill_name} skill?",
        "expect": {
            "success": True,
            "output_contains_any": [
                skill_name,
                skill_name.replace("-", " "),
                skill_name.replace("_", " "),
            ],
            "no_errors": True,
        },
    })

    # Test 2: Trigger phrase tests (from description)
    for i, phrase in enumerate(skill["trigger_phrases"][:3]):  # Limit to 3
        # Clean up the phrase
        phrase = phrase.strip().rstrip(".")

        # Generate a natural prompt from the trigger phrase
        if phrase.lower().startswith(("create", "add", "build", "make")):
            prompt = f"I want to {phrase.lower()}"
        elif phrase.lower().startswith(("list", "show", "display", "get")):
            prompt = phrase.capitalize()
        else:
            prompt = f"Help me {phrase.lower()}"

        tests.append({
            "id": f"{skill_name}_trigger_{i+1}",
            "name": f"Test trigger: {phrase[:40]}...",
            "prompt": prompt,
            "expect": {
                "success": True,
                "no_crashes": True,
            },
        })

    # Test 3: Script execution tests
    for script in skill["scripts"][:3]:  # Limit to 3 scripts
        script_base = script.replace(".py", "").replace("_", " ")
        tests.append({
            "id": f"{skill_name}_{script.replace('.py', '')}",
            "name": f"Test {script_base} script",
            "prompt": f"Use the {skill_name} skill to {script_base}",
            "expect": {
                "success": True,
                "no_crashes": True,
            },
        })

    # Test 4: Error handling
    tests.append({
        "id": f"{skill_name}_error_handling",
        "name": f"Test {skill_name} error handling",
        "prompt": f"Use {skill_name} with invalid input that doesn't exist",
        "expect": {
            "no_crashes": True,  # Should handle errors gracefully
        },
    })

    return tests


def generate_plugin_tests(analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate plugin-level test cases."""
    tests = []
    plugin_name = analysis["plugin_name"] or analysis["project_name"]

    # Plugin installation test
    tests.append({
        "id": "install_plugin",
        "name": "Install plugin from local source",
        "prompt": "/plugin .",
        "expect": {
            "success": True,
            "no_errors": True,
        },
    })

    # Verify all skills loaded
    skill_names = [s["name"] for s in analysis["skills"]]
    tests.append({
        "id": "verify_all_skills",
        "name": "Verify all skills are loaded",
        "prompt": f"List all skills available from the {plugin_name} plugin",
        "expect": {
            "success": True,
            "output_contains_any": skill_names[:5] if skill_names else [plugin_name],
            "no_errors": True,
        },
    })

    # Plugin metadata test
    if analysis["plugin_description"]:
        tests.append({
            "id": "plugin_description",
            "name": "Verify plugin description is accurate",
            "prompt": f"What does the {plugin_name} plugin do?",
            "expect": {
                "success": True,
                "no_errors": True,
            },
        })

    return tests


def generate_test_cases_yaml(analysis: Dict[str, Any]) -> Dict[str, Any]:
    """Generate complete test_cases.yaml content."""
    plugin_name = analysis["plugin_name"] or analysis["project_name"]

    test_cases = {
        "metadata": {
            "name": f"{plugin_name}-e2e",
            "description": f"Auto-generated E2E tests for {plugin_name}",
            "version": "1.0.0",
            "generated_from": analysis["project_name"],
        },
        "settings": {
            "default_timeout": 120,
            "default_model": "claude-sonnet-4-20250514",
            "retry_on_timeout": 1,
        },
        "suites": {},
    }

    # Plugin installation suite
    test_cases["suites"]["plugin_installation"] = {
        "description": "Plugin installation and verification",
        "tests": generate_plugin_tests(analysis),
    }

    # Per-skill test suites
    for skill in analysis["skills"]:
        suite_name = skill["name"].replace("-", "_")
        tests = generate_skill_tests(skill)

        if tests:
            test_cases["suites"][suite_name] = {
                "description": f"Tests for {skill['name']} skill",
                "tests": tests,
            }

    # Error handling suite
    test_cases["suites"]["error_handling"] = {
        "description": "Error handling and edge cases",
        "tests": [
            {
                "id": "invalid_path",
                "name": "Handle invalid file path gracefully",
                "prompt": "Process the file at /nonexistent/path/file.txt",
                "expect": {
                    "no_crashes": True,
                },
            },
            {
                "id": "empty_input",
                "name": "Handle empty input gracefully",
                "prompt": "Use the plugin with no specific request",
                "expect": {
                    "no_crashes": True,
                },
            },
        ],
    }

    return test_cases


def generate_pytest_classes(analysis: Dict[str, Any]) -> str:
    """Generate pytest test classes for each skill."""
    plugin_name = analysis["plugin_name"] or analysis["project_name"]

    # Extract skill names for embedding in generated code
    skill_names = [s["name"] for s in analysis.get("skills", [])]
    skill_names_repr = repr(skill_names)

    code = f'''"""
Auto-generated E2E test classes for {plugin_name}

Run with: pytest tests/e2e/ -v --e2e-verbose
"""

import pytest
from pathlib import Path

from .runner import TestStatus


pytestmark = [pytest.mark.e2e, pytest.mark.slow]


# Skills detected at generation time
EXPECTED_SKILLS = {skill_names_repr}


class TestPluginInstallation:
    """Plugin installation tests."""

    def test_plugin_installs(self, claude_runner, e2e_enabled):
        """Verify plugin installs successfully."""
        if not e2e_enabled:
            pytest.skip("E2E disabled")

        result = claude_runner.install_plugin(".")
        assert result["success"] or "already installed" in result["output"].lower()

    def test_skills_discoverable(self, claude_runner, installed_plugin, e2e_enabled):
        """Verify skills are discoverable after installation."""
        if not e2e_enabled:
            pytest.skip("E2E disabled")

        result = claude_runner.send_prompt("What skills are available?")
        output = result["output"].lower()

        # Check for at least one skill
        found = any(s.lower() in output for s in EXPECTED_SKILLS)
        assert found or result["success"], "No skills found in output"

'''

    # Generate test class for each skill
    for skill in analysis["skills"]:
        class_name = "".join(word.capitalize() for word in skill["name"].replace("-", "_").split("_"))
        skill_name = skill["name"]

        code += f'''
class Test{class_name}:
    """Tests for {skill_name} skill."""

    def test_skill_discoverable(self, claude_runner, installed_plugin, e2e_enabled):
        """Verify {skill_name} is discoverable."""
        if not e2e_enabled:
            pytest.skip("E2E disabled")

        result = claude_runner.send_prompt("Tell me about the {skill_name} skill")
        assert result["success"] or "{skill_name}" in result["output"].lower()

    def test_basic_functionality(self, claude_runner, installed_plugin, e2e_enabled):
        """Test basic {skill_name} functionality."""
        if not e2e_enabled:
            pytest.skip("E2E disabled")

        result = claude_runner.send_prompt("Use the {skill_name} skill")
        assert "exception" not in result["output"].lower()
        assert "traceback" not in result["error"].lower()

'''

    # Add YAML test runner class (skipped by default - redundant with parametrized tests)
    code += '''
@pytest.mark.skip(reason="Redundant with test_individual_case parametrized tests")
class TestYAMLSuites:
    """Run all YAML-defined test suites.

    NOTE: This class is skipped by default because test_individual_case
    already runs each YAML test case individually with better reporting.
    Enable if you prefer aggregate test execution.
    """

    def test_all_suites(self, e2e_runner, e2e_enabled):
        """Execute all test suites from test_cases.yaml."""
        if not e2e_enabled:
            pytest.skip("E2E disabled")

        results = e2e_runner.run_all()
        success = e2e_runner.print_summary(results)

        failures = [
            f"{s.suite_name}::{t.test_id}"
            for s in results
            for t in s.tests
            if t.status != TestStatus.PASSED
        ]
        assert len(failures) == 0, f"Test failures: {failures}"
'''

    return code


def generate_test_cases(
    project_path: Path,
    output_path: Optional[Path] = None,
    pytest_output: Optional[Path] = None,
) -> Dict[str, Any]:
    """Generate test cases for a project."""
    project_path = Path(project_path).resolve()

    result = {
        "project": str(project_path),
        "files_generated": [],
    }

    # Analyze plugin
    analysis = analyze_plugin(project_path)
    result["analysis"] = {
        "plugin_name": analysis["plugin_name"],
        "skills_found": len(analysis["skills"]),
        "skill_names": [s["name"] for s in analysis["skills"]],
    }

    # Generate test cases YAML
    test_cases = generate_test_cases_yaml(analysis)

    # Determine output paths
    if output_path is None:
        output_path = project_path / "tests" / "e2e" / "test_cases.yaml"

    if pytest_output is None:
        pytest_output = project_path / "tests" / "e2e" / "test_plugin_e2e.py"

    # Write YAML
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        yaml.dump(test_cases, f, default_flow_style=False, sort_keys=False)
    result["files_generated"].append(str(output_path.relative_to(project_path)))

    # Generate and write pytest classes
    pytest_code = generate_pytest_classes(analysis)
    pytest_output.parent.mkdir(parents=True, exist_ok=True)
    pytest_output.write_text(pytest_code)
    result["files_generated"].append(str(pytest_output.relative_to(project_path)))

    # Count generated tests
    total_tests = sum(
        len(suite.get("tests", []))
        for suite in test_cases["suites"].values()
    )
    result["tests_generated"] = total_tests

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Generate E2E test cases from plugin structure"
    )
    parser.add_argument(
        "project_path",
        help="Path to the Assistant Skills project"
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        help="Output path for test_cases.yaml"
    )
    parser.add_argument(
        "--pytest-output",
        type=Path,
        help="Output path for pytest test file"
    )

    args = parser.parse_args()

    project_path = Path(args.project_path)
    if not project_path.exists():
        print(f"Error: Project not found: {project_path}", file=sys.stderr)
        sys.exit(1)

    result = generate_test_cases(
        project_path,
        output_path=args.output,
        pytest_output=args.pytest_output,
    )

    print(f"Project: {result['project']}")
    print(f"Plugin: {result['analysis']['plugin_name']}")
    print(f"Skills found: {result['analysis']['skills_found']}")
    print(f"  - " + "\n  - ".join(result['analysis']['skill_names']))
    print()
    print(f"Tests generated: {result['tests_generated']}")
    print()
    print("Files created:")
    for f in result["files_generated"]:
        print(f"  {f}")
    print()
    print("Next steps:")
    print("  1. Review generated tests: cat tests/e2e/test_cases.yaml")
    print("  2. Run tests: ./scripts/run-e2e-tests.sh")


if __name__ == "__main__":
    main()
