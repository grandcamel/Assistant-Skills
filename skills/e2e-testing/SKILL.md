---
name: e2e-testing
description: Set up end-to-end testing infrastructure for Assistant Skills plugins. Use when user wants to "add E2E tests", "test my plugin", "set up integration testing", "create plugin tests", or needs to validate their Claude Code plugin works correctly with real API calls.
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

## Scripts Reference

| Script | Purpose |
|--------|---------|
| `setup_e2e.py` | Initialize E2E testing infrastructure |
| `generate_test_cases.py` | Auto-generate test cases from plugin |
| `run_tests.py` | Execute tests with multiple output formats |
| `update_docs.py` | Update project documentation |

## Authentication

| Method | Location | Setup |
|--------|----------|-------|
| OAuth | `~/.claude.json` | `claude auth login` |
| API Key | Environment | `export ANTHROPIC_API_KEY="sk-ant-..."` |

Local runs (`--local`) prefer OAuth credentials over API keys.

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `E2E_TEST_TIMEOUT` | 120 | Timeout per test (seconds) |
| `E2E_TEST_MODEL` | claude-sonnet-4-20250514 | Claude model |
| `E2E_MAX_TURNS` | 5 | Max conversation turns |

## Output Formats

| Format | Flag | Description |
|--------|------|-------------|
| Console | (default) | Colored terminal output |
| JSON | `--output results.json` | Machine-readable results |
| JUnit | `--junit results.xml` | CI/CD integration |
| HTML | `--html report.html` | Visual report |

## Cost Estimates

| Model | Cost per Test | 20 Tests |
|-------|---------------|----------|
| Haiku | ~$0.001 | ~$0.02 |
| Sonnet | ~$0.01 | ~$0.20 |
| Opus | ~$0.05 | ~$1.00 |

## Customizing Tests

Edit `tests/e2e/test_cases.yaml` to add custom test cases:

```yaml
suites:
  custom:
    tests:
      - id: my_test
        prompt: "Do something specific"
        timeout: 180      # Override default
        max_turns: 10     # Override default
        expect:
          output_contains: ["expected"]
```

## Response Logging

Failed test responses logged to `test-results/e2e/responses_latest.log`.

## More Information

- **Detailed guide**: See `tests/e2e/README.md`
- **Prompt patterns**: See `docs/test-prompt-best-practices.md`
- **Troubleshooting**: See `docs/troubleshooting.md`
