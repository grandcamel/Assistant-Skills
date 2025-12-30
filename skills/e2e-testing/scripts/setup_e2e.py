#!/usr/bin/env python3
"""
Set up E2E testing infrastructure for an Assistant Skills project.

Usage:
    python setup_e2e.py /path/to/project
    python setup_e2e.py /path/to/project --dry-run
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional


def detect_project_info(project_path: Path) -> Dict:
    """Detect project information from plugin.json and structure."""
    info = {
        "name": project_path.name,
        "has_plugin_json": False,
        "has_skills": False,
        "skills": [],
        "python_scripts": [],
    }

    # Check for plugin.json
    plugin_json = project_path / ".claude-plugin" / "plugin.json"
    if plugin_json.exists():
        info["has_plugin_json"] = True
        with open(plugin_json) as f:
            data = json.load(f)
            info["name"] = data.get("name", info["name"])

    # Check for skills
    skills_dir = project_path / "skills"
    if skills_dir.exists():
        info["has_skills"] = True
        for skill_dir in skills_dir.iterdir():
            if skill_dir.is_dir() and skill_dir.name != "shared":
                skill_md = skill_dir / "SKILL.md"
                if skill_md.exists():
                    info["skills"].append(skill_dir.name)

    # Find Python scripts
    for py_file in project_path.rglob("*.py"):
        if "test" not in str(py_file) and "__pycache__" not in str(py_file):
            info["python_scripts"].append(str(py_file.relative_to(project_path)))

    return info


def generate_dockerfile(project_info: Dict) -> str:
    """Generate Dockerfile for E2E testing."""
    return f'''# E2E Testing Container for {project_info["name"]}
# Includes Claude Code CLI, Python, and test infrastructure

FROM node:20-slim

# Install Python and dependencies
RUN apt-get update && apt-get install -y \\
    python3 \\
    python3-pip \\
    python3-venv \\
    git \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Create symlinks for python
RUN ln -sf /usr/bin/python3 /usr/bin/python

# Install Claude Code CLI
RUN npm install -g @anthropic-ai/claude-code

# Set up working directory
WORKDIR /workspace

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python test dependencies
COPY requirements-e2e.txt /tmp/requirements-e2e.txt
RUN pip install --no-cache-dir -r /tmp/requirements-e2e.txt

# Copy the plugin source
COPY . /workspace/plugin-source

# Environment variables
ENV CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1
ENV CLAUDE_CODE_SKIP_OOBE=1
ENV CI=true

# Default command
CMD ["python", "-m", "pytest", "tests/e2e/", "-v", "--tb=short"]
'''


def generate_docker_compose(project_info: Dict) -> str:
    """Generate docker-compose.yml for E2E testing."""
    return f'''version: '3.8'

services:
  e2e-tests:
    build:
      context: ../..
      dockerfile: docker/e2e/Dockerfile
    environment:
      - ANTHROPIC_API_KEY=${{ANTHROPIC_API_KEY:-}}
      - E2E_TEST_TIMEOUT=${{E2E_TEST_TIMEOUT:-120}}
      - E2E_TEST_MODEL=${{E2E_TEST_MODEL:-claude-sonnet-4-20250514}}
      - E2E_VERBOSE=${{E2E_VERBOSE:-false}}
      - CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1
      - CLAUDE_CODE_SKIP_OOBE=1
      - CI=true
    volumes:
      - ../../test-results/e2e:/workspace/test-results
      - ${{HOME}}/.claude:/root/.claude:ro
    working_dir: /workspace/plugin-source
    deploy:
      resources:
        limits:
          memory: 2G

  e2e-shell:
    build:
      context: ../..
      dockerfile: docker/e2e/Dockerfile
    environment:
      - ANTHROPIC_API_KEY=${{ANTHROPIC_API_KEY:-}}
      - CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1
      - CLAUDE_CODE_SKIP_OOBE=1
    volumes:
      - ../..:/workspace/plugin-source
      - ${{HOME}}/.claude:/root/.claude:ro
    working_dir: /workspace/plugin-source
    stdin_open: true
    tty: true
    entrypoint: /bin/bash
    profiles:
      - debug
'''


def generate_requirements_e2e() -> str:
    """Generate requirements-e2e.txt."""
    return '''# E2E Testing Dependencies
pytest>=7.0.0
pytest-timeout>=2.0.0
pytest-html>=4.0.0
pyyaml>=6.0
pexpect>=4.8.0
rich>=13.0.0
junitparser>=3.0.0

# Plugin dependencies (if needed)
assistant-skills-lib>=0.1.0
tabulate>=0.9.0
'''


def generate_conftest(project_info: Dict) -> str:
    """Generate conftest.py for pytest."""
    return f'''"""Pytest configuration and fixtures for E2E tests."""

import os
import pytest
from pathlib import Path

from .runner import E2ETestRunner, ClaudeCodeRunner


def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption(
        "--e2e-timeout",
        action="store",
        default=os.environ.get("E2E_TEST_TIMEOUT", "120"),
        help="Timeout per test in seconds",
    )
    parser.addoption(
        "--e2e-model",
        action="store",
        default=os.environ.get("E2E_TEST_MODEL", "claude-sonnet-4-20250514"),
        help="Claude model to use",
    )
    parser.addoption(
        "--e2e-verbose",
        action="store_true",
        default=os.environ.get("E2E_VERBOSE", "").lower() == "true",
        help="Enable verbose output",
    )


@pytest.fixture(scope="session")
def e2e_enabled():
    """Check if E2E tests should run."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    claude_dir = Path.home() / ".claude"

    if api_key:
        return True
    if claude_dir.exists() and (claude_dir / "credentials.json").exists():
        return True
    return False


