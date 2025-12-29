# E2E Testing Framework for Claude Code Plugins

End-to-end tests that validate the assistant-skills plugin by interacting with the actual Claude Code CLI.

## Overview

This framework:
- Installs the plugin in a Docker container
- Sends real prompts to Claude Code CLI
- Validates responses against expected outcomes
- Reports pass/fail status with detailed output

## Prerequisites

### Authentication (Choose One)

**Option 1: API Key (Recommended for CI/testing)**
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

**Option 2: Claude Code OAuth**
```bash
# Authenticate once
claude auth login

# Credentials stored in ~/.claude/credentials.json
# Docker will mount this directory automatically
```

**Option 3: Environment File**
```bash
# Create .env file
echo "ANTHROPIC_API_KEY=sk-ant-..." > .env
```

## Quick Start

```bash
# Run E2E tests in Docker (recommended)
./scripts/run-e2e-tests.sh

# Run locally (no Docker)
./scripts/run-e2e-tests.sh --local

# Open shell for debugging
./scripts/run-e2e-tests.sh --shell

# Verbose output
./scripts/run-e2e-tests.sh --verbose
```

## Test Structure

```
tests/e2e/
├── README.md              # This file
├── __init__.py
├── conftest.py            # Pytest fixtures
├── runner.py              # Standalone test runner
├── test_cases.yaml        # Test case definitions
└── test_plugin_e2e.py     # Pytest test module
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ANTHROPIC_API_KEY` | - | API key for Claude |
| `E2E_TEST_TIMEOUT` | 120 | Timeout per test (seconds) |
| `E2E_TEST_MODEL` | claude-sonnet-4-20250514 | Claude model to use |
| `E2E_VERBOSE` | false | Enable verbose output |

### Using Different Models

```bash
# Use Haiku for faster/cheaper tests
E2E_TEST_MODEL=claude-haiku-3-5-20250110 ./scripts/run-e2e-tests.sh

# Use Opus for most capable responses
E2E_TEST_MODEL=claude-opus-4-20250514 ./scripts/run-e2e-tests.sh
```

## Writing Test Cases

Test cases are defined in `test_cases.yaml`:

```yaml
suites:
  my_suite:
    description: My test suite
    tests:
      - id: my_test
        name: Test something
        prompt: "Ask Claude to do something"
        expect:
          success: true
          output_contains:
            - "expected text"
          output_contains_any:
            - "option 1"
            - "option 2"
          no_errors: true
          no_crashes: true
```

### Expectation Types

| Expectation | Description |
|-------------|-------------|
| `success: true` | Test passes if no hard errors |
| `output_contains` | All listed strings must appear in output |
| `output_contains_any` | At least one string must appear |
| `no_errors` | No error patterns in output |
| `no_crashes` | No crash indicators (segfault, panic, etc.) |

## Running Specific Tests

```bash
# Run specific suite
python tests/e2e/runner.py --suite assistant_builder

# Run specific test
python tests/e2e/runner.py --test validate_project

# Multiple filters
python tests/e2e/runner.py --suite plugin_installation --test install_plugin
```

## Docker Commands

```bash
# Build the E2E container
docker compose -f docker/e2e/docker-compose.yml build

# Run tests
docker compose -f docker/e2e/docker-compose.yml run --rm e2e-tests

# Interactive debugging
docker compose -f docker/e2e/docker-compose.yml run --rm e2e-shell

# Clean up
docker compose -f docker/e2e/docker-compose.yml down
```

## Pytest Integration

Run with pytest for integration with other test tooling:

```bash
# Run all E2E tests
pytest tests/e2e/ -v

# Run with markers
pytest tests/e2e/ -v -m e2e

# Skip slow tests
pytest tests/e2e/ -v -m "not slow"

# Generate JUnit XML report
pytest tests/e2e/ -v --junitxml=test-results/e2e/results.xml
```

## Cost Considerations

E2E tests make real API calls and incur costs:

| Model | Approximate Cost per Test |
|-------|--------------------------|
| claude-haiku-3-5-20250110 | ~$0.001 |
| claude-sonnet-4-20250514 | ~$0.01 |
| claude-opus-4-20250514 | ~$0.05 |

**Recommendations:**
- Use Haiku for frequent testing
- Use Sonnet for release validation
- Run manually, not in CI (to control costs)

## Troubleshooting

### Authentication Errors

```
ERROR: No authentication configured
```

**Solution:** Set `ANTHROPIC_API_KEY` or run `claude auth login`

### Claude CLI Not Found

```
Claude Code CLI not found
```

**Solution:** `npm install -g @anthropic-ai/claude-code`

### Timeout Errors

```
Command timed out after 120s
```

**Solution:** Increase timeout with `E2E_TEST_TIMEOUT=300`

### Permission Denied (Docker)

```
permission denied while trying to connect to Docker daemon
```

**Solution:** Add user to docker group or use `sudo`

## Adding New Test Suites

1. Add test cases to `test_cases.yaml`:
```yaml
suites:
  new_skill:
    description: Tests for new skill
    tests:
      - id: basic_test
        name: Basic functionality
        prompt: "Test the new skill"
        expect:
          success: true
```

2. Optionally add pytest tests in `test_plugin_e2e.py`:
```python
class TestNewSkill:
    def test_basic(self, claude_runner, e2e_enabled):
        if not e2e_enabled:
            pytest.skip("E2E disabled")
        result = claude_runner.send_prompt("Test new skill")
        assert result["success"]
```

## CI/CD Integration

For GitHub Actions (manual trigger only to control costs):

```yaml
name: E2E Tests

on:
  workflow_dispatch:
    inputs:
      model:
        description: 'Claude model'
        default: 'claude-sonnet-4-20250514'

jobs:
  e2e:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run E2E tests
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          E2E_TEST_MODEL: ${{ github.event.inputs.model }}
        run: ./scripts/run-e2e-tests.sh
```
