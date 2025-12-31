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

## Workflow Overview

### Phase 1: Setup Infrastructure
```
setup_e2e.py
├── Create docker/e2e/
│   ├── Dockerfile
│   └── docker-compose.yml
├── Create tests/e2e/
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

| Method | Location | Setup |
|--------|----------|-------|
| OAuth | `~/.claude.json` | `claude auth login` |
| OAuth (legacy) | `~/.claude/credentials.json` | Older Claude Code versions |
| API Key | Environment | `export ANTHROPIC_API_KEY="sk-ant-..."` |

The test framework checks all locations automatically.

**Local runs prefer OAuth**: When running with `--local`, OAuth credentials take precedence over API keys. This ensures local development uses your authenticated Claude session rather than a separate API key.

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
| `E2E_MAX_TURNS` | 5 | Max conversation turns per test |
| `E2E_VERBOSE` | false | Verbose output |

### Model Selection

Default is Sonnet for balance of capability and cost:

```bash
# Use Haiku for faster/cheaper tests
E2E_TEST_MODEL=claude-haiku-4-20250514 ./scripts/run-e2e-tests.sh

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

## Test Prompt Best Practices

Well-designed test prompts complete in fewer turns and produce consistent results.

### Avoid Exploration Triggers

Prompts that trigger file exploration can exhaust turns before producing output:

```yaml
# BAD - May cause Claude to read files for multiple turns
prompt: "What templates are available for this project?"
prompt: "Analyze the shared library structure"
prompt: "What are the main dependencies?"

# GOOD - Direct questions that don't require file exploration
prompt: "Without reading files, what templates are typically used for Assistant Skills projects?"
prompt: "Without reading files, describe typical Python package dependencies for plugins."
prompt: "Briefly explain what a landing-page skill typically does."
```

### Use Flexible Expectations

Test validation should be lenient to handle Claude's varied responses:

```yaml
# BAD - Exact match is fragile
expect:
  output_contains:
    - "assistant-skills-lib"

# GOOD - Any of these terms indicates success
expect:
  output_contains_any:
    - "skill"
    - "plugin"
    - "SKILL"
    - "claude"
  no_crashes: true  # More lenient than no_errors
```

### Prompt Design Patterns

| Pattern | Example | Purpose |
|---------|---------|---------|
| Prefix constraint | "Without reading files, ..." | Prevents file exploration |
| Direct question | "What is X?" vs "Analyze X" | Faster response |
| Conceptual focus | "What does X typically do?" | Avoids project-specific exploration |
| Flexible terms | Multiple synonyms in `output_contains_any` | Handles response variation |

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
        timeout: 180        # Optional: override default timeout (seconds)
        max_turns: 5        # Optional: override default max turns
        expect:
          output_contains:
            - "expected output"
          no_errors: true
```

Per-test `timeout` and `max_turns` override the global defaults for tests that need more time or conversation turns.

### Adding Pytest Tests

Edit `tests/e2e/test_plugin_e2e.py`:

```python
class TestCustom:
    def test_my_feature(self, claude_runner, e2e_enabled):
        if not e2e_enabled:
            pytest.skip("E2E disabled")

        result = claude_runner.send_prompt("My prompt")
        assert "expected" in result["output"].lower()

    def test_complex_feature(self, claude_runner, e2e_enabled):
        """Test that needs more turns or longer timeout."""
        if not e2e_enabled:
            pytest.skip("E2E disabled")

        result = claude_runner.send_prompt(
            "Complex prompt requiring exploration",
            timeout=180,    # Override default timeout
            max_turns=10    # Override default max turns
        )
        assert result["success"]
```

## Response Logging

All Claude responses are automatically logged for troubleshooting:

| Location | Description |
|----------|-------------|
| `test-results/e2e/responses_latest.log` | Symlink to most recent log |
| `test-results/e2e/responses_YYYYMMDD_HHMMSS.log` | Timestamped logs |

### Log Contents

Each prompt/response pair is logged with:
- Timestamp
- Test ID (if available)
- Prompt text (truncated to 200 chars)
- Full response output (stdout)
- Stderr (if any)
- Exit code and duration

### Viewing Failed Test Responses

When tests fail, responses are shown:
1. **In pytest output** - Truncated response in assertion message
2. **In test summary** - Full response output for each failure
3. **In log file** - Complete untruncated responses

```bash
# View latest responses after test run
cat test-results/e2e/responses_latest.log

# Search for specific test
grep -A 50 "test_my_feature" test-results/e2e/responses_latest.log
```

## Troubleshooting

### No authentication configured
```bash
# Option 1: API Key
export ANTHROPIC_API_KEY="sk-ant-..."

# Option 2: OAuth (creates ~/.claude.json)
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

### Tests showing "Reached max turns"
This usually means prompts are triggering file exploration. Fix by:
1. Redesigning prompts (see Test Prompt Best Practices above)
2. Increasing turn limit for complex tests:
```bash
E2E_MAX_TURNS=10 ./scripts/run-e2e-tests.sh
```

### Tests fail with "cannot use with root privileges"
The Docker container runs as non-root user (`testuser`) to support `--dangerously-skip-permissions`. If you encounter permission issues with mounted volumes, check ownership settings in docker-compose.yml.

### Docker volume permission errors
If you see "Operation not permitted" errors on `.claude` directory:
```bash
# Remove stale Docker volume and rebuild
docker volume rm e2e_claude-data
docker compose -f docker/e2e/docker-compose.yml build --no-cache e2e-tests
```

### Tests skip with "E2E tests disabled"
Ensure API key is passed to the container:
```bash
# Verify key is set
echo "Key length: ${#ANTHROPIC_API_KEY}"

# Run with explicit key passing
docker run --rm --entrypoint bash \
  -e "ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY" \
  -w /workspace/plugin-source \
  e2e_e2e-tests \
  -c 'python -m pytest tests/e2e/ -v'
```