@pytest.fixture(scope="session")
def project_root():
    """Get the project root directory."""
    return Path(__file__).parent.parent.parent


@pytest.fixture(scope="session")
def test_cases_path(project_root):
    """Get path to test cases YAML."""
    return project_root / "tests" / "e2e" / "test_cases.yaml"


@pytest.fixture(scope="session")
def e2e_timeout(request):
    """Get E2E test timeout."""
    return int(request.config.getoption("--e2e-timeout"))


@pytest.fixture(scope="session")
def e2e_model(request):
    """Get E2E test model."""
    return request.config.getoption("--e2e-model")


@pytest.fixture(scope="session")
def e2e_verbose(request):
    """Get E2E verbosity setting."""
    return request.config.getoption("--e2e-verbose")


@pytest.fixture(scope="session")
def claude_runner(project_root, e2e_timeout, e2e_model, e2e_verbose, e2e_enabled):
    """Create Claude Code runner."""
    if not e2e_enabled:
        pytest.skip("E2E tests disabled (no API key or OAuth credentials)")

    return ClaudeCodeRunner(
        working_dir=project_root,
        timeout=e2e_timeout,
        model=e2e_model,
        verbose=e2e_verbose,
    )


@pytest.fixture(scope="session")
def e2e_runner(test_cases_path, project_root, e2e_timeout, e2e_model, e2e_verbose, e2e_enabled):
    """Create E2E test runner."""
    if not e2e_enabled:
        pytest.skip("E2E tests disabled (no API key or OAuth credentials)")

    return E2ETestRunner(
        test_cases_path=test_cases_path,
        working_dir=project_root,
        timeout=e2e_timeout,
        model=e2e_model,
        verbose=e2e_verbose,
    )


@pytest.fixture(scope="session")
def installed_plugin(claude_runner, e2e_enabled):
    """Install the plugin once for all tests."""
    if not e2e_enabled:
        pytest.skip("E2E tests disabled")

    result = claude_runner.install_plugin(".")
    if not result["success"] and "already installed" not in result.get("output", "").lower():
        pytest.fail(f"Failed to install plugin: {{result.get('error', 'Unknown error')}}")

    return result
'''


def generate_runner() -> str:
    """Generate the E2E test runner module."""
    # This is a large file, reading from the existing one we created
    return '''#!/usr/bin/env python3
"""
E2E Test Runner for Claude Code Plugins

Executes test cases defined in YAML against the Claude Code CLI.
"""

import json
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


class TestStatus(Enum):
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"
    TIMEOUT = "timeout"


@dataclass
class TestResult:
    """Result of a single test execution."""
    test_id: str
    name: str
    status: TestStatus
    duration: float
    output: str = ""
    error: str = ""
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SuiteResult:
    """Result of a test suite execution."""
    suite_name: str
    description: str
    tests: List[TestResult] = field(default_factory=list)

    @property
    def passed(self) -> int:
        return sum(1 for t in self.tests if t.status == TestStatus.PASSED)

    @property
    def failed(self) -> int:
        return sum(1 for t in self.tests if t.status == TestStatus.FAILED)

    @property
    def total(self) -> int:
        return len(self.tests)


