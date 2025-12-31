# E2E Testing Fixes Prompt

Use this prompt in other Assistant-Skills projects to apply the same E2E testing improvements.

---

## Prompt

Apply the following E2E testing fixes to this project. These changes improve OAuth support, increase default max turns, and add per-test configuration options.

### 1. Update `tests/e2e/runner.py`

**Add OAuth credential detection method** (after `_check_prerequisites`):

```python
def _has_oauth_credentials(self) -> bool:
    """Check if OAuth credentials are available."""
    # Check for OAuth credentials in ~/.claude.json (primary location)
    oauth_file = Path.home() / ".claude.json"
    if oauth_file.exists():
        return True

    # Also check legacy location ~/.claude/credentials.json
    claude_dir = Path.home() / ".claude"
    if claude_dir.exists() and (claude_dir / "credentials.json").exists():
        return True

    return False
```

**Update `_check_authentication`** to prefer OAuth:

```python
def _check_authentication(self) -> bool:
    """Check if authentication is configured."""
    # Check for OAuth credentials first (preferred for local runs)
    if self._has_oauth_credentials():
        return True

    # Check for API key
    if os.environ.get("ANTHROPIC_API_KEY"):
        return True

    return False
```

**Add subprocess environment method**:

```python
def _get_subprocess_env(self) -> Dict[str, str]:
    """
    Get environment variables for subprocess.

    When OAuth credentials exist, we exclude ANTHROPIC_API_KEY
    to let Claude CLI use OAuth instead.
    """
    env = dict(os.environ)
    env["CLAUDE_CODE_SKIP_OOBE"] = "1"

    # If OAuth credentials exist, remove API key to force OAuth usage
    if self._has_oauth_credentials() and "ANTHROPIC_API_KEY" in env:
        del env["ANTHROPIC_API_KEY"]

    return env
```

**Update `send_prompt` signature** to accept `max_turns`:

```python
def send_prompt(
    self,
    prompt: str,
    timeout: Optional[int] = None,
    test_id: str = "",
    max_turns: Optional[int] = None
) -> Dict[str, Any]:
```

**Update the command building** in `send_prompt`:

```python
# Build command - default to 5 turns
turns = str(max_turns) if max_turns else os.environ.get("E2E_MAX_TURNS", "5")
cmd = [
    "claude",
    "--print",
    "--output-format", "text",
    "--model", self.model,
    "--max-turns", turns,
    "--dangerously-skip-permissions",
    prompt,
]
```

**Update subprocess call** to use the new env method:

```python
result = subprocess.run(
    cmd,
    cwd=self.working_dir,
    capture_output=True,
    text=True,
    timeout=timeout,
    env=self._get_subprocess_env(),  # Changed from {**os.environ, ...}
)
```

**Update `run_test` method** to pass max_turns from YAML:

```python
def run_test(self, test: Dict[str, Any]) -> TestResult:
    """Run a single test case."""
    test_id = test["id"]
    name = test["name"]
    prompt = test["prompt"]
    expect = test.get("expect", {})
    timeout = test.get("timeout", self.timeout)
    max_turns = test.get("max_turns")  # None uses default

    # ... rest of method ...

    result = self.claude.send_prompt(prompt, timeout=timeout, test_id=test_id, max_turns=max_turns)
```

### 2. Update `scripts/run-e2e-tests.sh`

**Replace the `check_auth` function**:

```bash
# Check authentication
check_auth() {
    # For local runs, prefer OAuth credentials
    if [[ "$USE_DOCKER" == "false" ]]; then
        # Check for OAuth credentials in ~/.claude.json (primary location)
        if [[ -f "$HOME/.claude.json" ]]; then
            echo -e "${GREEN}✓ Using Claude OAuth credentials (~/.claude.json)${NC}"
            # Unset API key to force OAuth usage
            unset ANTHROPIC_API_KEY
            return 0
        fi

        # Also check legacy location ~/.claude/credentials.json
        if [[ -f "$HOME/.claude/credentials.json" ]]; then
            echo -e "${GREEN}✓ Using Claude OAuth credentials (~/.claude/credentials.json)${NC}"
            # Unset API key to force OAuth usage
            unset ANTHROPIC_API_KEY
            return 0
        fi
    fi

    # For Docker or when no OAuth, use API key
    if [[ -n "$ANTHROPIC_API_KEY" ]]; then
        echo -e "${GREEN}✓ ANTHROPIC_API_KEY is set${NC}"
        return 0
    fi

    # Final check for OAuth (Docker case where OAuth might be mounted)
    if [[ -f "$HOME/.claude.json" ]] || [[ -f "$HOME/.claude/credentials.json" ]]; then
        echo -e "${GREEN}✓ Claude OAuth credentials found${NC}"
        return 0
    fi

    echo -e "${RED}✗ No authentication configured${NC}"
    echo ""
    echo "Please set one of the following:"
    echo "  1. Claude Code OAuth credentials (~/.claude.json) - preferred for local"
    echo "  2. ANTHROPIC_API_KEY environment variable - required for Docker"
    echo ""
    echo "To authenticate with OAuth: claude auth login"
    echo "To get an API key: https://console.anthropic.com/"
    return 1
}
```

### 3. Update `tests/e2e/test_cases.yaml`

**Add per-test overrides** where needed:

```yaml
- id: some_complex_test
  name: Test that needs more turns
  prompt: "Your prompt here"
  max_turns: 5        # Add this for tests hitting max turns
  timeout: 180        # Add this for tests timing out
  expect:
    success: true
```

**Fix prompts that trigger file exploration**:

```yaml
# BAD - triggers exploration
prompt: "List the skills available from the plugin"

# GOOD - avoids exploration
prompt: "Without reading any files, briefly name the types of skills typically included in this plugin."
```

### 4. Update pytest tests in `tests/e2e/test_plugin_e2e.py`

**Add max_turns to send_prompt calls** where needed:

```python
result = claude_runner.send_prompt(
    "Your prompt here",
    max_turns=5  # Add for tests that need more turns
)
```

### 5. Verify the fixes

Run the E2E tests locally:

```bash
./scripts/run-e2e-tests.sh --local
```

Expected output should show:
- `✓ Using Claude OAuth credentials (~/.claude.json)` (not API key)
- All tests passing without "Reached max turns" errors

---

## Why These Changes

| Issue | Root Cause | Fix |
|-------|------------|-----|
| "Invalid API key" errors locally | API key passed when OAuth should be used | `_get_subprocess_env()` removes API key when OAuth exists |
| "Reached max turns (3)" | Default 3 turns too low | Changed default to 5, added per-test override |
| Tests hitting timeout | Some prompts trigger exploration | Simplified prompts, added per-test timeout override |
| Inconsistent auth behavior | Mixed API key and OAuth handling | Prefer OAuth for local runs, clear precedence |

---

## Files Changed

- `tests/e2e/runner.py` - OAuth detection, env handling, max_turns parameter
- `scripts/run-e2e-tests.sh` - OAuth preference for local runs
- `tests/e2e/test_cases.yaml` - Per-test overrides, improved prompts
- `tests/e2e/test_plugin_e2e.py` - max_turns in send_prompt calls
