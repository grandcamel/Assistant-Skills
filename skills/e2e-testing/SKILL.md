---
name: e2e-testing
description: Set up end-to-end testing infrastructure for Assistant Skills plugins. Use when user wants to "add E2E tests", "test my plugin", "set up integration testing", "create plugin tests", or needs to validate their Claude Code plugin works correctly with real API calls.
when_to_use:
  - User wants to add E2E testing to their plugin
  - User asks about testing Claude Code plugins
  - User wants to validate plugin functionality
  - User mentions integration testing for skills
---

# E2E Testing

Set up comprehensive end-to-end testing infrastructure for Assistant Skills plugins. Auto-generates test cases from your plugin structure and skills.

## Quick Start

```bash
# Initialize E2E testing infrastructure
python skills/e2e-testing/scripts/setup_e2e.py /path/to/project

# Auto-generate test cases from plugin structure
python skills/e2e-testing/scripts/generate_test_cases.py /path/to/project

# Run tests
./scripts/run-e2e-tests.sh

# Update project documentation
python skills/e2e-testing/scripts/update_docs.py /path/to/project
```

## Workflow Overview

### Phase 1: Setup Infrastructure
```
setup_e2e.py
├── Create docker/e2e/
│   ├── Dockerfile
│   └── docker-compose.yml
├── Create tests/e2e/
│   ├── __init__.py
│   ├── conftest.py
│   ├── runner.py
│   └── test_plugin_e2e.py
├── Create requirements-e2e.txt
└── Create scripts/run-e2e-tests.sh
```

### Phase 2: Generate Test Cases
```
generate_test_cases.py
├── Analyze plugin.json
├── Scan all SKILL.md files
├── Parse skill descriptions for test prompts
├── Generate test_cases.yaml
│   ├── Plugin installation tests
│   ├── Skill discovery tests
│   ├── Per-skill functionality tests
│   └── Error handling tests
└── Generate pytest test classes
```

### Phase 3: Run Tests
```
run_tests.py / run-e2e-tests.sh
├── Check authentication (API key or OAuth)
├── Execute tests (Docker or local)
├── Generate reports
│   ├── Console output
│   ├── JSON results
│   ├── JUnit XML
│   └── HTML report
└── Return exit code
```

### Phase 4: Update Documentation
```
update_docs.py
├── Add E2E section to README.md
├── Update CLAUDE.md with test commands
└── Generate tests/e2e/README.md
```

## Scripts Reference

| Script | Purpose |
|--------|---------|
| `setup_e2e.py` | Initialize E2E testing infrastructure |
| `generate_test_cases.py` | Auto-generate test cases from plugin |
| `run_tests.py` | Execute tests with multiple output formats |
| `update_docs.py` | Update project documentation |

## Authentication

Tests require Claude API access. Supported methods:

| Method | Setup |
|--------|-------|
| API Key | `export ANTHROPIC_API_KEY="sk-ant-..."` |
| OAuth | `claude auth login` |
| Config file | Mount `~/.claude/` directory |

## Test Case Generation

The `generate_test_cases.py` script analyzes your plugin and generates intelligent test cases:

### From plugin.json
- Plugin installation test
- Version verification
- Metadata validation

### From SKILL.md files
- Skill discovery tests
- Trigger phrase tests (from description)
- Script execution tests
- Error handling tests

### Example Generated Test
```yaml
suites:
  jira_issues:
    description: Tests for jira-issues skill
    tests:
      - id: discover_skill
        name: Verify jira-issues skill is discoverable
        prompt: "What skills do you have for Jira issues?"
        expect:
          output_contains_any:
            - "jira-issues"
            - "issue"
            - "Jira"
          no_errors: true

      - id: list_issues
        name: Test listing Jira issues
        prompt: "List recent Jira issues"
        expect:
          success: true
          no_crashes: true
```

## Output Formats

| Format | Flag | Description |
|--------|------|-------------|
| Console | (default) | Colored terminal output |
| JSON | `--output results.json` | Machine-readable results |
| JUnit | `--junit results.xml` | CI/CD integration |
| HTML | `--html report.html` | Visual report |

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ANTHROPIC_API_KEY` | - | API key for Claude |
| `E2E_TEST_TIMEOUT` | 120 | Timeout per test (seconds) |
| `E2E_TEST_MODEL` | claude-sonnet-4-20250514 | Claude model |
| `E2E_VERBOSE` | false | Verbose output |

### Model Selection

Default is Sonnet for balance of capability and cost:

```bash
# Use Haiku for faster/cheaper tests
E2E_TEST_MODEL=claude-haiku-3-5-20250110 ./scripts/run-e2e-tests.sh

# Use Opus for most capable
E2E_TEST_MODEL=claude-opus-4-20250514 ./scripts/run-e2e-tests.sh
```

## Example: Full Setup

```bash
# 1. Initialize infrastructure
python ~/Assistant-Skills/skills/e2e-testing/scripts/setup_e2e.py .

# 2. Generate test cases from your plugin
python ~/Assistant-Skills/skills/e2e-testing/scripts/generate_test_cases.py .

# 3. Review generated tests
cat tests/e2e/test_cases.yaml

# 4. Run tests
export ANTHROPIC_API_KEY="sk-ant-..."
./scripts/run-e2e-tests.sh --verbose

# 5. Update documentation
python ~/Assistant-Skills/skills/e2e-testing/scripts/update_docs.py .

# 6. Commit
git add . && git commit -m "feat(testing): add E2E test infrastructure"
```

## Cost Estimates

| Model | Cost per Test | 20 Tests |
|-------|---------------|----------|
| Haiku | ~$0.001 | ~$0.02 |
| Sonnet | ~$0.01 | ~$0.20 |
| Opus | ~$0.05 | ~$1.00 |

## Customizing Tests

### Adding Custom Test Cases

Edit `tests/e2e/test_cases.yaml`:

```yaml
suites:
  custom:
    description: Custom test suite
    tests:
      - id: my_test
        name: My custom test
        prompt: "Do something specific"
        expect:
          output_contains:
            - "expected output"
          no_errors: true
```

### Adding Pytest Tests

Edit `tests/e2e/test_plugin_e2e.py`:

```python
class TestCustom:
    def test_my_feature(self, claude_runner, e2e_enabled):
        if not e2e_enabled:
            pytest.skip("E2E disabled")

        result = claude_runner.send_prompt("My prompt")
        assert "expected" in result["output"].lower()
```

## Troubleshooting

### No authentication configured
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
# or
claude auth login
```

### Tests timing out
```bash
E2E_TEST_TIMEOUT=300 ./scripts/run-e2e-tests.sh
```

### Docker permission denied
```bash
sudo usermod -aG docker $USER
# Then log out and back in
```