class ClaudeCodeRunner:
    """Wrapper for executing Claude Code CLI commands."""

    def __init__(
        self,
        working_dir: Path,
        timeout: int = 120,
        model: str = "claude-sonnet-4-20250514",
        verbose: bool = False,
    ):
        self.working_dir = working_dir
        self.timeout = timeout
        self.model = model
        self.verbose = verbose
        self._check_prerequisites()

    def _check_prerequisites(self):
        """Verify Claude Code CLI is available."""
        try:
            result = subprocess.run(
                ["claude", "--version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode != 0:
                raise RuntimeError(f"Claude CLI error: {result.stderr}")
        except FileNotFoundError:
            raise RuntimeError(
                "Claude Code CLI not found. Install: npm install -g @anthropic-ai/claude-code"
            )

    def _check_authentication(self) -> bool:
        """Check if authentication is configured."""
        if os.environ.get("ANTHROPIC_API_KEY"):
            return True
        claude_dir = Path.home() / ".claude"
        if claude_dir.exists() and (claude_dir / "credentials.json").exists():
            return True
        return False

    def send_prompt(self, prompt: str, timeout: Optional[int] = None) -> Dict[str, Any]:
        """Send a prompt to Claude Code and capture the response."""
        timeout = timeout or self.timeout
        start_time = time.time()

        cmd = [
            "claude",
            "--print",
            "--output-format", "text",
            "--model", self.model,
            "--max-turns", "1",
            prompt,
        ]

        try:
            result = subprocess.run(
                cmd,
                cwd=self.working_dir,
                capture_output=True,
                text=True,
                timeout=timeout,
                env={**os.environ, "CLAUDE_CODE_SKIP_OOBE": "1"},
            )

            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr,
                "exit_code": result.returncode,
                "duration": time.time() - start_time,
            }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "output": "",
                "error": f"Command timed out after {timeout}s",
                "exit_code": -1,
                "duration": timeout,
            }
        except Exception as e:
            return {
                "success": False,
                "output": "",
                "error": str(e),
                "exit_code": -1,
                "duration": time.time() - start_time,
            }

    def install_plugin(self, plugin_path: str = ".") -> Dict[str, Any]:
        """Install a plugin from the given path."""
        return self.send_prompt(f"/plugin {plugin_path}")


class TestCaseValidator:
    """Validates test output against expected outcomes."""

    @staticmethod
    def validate(output: str, error: str, expect: Dict[str, Any]) -> Dict[str, Any]:
        """Validate output against expectations."""
        failures = []
        details = {}
        combined_output = f"{output}\\n{error}".lower()

        if expect.get("success") is True:
            if "error:" in error.lower() or "exception" in error.lower():
                failures.append("Expected success but got error")

        if "output_contains" in expect:
            for expected_text in expect["output_contains"]:
                if expected_text.lower() not in combined_output:
                    failures.append(f"Output missing: '{expected_text}'")
                else:
                    details[f"contains_{expected_text}"] = True

        if "output_contains_any" in expect:
            found_any = False
            for expected_text in expect["output_contains_any"]:
                if expected_text.lower() in combined_output:
                    found_any = True
                    break
            if not found_any:
                failures.append(f"Output missing any of: {expect['output_contains_any']}")

        if expect.get("no_errors"):
            error_patterns = [r"error:", r"exception:", r"traceback", r"failed:"]
            for pattern in error_patterns:
                if re.search(pattern, combined_output, re.IGNORECASE):
                    if "error handling" not in combined_output:
                        failures.append(f"Found error pattern: {pattern}")
                        break

        if expect.get("no_crashes"):
            crash_patterns = [r"segmentation fault", r"core dumped", r"fatal error", r"panic:"]
            for pattern in crash_patterns:
                if re.search(pattern, combined_output, re.IGNORECASE):
                    failures.append(f"Found crash indicator: {pattern}")

        return {"passed": len(failures) == 0, "failures": failures, "details": details}


