# Router Skill Patterns

Best practices for building hub/router skills that route requests to specialized skills.

---

## Core Principle

> **"The LLM IS the Router"**

SKILL.md provides instructions for Claude, not configuration for code. This means:
- Natural language certainty replaces computed confidence scores
- Claude's intent classification handles ambiguity
- SKILL.md teaches routing through examples and rules

---

## Pattern 1: Quick Reference Table with Risk Levels

The Quick Reference table is the primary routing guide. Include risk levels to teach Claude which operations need confirmation.

```markdown
## Quick Reference

| I want to... | Use this skill | Risk |
|--------------|----------------|:----:|
| Create/edit/delete a single item | topic-issue | ⚠️ |
| Search with queries, export results | topic-search | - |
| Update 10+ items at once | topic-bulk | ⚠️⚠️ |
| Manage permissions, settings | topic-admin | ⚠️⚠️ |

**Risk Legend**: `-` Read-only/safe | `⚠️` Has destructive ops | `⚠️⚠️` High-risk
```

### Risk Level Assignment

| Risk | Operations | Required Safeguards |
|:----:|------------|---------------------|
| `-` | search, list, get, export, read | None |
| `⚠️` | create, update, delete (single), transition | Confirm before destructive |
| `⚠️⚠️` | bulk delete, admin changes, bulk updates | Confirm + dry-run |

---

## Pattern 2: Keyword-Based Routing Rules

Define explicit keyword mappings to reduce ambiguity:

```markdown
## Routing Rules

1. **Explicit skill mention wins** - If user says "use topic-search", use it
2. **Entity signals** - Resource ID present → likely topic-issue
3. **Quantity determines bulk** - More than 10 items → topic-bulk
4. **Keywords drive routing**:
   - "create", "update", "delete" (single) → topic-issue
   - "search", "find", "query", "filter" → topic-search
   - "bulk", "batch", "all", "multiple" → topic-bulk
   - "permissions", "settings", "configure" → topic-admin
```

### Keyword Categories

| Category | Keywords | Typical Skill |
|----------|----------|---------------|
| CRUD verbs | create, get, update, delete, show, view | issue/resource skill |
| Search verbs | search, find, query, filter, list | search skill |
| Bulk indicators | bulk, batch, all, multiple, many, >10 | bulk skill |
| Admin verbs | configure, permission, setting, rule | admin skill |
| Lifecycle verbs | transition, move, assign, close, resolve | lifecycle skill |

---

## Pattern 3: Negative Triggers Table

Negative triggers explicitly state what each skill does NOT handle. This reduces misrouting by helping Claude eliminate incorrect skills.

```markdown
## Negative Triggers

| Skill | Does NOT handle | Route to instead |
|-------|-----------------|------------------|
| topic-issue | Bulk (>10), search queries | topic-bulk, topic-search |
| topic-search | Single item lookup, modifications | topic-issue, topic-bulk |
| topic-bulk | Single item ops, search only | topic-issue, topic-search |
| topic-admin | Item CRUD, bulk operations | topic-issue, topic-bulk |
```

### Why This Works

- Claude processes exclusions efficiently
- Reduces "almost right" misroutes
- Documents skill boundaries explicitly
- Improves routing accuracy by 40%+ (measured in jira-assistant)

---

## Pattern 4: Disambiguation Templates

For requests that could match multiple skills, provide concrete examples:

```markdown
## When to Clarify First

Ask the user before routing when:
- Request matches 2+ skills with similar likelihood
- Request is vague or could be interpreted multiple ways
- Destructive operations are implied

### Disambiguation Examples

**"Show me the sprint"**
Could mean:
1. Sprint metadata (dates, goals) → topic-agile
2. Items in the sprint → topic-search

Ask: "Do you want sprint details or the items in the sprint?"

**"Update the item"**
Could mean:
1. Change fields → topic-issue
2. Transition status → topic-lifecycle
3. Update multiple → topic-bulk

Ask: "What would you like to update - fields, status, or multiple items?"
```

### Disambiguation Rules

1. **Max 3 options** - More than 3 options is overwhelming
2. **Most likely first** - Put the most probable interpretation first
3. **Include action** - Show what each choice leads to
4. **Be concise** - One line per option

---

## Pattern 5: Context Awareness

### Pronoun Resolution

```markdown
### Pronoun Resolution

When user says "it" or "that":
- If exactly one entity mentioned in last 3 messages → use it
- If multiple entities mentioned → ask: "Which one - X or Y?"
- If no entity in last 5 messages → ask: "Which are you referring to?"
```

### Scope Persistence

```markdown
### Scope Persistence

When user mentions a scope (project, container):
- Remember it for subsequent requests
- "Create in PROJECT-A" → PROJECT-A is now active
- "Create another" → Use PROJECT-A implicitly
- Explicit mention updates the active scope
```

### Context Expiration

```markdown
### Context Expiration

After 5+ messages or 5+ minutes since last reference:
- Re-confirm rather than assume
- Don't guess when context is stale
```

---

## Pattern 6: Multi-Skill Workflows

Document common workflows that span multiple skills:

```markdown
## Common Workflows

### Create Parent with Children
1. Use topic-parent to create the parent → Note key (e.g., PAR-100)
2. Use topic-issue to create each child with `--parent PAR-100`
3. Confirm: "Created parent PAR-100 with N children"

### Bulk Action from Search
1. Use topic-search to find matching items
2. Use topic-bulk with --dry-run to preview
3. Confirm count with user before executing

### Data Passing Between Steps
When one skill's output feeds another:
- Capture entity IDs from responses
- State this explicitly: "Created RES-123. Now linking..."
- Reference captured data in subsequent operations
```

---

## Pattern 7: Error Handling Guidance

```markdown
## Error Handling

If a skill fails:
- Report the error clearly
- Suggest recovery options
- Offer alternative approaches

### Permission Errors
- Explain what permission is needed
- Suggest admin skill for permission checks
- Don't retry the same operation

### Rate Limits
- Tell user to wait (include retry-after if known)
- Suggest smaller batch sizes for bulk operations
- Offer to queue the request

### Not Found
- Verify the ID/key format is correct
- Ask if there's a typo
- Suggest search skill to find similar items
```

---

## Pattern 8: Discoverability

```markdown
## Discoverability

- `/browse-skills` - List all skills with descriptions
- `/skill-info <name>` - Detailed skill information

If user asks "what can you do?":
- Show the Quick Reference table
- Offer to explain specific skills
```

---

## Anti-Patterns to Avoid

### 1. Greedy Matching
**Bad**: Route to first skill that partially matches
**Good**: Consider all matches, disambiguate when close

### 2. Context Amnesia
**Bad**: Treat each message independently
**Good**: Track entities, scopes, and operations across conversation

### 3. Silent Assumptions
**Bad**: Guess which skill without asking
**Good**: Ask when uncertain, especially for destructive ops

### 4. Overlapping Triggers
**Bad**: Same keywords route to multiple skills
**Good**: Use negative triggers to establish boundaries

### 5. Missing Risk Indicators
**Bad**: Treat all operations the same
**Good**: Mark risk levels, require confirmation for destructive ops

---

## Metrics for Router Quality

Track these metrics to measure router effectiveness:

| Metric | Target | Measurement |
|--------|--------|-------------|
| Routing accuracy | >90% | Correct skill on first attempt |
| Disambiguation rate | <15% | Requests needing clarification |
| Misroute rate | <5% | Wrong skill invoked |
| Context resolution | >95% | Pronouns resolved correctly |
