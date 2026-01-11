# GitHub API GAP Analysis

**Project:** GitHub-Assistant-Skills
**Date:** 2024-01-15
**Status:** Approved

---

## Executive Summary

This analysis evaluates the GitHub REST API capabilities against the requirements for the GitHub Assistant Skills project.

**Key Findings:**
- Total API endpoints available: 200+
- Endpoints needed for MVP: 45
- Identified gaps/limitations: 3
- Recommended skills: 8

---

## 1. API Capability Inventory

### 1.1 Authentication

| Aspect | API Capability | Notes |
|--------|---------------|-------|
| **Method** | Personal Access Token (PAT), OAuth 2.0, GitHub App | PAT recommended for CLI |
| **Credential Location** | Authorization header | `Bearer {token}` format |
| **Token Refresh** | No (PAT doesn't expire unless set) | OAuth tokens expire |
| **Scopes Available** | repo, user, read:org, write:org, admin:org, etc. | Fine-grained available |
| **Multi-tenant Support** | Yes (via org context) | |

### 1.2 Core Resources

| Resource | Create | Read | Update | Delete | List | Search | Notes |
|----------|--------|------|--------|--------|------|--------|-------|
| Repositories | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | |
| Issues | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ | No delete, only close |
| Pull Requests | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ | No delete |
| Branches | ✅ | ✅ | ❌ | ✅ | ✅ | ❌ | No update, rename only |
| Commits | ❌ | ✅ | ❌ | ❌ | ✅ | ❌ | Read-only via API |
| Releases | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | |
| Actions | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | Workflows, runs |
| Organizations | ❌ | ✅ | ✅ | ❌ | ✅ | ❌ | Cannot create via API |

### 1.3 Advanced Operations

| Operation | Supported | Endpoint | Notes |
|-----------|-----------|----------|-------|
| Bulk Create | ❌ | N/A | Must loop |
| Bulk Update | ❌ | N/A | Must loop |
| Bulk Delete | ❌ | N/A | Must loop |
| Export | ⚠️ | Archive API | Limited to repo archives |
| Import | ⚠️ | Import API | Org-level only |
| Webhooks | ✅ | `/repos/{owner}/{repo}/hooks` | |

### 1.4 Rate Limits

| Limit Type | Value | Scope | Notes |
|------------|-------|-------|-------|
| Requests per hour | 5,000 | Per user (authenticated) | |
| Requests per hour | 60 | Per IP (unauthenticated) | |
| Search requests | 30/min | Per user | Separate limit |
| GraphQL points | 5,000 | Per hour | Point-based |

### 1.5 Pagination

| Aspect | Value |
|--------|-------|
| **Style** | Link header (rel=next) |
| **Default page size** | 30 |
| **Max page size** | 100 |
| **Total count provided** | Only for search results |

---

## 2. Feature-to-Endpoint Mapping

### 2.1 Desired Features

| Feature ID | Feature Description | Priority | Complexity |
|------------|---------------------|----------|------------|
| F001 | List and search repositories | High | Low |
| F002 | Issue CRUD operations | High | Medium |
| F003 | Pull request management | High | Medium |
| F004 | Branch operations | Medium | Low |
| F005 | Release management | Medium | Medium |
| F006 | Actions workflow control | Medium | High |
| F007 | Organization management | Low | Medium |
| F008 | Bulk issue operations | High | Medium |

### 2.2 Feature-to-Endpoint Matrix

| Feature ID | Required Endpoints | API Support | Gap? |
|------------|-------------------|-------------|------|
| F001 | `GET /user/repos`, `GET /search/repositories` | ✅ Full | No |
| F002 | `GET/POST/PATCH /repos/{o}/{r}/issues/{n}` | ✅ Full | No |
| F003 | `GET/POST/PATCH /repos/{o}/{r}/pulls/{n}` | ✅ Full | No |
| F004 | `GET/POST/DELETE /repos/{o}/{r}/branches/{b}` | ⚠️ Partial | Yes - no rename |
| F005 | `GET/POST/PATCH/DELETE /repos/{o}/{r}/releases` | ✅ Full | No |
| F006 | `GET/POST /repos/{o}/{r}/actions/workflows` | ✅ Full | No |
| F007 | `GET/PATCH /orgs/{org}` | ⚠️ Partial | Yes - no create |
| F008 | Multiple issue endpoints | ⚠️ Partial | Yes - no bulk API |

### 2.3 Gap Details

#### GAP-001: No Branch Rename API

- **Feature:** F004 - Branch operations
- **Required:** Rename branch via API
- **Available:** Create new + delete old
- **Workaround:** Create branch at same ref, delete old (loses protection rules)
- **Impact:** Minor - rarely needed
- **Recommendation:** Document limitation, implement as create+delete

#### GAP-002: Cannot Create Organizations

- **Feature:** F007 - Organization management
- **Required:** Create new organizations
- **Available:** Update and read only
- **Workaround:** None - must use web UI
- **Impact:** Low - rare operation
- **Recommendation:** Exclude from skill, document limitation

#### GAP-003: No Bulk Issue Operations

- **Feature:** F008 - Bulk issue operations
- **Required:** Update/close/label 100+ issues at once
- **Available:** Single-issue endpoints only
- **Workaround:** Parallel requests with rate limit awareness
- **Impact:** Medium - slower bulk operations
- **Recommendation:** Implement with batching, concurrency, and progress reporting

---

## 3. Skill Architecture Mapping

### 3.1 Proposed Skills

| Skill Name | Resources | Key Operations | Endpoints Used |
|------------|-----------|----------------|----------------|
| `github-repo` | Repositories | CRUD, fork, transfer | 8 endpoints |
| `github-issue` | Issues, Labels, Milestones | CRUD, assign, label | 12 endpoints |
| `github-pr` | Pull Requests, Reviews | CRUD, merge, review | 10 endpoints |
| `github-branch` | Branches, Protection | CRUD, protect | 6 endpoints |
| `github-release` | Releases, Assets | CRUD, upload | 8 endpoints |
| `github-actions` | Workflows, Runs | Trigger, cancel, view | 10 endpoints |
| `github-search` | All resources | Search, filter | 5 endpoints |
| `github-assistant` | N/A | Router | N/A |

### 3.2 Shared Library Requirements

| Component | Purpose | Complexity |
|-----------|---------|------------|
| HTTP Client | Retry, rate limiting, Link header pagination | High |
| Config Manager | Multi-profile, env vars, GitHub Enterprise | Medium |
| Error Handler | Status code mapping, OAuth errors | Medium |
| Validators | Repo names, issue numbers, SHAs | Low |
| Formatters | Markdown output, tables, JSON | Low |

---

## 4. Limitations & Constraints

### 4.1 API Limitations

| Limitation | Impact | Mitigation |
|------------|--------|------------|
| 5,000 req/hour rate limit | May hit during bulk ops | Implement caching, batching |
| 30 search req/min | Slow bulk search | Cache results, rate limit |
| No issue delete | Cannot fully remove | Use close + lock |
| GraphQL complexity | Large queries fail | Pagination, smaller queries |

### 4.2 Implementation Constraints

| Constraint | Reason | Approach |
|------------|--------|----------|
| Python 3.8+ | Type hints, pathlib | Document requirement |
| No `gh` CLI dep | Portability | Pure Python implementation |
| Link header parsing | Pagination | Implement in client |

---

## 5. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Rate limit exceeded | Medium | Medium | Exponential backoff, caching |
| API deprecation | Low | High | Monitor changelog, use stable endpoints |
| Token scope issues | Medium | Low | Document required scopes |
| Breaking API changes | Low | High | Integration tests, alerts |

---

## 6. Recommendations

### 6.1 MVP Scope

**Include in MVP:**
1. github-repo (repository CRUD)
2. github-issue (issue management)
3. github-pr (pull request management)
4. github-search (unified search)
5. github-assistant (router)

**Defer to v2:**
1. github-actions (workflow control)
2. github-release (release management)
3. github-branch (branch/protection management)

### 6.2 Implementation Order

1. **Phase 1:** Shared library + github-repo (foundation)
2. **Phase 2:** github-issue + github-pr (core workflows)
3. **Phase 3:** github-search (discovery)
4. **Phase 4:** github-assistant (router)
5. **Phase 5:** Remaining skills (v2)

### 6.3 Test Strategy

- Unit tests: Mock API responses with `responses` library
- Integration tests: Use GitHub's test repositories
- Coverage target: 80% unit, 100% happy path integration

---

## 7. Appendix

### A. Endpoint Reference

```
# Repositories
GET    /user/repos
GET    /repos/{owner}/{repo}
POST   /user/repos
PATCH  /repos/{owner}/{repo}
DELETE /repos/{owner}/{repo}

# Issues
GET    /repos/{owner}/{repo}/issues
GET    /repos/{owner}/{repo}/issues/{issue_number}
POST   /repos/{owner}/{repo}/issues
PATCH  /repos/{owner}/{repo}/issues/{issue_number}

# Pull Requests
GET    /repos/{owner}/{repo}/pulls
GET    /repos/{owner}/{repo}/pulls/{pull_number}
POST   /repos/{owner}/{repo}/pulls
PATCH  /repos/{owner}/{repo}/pulls/{pull_number}
PUT    /repos/{owner}/{repo}/pulls/{pull_number}/merge

# Search
GET    /search/repositories?q={query}
GET    /search/issues?q={query}
GET    /search/code?q={query}
```

### B. Error Codes Reference

| HTTP Code | GitHub Meaning | Skill Behavior |
|-----------|----------------|----------------|
| 400 | Bad request | ValidationError |
| 401 | Bad credentials | AuthenticationError |
| 403 | Forbidden / Rate limited | PermissionError / RateLimitError |
| 404 | Not found | NotFoundError |
| 422 | Validation failed | ValidationError (with details) |
| 5xx | Server error | Retry then fail |

---

## Sign-off

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Author | Developer | 2024-01-15 | ✓ |
| Reviewer | Tech Lead | 2024-01-16 | ✓ |
