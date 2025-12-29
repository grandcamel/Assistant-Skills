#!/usr/bin/env python3
"""
Update project documentation with E2E testing information.

Updates README.md, CLAUDE.md, and generates tests/e2e/README.md.

Usage:
    python update_docs.py /path/to/project
    python update_docs.py /path/to/project --dry-run
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional


def detect_project_info(project_path: Path) -> Dict:
    """Detect project information."""
    info = {
        "name": project_path.name,
        "has_readme": (project_path / "README.md").exists(),
        "has_claude_md": (project_path / "CLAUDE.md").exists(),
        "has_e2e_tests": (project_path / "tests" / "e2e").exists(),
        "skills_count": 0,
    }

    # Count skills
    skills_dir = project_path / "skills"
    if skills_dir.exists():
        info["skills_count"] = len([
            d for d in skills_dir.iterdir()
            if d.is_dir() and d.name != "shared" and (d / "SKILL.md").exists()
        ])

    # Get plugin name
    plugin_json = project_path / ".claude-plugin" / "plugin.json"
    if plugin_json.exists():
        with open(plugin_json) as f:
            data = json.load(f)
            info["name"] = data.get("name", info["name"])

    return info


def generate_e2e_readme(project_info: Dict) -> str:
    """Generate tests/e2e/README.md content."""
    return f'''# E2E Tests for {project_info["name"]}

End-to-end tests that validate the plugin by interacting with the Claude Code CLI.

## Prerequisites

### Authentication (Choose One)

**Option 1: API Key**
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

**Option 2: OAuth**
```bash
claude auth login
```

## Quick Start

```bash
# Run all tests
./scripts/run-e2e-tests.sh

# Run locally (no Docker)
./scripts/run-e2e-tests.sh --local

# Verbose output
./scripts/run-e2e-tests.sh --verbose

# Debug shell
./scripts/run-e2e-tests.sh --shell
```

## Test Structure

```
tests/e2e/
├── __init__.py
├── conftest.py          # Pytest fixtures
├── runner.py            # Test execution engine
├── test_cases.yaml      # YAML test definitions
└── test_plugin_e2e.py   # Pytest test classes
```

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `ANTHROPIC_API_KEY` | - | API key |
| `E2E_TEST_TIMEOUT` | 120 | Timeout per test (seconds) |
| `E2E_TEST_MODEL` | claude-sonnet-4-20250514 | Model to use |
| `E2E_VERBOSE` | false | Verbose output |

## Output Formats

```bash
# JSON report
python -m tests.e2e.run_tests --json results.json

# JUnit XML (CI integration)
python -m tests.e2e.run_tests --junit results.xml

# HTML report
python -m tests.e2e.run_tests --html report.html

# All formats
python -m tests.e2e.run_tests --all-formats
```

## Adding Tests

### YAML Test Cases

Edit `test_cases.yaml`:

```yaml
suites:
  my_suite:
    description: My tests
    tests:
      - id: my_test
        name: Test something
        prompt: "Do something"
        expect:
          output_contains:
            - "expected"
          no_errors: true
```

### Pytest Classes

Edit `test_plugin_e2e.py`:

```python
class TestMyFeature:
    def test_something(self, claude_runner, e2e_enabled):
        if not e2e_enabled:
            pytest.skip("E2E disabled")

        result = claude_runner.send_prompt("My prompt")
        assert "expected" in result["output"]
```

## Cost Estimates

| Model | Per Test | 20 Tests |
|-------|----------|----------|
| Haiku | ~$0.001 | ~$0.02 |
| Sonnet | ~$0.01 | ~$0.20 |
| Opus | ~$0.05 | ~$1.00 |
'''


def add_e2e_section_to_readme(content: str, project_info: Dict) -> str:
    """Add E2E testing section to README.md."""
    # Check if E2E section already exists
    if "## E2E Testing" in content or "### E2E Tests" in content or "### Run E2E Tests" in content:
        return content  # Already has E2E section

    e2e_section = '''
### Run E2E Tests

E2E tests validate the plugin with the Claude Code CLI:

```bash
# Requires ANTHROPIC_API_KEY
./scripts/run-e2e-tests.sh           # Docker
./scripts/run-e2e-tests.sh --local   # Local
```

See [tests/e2e/README.md](tests/e2e/README.md) for details.
'''

    # Find the Development section and add after "Run Tests"
    patterns = [
        (r'(### Run Tests\n```.*?```)', r'\1\n' + e2e_section),
        (r'(## Development\n)', r'\1' + e2e_section + '\n'),
        (r'(## Testing\n)', r'\1' + e2e_section + '\n'),
    ]

    for pattern, replacement in patterns:
        if re.search(pattern, content, re.DOTALL):
            content = re.sub(pattern, replacement, content, count=1, flags=re.DOTALL)
            return content

    # If no good insertion point, add before Contributing or at end
    if "## Contributing" in content:
        content = content.replace("## Contributing", f"## E2E Testing\n{e2e_section}\n---\n\n## Contributing")
    else:
        content += f"\n---\n\n## E2E Testing\n{e2e_section}"

    return content


def update_claude_md(content: str, project_info: Dict) -> str:
    """Update CLAUDE.md with E2E test commands."""
    # Check if E2E section already exists
    if "E2E" in content and "run-e2e-tests" in content:
        return content

    e2e_section = '''
### Run E2E Tests

```bash
# Requires ANTHROPIC_API_KEY
./scripts/run-e2e-tests.sh           # Docker
./scripts/run-e2e-tests.sh --local   # Local
./scripts/run-e2e-tests.sh --verbose # Verbose
```
'''

    # Find Commands section or Run Tests section
    patterns = [
        (r'(### Run.*?Tests?\n```.*?```)', r'\1\n' + e2e_section),
        (r'(## Commands\n)', r'\1' + e2e_section + '\n'),
    ]

    for pattern, replacement in patterns:
        if re.search(pattern, content, re.DOTALL):
            content = re.sub(pattern, replacement, content, count=1, flags=re.DOTALL)
            return content

    # Add at end of file
    content += f"\n{e2e_section}"
    return content


def update_docs(
    project_path: Path,
    dry_run: bool = False,
) -> Dict:
    """Update all documentation files."""
    project_path = Path(project_path).resolve()
    project_info = detect_project_info(project_path)

    result = {
        "project": str(project_path),
        "files_updated": [],
        "files_created": [],
    }

    # Generate tests/e2e/README.md
    e2e_readme_path = project_path / "tests" / "e2e" / "README.md"
    if project_info["has_e2e_tests"]:
        e2e_readme_content = generate_e2e_readme(project_info)
        if not dry_run:
            e2e_readme_path.write_text(e2e_readme_content)
        if e2e_readme_path.exists():
            result["files_updated"].append("tests/e2e/README.md")
        else:
            result["files_created"].append("tests/e2e/README.md")

    # Update README.md
    readme_path = project_path / "README.md"
    if readme_path.exists():
        content = readme_path.read_text()
        new_content = add_e2e_section_to_readme(content, project_info)
        if new_content != content:
            if not dry_run:
                readme_path.write_text(new_content)
            result["files_updated"].append("README.md")

    # Update CLAUDE.md
    claude_md_path = project_path / "CLAUDE.md"
    if claude_md_path.exists():
        content = claude_md_path.read_text()
        new_content = update_claude_md(content, project_info)
        if new_content != content:
            if not dry_run:
                claude_md_path.write_text(new_content)
            result["files_updated"].append("CLAUDE.md")

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Update project documentation with E2E testing info"
    )
    parser.add_argument(
        "project_path",
        nargs="?",
        default=".",
        help="Path to the project"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed"
    )

    args = parser.parse_args()

    project_path = Path(args.project_path)
    if not project_path.exists():
        print(f"Error: Project not found: {project_path}")
        sys.exit(1)

    result = update_docs(project_path, dry_run=args.dry_run)

    print(f"Project: {result['project']}")
    print()

    if args.dry_run:
        print("DRY RUN - would update:")
    else:
        print("Updated:")

    for f in result["files_updated"]:
        print(f"  {f}")

    if result["files_created"]:
        print()
        if args.dry_run:
            print("Would create:")
        else:
            print("Created:")
        for f in result["files_created"]:
            print(f"  {f}")

    if not result["files_updated"] and not result["files_created"]:
        print("  No changes needed")

    if not args.dry_run and (result["files_updated"] or result["files_created"]):
        print()
        print("Next steps:")
        print("  git add README.md CLAUDE.md tests/e2e/README.md")
        print('  git commit -m "docs: add E2E testing documentation"')


if __name__ == "__main__":
    main()
