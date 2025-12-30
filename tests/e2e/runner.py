#!/usr/bin/env python3
"""
E2E Test Runner for Claude Code Plugins

Executes test cases defined in YAML against the Claude Code CLI,
capturing output and validating against expected outcomes.
"""

import json
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass, field
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
            if self.verbose:
                print(f"Claude CLI version: {result.stdout.strip()}")
        except FileNotFoundError:
            raise RuntimeError(
                "Claude Code CLI not found. Install with: npm install -g @anthropic-ai/claude-code"
            )

    def _check_authentication(self) -> bool:
        """Check if authentication is configured."""
        # Check for API key
        if os.environ.get("ANTHROPIC_API_KEY"):
            return True

        # Check for Claude config directory (OAuth)
        claude_dir = Path.home() / ".claude"
        if claude_dir.exists():
            # Look for credentials file
            creds_file = claude_dir / "credentials.json"
            if creds_file.exists():
                return True

        return False

    def send_prompt(self, prompt: str, timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        Send a prompt to Claude Code and capture the response.

        Returns dict with:
            - success: bool
            - output: str
            - error: str
            - exit_code: int
            - duration: float
        """
        timeout = timeout or self.timeout
        start_time = time.time()

        # Build command
        # Use 3 turns to allow Claude to explore and respond
        max_turns = os.environ.get("E2E_MAX_TURNS", "3")
        cmd = [
            "claude",
            "--print",  # Non-interactive mode, print response
            "--output-format", "text",  # Plain text output
            "--model", self.model,
            "--max-turns", max_turns,
            "--dangerously-skip-permissions",  # Skip prompts in sandboxed test environment
            prompt,
        ]

        if self.verbose:
            print(f"Executing: {' '.join(cmd[:5])}...")

        try:
            result = subprocess.run(
                cmd,
                cwd=self.working_dir,
                capture_output=True,
                text=True,
                timeout=timeout,
                env={**os.environ, "CLAUDE_CODE_SKIP_OOBE": "1"},
            )

            duration = time.time() - start_time

            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr,
                "exit_code": result.returncode,
                "duration": duration,
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
        """
        Validate output against expectations.

        Returns dict with:
            - passed: bool
            - failures: list of failure messages
            - details: validation details
        """
        failures = []
        details = {}
        combined_output = f"{output}\n{error}".lower()

        # Check success expectation
        if expect.get("success") is True:
            if not output or "error" in error.lower():
                # Only fail if there's a clear error indicator
                if "error:" in error.lower() or "exception" in error.lower():
                    failures.append("Expected success but got error")

        # Check output_contains
        if "output_contains" in expect:
            for expected_text in expect["output_contains"]:
                if expected_text.lower() not in combined_output:
                    failures.append(f"Output missing expected text: '{expected_text}'")
                else:
                    details[f"contains_{expected_text}"] = True

        # Check output_contains_any (at least one must match)
        if "output_contains_any" in expect:
            found_any = False
            for expected_text in expect["output_contains_any"]:
                if expected_text.lower() in combined_output:
                    found_any = True
                    details[f"contains_{expected_text}"] = True
                    break
            if not found_any:
                failures.append(
                    f"Output missing any of: {expect['output_contains_any']}"
                )

        # Check no_errors
        if expect.get("no_errors"):
            error_patterns = [
                r"error:",
                r"exception:",
                r"traceback",
                r"failed:",
            ]
            for pattern in error_patterns:
                if re.search(pattern, combined_output, re.IGNORECASE):
                    # Check if it's just mentioning "error" in context vs actual error
                    if "error" in pattern and "error handling" not in combined_output:
                        if re.search(r"error[:\s]", combined_output, re.IGNORECASE):
                            failures.append(f"Found error pattern: {pattern}")
                            break

        # Check no_crashes
        if expect.get("no_crashes"):
            crash_patterns = [
                r"segmentation fault",
                r"core dumped",
                r"fatal error",
                r"panic:",
            ]
            for pattern in crash_patterns:
                if re.search(pattern, combined_output, re.IGNORECASE):
                    failures.append(f"Found crash indicator: {pattern}")

        return {
            "passed": len(failures) == 0,
            "failures": failures,
            "details": details,
        }


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
            print(f"\n  Running: {name}")

        # Execute prompt
        result = self.claude.send_prompt(prompt, timeout=timeout)

        # Handle timeout
        if result["exit_code"] == -1 and "timed out" in result["error"]:
            return TestResult(
                test_id=test_id,
                name=name,
                status=TestStatus.TIMEOUT,
                duration=result["duration"],
                output=result["output"],
                error=result["error"],
            )

        # Validate output
        validation = self.validator.validate(
            result["output"],
            result["error"],
            expect,
        )

        status = TestStatus.PASSED if validation["passed"] else TestStatus.FAILED

        return TestResult(
            test_id=test_id,
            name=name,
            status=status,
            duration=result["duration"],
            output=result["output"],
            error=result["error"],
            details={
                "validation": validation,
                "exit_code": result["exit_code"],
            },
        )

    def run_suite(self, suite_name: str, suite: Dict[str, Any]) -> SuiteResult:
        """Run all tests in a suite."""
        result = SuiteResult(
            suite_name=suite_name,
            description=suite.get("description", ""),
        )

        if self.verbose:
            print(f"\nSuite: {suite_name}")
            print(f"  {suite.get('description', '')}")

        for test in suite.get("tests", []):
            test_result = self.run_test(test)
            result.tests.append(test_result)

            if self.verbose:
                status_symbol = "✓" if test_result.status == TestStatus.PASSED else "✗"
                print(f"    {status_symbol} {test_result.name} ({test_result.duration:.1f}s)")

        return result

    def run_all(
        self,
        suites: Optional[List[str]] = None,
        tests: Optional[List[str]] = None,
    ) -> List[SuiteResult]:
        """
        Run all test suites.

        Args:
            suites: Optional list of suite names to run (runs all if None)
            tests: Optional list of test IDs to run (runs all if None)
        """
        test_cases = self.load_test_cases()
        results = []

        for suite_name, suite in test_cases.get("suites", {}).items():
            # Filter by suite name if specified
            if suites and suite_name not in suites:
                continue

            # Filter tests if specified
            if tests:
                suite = dict(suite)
                suite["tests"] = [
                    t for t in suite.get("tests", [])
                    if t["id"] in tests
                ]
                if not suite["tests"]:
                    continue

            suite_result = self.run_suite(suite_name, suite)
            results.append(suite_result)

        return results

    def print_summary(self, results: List[SuiteResult]):
        """Print test execution summary."""
        total_passed = sum(r.passed for r in results)
        total_failed = sum(r.failed for r in results)
        total_tests = sum(r.total for r in results)

        print("\n" + "=" * 60)
        print("E2E TEST SUMMARY")
        print("=" * 60)

        for result in results:
            status = "PASS" if result.failed == 0 else "FAIL"
            print(f"  {result.suite_name}: {result.passed}/{result.total} ({status})")

        print("-" * 60)
        print(f"  Total: {total_passed}/{total_tests} passed")

        if total_failed > 0:
            print(f"\n  FAILURES ({total_failed}):")
            for result in results:
                for test in result.tests:
                    if test.status != TestStatus.PASSED:
                        print(f"    - {result.suite_name}::{test.test_id}")
                        if test.details.get("validation", {}).get("failures"):
                            for failure in test.details["validation"]["failures"]:
                                print(f"      {failure}")

        print("=" * 60)

        return total_failed == 0


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="E2E Test Runner for Claude Code Plugins"
    )
    parser.add_argument(
        "--test-cases", "-t",
        type=Path,
        default=Path(__file__).parent / "test_cases.yaml",
        help="Path to test cases YAML file",
    )
    parser.add_argument(
        "--working-dir", "-w",
        type=Path,
        default=Path.cwd(),
        help="Working directory for tests",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=int(os.environ.get("E2E_TEST_TIMEOUT", 120)),
        help="Default timeout per test in seconds",
    )
    parser.add_argument(
        "--model",
        default=os.environ.get("E2E_TEST_MODEL", "claude-sonnet-4-20250514"),
        help="Claude model to use",
    )
    parser.add_argument(
        "--suite", "-s",
        action="append",
        help="Run specific suite(s) only",
    )
    parser.add_argument(
        "--test", "-T",
        action="append",
        help="Run specific test(s) only",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        default=os.environ.get("E2E_VERBOSE", "").lower() == "true",
        help="Verbose output",
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        help="Write results to JSON file",
    )

    args = parser.parse_args()

    # Check authentication
    runner = E2ETestRunner(
        test_cases_path=args.test_cases,
        working_dir=args.working_dir,
        timeout=args.timeout,
        model=args.model,
        verbose=args.verbose,
    )

    if not runner.claude._check_authentication():
        print("ERROR: No authentication configured.")
        print("Set ANTHROPIC_API_KEY or configure Claude Code OAuth.")
        sys.exit(1)

    # Run tests
    results = runner.run_all(
        suites=args.suite,
        tests=args.test,
    )

    # Print summary
    success = runner.print_summary(results)

    # Write JSON output if requested
    if args.output:
        output_data = {
            "suites": [
                {
                    "name": r.suite_name,
                    "description": r.description,
                    "passed": r.passed,
                    "failed": r.failed,
                    "total": r.total,
                    "tests": [
                        {
                            "id": t.test_id,
                            "name": t.name,
                            "status": t.status.value,
                            "duration": t.duration,
                            "details": t.details,
                        }
                        for t in r.tests
                    ],
                }
                for r in results
            ],
        }
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, "w") as f:
            json.dump(output_data, f, indent=2)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