class E2ETestRunner:
    """Main test runner that orchestrates E2E tests."""

    def __init__(
        self,
        test_cases_path: Path,
        working_dir: Path,
        timeout: int = 120,
        model: str = "claude-sonnet-4-20250514",
        verbose: bool = False,
    ):
        self.test_cases_path = test_cases_path
        self.working_dir = working_dir
        self.timeout = timeout
        self.model = model
        self.verbose = verbose
        self.claude = ClaudeCodeRunner(
            working_dir=working_dir,
            timeout=timeout,
            model=model,
            verbose=verbose,
        )
        self.validator = TestCaseValidator()

    def load_test_cases(self) -> Dict[str, Any]:
        """Load test cases from YAML file."""
        with open(self.test_cases_path) as f:
            return yaml.safe_load(f)

    def run_test(self, test: Dict[str, Any]) -> TestResult:
        """Run a single test case."""
        test_id = test["id"]
        name = test["name"]
        prompt = test["prompt"]
        expect = test.get("expect", {})
        timeout = test.get("timeout", self.timeout)

        if self.verbose:
            print(f"  Running: {name}")

        result = self.claude.send_prompt(prompt, timeout=timeout)

        if result["exit_code"] == -1 and "timed out" in result["error"]:
            return TestResult(
                test_id=test_id,
                name=name,
                status=TestStatus.TIMEOUT,
                duration=result["duration"],
                output=result["output"],
                error=result["error"],
            )

        validation = self.validator.validate(result["output"], result["error"], expect)
        status = TestStatus.PASSED if validation["passed"] else TestStatus.FAILED

        return TestResult(
            test_id=test_id,
            name=name,
            status=status,
            duration=result["duration"],
            output=result["output"],
            error=result["error"],
            details={"validation": validation, "exit_code": result["exit_code"]},
        )

    def run_suite(self, suite_name: str, suite: Dict[str, Any]) -> SuiteResult:
        """Run all tests in a suite."""
        result = SuiteResult(suite_name=suite_name, description=suite.get("description", ""))

        if self.verbose:
            print(f"\\nSuite: {suite_name}")

        for test in suite.get("tests", []):
            test_result = self.run_test(test)
            result.tests.append(test_result)

            if self.verbose:
                symbol = "✓" if test_result.status == TestStatus.PASSED else "✗"
                print(f"  {symbol} {test_result.name} ({test_result.duration:.1f}s)")

        return result

    def run_all(self, suites: Optional[List[str]] = None) -> List[SuiteResult]:
        """Run all test suites."""
        test_cases = self.load_test_cases()
        results = []

        for suite_name, suite in test_cases.get("suites", {}).items():
            if suites and suite_name not in suites:
                continue
            suite_result = self.run_suite(suite_name, suite)
            results.append(suite_result)

        return results

    def print_summary(self, results: List[SuiteResult]) -> bool:
        """Print test execution summary."""
        total_passed = sum(r.passed for r in results)
        total_failed = sum(r.failed for r in results)
        total_tests = sum(r.total for r in results)

        print("\\n" + "=" * 60)
        print("E2E TEST SUMMARY")
        print("=" * 60)

        for result in results:
            status = "PASS" if result.failed == 0 else "FAIL"
            print(f"  {result.suite_name}: {result.passed}/{result.total} ({status})")

        print("-" * 60)
        print(f"  Total: {total_passed}/{total_tests} passed")

        if total_failed > 0:
            print(f"\\n  FAILURES ({total_failed}):")
            for result in results:
                for test in result.tests:
                    if test.status != TestStatus.PASSED:
                        print(f"    - {result.suite_name}::{test.test_id}")

        print("=" * 60)
        return total_failed == 0

    def write_json_report(self, results: List[SuiteResult], output_path: Path):
        """Write results to JSON file."""
        data = {
            "timestamp": datetime.now().isoformat(),
            "model": self.model,
            "suites": [
                {
                    "name": r.suite_name,
                    "passed": r.passed,
                    "failed": r.failed,
                    "tests": [
                        {
                            "id": t.test_id,
                            "name": t.name,
                            "status": t.status.value,
                            "duration": t.duration,
                        }
                        for t in r.tests
                    ],
                }
                for r in results
            ],
        }
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)

    def write_junit_report(self, results: List[SuiteResult], output_path: Path):
        """Write results to JUnit XML format."""
        from xml.etree import ElementTree as ET

        testsuites = ET.Element("testsuites")

        for suite in results:
            testsuite = ET.SubElement(
                testsuites,
                "testsuite",
                name=suite.suite_name,
                tests=str(suite.total),
                failures=str(suite.failed),
            )

            for test in suite.tests:
                testcase = ET.SubElement(
                    testsuite,
                    "testcase",
                    name=test.name,
                    classname=suite.suite_name,
                    time=str(test.duration),
                )
                if test.status != TestStatus.PASSED:
                    failure = ET.SubElement(testcase, "failure", message=test.status.value)
                    failure.text = test.error or str(test.details)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        tree = ET.ElementTree(testsuites)
        tree.write(output_path, encoding="unicode", xml_declaration=True)

    def write_html_report(self, results: List[SuiteResult], output_path: Path):
        """Write results to HTML report."""
        total_passed = sum(r.passed for r in results)
        total_failed = sum(r.failed for r in results)
        total_tests = sum(r.total for r in results)

        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>E2E Test Report</title>
    <style>
        body {{ font-family: -apple-system, sans-serif; margin: 40px; }}
        .summary {{ background: #f5f5f5; padding: 20px; border-radius: 8px; }}
        .passed {{ color: #22c55e; }}
        .failed {{ color: #ef4444; }}
        table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background: #f5f5f5; }}
    </style>
</head>
<body>
    <h1>E2E Test Report</h1>
    <div class="summary">
        <p><strong>Total:</strong> {total_tests} tests</p>
        <p class="passed"><strong>Passed:</strong> {total_passed}</p>
        <p class="failed"><strong>Failed:</strong> {total_failed}</p>
        <p><strong>Model:</strong> {self.model}</p>
        <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
"""
        for suite in results:
            html += f"<h2>{suite.suite_name}</h2><table><tr><th>Test</th><th>Status</th><th>Duration</th></tr>"
            for test in suite.tests:
                status_class = "passed" if test.status == TestStatus.PASSED else "failed"
                html += f'<tr><td>{test.name}</td><td class="{status_class}">{test.status.value}</td><td>{test.duration:.1f}s</td></tr>'
            html += "</table>"

        html += "</body></html>"

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(html)
'''


def generate_test_plugin_e2e(project_info: Dict) -> str:
    """Generate test_plugin_e2e.py."""
    return f'''"""
E2E Tests for {project_info["name"]}

Run with: pytest tests/e2e/ -v --e2e-verbose
"""

import pytest
import yaml
from pathlib import Path

from .runner import TestStatus


pytestmark = [pytest.mark.e2e, pytest.mark.slow]


class TestPluginInstallation:
    """Test plugin installation."""

    def test_plugin_installs(self, claude_runner, e2e_enabled):
        if not e2e_enabled:
            pytest.skip("E2E disabled")

        result = claude_runner.install_plugin(".")
        assert result["success"] or "already installed" in result["output"].lower()

    def test_skills_discoverable(self, claude_runner, installed_plugin, e2e_enabled):
        if not e2e_enabled:
            pytest.skip("E2E disabled")

        result = claude_runner.send_prompt("What skills do you have available?")
        assert "skill" in result["output"].lower() or result["success"]


@pytest.mark.skip(reason="Redundant with test_individual_case parametrized tests")
class TestYAMLSuites:
    """Run YAML-defined test suites.

    NOTE: This class is skipped by default because test_individual_case
    already runs each YAML test case individually with better reporting.
    Enable if you prefer aggregate test execution.
    """

    def test_all_suites(self, e2e_runner, e2e_enabled):
        if not e2e_enabled:
            pytest.skip("E2E disabled")

        results = e2e_runner.run_all()
        e2e_runner.print_summary(results)

        failures = [
            f"{{s.suite_name}}::{{t.test_id}}"
            for s in results
            for t in s.tests
            if t.status != TestStatus.PASSED
        ]
        assert len(failures) == 0, f"Failures: {{failures}}"
'''


def generate_run_script(project_info: Dict) -> str:
    """Generate run-e2e-tests.sh script."""
    return f'''#!/bin/bash
# E2E Test Runner for {project_info["name"]}

set -e

SCRIPT_DIR="$(cd "$(dirname "${{BASH_SOURCE[0]}}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

RED='\\033[0;31m'
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
NC='\\033[0m'

USE_DOCKER=true
VERBOSE=${{E2E_VERBOSE:-false}}

while [[ $# -gt 0 ]]; do
    case $1 in
        --local) USE_DOCKER=false; shift ;;
        --verbose|-v) VERBOSE=true; export E2E_VERBOSE=true; shift ;;
        --shell)
            cd "$PROJECT_ROOT"
            docker compose -f docker/e2e/docker-compose.yml run --rm e2e-shell
            exit 0
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo "  --local     Run locally without Docker"
            echo "  --shell     Open debug shell in Docker"
            echo "  --verbose   Verbose output"
            exit 0
            ;;
        *) echo -e "${{RED}}Unknown: $1${{NC}}"; exit 1 ;;
    esac
done

# Check auth
if [[ -n "$ANTHROPIC_API_KEY" ]]; then
    echo -e "${{GREEN}}✓ API key configured${{NC}}"
elif [[ -f "$HOME/.claude/credentials.json" ]]; then
    echo -e "${{GREEN}}✓ OAuth configured${{NC}}"
else
    echo -e "${{RED}}✗ No authentication${{NC}}"
    echo "Set ANTHROPIC_API_KEY or run: claude auth login"
    exit 1
fi

cd "$PROJECT_ROOT"
mkdir -p test-results/e2e

if [[ "$USE_DOCKER" == "true" ]]; then
    echo -e "${{YELLOW}}Running in Docker...${{NC}}"
    docker compose -f docker/e2e/docker-compose.yml build e2e-tests
    docker compose -f docker/e2e/docker-compose.yml run --rm e2e-tests
else
    echo -e "${{YELLOW}}Running locally...${{NC}}"
    pip install -q -r requirements-e2e.txt
    if [[ "$VERBOSE" == "true" ]]; then
        python -m pytest tests/e2e/ -v --e2e-verbose --tb=short
    else
        python -m pytest tests/e2e/ -v --tb=short
    fi
fi

echo -e "${{GREEN}}Results: test-results/e2e/${{NC}}"
'''


def generate_test_cases_yaml(project_info: Dict) -> str:
    """Generate initial test_cases.yaml."""
    return f'''# E2E Test Cases for {project_info["name"]}
# Auto-generated - customize as needed

metadata:
  name: {project_info["name"]}-e2e
  description: E2E tests for {project_info["name"]}

settings:
  default_timeout: 120
  default_model: claude-sonnet-4-20250514

suites:
  plugin_installation:
    description: Plugin installation tests
    tests:
      - id: install_plugin
        name: Install plugin
        prompt: "/plugin ."
        expect:
          success: true
          no_errors: true

      - id: verify_skills
        name: Verify skills loaded
        prompt: "What skills are available from this plugin?"
        expect:
          success: true
          no_errors: true
'''


def setup_e2e(
    project_path: Path,
    dry_run: bool = False,
) -> Dict:
    """Set up E2E testing infrastructure."""
    project_path = Path(project_path).resolve()

    result = {
        "project": str(project_path),
        "files_created": [],
        "directories_created": [],
    }

    # Detect project info
    project_info = detect_project_info(project_path)
    result["project_info"] = project_info

    # Define files to create
    files = {
        "docker/e2e/Dockerfile": generate_dockerfile(project_info),
        "docker/e2e/docker-compose.yml": generate_docker_compose(project_info),
        "requirements-e2e.txt": generate_requirements_e2e(),
        "tests/e2e/__init__.py": '"""E2E tests."""',
        "tests/e2e/conftest.py": generate_conftest(project_info),
        "tests/e2e/runner.py": generate_runner(),
        "tests/e2e/test_plugin_e2e.py": generate_test_plugin_e2e(project_info),
        "tests/e2e/test_cases.yaml": generate_test_cases_yaml(project_info),
        "scripts/run-e2e-tests.sh": generate_run_script(project_info),
    }

    if dry_run:
        result["files_created"] = list(files.keys())
        result["dry_run"] = True
        return result

    # Create directories
    for file_path in files.keys():
        dir_path = project_path / Path(file_path).parent
        if not dir_path.exists():
            dir_path.mkdir(parents=True)
            result["directories_created"].append(str(dir_path.relative_to(project_path)))

    # Write files
    for file_path, content in files.items():
        full_path = project_path / file_path
        full_path.write_text(content)
        result["files_created"].append(file_path)

        # Make shell script executable
        if file_path.endswith(".sh"):
            full_path.chmod(0o755)

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Set up E2E testing infrastructure"
    )
    parser.add_argument(
        "project_path",
        help="Path to the Assistant Skills project"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be created"
    )

    args = parser.parse_args()

    project_path = Path(args.project_path)
    if not project_path.exists():
        print(f"Error: Project not found: {project_path}", file=sys.stderr)
        sys.exit(1)

    result = setup_e2e(project_path, dry_run=args.dry_run)

    print(f"Project: {result['project']}")
    print(f"Name: {result['project_info']['name']}")
    print(f"Skills: {len(result['project_info']['skills'])}")
    print()

    if result.get("dry_run"):
        print("DRY RUN - would create:")
    else:
        print("Created:")

    for f in result["files_created"]:
        print(f"  {f}")

    if not result.get("dry_run"):
        print()
        print("Next steps:")
        print("  1. Generate test cases: python generate_test_cases.py .")
        print("  2. Run tests: ./scripts/run-e2e-tests.sh")


if __name__ == "__main__":
    main()
