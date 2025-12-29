# Conventional Commits Reference

Quick reference for [Conventional Commits](https://www.conventionalcommits.org/) in Assistant Skills projects.

---

## Commit Message Format

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

---

## Types

| Type | Description | Example |
|------|-------------|---------|
| `feat` | New feature or functionality | `feat(jira-issue): add bulk create support` |
| `fix` | Bug fix | `fix(shared): correct retry backoff calculation` |
| `docs` | Documentation only | `docs: update README quick start` |
| `test` | Adding or updating tests | `test(jira-search): add JQL validation tests` |
| `refactor` | Code change without feature/fix | `refactor(client): simplify error handling` |
| `style` | Formatting, no logic change | `style: fix indentation in scripts` |
| `perf` | Performance improvement | `perf(search): cache field metadata` |
| `build` | Build system changes | `build: update pytest to 7.4` |
| `ci` | CI configuration | `ci: add coverage reporting` |
| `chore` | Other maintenance | `chore: clean up unused imports` |

---

## Scopes

Use the skill or component name as scope:

```
feat(jira-issue): ...       # Skill-specific
fix(shared): ...            # Shared library
test(jira-search): ...      # Test changes
docs(README): ...           # Documentation
ci(workflows): ...          # CI/CD
```

### Multiple Scopes

For changes spanning multiple areas:

```
feat(jira-issue,jira-search): add common filter parameter
```

---

## Breaking Changes

Indicate breaking changes with `!` after type/scope:

```
feat(config)!: change settings format to YAML

BREAKING CHANGE: settings.json is now settings.yaml
Users must migrate their configuration files.
```

---

## Description Guidelines

- Use imperative mood: "add" not "added" or "adds"
- Lowercase first letter
- No period at end
- Keep under 72 characters

### Good Examples

```
feat(jira-issue): add support for custom fields
fix(client): handle empty response body
docs: add troubleshooting section for auth errors
test(jira-agile): add sprint creation tests
```

### Bad Examples

```
feat(jira-issue): Added support for custom fields.  # Past tense, period
Fix: authentication bug                             # Missing scope, capitalized
Updated README                                      # No type, past tense
```

---

## Body Guidelines

- Explain what and why, not how
- Wrap at 72 characters
- Separate from description with blank line

```
fix(client): handle rate limit with exponential backoff

The previous implementation used fixed delays which still triggered
rate limits under heavy load. This change implements exponential
backoff starting at 2 seconds with a maximum of 60 seconds.

Fixes #123
```

---

## Footer Guidelines

### Issue References

```
Fixes #123
Closes #456
Refs: PROJ-789
```

### Co-authors

```
Co-authored-by: Name <email@example.com>
```

### Breaking Change Details

```
BREAKING CHANGE: Configuration format changed from JSON to YAML.

To migrate:
1. Rename settings.json to settings.yaml
2. Convert JSON syntax to YAML
3. Update any scripts that read the file
```

---

## TDD Commit Pattern

For Test-Driven Development, use two commits per feature:

### 1. Failing Tests Commit

```
test(skill-name): add failing tests for feature_name

Tests define expected behavior for feature_name:
- Test valid input handling
- Test error conditions
- Test edge cases

All tests currently fail (no implementation yet).
```

### 2. Implementation Commit

```
feat(skill-name): implement feature_name (12/12 tests passing)

Implements minimum code to pass all tests:
- Added script.py with core logic
- Integrated with shared library
- Added --help documentation

All tests now pass.
```

---

## Common Commit Patterns

### Adding a New Script

```
test(jira-issue): add failing tests for create_issue

feat(jira-issue): implement create_issue.py (8/8 tests passing)
```

### Fixing a Bug

```
fix(shared): handle empty API response in client.get()

Previously, an empty response body would raise JSONDecodeError.
Now returns empty dict when response has no content.

Fixes #42
```

### Adding Documentation

```
docs(jira-admin): add workflow guide for permission setup
```

### Refactoring

```
refactor(validators): extract common patterns to base class

No functional changes. Reduces duplication across validation
functions.
```

### Updating Dependencies

```
build(deps): update requests to 2.31.0

Security fix for CVE-2023-XXXXX
```

---

## Commit Checklist

Before committing:

- [ ] Type is appropriate for the change
- [ ] Scope identifies the affected area
- [ ] Description is imperative and clear
- [ ] Body explains why (if not obvious)
- [ ] Breaking changes are marked with `!`
- [ ] Issue references are included (if applicable)
- [ ] Tests pass (for implementation commits)
- [ ] Test count included (for TDD commits)

---

## Quick Reference Card

```
Types:     feat | fix | docs | test | refactor | style | perf | build | ci | chore
Breaking:  feat(scope)!: description
Footer:    Fixes #123 | BREAKING CHANGE: details | Co-authored-by: Name <email>

TDD Pattern:
  1. test(scope): add failing tests for X
  2. feat(scope): implement X (N/N tests passing)
```
