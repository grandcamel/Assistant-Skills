# TDD Commit Workflow

Complete guide to the two-commit pattern for Test-Driven Development.

---

## Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                     TDD TWO-COMMIT PATTERN                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────────┐        ┌──────────────────┐                   │
│  │  COMMIT 1:       │        │  COMMIT 2:       │                   │
│  │  Failing Tests   │───────▶│  Implementation  │                   │
│  │                  │        │                  │                   │
│  │  test(scope):    │        │  feat(scope):    │                   │
│  │  add failing     │        │  implement X     │                   │
│  │  tests for X     │        │  (N/N passing)   │                   │
│  └──────────────────┘        └──────────────────┘                   │
│                                                                      │
│  Tests: ALL FAIL             Tests: ALL PASS                        │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Why Two Commits?

1. **Clear History**: Separates test specification from implementation
2. **Reviewability**: Reviewers see what behavior was defined vs. how it was built
3. **Revertability**: Can revert implementation without losing test spec
4. **Documentation**: Tests commit documents expected behavior
5. **Accountability**: Shows TDD was actually followed

---

## Workflow Steps

### Step 1: Write Tests

Write comprehensive tests for the feature before any implementation.

```python
# test_create_issue.py

def test_creates_issue_with_required_fields():
    """Should create issue with summary and project."""
    pass  # Will fail

def test_validates_project_key():
    """Should reject invalid project key format."""
    pass  # Will fail

def test_returns_created_issue_id():
    """Should return the new issue's ID."""
    pass  # Will fail
```

### Step 2: Verify Tests Fail

```bash
$ pytest tests/test_create_issue.py -v

test_create_issue.py::test_creates_issue_with_required_fields FAILED
test_create_issue.py::test_validates_project_key FAILED
test_create_issue.py::test_returns_created_issue_id FAILED

3 failed
```

All tests MUST fail. If any pass, you may have existing code or the test isn't testing anything new.

### Step 3: Commit Failing Tests

```bash
$ git add tests/test_create_issue.py
$ git commit -m "test(jira-issue): add failing tests for create_issue

Tests define expected behavior:
- Creates issue with summary and project key
- Validates project key format (PROJECT-123)
- Returns the created issue ID

All tests currently fail - no implementation yet."
```

### Step 4: Implement Minimum Code

Write just enough code to pass the tests. No more, no less.

```python
# create_issue.py - Implement only what tests require
```

### Step 5: Verify Tests Pass

```bash
$ pytest tests/test_create_issue.py -v

test_create_issue.py::test_creates_issue_with_required_fields PASSED
test_create_issue.py::test_validates_project_key PASSED
test_create_issue.py::test_returns_created_issue_id PASSED

3 passed
```

All tests MUST pass.

### Step 6: Commit Implementation

```bash
$ git add scripts/create_issue.py
$ git commit -m "feat(jira-issue): implement create_issue.py (3/3 tests passing)

Implements issue creation with:
- Required fields: summary, project_key
- Project key validation (format: PROJECT-123)
- Returns created issue ID

All tests pass."
```

### Step 7: Run Regression

Before moving to the next feature:

```bash
$ pytest .claude/skills/ -v

# ALL tests across the project must pass
```

If any tests fail, fix them before continuing.

---

## Commit Message Examples

### Failing Tests Commit

```
test(jira-search): add failing tests for jql_validate

Tests define JQL validation behavior:
- Accepts valid JQL syntax
- Rejects malformed queries
- Returns parse errors with line/column
- Suggests corrections for common mistakes

6 tests defined, all currently failing.
```

### Implementation Commit

```
feat(jira-search): implement jql_validate.py (6/6 tests passing)

Adds JQL validation using JIRA's parse API:
- POST to /rest/api/3/jql/parse
- Extracts structured errors from response
- Formats suggestions for user display

Uses shared library for HTTP client and error handling.
```

---

## When to Deviate

### Bug Fixes

For bug fixes, you might add tests and fix in one commit:

```
fix(client): handle empty response body

Adds test for empty response scenario and fixes the bug.

Previously raised JSONDecodeError. Now returns empty dict.

Fixes #123
```

### Refactoring

No new tests needed for pure refactoring:

```
refactor(validators): extract common patterns

No functional changes. Tests still pass.
```

### Documentation

Tests typically not needed:

```
docs(README): add installation troubleshooting section
```

---

## Common Mistakes

### Mistake 1: Implementation Before Tests

❌ **Wrong:**
```
feat(skill): implement feature X  # No tests exist
test(skill): add tests for feature X  # Added after
```

✅ **Correct:**
```
test(skill): add failing tests for feature X
feat(skill): implement feature X (N/N passing)
```

### Mistake 2: Tests That Pass Initially

❌ **Wrong:**
```
test(skill): add tests for feature X
# Tests pass because code already exists!
```

✅ **Correct:**
Write tests that ONLY pass with new code.

### Mistake 3: Missing Test Count

❌ **Wrong:**
```
feat(skill): implement feature X
```

✅ **Correct:**
```
feat(skill): implement feature X (12/12 tests passing)
```

### Mistake 4: Skipping Regression

❌ **Wrong:**
```
# Commit new feature
# Move to next feature without running full test suite
```

✅ **Correct:**
```bash
# After every implementation commit:
pytest .claude/skills/ -v
# Only proceed if ALL tests pass
```

---

## Test Count Format

Always include test counts in implementation commits:

| Format | When to Use |
|--------|-------------|
| `(5/5 tests passing)` | All tests for this feature pass |
| `(5/5 unit, 3/3 integration)` | When both types exist |
| `(12/15 tests passing)` | NEVER - fix failing tests first |

---

## Regression Checkpoints

Run full test suite at these points:

1. **After each implementation commit**
2. **Before starting a new skill**
3. **After any refactoring**
4. **Before merging to main**
5. **After resolving merge conflicts**

```bash
# Full regression
pytest .claude/skills/ -v

# With coverage
pytest .claude/skills/ --cov=.claude/skills/shared/scripts/lib -v
```

---

## Checklist

### Before Failing Tests Commit

- [ ] Tests are comprehensive (happy path, errors, edge cases)
- [ ] Tests use descriptive names
- [ ] All tests actually fail
- [ ] Commit message lists what tests cover

### Before Implementation Commit

- [ ] All tests pass
- [ ] No extra code beyond what tests require
- [ ] Test count is in commit message
- [ ] Regression suite passes

### Before Moving to Next Feature

- [ ] Both commits are complete
- [ ] Full regression passes
- [ ] Implementation plan updated

---

## Quick Reference

```bash
# 1. Write tests
vim tests/test_feature.py

# 2. Verify failure
pytest tests/test_feature.py -v  # All fail

# 3. Commit tests
git add tests/test_feature.py
git commit -m "test(scope): add failing tests for feature"

# 4. Implement
vim scripts/feature.py

# 5. Verify pass
pytest tests/test_feature.py -v  # All pass

# 6. Commit implementation
git add scripts/feature.py
git commit -m "feat(scope): implement feature (N/N passing)"

# 7. Regression
pytest .claude/skills/ -v  # All pass

# 8. Repeat for next feature
```
