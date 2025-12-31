# Implementation Plan Template

## Purpose

Create a detailed TDD implementation plan with phases, milestones, test targets, and regression checkpoints.

## Prerequisites

- Completed architecture design
- Skill inventory with scripts identified
- Shared library components defined
- Test strategy determined

## Placeholders

- `{{PROJECT_NAME}}` - Full project name
- `{{TOPIC}}` - Lowercase skill prefix
- `{{DATE}}` - Plan creation date
- `{{TARGET_DATE}}` - Target completion date

---

# {{PROJECT_NAME}} Implementation Plan

**Created:** {{DATE}}
**Target Completion:** {{TARGET_DATE}}
**Status:** 🔴 Not Started | 🟡 In Progress | 🟢 Complete

---

## Overview

| Metric | Target |
|--------|--------|
| Total Skills | <!-- number --> |
| Total Scripts | <!-- number --> |
| Unit Test Coverage | 80%+ |
| Integration Test Coverage | 100% happy path |
| Phases | <!-- number --> |

---

## Phase 1: Foundation

**Goal:** Shared library and configuration working
**Status:** 🔴 Not Started
**Test Target:** 100% unit coverage on shared lib

### 1.1 Project Scaffolding

| Task | Status | Tests | Commit |
|------|--------|-------|--------|
| Create directory structure | ⬜ | N/A | |
| Create CLAUDE.md | ⬜ | N/A | |
| Create README.md | ⬜ | N/A | |
| Create settings.json template | ⬜ | N/A | |
| Create pyproject.toml | ⬜ | N/A | |

### 1.2 Shared Library - Config Manager

| Task | Status | Tests | Commit |
|------|--------|-------|--------|
| Write failing tests for config_manager.py | ⬜ | 0/N | |
| Implement config loading from env vars | ⬜ | N/N | |
| Implement config loading from settings.json | ⬜ | N/N | |
| Implement profile switching | ⬜ | N/N | |
| Implement config merging | ⬜ | N/N | |

### 1.3 Shared Library - HTTP Client

| Task | Status | Tests | Commit |
|------|--------|-------|--------|
| Write failing tests for client.py | ⬜ | 0/N | |
| Implement basic GET/POST/PUT/DELETE | ⬜ | N/N | |
| Implement authentication handling | ⬜ | N/N | |
| Implement retry with exponential backoff | ⬜ | N/N | |
| Implement rate limit handling | ⬜ | N/N | |
| Implement pagination helper | ⬜ | N/N | |

### 1.4 Shared Library - Error Handler

| Task | Status | Tests | Commit |
|------|--------|-------|--------|
| Write failing tests for error_handler.py | ⬜ | 0/N | |
| Implement exception hierarchy | ⬜ | N/N | |
| Implement HTTP status code mapping | ⬜ | N/N | |
| Implement error message formatting | ⬜ | N/N | |

### 1.5 Shared Library - Validators

| Task | Status | Tests | Commit |
|------|--------|-------|--------|
| Write failing tests for validators.py | ⬜ | 0/N | |
| Implement input validation functions | ⬜ | N/N | |

### 1.6 Shared Library - Formatters

| Task | Status | Tests | Commit |
|------|--------|-------|--------|
| Write failing tests for formatters.py | ⬜ | 0/N | |
| Implement table formatting | ⬜ | N/N | |
| Implement JSON formatting | ⬜ | N/N | |
| Implement success/error output | ⬜ | N/N | |

### Phase 1 Checkpoint

- [ ] All shared library tests passing
- [ ] Coverage report shows 80%+ for shared lib
- [ ] Manual verification of config loading
- [ ] Manual verification of API connectivity
- [ ] Commit: `feat(shared): implement shared library foundation`

---

## Phase 2: Core Skill - {{TOPIC}}-{skill1}

**Goal:** First skill fully functional with TDD
**Status:** 🔴 Not Started
**Test Target:** 80% unit, 100% happy path integration

### 2.1 Skill Structure

| Task | Status | Tests | Commit |
|------|--------|-------|--------|
| Create skill directory structure | ⬜ | N/A | |
| Create SKILL.md (Level 1-2) | ⬜ | N/A | |

### 2.2 Script: list_{resource}.py

| Task | Status | Tests | Commit |
|------|--------|-------|--------|
| Write failing tests | ⬜ | 0/N | `test({{TOPIC}}-{skill1}): add failing tests for list_{resource}` |
| Implement script | ⬜ | N/N | `feat({{TOPIC}}-{skill1}): implement list_{resource}.py (N/N passing)` |

### 2.3 Script: get_{resource}.py

| Task | Status | Tests | Commit |
|------|--------|-------|--------|
| Write failing tests | ⬜ | 0/N | |
| Implement script | ⬜ | N/N | |

### 2.4 Script: create_{resource}.py

| Task | Status | Tests | Commit |
|------|--------|-------|--------|
| Write failing tests | ⬜ | 0/N | |
| Implement script | ⬜ | N/N | |

### 2.5 Script: update_{resource}.py

| Task | Status | Tests | Commit |
|------|--------|-------|--------|
| Write failing tests | ⬜ | 0/N | |
| Implement script | ⬜ | N/N | |

