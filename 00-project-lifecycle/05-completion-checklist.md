# Completion Checklist

## Purpose

Verify all aspects of the project are complete before release.

## Prerequisites

- All implementation phases completed
- All tests passing
- Documentation drafted

---

# {{PROJECT_NAME}} Completion Checklist

**Date:** {{DATE}}
**Version:** {{VERSION}}

---

## 1. Code Quality

### 1.1 All Scripts

- [ ] Every script has `--help` with examples
- [ ] Every script has `--profile` support
- [ ] Every script uses shared library imports
- [ ] Every script follows error handling patterns
- [ ] Every script is executable (`chmod +x`)
- [ ] Every script has proper shebang (`#!/usr/bin/env python3`)
- [ ] No hardcoded credentials or URLs
- [ ] No TODO comments left unresolved
- [ ] Consistent code style across all scripts

### 1.2 Shared Library

- [ ] All modules have docstrings
- [ ] Exception hierarchy complete
- [ ] Config merging tested (env > local > settings)
- [ ] HTTP client handles all error codes
- [ ] Retry logic tested with mocks
- [ ] Validators cover all input types
- [ ] Formatters produce clean output

### 1.3 Skills

- [ ] Each skill is self-contained
- [ ] Each skill has clear boundaries
- [ ] No circular dependencies between skills
- [ ] Router skill routes to all other skills
- [ ] Multi-skill operations documented

---

## 2. Testing

### 2.1 Unit Tests

- [ ] Coverage >= 80% for shared library
- [ ] Coverage >= 80% for each skill
- [ ] All edge cases covered
- [ ] All error paths covered
- [ ] Mock fixtures well-organized
- [ ] Tests run in isolation (no shared state)

### 2.2 Integration Tests

- [ ] Happy path tested for each script
- [ ] Lifecycle tests (create → read → update → delete)
- [ ] Tests use test/sandbox environment
- [ ] Cleanup fixtures work correctly
- [ ] Tests can run independently
- [ ] Profile parameter works

### 2.3 Test Execution

- [ ] `pytest .claude/skills/ -v` passes
- [ ] `pytest --cov` shows target coverage
- [ ] No flaky tests
- [ ] Tests run in reasonable time (<5 min)

---

## 3. Documentation

### 3.1 SKILL.md Files

- [ ] Every skill has SKILL.md
- [ ] Level 1: Frontmatter complete (name, description, triggers)
- [ ] Level 2: Quick reference tables present
- [ ] Level 3: Deep docs linked (if applicable)
- [ ] Examples are realistic and tested
- [ ] All scripts documented

### 3.2 CLAUDE.md

- [ ] Project overview complete
- [ ] Architecture documented
- [ ] Shared library patterns explained
- [ ] Configuration system documented
- [ ] Error handling strategy explained
- [ ] Git commit guidelines included
- [ ] Testing instructions complete
- [ ] Adding new scripts guide present
- [ ] Adding new skills guide present

### 3.3 README.md

- [ ] Quick start section works
- [ ] Installation instructions accurate
- [ ] Configuration steps clear
- [ ] Example commands tested
- [ ] All skills listed with descriptions
- [ ] Contributing guidelines present
- [ ] License specified

### 3.4 Additional Docs

- [ ] TROUBLESHOOTING.md covers common issues
- [ ] QUICK-REFERENCE.md has all commands
- [ ] WORKFLOWS.md has step-by-step guides (if needed)
- [ ] API-specific docs present (if needed)

---

## 4. Configuration

### 4.1 Settings

- [ ] settings.json has sensible defaults
- [ ] config.schema.json validates correctly
- [ ] Profile structure documented
- [ ] Example configurations provided

### 4.2 Environment Variables

- [ ] All env vars documented
- [ ] Env vars have consistent naming
- [ ] Optional vs required marked
- [ ] No sensitive defaults

### 4.3 Security

- [ ] .gitignore includes settings.local.json
- [ ] .gitignore includes .env files
- [ ] No credentials in committed files
- [ ] HTTPS-only for API connections
- [ ] Token handling is secure

---

## 5. Project Structure

### 5.1 Directory Layout

- [ ] Consistent structure across skills
- [ ] Shared library in correct location
- [ ] Tests alongside or within skills
- [ ] Assets/templates organized
- [ ] No orphaned files

### 5.2 Python Project

- [ ] pyproject.toml correct
- [ ] requirements.txt accurate
- [ ] Python version specified
- [ ] Dependencies pinned (or range specified)

---

## 6. Version Control

### 6.1 Git

- [ ] All changes committed
- [ ] Commit messages follow conventions
- [ ] No large binary files committed
- [ ] .gitignore comprehensive
- [ ] Branches cleaned up

### 6.2 CI/CD

- [ ] GitHub Actions configured
- [ ] Tests run on PR/push
- [ ] Coverage reported
- [ ] Linting configured (optional)
- [ ] Release workflow ready (optional)

---

## 7. Final Verification

### 7.1 Fresh Clone Test

```bash
# Test that project works from fresh clone
git clone <repo> test-clone
cd test-clone
pip install -r .claude/skills/shared/scripts/lib/requirements.txt
export API_TOKEN="test-token"
export API_EMAIL="test@example.com"
export API_URL="https://api.example.com"
pytest .claude/skills/ -v
```

- [ ] Fresh clone builds successfully
- [ ] Tests pass on fresh clone
- [ ] No missing dependencies

### 7.2 Manual Testing

- [ ] Tested with real API credentials
- [ ] All major workflows tested manually
- [ ] Error messages are helpful
- [ ] Output formatting looks correct
- [ ] Performance acceptable

### 7.3 User Experience

- [ ] Clear what each skill does
- [ ] Natural language triggers work
- [ ] Error recovery is graceful
- [ ] Help is discoverable

---

## 8. Release Preparation

### 8.1 Version

- [ ] Version number set appropriately
- [ ] CHANGELOG updated
- [ ] Release notes drafted

### 8.2 Tagging

- [ ] Tag created for release
- [ ] Tag pushed to remote
- [ ] GitHub release created (if applicable)

---

## Sign-off

| Check | Verified By | Date |
|-------|-------------|------|
| Code Quality | | |
| Testing | | |
| Documentation | | |
| Configuration | | |
| Security | | |
| Final Verification | | |

**Release Approved:** ⬜ Yes / ⬜ No

**Notes:**
<!-- Any notes or exceptions -->
