# GAP Analysis Template

## Purpose

Document the gap between API capabilities and desired skill features to create a clear implementation roadmap.

## Prerequisites

- Completed API research (from `01-api-research-prompt.md`)
- Understanding of target use cases
- List of desired features/operations

## Placeholders

- `{{API_NAME}}` - Name of the target API
- `{{PROJECT_NAME}}` - Name of your skills project
- `{{DATE}}` - Date of analysis

---

# {{API_NAME}} GAP Analysis

**Project:** {{PROJECT_NAME}}
**Date:** {{DATE}}
**Status:** Draft | In Review | Approved

---

## Executive Summary

<!-- 2-3 sentence summary of the analysis findings -->

This analysis evaluates the {{API_NAME}} API capabilities against the requirements for the {{PROJECT_NAME}} Assistant Skills project.

**Key Findings:**
- Total API endpoints available: _____
- Endpoints needed for MVP: _____
- Identified gaps/limitations: _____
- Recommended skills: _____

---

## 1. API Capability Inventory

### 1.1 Authentication

| Aspect | API Capability | Notes |
|--------|---------------|-------|
| **Method** | <!-- API key / OAuth 2.0 / JWT / etc. --> | |
| **Credential Location** | <!-- Header / Query / Body --> | |
| **Token Refresh** | <!-- Yes/No, mechanism --> | |
| **Scopes Available** | <!-- List scopes --> | |
| **Multi-tenant Support** | <!-- Yes/No --> | |

### 1.2 Core Resources

<!-- List all major resources/entities in the API -->

| Resource | Create | Read | Update | Delete | List | Search | Notes |
|----------|--------|------|--------|--------|------|--------|-------|
| Resource1 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | |
| Resource2 | ✅ | ✅ | ❌ | ❌ | ✅ | ❌ | Read-only |
| Resource3 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | |

### 1.3 Advanced Operations

| Operation | Supported | Endpoint | Notes |
|-----------|-----------|----------|-------|
| Bulk Create | <!-- Yes/No --> | <!-- endpoint --> | |
| Bulk Update | <!-- Yes/No --> | <!-- endpoint --> | |
| Bulk Delete | <!-- Yes/No --> | <!-- endpoint --> | |
| Export | <!-- Yes/No --> | <!-- endpoint --> | |
| Import | <!-- Yes/No --> | <!-- endpoint --> | |
| Webhooks | <!-- Yes/No --> | <!-- endpoint --> | |

### 1.4 Rate Limits

| Limit Type | Value | Scope | Notes |
|------------|-------|-------|-------|
| Requests per minute | <!-- value --> | <!-- per user/org/IP --> | |
| Requests per hour | <!-- value --> | <!-- per user/org/IP --> | |
| Requests per day | <!-- value --> | <!-- per user/org/IP --> | |
| Concurrent connections | <!-- value --> | | |

### 1.5 Pagination

| Aspect | Value |
|--------|-------|
| **Style** | <!-- offset / cursor / page / link-header --> |
| **Default page size** | <!-- number --> |
| **Max page size** | <!-- number --> |
| **Total count provided** | <!-- Yes/No, how --> |

---

## 2. Feature-to-Endpoint Mapping

### 2.1 Desired Features

<!-- List all features you want to implement -->

| Feature ID | Feature Description | Priority | Complexity |
|------------|---------------------|----------|------------|
| F001 | <!-- description --> | High/Med/Low | High/Med/Low |
| F002 | <!-- description --> | High/Med/Low | High/Med/Low |
| F003 | <!-- description --> | High/Med/Low | High/Med/Low |

### 2.2 Feature-to-Endpoint Matrix

| Feature ID | Required Endpoints | API Support | Gap? |
|------------|-------------------|-------------|------|
| F001 | `GET /resource`, `POST /resource` | ✅ Full | No |
| F002 | `GET /resource/search` | ⚠️ Partial | Yes - no fuzzy search |
| F003 | `POST /resource/bulk` | ❌ None | Yes - must loop |

### 2.3 Gap Details

<!-- For each gap identified, provide details -->

#### GAP-001: {{Gap Title}}

