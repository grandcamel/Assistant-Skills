"""Tests for run_tests.py script."""

import json
import pytest
import sys
from pathlib import Path
from xml.etree import ElementTree as ET

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from run_tests import (
    check_authentication,
    TestStatus,
    write_json_report,
    write_junit_report,
    write_html_report,
)


class MockTestResult:
    """Mock test result for report testing."""

    def __init__(self, test_id, name, status, duration=1.0, output="", error=""):
        self.test_id = test_id
        self.name = name
        self.status = status
        self.duration = duration
        self.output = output
        self.error = error
        self.details = {}


class MockSuiteResult:
    """Mock suite result for report testing."""

    def __init__(self, suite_name, tests):
        self.suite_name = suite_name
        self.description = f"Tests for {suite_name}"
        self.tests = tests
        self.total = len(tests)
        self.passed = sum(1 for t in tests if t.status == TestStatus.PASSED)
        self.failed = self.total - self.passed


class TestCheckAuthentication:
    """Tests for authentication checking."""

    def test_detects_api_key(self, monkeypatch):
        """Should detect ANTHROPIC_API_KEY."""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test")

        result = check_authentication()

        assert result["api_key"] is True
        assert result["authenticated"] is True

    def test_no_auth_without_key(self, monkeypatch):
        """Should report no auth without API key."""
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

        result = check_authentication()

        assert result["api_key"] is False
        # Note: oauth might be true if ~/.claude exists


class TestWriteJsonReport:
    """Tests for JSON report generation."""

    def test_creates_valid_json(self, tmp_path):
        """Should create valid JSON file."""
        output_path = tmp_path / "results.json"
        results = [
            MockSuiteResult("suite1", [
                MockTestResult("test1", "Test 1", TestStatus.PASSED),
                MockTestResult("test2", "Test 2", TestStatus.FAILED, error="Failed"),
            ])
        ]

        write_json_report(results, output_path, "claude-sonnet-4-20250514")

        assert output_path.exists()
        data = json.loads(output_path.read_text())
        assert "timestamp" in data
        assert "summary" in data
        assert "suites" in data

    def test_includes_summary(self, tmp_path):
        """Should include test summary."""
        output_path = tmp_path / "results.json"
        results = [
            MockSuiteResult("suite1", [
                MockTestResult("test1", "Test 1", TestStatus.PASSED),
                MockTestResult("test2", "Test 2", TestStatus.PASSED),
                MockTestResult("test3", "Test 3", TestStatus.FAILED),
            ])
        ]

        write_json_report(results, output_path, "claude-sonnet-4-20250514")

        data = json.loads(output_path.read_text())
        assert data["summary"]["total"] == 3
        assert data["summary"]["passed"] == 2
        assert data["summary"]["failed"] == 1

    def test_creates_parent_directory(self, tmp_path):
        """Should create parent directory if needed."""
        output_path = tmp_path / "nested" / "dir" / "results.json"
        results = [MockSuiteResult("suite1", [])]

        write_json_report(results, output_path, "claude-sonnet-4-20250514")

        assert output_path.exists()


class TestWriteJunitReport:
    """Tests for JUnit XML report generation."""

    def test_creates_valid_xml(self, tmp_path):
        """Should create valid XML file."""
        output_path = tmp_path / "results.xml"
        results = [
            MockSuiteResult("suite1", [
                MockTestResult("test1", "Test 1", TestStatus.PASSED),
            ])
        ]

        write_junit_report(results, output_path)

        assert output_path.exists()
        tree = ET.parse(output_path)
        root = tree.getroot()
        assert root.tag == "testsuites"

    def test_includes_test_counts(self, tmp_path):
        """Should include test counts in attributes."""
        output_path = tmp_path / "results.xml"
        results = [
            MockSuiteResult("suite1", [
                MockTestResult("test1", "Test 1", TestStatus.PASSED),
                MockTestResult("test2", "Test 2", TestStatus.FAILED),
            ])
        ]

        write_junit_report(results, output_path)

        tree = ET.parse(output_path)
        root = tree.getroot()
        assert root.get("tests") == "2"
        assert root.get("failures") == "1"

    def test_includes_failure_details(self, tmp_path):
        """Should include failure details."""
        output_path = tmp_path / "results.xml"
        results = [
            MockSuiteResult("suite1", [
                MockTestResult("test1", "Test 1", TestStatus.FAILED, error="Something went wrong"),
            ])
        ]

        write_junit_report(results, output_path)

        tree = ET.parse(output_path)
        failure = tree.find(".//failure")
        assert failure is not None
        assert failure.text == "Something went wrong"


class TestWriteHtmlReport:
    """Tests for HTML report generation."""

    def test_creates_html_file(self, tmp_path):
        """Should create HTML file."""
        output_path = tmp_path / "report.html"
        results = [
            MockSuiteResult("suite1", [
                MockTestResult("test1", "Test 1", TestStatus.PASSED),
            ])
        ]

        write_html_report(results, output_path, "claude-sonnet-4-20250514")

        assert output_path.exists()
        content = output_path.read_text()
        assert "<!DOCTYPE html>" in content
        assert "E2E Test Report" in content

    def test_includes_summary_stats(self, tmp_path):
        """Should include summary statistics."""
        output_path = tmp_path / "report.html"
        results = [
            MockSuiteResult("suite1", [
                MockTestResult("test1", "Test 1", TestStatus.PASSED),
                MockTestResult("test2", "Test 2", TestStatus.PASSED),
                MockTestResult("test3", "Test 3", TestStatus.FAILED),
            ])
        ]

        write_html_report(results, output_path, "claude-sonnet-4-20250514")

        content = output_path.read_text()
        assert "Total Tests" in content
        assert "Passed" in content
        assert "Failed" in content
        assert "Pass Rate" in content

    def test_includes_suite_details(self, tmp_path):
        """Should include suite details."""
        output_path = tmp_path / "report.html"
        results = [
            MockSuiteResult("my_suite", [
                MockTestResult("test1", "My Test", TestStatus.PASSED, duration=2.5),
            ])
        ]

        write_html_report(results, output_path, "claude-sonnet-4-20250514")

        content = output_path.read_text()
        assert "my_suite" in content
        assert "My Test" in content
        assert "2.50s" in content

    def test_includes_model_info(self, tmp_path):
        """Should include model information."""
        output_path = tmp_path / "report.html"
        results = [MockSuiteResult("suite1", [])]

        write_html_report(results, output_path, "claude-sonnet-4-20250514")

        content = output_path.read_text()
        assert "claude-sonnet-4-20250514" in content


class TestTestStatus:
    """Tests for TestStatus enum."""

    def test_has_expected_values(self):
        """Should have expected status values."""
        assert TestStatus.PASSED == "passed"
        assert TestStatus.FAILED == "failed"
        assert TestStatus.SKIPPED == "skipped"
        assert TestStatus.ERROR == "error"
        assert TestStatus.TIMEOUT == "timeout"
