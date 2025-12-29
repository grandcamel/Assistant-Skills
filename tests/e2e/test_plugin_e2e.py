"""
E2E Tests for Assistant-Skills Plugin

These tests interact with the actual Claude Code CLI and require:
- ANTHROPIC_API_KEY environment variable, OR
- Claude Code OAuth credentials (~/.claude/credentials.json)

Run with:
    pytest tests/e2e/ -v --e2e-verbose

Note: These tests make real API calls and will incur costs.
"""

import pytest
import yaml
from pathlib import Path

from .runner import TestStatus


# Mark all tests in this module as E2E
pytestmark = [
    pytest.mark.e2e,
    pytest.mark.slow,
]


class TestPluginInstallation:
    """Test plugin installation and basic functionality."""

    def test_plugin_installs_successfully(self, claude_runner, project_root, e2e_enabled):
        """Verify plugin can be installed from local source."""
        if not e2e_enabled:
            pytest.skip("E2E tests disabled")

        result = claude_runner.install_plugin(".")

        assert result["success"] or "already installed" in result["output"].lower(), \
            f"Plugin installation failed: {result['error']}"

    def test_skills_are_discoverable(self, claude_runner, installed_plugin, e2e_enabled):
        """Verify all skills are discoverable after installation."""
        if not e2e_enabled:
            pytest.skip("E2E tests disabled")

        result = claude_runner.send_prompt(
            "List the skills available from the assistant-skills plugin"
        )

        output = result["output"].lower()

        # Check that key skills are mentioned
        expected_skills = ["assistant-builder", "skills-optimizer", "landing-page", "library-publisher"]
        found_skills = [s for s in expected_skills if s in output]

        # At least some skills should be found (Claude may phrase differently)
        assert len(found_skills) >= 2 or "skill" in output, \
            f"Skills not properly discoverable. Output: {result['output'][:500]}"


class TestAssistantBuilder:
    """Test the assistant-builder skill."""

    def test_validate_project(self, claude_runner, installed_plugin, e2e_enabled):
        """Test project validation on this repository."""
        if not e2e_enabled:
            pytest.skip("E2E tests disabled")

        result = claude_runner.send_prompt(
            "Validate this Assistant Skills project structure"
        )

        # Should not have fatal errors
        assert "exception" not in result["output"].lower(), \
            f"Validation caused exception: {result['output']}"
        assert "traceback" not in result["error"].lower(), \
            f"Validation caused traceback: {result['error']}"

    def test_list_templates(self, claude_runner, installed_plugin, e2e_enabled):
        """Test listing available templates."""
        if not e2e_enabled:
            pytest.skip("E2E tests disabled")

        result = claude_runner.send_prompt(
            "What templates are available for creating new Assistant Skills projects?"
        )

        # Should mention templates in some form
        assert result["success"] or "template" in result["output"].lower(), \
            f"Template listing failed: {result['output']}"


class TestSkillsOptimizer:
    """Test the skills-optimizer skill."""

    def test_analyze_skill(self, claude_runner, installed_plugin, e2e_enabled):
        """Test skill analysis for token efficiency."""
        if not e2e_enabled:
            pytest.skip("E2E tests disabled")

        result = claude_runner.send_prompt(
            "Analyze the assistant-builder skill for token efficiency"
        )

        # Should complete without crashing
        assert "exception" not in result["output"].lower()
        assert "traceback" not in result["error"].lower()


class TestLibraryPublisher:
    """Test the library-publisher skill."""

    def test_analyze_library(self, claude_runner, installed_plugin, e2e_enabled):
        """Test shared library analysis."""
        if not e2e_enabled:
            pytest.skip("E2E tests disabled")

        result = claude_runner.send_prompt(
            "Analyze the shared library structure in this project"
        )

        # Should complete without errors
        assert "exception" not in result["output"].lower()


class TestYAMLTestCases:
    """Run all test cases defined in test_cases.yaml."""

    def test_yaml_suites(self, e2e_runner, e2e_enabled):
        """Run all YAML-defined test suites."""
        if not e2e_enabled:
            pytest.skip("E2E tests disabled")

        results = e2e_runner.run_all()

        # Print summary
        e2e_runner.print_summary(results)

        # Collect failures
        failures = []
        for suite in results:
            for test in suite.tests:
                if test.status != TestStatus.PASSED:
                    failures.append(f"{suite.suite_name}::{test.test_id}: {test.status.value}")
                    if test.details.get("validation", {}).get("failures"):
                        for f in test.details["validation"]["failures"]:
                            failures.append(f"  - {f}")

        assert len(failures) == 0, f"Test failures:\n" + "\n".join(failures)


# Parameterized tests from YAML
def load_test_cases():
    """Load test cases from YAML for parametrization."""
    test_cases_path = Path(__file__).parent / "test_cases.yaml"
    if not test_cases_path.exists():
        return []

    with open(test_cases_path) as f:
        data = yaml.safe_load(f)

    tests = []
    for suite_name, suite in data.get("suites", {}).items():
        for test in suite.get("tests", []):
            tests.append((suite_name, test["id"], test["name"], test))

    return tests


@pytest.mark.parametrize(
    "suite_name,test_id,test_name,test_case",
    load_test_cases(),
    ids=lambda x: x if isinstance(x, str) else x.get("id", "unknown"),
)
def test_individual_case(
    suite_name,
    test_id,
    test_name,
    test_case,
    e2e_runner,
    e2e_enabled,
):
    """Run individual test case from YAML."""
    if not e2e_enabled:
        pytest.skip("E2E tests disabled")

    result = e2e_runner.run_test(test_case)

    assert result.status == TestStatus.PASSED, \
        f"Test {test_id} failed: {result.details.get('validation', {}).get('failures', [])}"