- **Feature:** F002 - Search with fuzzy matching
- **Required:** Fuzzy text search across multiple fields
- **Available:** Exact match search only
- **Workaround:** Client-side fuzzy matching after retrieval
- **Impact:** Performance degradation for large datasets
- **Recommendation:** Implement with warning about performance

#### GAP-002: {{Gap Title}}

- **Feature:** F003 - Bulk operations
- **Required:** Create/update 100+ items in one call
- **Available:** Single-item endpoints only
- **Workaround:** Parallel requests with rate limit awareness
- **Impact:** Slower bulk operations, rate limit risk
- **Recommendation:** Implement with batching and progress reporting

---

## 3. Skill Architecture Mapping

### 3.1 Proposed Skills

<!-- Map API capabilities to skills -->

| Skill Name | Resources | Key Operations | Endpoints Used |
|------------|-----------|----------------|----------------|
| `{{topic}}-resource1` | Resource1 | CRUD, search | 6 endpoints |
| `{{topic}}-resource2` | Resource2 | Read, list | 3 endpoints |
| `{{topic}}-bulk` | Multiple | Bulk operations | 4 endpoints |
| `{{topic}}-assistant` | N/A | Router | N/A |

### 3.2 Shared Library Requirements

| Component | Purpose | Complexity |
|-----------|---------|------------|
| HTTP Client | Retry, rate limiting, auth | High |
| Config Manager | Multi-profile, env vars | Medium |
| Error Handler | Status code mapping | Medium |
| Validators | Input validation | Low |
| Formatters | Output formatting | Low |
| Pagination Helper | Handle pagination styles | Medium |

---

## 4. Limitations & Constraints

### 4.1 API Limitations

| Limitation | Impact | Mitigation |
|------------|--------|------------|
| <!-- limitation --> | <!-- impact --> | <!-- mitigation --> |

### 4.2 Implementation Constraints

| Constraint | Reason | Approach |
|------------|--------|----------|
| Python 3.8+ | Type hints, pathlib | Document requirement |
| No external CLI | Portability | Pure Python implementation |
| Credentials security | Security | Env vars, gitignore |

---

## 5. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Rate limit exceeded | Medium | Medium | Exponential backoff, caching |
| API deprecation | Low | High | Monitor changelog, version pin |
| Auth token expiry | Medium | Low | Auto-refresh implementation |
| Breaking API changes | Low | High | Integration tests, alerts |

---

## 6. Recommendations

### 6.1 MVP Scope

**Include in MVP:**
1. <!-- Core feature 1 -->
2. <!-- Core feature 2 -->
3. <!-- Core feature 3 -->

**Defer to v2:**
1. <!-- Advanced feature 1 -->
2. <!-- Advanced feature 2 -->

### 6.2 Implementation Order

1. **Phase 1:** Shared library + core CRUD skill
2. **Phase 2:** Search and list operations
3. **Phase 3:** Bulk operations
4. **Phase 4:** Advanced features
5. **Phase 5:** Router skill + documentation

### 6.3 Test Strategy

- Unit tests: Mock API responses
- Integration tests: Use sandbox/test environment
- Coverage target: 80% unit, 100% happy path integration

---

## 7. Appendix

### A. Endpoint Reference

<!-- Full list of endpoints to be used -->

```
GET    /api/v1/resources
GET    /api/v1/resources/{id}
POST   /api/v1/resources
PUT    /api/v1/resources/{id}
DELETE /api/v1/resources/{id}
GET    /api/v1/resources/search?q={query}
...
```

### B. Error Codes Reference

| HTTP Code | API Meaning | Skill Behavior |
|-----------|-------------|----------------|
| 400 | Bad request | ValidationError |
| 401 | Unauthorized | AuthenticationError |
| 403 | Forbidden | PermissionError |
| 404 | Not found | NotFoundError |
| 429 | Rate limited | Retry with backoff |
| 5xx | Server error | Retry then fail |

### C. Data Model Reference

<!-- Key entities and their fields -->

```json
{
  "Resource1": {
    "id": "string",
    "name": "string",
    "created_at": "datetime",
    "updated_at": "datetime"
  }
}
```

---

## Sign-off

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Author | | | |
| Reviewer | | | |
