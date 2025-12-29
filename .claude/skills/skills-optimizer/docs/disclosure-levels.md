# Progressive Disclosure Level Specification

## Overview

The 3-level progressive disclosure system ensures Claude can scale to 100+ skills without context penalty. Each level has specific constraints and purposes.

---

## Level 1: Metadata

### Purpose
Enable autonomous skill matching at startup with minimal context cost.

### What Gets Loaded
- `name` field from YAML frontmatter
- `description` field from YAML frontmatter

### Constraints

| Field | Max Length | Required |
|-------|------------|----------|
| name | 64 characters | Yes |
| description | 1024 characters | Yes |

### Token Budget
- Target: ~50-200 tokens per skill
- 100 skills = ~5,000-20,000 tokens total
- This is the **only** content loaded for inactive skills

### Best Practices

**Description Structure**:
```
[WHAT it does] + [WHEN to use it]
```

**Good Example**:
```yaml
description: "Generate OpenAPI 3.0 docs from Express routes. Use when creating API documentation, documenting endpoints, or building API specs."
```

**Bad Examples**:
```yaml
# Too vague
description: "Helps with API documentation."

# No trigger conditions
description: "A comprehensive guide to creating REST API documentation with examples."

# Too long (wastes tokens on inactive skills)
description: "This skill provides a complete framework for generating, validating, and maintaining OpenAPI 3.0 documentation from your Express.js backend routes, including support for authentication schemes, request/response schemas, error handling documentation, and integration with Swagger UI for interactive testing..."
```

### Validation Checklist
- [ ] Name is <= 64 characters
- [ ] Description is <= 1024 characters
- [ ] Description includes "what" (functionality)
- [ ] Description includes "when" (trigger conditions)
- [ ] Keywords front-loaded
- [ ] Written in third person
- [ ] No redundant explanation of common concepts

---

## Level 2: SKILL.md Body

### Purpose
Provide core instructions and navigation when skill is actively triggered.

### What Gets Loaded
Everything in SKILL.md after the YAML frontmatter.

### Constraints

| Metric | Target | Maximum |
|--------|--------|---------|
| Line count | 200-300 | 500 |
| Word count | 1000-2000 | 4000 |
| Token count | 1500-3000 | 6000 |
| Code blocks | 3-5 | 10 |
| Max code block | 20 lines | 50 lines |

### Content Priority

**Must Include**:
1. Quick Start (80% use case)
2. Prerequisites
3. Core workflow steps
4. Navigation to Level 3 resources

**Move to Level 3**:
1. Complete API references
2. Extensive code examples (> 30 lines)
3. Troubleshooting guides
4. Configuration schemas
5. Alternative approaches
6. Historical context

### Structure Template

```markdown
# Skill Name

## What This Skill Does
[2-3 sentences max]

## Prerequisites
- [Bullet list]

## Quick Start
[Most common use case - 80% of users]

---

## Core Workflow

### Step 1: [Action]
[Brief instructions]

### Step 2: [Action]
[Brief instructions]

---

## Reference Documentation
- [Link to detailed doc 1](docs/doc1.md)
- [Link to detailed doc 2](docs/doc2.md)
```

### Validation Checklist
- [ ] Under 500 lines total
- [ ] Quick Start appears early
- [ ] No inline code blocks > 50 lines
- [ ] Heavy content referenced, not embedded
- [ ] Navigation links are one level deep
- [ ] Acts as guide, not encyclopedia

---

## Level 3+: Nested Resources

### Purpose
Provide deep-dive content only when explicitly requested.

### What Gets Loaded
Only the specific file Claude navigates to.

### Directory Structure

```
skill-name/
├── SKILL.md              # Level 2
├── docs/                 # Level 3 documentation
│   ├── advanced.md
│   ├── troubleshooting.md
│   └── api-reference.md
├── resources/            # Level 3 static files
│   ├── templates/
│   ├── examples/
│   └── schemas/
└── scripts/              # Level 3 executables
    ├── setup.sh
    └── validate.js
```

### Constraints

| Metric | Recommendation |
|--------|----------------|
| Nesting depth | 1 level from SKILL.md |
| File size | No limit (loaded on demand) |
| Directory count | As needed |

### Deep Nesting Problem

**Problem**: When references chain (A -> B -> C), Claude may only preview files (`head -100`) instead of reading fully.

**Bad**:
```
SKILL.md -> docs/setup.md -> docs/advanced/config.md -> docs/advanced/options/database.md
```

**Good**:
```
SKILL.md -> docs/setup.md
SKILL.md -> docs/advanced-config.md
SKILL.md -> docs/database-options.md
```

### Reference Patterns

**Markdown Links**:
```markdown
See [Advanced Configuration](docs/advanced.md) for complex scenarios.
```

**File Path References**:
```markdown
Use template: `resources/templates/api-template.js`
```

**Script Execution** (avoids loading source):
```markdown
Run setup: `./scripts/setup.sh`
```

### Validation Checklist
- [ ] All docs/ files directly referenced from SKILL.md
- [ ] No file references other files in docs/
- [ ] Scripts executable without reading source
- [ ] Templates copied, not parsed
- [ ] Large examples in resources/examples/

---

## Token Impact Analysis

### Scenario: 50 Installed Skills

| Level | When Loaded | Token Cost |
|-------|-------------|------------|
| Level 1 | Always (all 50) | ~5,000 tokens |
| Level 2 | Active skill only | ~3,000 tokens |
| Level 3 | On explicit access | Variable |

**Total context for idle state**: ~5,000 tokens
**Total context with 1 active skill**: ~8,000 tokens

Compare to non-optimized (all Level 2 always loaded):
~150,000 tokens = context overflow

---

## Migration Guide

### From Monolithic to Progressive

1. **Identify Level 1** (keep in frontmatter):
   - Skill name
   - Trigger description

2. **Identify Level 2** (keep in SKILL.md):
   - Quick start
   - Core workflow
   - Essential commands

3. **Extract to Level 3** (move to docs/):
   - Detailed explanations
   - Full API references
   - Comprehensive examples
   - Troubleshooting

### Example Migration

**Before** (800 lines, ~12KB):
```markdown
---
name: "API Builder"
description: "Builds APIs"
---
# API Builder
[800 lines of content including full REST tutorial,
GraphQL guide, authentication deep-dive, 50 examples...]
```

**After**:
```
api-builder/
├── SKILL.md (200 lines, ~3KB)
├── docs/
│   ├── rest-guide.md
│   ├── graphql-guide.md
│   ├── authentication.md
│   └── examples.md
└── resources/
    └── templates/
```
