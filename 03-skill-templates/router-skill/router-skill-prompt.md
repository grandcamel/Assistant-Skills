# Router Skill Creation Prompt

## Purpose

Create the meta-skill that routes user requests to appropriate specialized skills.

## Prerequisites

- All specialized skills implemented
- Skills tested and documented
- Clear understanding of skill boundaries

## Placeholders

- `{{TOPIC}}` - Lowercase prefix (e.g., "github")
- `{{API_NAME}}` - Friendly API name (e.g., "GitHub")
- `{{SKILLS_LIST}}` - List of all specialized skills

---

## Prompt

```
Create the router meta-skill: {{TOPIC}}-assistant

This skill acts as the hub that routes user requests to specialized skills.

**Available Skills:**
{{SKILLS_LIST}}

## 1. Directory Structure

```
.claude/skills/{{TOPIC}}-assistant/
├── SKILL.md                    # Router documentation
└── docs/
    ├── SCRIPT_EXECUTION.md     # Common script patterns
    ├── QUICK_REFERENCE.md      # Quick lookup tables
    └── BEST_PRACTICES.md       # Usage guidance
```

## 2. SKILL.md Content

Create a comprehensive routing document with:

### Frontmatter
```yaml
---
name: "{{API_NAME}} Assistant"
description: "{{API_NAME}} automation hub routing to N specialized skills for any {{API_NAME}} task"
when_to_use: |
  - Need to work with {{API_NAME}} in any capacity
  - Unsure which skill applies to your task
  - Need to combine multiple operations in one flow
---
```

### Quick Start Section
- Tell me what you need in natural language
- I'll load the appropriate specialized skill
- Example requests with expected skill routing

### Skill Routing Guide

Create tables organized by use case:

```markdown
## Skill Routing Guide

### Resource Management

| Need | Skill | Triggers |
|------|-------|----------|
| CRUD on resource1 | `{{TOPIC}}-resource1` | "create resource1", "list resource1", "update resource1" |
| CRUD on resource2 | `{{TOPIC}}-resource2` | "create resource2", "get resource2", "delete resource2" |

### Search & Discovery

| Need | Skill | Triggers |
|------|-------|----------|
| Search resources | `{{TOPIC}}-search` | "search", "find", "query" |
| Filter by criteria | `{{TOPIC}}-search` | "filter", "show me", "list with" |

### Advanced Operations

| Need | Skill | Triggers |
|------|-------|----------|
| Bulk operations | `{{TOPIC}}-bulk` | "bulk", "batch", "mass update" |
| Admin tasks | `{{TOPIC}}-admin` | "configure", "settings", "permissions" |
```

### How This Works Section
1. User describes task in natural language
2. Router identifies which skill applies
3. Router invokes skill (e.g., `Skill: {{TOPIC}}-resource1`)
4. Skill loads with detailed scripts and instructions
5. Request executed using loaded capabilities

### Multi-Skill Operations Section

Document common multi-skill workflows:

```markdown
## Multi-Skill Operations

Some tasks require multiple skills loaded sequentially:

**Example: "Create resource and link to another"**
1. Load `{{TOPIC}}-resource1` - Create the resource
2. Load `{{TOPIC}}-relationships` - Create the link

**Example: "Find items and bulk update them"**
1. Load `{{TOPIC}}-search` - Find items with query
2. Load `{{TOPIC}}-bulk` - Bulk update the results
```

### Quick Reference Section
- Common operations table
- Frequently used commands
- Link to detailed reference

### Configuration Section
- Environment variables
- Profile support
- Settings locations

## 3. Supporting Documentation

### docs/SCRIPT_EXECUTION.md
- Common script patterns
- Error handling
- Output formats
- Profile usage

### docs/QUICK_REFERENCE.md
- All scripts organized by skill
- One-line descriptions
- Common flags

### docs/BEST_PRACTICES.md
- When to use which skill
- Combining operations efficiently
- Error recovery
- Performance tips

## 4. Routing Logic

The router should:
- Match user intent to skill using keyword triggers
- Handle ambiguous requests by asking clarifying questions
- Support explicit skill invocation: "use {{TOPIC}}-resource1"
- Chain skills for complex operations
- Provide discovery: "what skills are available?"

## 5. Disambiguation

When a request could match multiple skills:
- Ask user to clarify
- Suggest most likely skill based on context
- Allow user to specify skill explicitly

## 6. Verification

After creation:
- [ ] SKILL.md documents all skills
- [ ] Routing table covers all triggers
- [ ] Multi-skill examples are realistic
- [ ] Quick reference is complete
- [ ] Each skill can be invoked
```

---

## Expected Outputs

1. **SKILL.md** - Comprehensive routing documentation
2. **docs/SCRIPT_EXECUTION.md** - Common patterns
3. **docs/QUICK_REFERENCE.md** - All commands reference
4. **docs/BEST_PRACTICES.md** - Usage guidance

---

## Router Design Principles

### Exhaustive Coverage
Every capability should be routable through the assistant.

### Clear Boundaries
User should understand which skill handles what.

### Minimal Overlap
Triggers should uniquely identify one skill when possible.

### Graceful Ambiguity
When unclear, ask rather than guess wrong.

### Composability
Support combining skills for complex workflows.

---

## Trigger Keyword Best Practices

- Use action verbs: "create", "list", "update", "delete", "search"
- Use resource nouns: "issue", "user", "project"
- Include synonyms: "find" = "search" = "query"
- Support natural phrases: "show me", "what are", "how many"

---

## Testing the Router

1. Try various natural language requests
2. Verify correct skill is suggested
3. Test ambiguous requests
4. Test multi-skill workflows
5. Test explicit skill invocation
