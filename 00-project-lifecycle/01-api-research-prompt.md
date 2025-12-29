# API Research Prompt

## Purpose

Comprehensively research a target REST API before implementation to understand all capabilities, authentication, limitations, and patterns.

## Prerequisites

- Target API name and documentation URL
- Access to API documentation (public or authenticated)
- Optional: API credentials for testing endpoints

## Placeholders

- `{{API_NAME}}` - The name of the API (e.g., "GitHub", "Stripe", "Slack")
- `{{API_DOCS_URL}}` - URL to official API documentation
- `{{API_BASE_URL}}` - Base URL for API requests

---

## Prompt

```
I need to research the {{API_NAME}} API to prepare for building a Claude Code Assistant Skills project.

**API Documentation:** {{API_DOCS_URL}}
**Base URL:** {{API_BASE_URL}}

Please conduct comprehensive research covering:

## 1. API Overview
- What is the purpose of this API?
- What are the major resource types/entities?
- Is this REST, GraphQL, or hybrid?
- What API versions exist and which is current?

## 2. Authentication & Authorization
- What authentication methods are supported? (API key, OAuth 2.0, JWT, etc.)
- How are credentials passed? (Header, query param, body)
- What scopes/permissions exist?
- How are tokens refreshed (if applicable)?
- What are the permission levels (read, write, admin)?

## 3. Endpoint Inventory
For each major resource, document:
- All CRUD endpoints (GET, POST, PUT/PATCH, DELETE)
- List endpoints with filtering/search capabilities
- Bulk operation endpoints
- Special action endpoints (e.g., /approve, /archive)

Create a table:
| Resource | Method | Endpoint | Description |
|----------|--------|----------|-------------|
| ... | ... | ... | ... |

## 4. Pagination Patterns
- What pagination style? (offset, cursor, page number, link header)
- What are the default and maximum page sizes?
- How is total count provided?
- Example pagination parameters

## 5. Rate Limiting
- What are the rate limits? (per minute, per hour, per day)
- How are limits communicated? (headers, response body)
- What happens when exceeded? (HTTP 429, backoff requirements)
- Are there different limits for different endpoints?

## 6. Request/Response Patterns
- Content-Type requirements (application/json, etc.)
- Common request headers required
- Response envelope pattern (if any)
- Error response format
- Date/time formats used

## 7. Webhooks & Events (if applicable)
- What events can trigger webhooks?
- Webhook payload format
- Webhook security (signatures, secrets)

## 8. SDKs & Libraries
- Official SDKs available?
- Community libraries?
- Recommended Python library (if any)

## 9. Known Limitations & Quirks
- Documented limitations
- Common gotchas or unexpected behaviors
- Deprecated endpoints to avoid
- Beta/preview features

## 10. Testing Capabilities
- Sandbox/test environment available?
- Test credentials or mock server?
- Rate limit exceptions for testing?

Please be thorough and cite specific documentation sections where relevant.
```

---

## Expected Outputs

After using this prompt, you should have documentation covering:

1. **API capability matrix** - All endpoints organized by resource
2. **Authentication guide** - How to authenticate requests
3. **Pagination strategy** - How to handle multi-page results
4. **Rate limit strategy** - How to avoid and handle 429 errors
5. **Known issues list** - Quirks and workarounds to implement

---

## Next Steps

1. Create GAP Analysis using `02-gap-analysis-template.md`
2. Use research to inform skill boundaries
3. Identify shared library requirements (pagination, auth, etc.)

---

## Tips

- **Save the research** - Copy Claude's response to a `docs/api-research.md` file
- **Test critical endpoints** - Use curl or Postman to verify understanding
- **Check for OpenAPI spec** - Many APIs publish OpenAPI/Swagger specs that provide structured endpoint data
- **Look for changelogs** - API changelogs reveal deprecations and new features
