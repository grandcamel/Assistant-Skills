#!/usr/bin/env python3
"""
Run E2E tests with multiple output format support.

Usage:
    python run_tests.py /path/to/project
    python run_tests.py /path/to/project --json results.json
    python run_tests.py /path/to/project --junit results.xml
    python run_tests.py /path/to/project --html report.html
    python run_tests.py /path/to/project --all-formats
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from xml.etree import ElementTree as ET

# Add the tests/e2e directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "tests" / "e2e"))

try:
    import yaml
except ImportError:
    print("Error: PyYAML not installed. Run: pip install pyyaml")
    sys.exit(1)


class TestStatus:
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"
    TIMEOUT = "timeout"


def check_authentication() -> Dict[str, bool]:
    """Check available authentication methods."""
    auth = {
        "api_key": bool(os.environ.get("ANTHROPIC_API_KEY")),
        "oauth": False,
        "authenticated": False,
    }

    claude_dir = Path.home() / ".claude"
    if claude_dir.exists():
        creds = claude_dir / "credentials.json"
        if creds.exists():
            auth["oauth"] = True

    auth["authenticated"] = auth["api_key"] or auth["oauth"]
    return auth


def run_pytest(
    project_path: Path,
    timeout: int = 120,
    model: str = "claude-sonnet-4-20250514",
    verbose: bool = False,
    suite: Optional[str] = None,
) -> Dict:
    """Run pytest and capture results."""
    import subprocess

    cmd = [
        sys.executable, "-m", "pytest",
        str(project_path / "tests" / "e2e"),
        "-v",
        "--tb=short",
        f"--e2e-timeout={timeout}",
        f"--e2e-model={model}",
    ]

    if verbose:
        cmd.append("--e2e-verbose")

    if suite:
        cmd.extend(["-k", suite])

    env = os.environ.copy()
    env["E2E_TEST_TIMEOUT"] = str(timeout)
    env["E2E_TEST_MODEL"] = model

    result = subprocess.run(
        cmd,
        cwd=project_path,
        capture_output=True,
        text=True,
        env=env,
    )

    return {
        "success": result.returncode == 0,
        "output": result.stdout,
        "error": result.stderr,
        "exit_code": result.returncode,
    }


def run_standalone(
    project_path: Path,
    timeout: int = 120,
    model: str = "claude-sonnet-4-20250514",
    verbose: bool = False,
    suite: Optional[str] = None,
) -> List[Dict]:
    """Run tests using standalone runner."""
    # Import runner from the project's tests/e2e
    runner_path = project_path / "tests" / "e2e" / "runner.py"
    if not runner_path.exists():
        print(f"Error: Runner not found at {runner_path}")
        print("Run setup_e2e.py first to create the test infrastructure.")
        sys.exit(1)

    # Load and execute runner
    import importlib.util
    spec = importlib.util.spec_from_file_location("runner", runner_path)
    runner_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner_module)

    test_cases_path = project_path / "tests" / "e2e" / "test_cases.yaml"
    if not test_cases_path.exists():
        print(f"Error: Test cases not found at {test_cases_path}")
        print("Run generate_test_cases.py first.")
        sys.exit(1)

    e2e_runner = runner_module.E2ETestRunner(
        test_cases_path=test_cases_path,
        working_dir=project_path,
        timeout=timeout,
        model=model,
        verbose=verbose,
    )

    suites = [suite] if suite else None
    results = e2e_runner.run_all(suites=suites)

    return results, e2e_runner


def write_json_report(results: List, output_path: Path, model: str):
    """Write JSON report."""
    data = {
        "timestamp": datetime.now().isoformat(),
        "model": model,
        "summary": {
            "total": sum(r.total for r in results),
            "passed": sum(r.passed for r in results),
            "failed": sum(r.failed for r in results),
        },
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
                        "status": t.status.value if hasattr(t.status, 'value') else t.status,
                        "duration": t.duration,
                        "output": t.output[:500] if t.output else "",
                        "error": t.error[:500] if t.error else "",
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

    print(f"JSON report: {output_path}")


def write_junit_report(results: List, output_path: Path):
    """Write JUnit XML report."""
    testsuites = ET.Element("testsuites")
    testsuites.set("tests", str(sum(r.total for r in results)))
    testsuites.set("failures", str(sum(r.failed for r in results)))
    testsuites.set("time", str(sum(sum(t.duration for t in r.tests) for r in results)))

    for suite_result in results:
        testsuite = ET.SubElement(testsuites, "testsuite")
        testsuite.set("name", suite_result.suite_name)
        testsuite.set("tests", str(suite_result.total))
        testsuite.set("failures", str(suite_result.failed))
        testsuite.set("time", str(sum(t.duration for t in suite_result.tests)))

        for test in suite_result.tests:
            testcase = ET.SubElement(testsuite, "testcase")
            testcase.set("name", test.name)
            testcase.set("classname", suite_result.suite_name)
            testcase.set("time", str(test.duration))

            status = test.status.value if hasattr(test.status, 'value') else test.status
            if status != "passed":
                failure = ET.SubElement(testcase, "failure")
                failure.set("message", status)
                failure.text = test.error or str(test.details)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    tree = ET.ElementTree(testsuites)
    tree.write(output_path, encoding="unicode", xml_declaration=True)

    print(f"JUnit report: {output_path}")


def write_html_report(results: List, output_path: Path, model: str):
    """Write HTML report."""
    total = sum(r.total for r in results)
    passed = sum(r.passed for r in results)
    failed = sum(r.failed for r in results)
    pass_rate = (passed / total * 100) if total > 0 else 0

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>E2E Test Report</title>
    <style>
        * {{ box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        h1 {{ color: #1a1a1a; border-bottom: 2px solid #6366f1; padding-bottom: 10px; }}
        h2 {{ color: #4b5563; margin-top: 30px; }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .stat {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            text-align: center;
        }}
        .stat-value {{ font-size: 2em; font-weight: bold; }}
        .stat-label {{ color: #6b7280; font-size: 0.9em; }}
        .passed {{ color: #22c55e; }}
        .failed {{ color: #ef4444; }}
        .suite {{
            background: white;
            border-radius: 8px;
            margin: 20px 0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .suite-header {{
            background: #f9fafb;
            padding: 15px 20px;
            border-bottom: 1px solid #e5e7eb;
            font-weight: 600;
        }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 12px 15px; text-align: left; border-bottom: 1px solid #e5e7eb; }}
        th {{ background: #f9fafb; font-weight: 600; }}
        tr:hover {{ background: #f9fafb; }}
        .status {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 9999px;
            font-size: 0.85em;
            font-weight: 500;
        }}
        .status-passed {{ background: #dcfce7; color: #166534; }}
        .status-failed {{ background: #fee2e2; color: #991b1b; }}
        .status-timeout {{ background: #fef3c7; color: #92400e; }}
        .meta {{ color: #6b7280; font-size: 0.9em; margin-top: 20px; }}
    </style>
</head>
<body>
    <h1>E2E Test Report</h1>

    <div class="summary">
        <div class="stat">
            <div class="stat-value">{total}</div>
            <div class="stat-label">Total Tests</div>
        </div>
        <div class="stat">
            <div class="stat-value passed">{passed}</div>
            <div class="stat-label">Passed</div>
        </div>
        <div class="stat">
            <div class="stat-value failed">{failed}</div>
            <div class="stat-label">Failed</div>
        </div>
        <div class="stat">
            <div class="stat-value">{pass_rate:.1f}%</div>
            <div class="stat-label">Pass Rate</div>
        </div>
    </div>
'''

    for suite_result in results:
        suite_status = "passed" if suite_result.failed == 0 else "failed"
        html += f'''
    <div class="suite">
        <div class="suite-header">
            {suite_result.suite_name}
            <span class="status status-{suite_status}">{suite_result.passed}/{suite_result.total}</span>
        </div>
        <table>
            <thead>
                <tr>
                    <th>Test</th>
                    <th>Status</th>
                    <th>Duration</th>
                </tr>
            </thead>
            <tbody>
'''
        for test in suite_result.tests:
            status = test.status.value if hasattr(test.status, 'value') else test.status
            html += f'''
                <tr>
                    <td>{test.name}</td>
                    <td><span class="status status-{status}">{status}</span></td>
                    <td>{test.duration:.2f}s</td>
                </tr>
'''
        html += '''
            </tbody>
        </table>
    </div>
'''

    html += f'''
    <div class="meta">
        <p><strong>Model:</strong> {model}</p>
        <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
</body>
</html>
'''

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html)

    print(f"HTML report: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Run E2E tests with multiple output formats"
    )
    parser.add_argument(
        "project_path",
        nargs="?",
        default=".",
        help="Path to the project (default: current directory)"
    )
    parser.add_argument(
        "--timeout", "-t",
        type=int,
        default=int(os.environ.get("E2E_TEST_TIMEOUT", 120)),
        help="Timeout per test in seconds"
    )
    parser.add_argument(
        "--model", "-m",
        default=os.environ.get("E2E_TEST_MODEL", "claude-sonnet-4-20250514"),
        help="Claude model to use"
    )
    parser.add_argument(
        "--suite", "-s",
        help="Run specific suite only"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--json",
        type=Path,
        help="Output JSON report to file"
    )
    parser.add_argument(
        "--junit",
        type=Path,
        help="Output JUnit XML report to file"
    )
    parser.add_argument(
        "--html",
        type=Path,
        help="Output HTML report to file"
    )
    parser.add_argument(
        "--all-formats",
        action="store_true",
        help="Generate all report formats in test-results/"
    )

    args = parser.parse_args()

    project_path = Path(args.project_path).resolve()
    if not project_path.exists():
        print(f"Error: Project not found: {project_path}")
        sys.exit(1)

    # Check authentication
    auth = check_authentication()
    if not auth["authenticated"]:
        print("Error: No authentication configured")
        print("Set ANTHROPIC_API_KEY or run: claude auth login")
        sys.exit(1)

    if auth["api_key"]:
        print("Authentication: API Key")
    else:
        print("Authentication: OAuth")

    print(f"Model: {args.model}")
    print(f"Timeout: {args.timeout}s")
    print()

    # Run tests
    results, runner = run_standalone(
        project_path,
        timeout=args.timeout,
        model=args.model,
        verbose=args.verbose,
        suite=args.suite,
    )

    # Print summary
    success = runner.print_summary(results)

    # Generate reports
    if args.all_formats:
        results_dir = project_path / "test-results" / "e2e"
        args.json = results_dir / "results.json"
        args.junit = results_dir / "results.xml"
        args.html = results_dir / "report.html"

    if args.json:
        write_json_report(results, args.json, args.model)

    if args.junit:
        write_junit_report(results, args.junit)

    if args.html:
        write_html_report(results, args.html, args.model)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
