# TDD Workflow Prompt

## Purpose

Guide the complete Test-Driven Development workflow for implementing skill scripts.

## Prerequisites

- Skill directory structure created
- Shared library implemented
- Understanding of the API endpoint to implement

## Placeholders

- `{{TOPIC}}` - Lowercase prefix
- `{{SKILL_NAME}}` - Skill name
- `{{SCRIPT_NAME}}` - Script being implemented (e.g., "list_issues")
- `{{API_ENDPOINT}}` - API endpoint the script will call

---

## Prompt

```
Implement {{SCRIPT_NAME}}.py for {{TOPIC}}-{{SKILL_NAME}} using TDD.

**API Endpoint:** {{API_ENDPOINT}}

Follow the strict TDD workflow:

## Phase 1: Write Failing Tests First

Before writing any implementation, create comprehensive tests in:
`.claude/skills/{{TOPIC}}-{{SKILL_NAME}}/tests/test_{{SCRIPT_NAME}}.py`

### Test Categories to Cover:

1. **Happy Path Tests**
   - Valid input returns expected output
   - Pagination works correctly (if applicable)
   - Different output formats (text, json)

2. **Input Validation Tests**
   - Missing required arguments
   - Invalid argument formats
   - Edge cases (empty values, special characters)

3. **API Response Tests**
   - Successful response handling
   - Empty results handling
   - Partial data handling

4. **Error Handling Tests**
   - 401 Unauthorized
   - 403 Forbidden
   - 404 Not Found
   - 429 Rate Limited
   - 500 Server Error
   - Network errors

5. **Output Format Tests**
   - Text format is readable
   - JSON format is valid
   - Table format aligns correctly

### Test Structure:

```python
import pytest
from unittest.mock import patch, MagicMock

class TestListResources:
    """Tests for {{SCRIPT_NAME}}.py"""

    # Happy path tests
    def test_returns_resources_on_success(self):
        """Should return formatted list of resources"""
        pass  # Implement test

    def test_handles_empty_results(self):
        """Should handle empty result set gracefully"""
        pass

    def test_respects_limit_parameter(self):
        """Should limit results to specified count"""
        pass

    # Input validation tests
    def test_validates_required_arguments(self):
        """Should error on missing required args"""
        pass

    def test_validates_argument_format(self):
        """Should error on invalid format"""
        pass

    # Error handling tests
    def test_handles_401_unauthorized(self):
        """Should show auth error with troubleshooting"""
        pass

    def test_handles_404_not_found(self):
        """Should show not found error"""
        pass

    def test_handles_429_rate_limit(self):
        """Should indicate rate limiting"""
        pass

    # Output format tests
    def test_json_output_is_valid(self):
        """Should produce valid JSON when --output json"""
        pass

    def test_text_output_is_readable(self):
        """Should produce human-readable text output"""
        pass
```

## Phase 2: Verify Tests Fail

Run the tests - they MUST fail (no implementation yet):

```bash
pytest .claude/skills/{{TOPIC}}-{{SKILL_NAME}}/tests/test_{{SCRIPT_NAME}}.py -v
```

Expected: All tests fail with ImportError or NotImplementedError.

## Phase 3: Commit Failing Tests

```bash
git add .claude/skills/{{TOPIC}}-{{SKILL_NAME}}/tests/test_{{SCRIPT_NAME}}.py
git commit -m "test({{TOPIC}}-{{SKILL_NAME}}): add failing tests for {{SCRIPT_NAME}}"
```

## Phase 4: Implement Minimum Code to Pass

Now implement {{SCRIPT_NAME}}.py with just enough code to pass tests:
- Import shared library
- Parse arguments
- Validate inputs
- Make API call
- Format output
- Handle errors

Use the standard script template.

## Phase 5: Verify Tests Pass

```bash
pytest .claude/skills/{{TOPIC}}-{{SKILL_NAME}}/tests/test_{{SCRIPT_NAME}}.py -v
```

Expected: All tests pass.

## Phase 6: Commit Implementation

```bash
git add .claude/skills/{{TOPIC}}-{{SKILL_NAME}}/scripts/{{SCRIPT_NAME}}.py
git commit -m "feat({{TOPIC}}-{{SKILL_NAME}}): implement {{SCRIPT_NAME}}.py (N/N tests passing)"
```

Include the test count (e.g., "12/12 tests passing").

## Phase 7: Run Regression Suite

Before moving to next script, run ALL tests:

```bash
pytest .claude/skills/ -v
```

All tests must pass. If any fail:
1. Fix the regression
2. Commit the fix
3. Re-run regression

## Phase 8: Refactor (Optional)

If code needs cleanup:
1. Refactor
2. Run tests to verify behavior unchanged
3. Commit with refactor type

```bash
git commit -m "refactor({{TOPIC}}-{{SKILL_NAME}}): improve {{SCRIPT_NAME}} error messages"
```

## Summary

| Step | Action | Verification |
|------|--------|--------------|
| 1 | Write tests | Tests defined |
| 2 | Run tests | All fail |
| 3 | Commit tests | `test(...)` commit |
| 4 | Implement | Code written |
| 5 | Run tests | All pass |
| 6 | Commit impl | `feat(...)` commit |
| 7 | Regression | All project tests pass |
| 8 | Refactor | (optional) cleanup |

Repeat for each script in the skill.
```

---

## Expected Outputs

1. **Test file** with comprehensive test cases
2. **Implementation** that passes all tests
3. **Two commits**: failing tests, then passing implementation

---

## Test Coverage Targets

| Category | Target |
|----------|--------|
| Unit tests | 80%+ line coverage |
| Happy path | 100% |
| Error handling | All error types tested |
| Edge cases | Empty, null, invalid inputs |

---

## Verification Commands

```bash
# Run specific test file
pytest .claude/skills/{{TOPIC}}-{{SKILL_NAME}}/tests/test_{{SCRIPT_NAME}}.py -v

# Run with coverage
pytest .claude/skills/{{TOPIC}}-{{SKILL_NAME}}/tests/ --cov=.claude/skills/{{TOPIC}}-{{SKILL_NAME}}/scripts -v

# Run skill tests only
pytest .claude/skills/{{TOPIC}}-{{SKILL_NAME}}/tests/ -v

# Run all project tests (regression)
pytest .claude/skills/ -v
```