### 2.6 Script: delete_{resource}.py

| Task | Status | Tests | Commit |
|------|--------|-------|--------|
| Write failing tests | ⬜ | 0/N | |
| Implement script | ⬜ | N/N | |

### 2.7 Live Integration Tests

| Task | Status | Tests | Commit |
|------|--------|-------|--------|
| Create test fixtures | ⬜ | N/A | |
| Implement lifecycle test | ⬜ | N/N | |

### 2.8 Documentation

| Task | Status | Commit |
|------|--------|--------|
| Complete SKILL.md Level 3 docs | ⬜ | |
| Add examples to SKILL.md | ⬜ | |

### Phase 2 Regression Checkpoint

- [ ] All Phase 1 tests still passing
- [ ] All Phase 2 tests passing
- [ ] Run: `pytest .claude/skills/ -v`
- [ ] Coverage meets targets
- [ ] Update this plan with actual test counts

---

## Phase 3: Additional Skills

**Goal:** Implement remaining skills with TDD
**Status:** 🔴 Not Started

<!-- Repeat the Phase 2 pattern for each skill -->

### 3.1 Skill: {{TOPIC}}-{skill2}

| Script | Tests Written | Tests Passing | Commit |
|--------|---------------|---------------|--------|
| script1.py | ⬜ 0/N | ⬜ 0/N | |
| script2.py | ⬜ 0/N | ⬜ 0/N | |
| script3.py | ⬜ 0/N | ⬜ 0/N | |

### 3.2 Skill: {{TOPIC}}-{skill3}

| Script | Tests Written | Tests Passing | Commit |
|--------|---------------|---------------|--------|
| script1.py | ⬜ 0/N | ⬜ 0/N | |
| script2.py | ⬜ 0/N | ⬜ 0/N | |

### Phase 3 Regression Checkpoint

- [ ] All Phase 1-2 tests still passing
- [ ] All Phase 3 tests passing
- [ ] Full regression: `pytest .claude/skills/ -v`

---

## Phase 4: Router Skill

**Goal:** Meta-skill routes to all other skills
**Status:** 🔴 Not Started

### 4.1 Router Implementation

| Task | Status | Commit |
|------|--------|--------|
| Create {{TOPIC}}-assistant structure | ⬜ | |
| Implement routing table | ⬜ | |
| Create SKILL.md with all triggers | ⬜ | |
| Document multi-skill operations | ⬜ | |

### 4.2 Router Verification

| Test | Status |
|------|--------|
| Route to skill1 | ⬜ |
| Route to skill2 | ⬜ |
| Route to skill3 | ⬜ |
| Multi-skill operation | ⬜ |
| Disambiguation works | ⬜ |

### Phase 4 Regression Checkpoint

- [ ] All previous tests passing
- [ ] Router correctly invokes all skills
- [ ] Full regression: `pytest .claude/skills/ -v`

---

## Phase 5: Documentation & Polish

**Goal:** Production-ready documentation
**Status:** 🔴 Not Started

### 5.1 Documentation

| Document | Status |
|----------|--------|
| CLAUDE.md complete | ⬜ |
| README.md polished | ⬜ |
| All SKILL.md files reviewed | ⬜ |
| TROUBLESHOOTING.md created | ⬜ |
| QUICK-REFERENCE.md created | ⬜ |

### 5.2 Final Verification

| Check | Status |
|-------|--------|
| All scripts support --help | ⬜ |
| All scripts support --profile | ⬜ |
| All error messages helpful | ⬜ |
| No hardcoded credentials | ⬜ |
| .gitignore complete | ⬜ |

### 5.3 CI/CD

| Task | Status |
|------|--------|
| GitHub Actions test workflow | ⬜ |
| Coverage reporting | ⬜ |
| Release workflow | ⬜ |

### Phase 5 Checkpoint

- [ ] Full test suite: `pytest .claude/skills/ -v --cov`
- [ ] All documentation reviewed
- [ ] Manual end-to-end testing
- [ ] Ready for release

---

## Progress Tracking

### Test Counts by Phase

| Phase | Unit Tests | Integration Tests | Coverage |
|-------|------------|-------------------|----------|
| Phase 1 | 0/__ | 0/__ | __% |
| Phase 2 | 0/__ | 0/__ | __% |
| Phase 3 | 0/__ | 0/__ | __% |
| Phase 4 | N/A | 0/__ | N/A |
| Phase 5 | N/A | N/A | __% |
| **Total** | **0/__** | **0/__** | **__%** |

### Commit Log

<!-- Update as commits are made -->

| Date | Commit | Type | Tests |
|------|--------|------|-------|
| | | | |

---

## Notes & Decisions

<!-- Document any decisions, changes, or issues during implementation -->

### Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| | | |

### Issues Encountered

| Issue | Resolution |
|-------|------------|
| | |

---

## Completion Criteria

Before marking complete:

- [ ] All phases completed
- [ ] All regression checkpoints passed
- [ ] Test coverage meets targets (80% unit, 100% happy path)
- [ ] Documentation complete and reviewed
- [ ] CI/CD configured and passing
- [ ] Manual testing performed
- [ ] Implementation plan reflects actual state
