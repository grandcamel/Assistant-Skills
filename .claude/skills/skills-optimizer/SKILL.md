---
name: skills-optimizer
description: Audit and optimize skills for token efficiency and progressive disclosure compliance. Use when user wants to "analyze skill tokens", "audit skills", "optimize skill size", "check token efficiency", or "validate progressive disclosure".
when_to_use:
  - Analyzing skill token footprint
  - Reformatting verbose skills into hierarchical structures
  - Ensuring skills follow the 3-level disclosure model
  - Auditing skill collections for performance
---

# Skills Optimizer

Audit skills for token efficiency and progressive disclosure compliance.

## What This Skill Does

| Operation | Script | Description |
|-----------|--------|-------------|
| Analyze Skill | `analyze-skill.sh` | Audit single skill's token footprint |
| Audit All | `audit-all-skills.sh` | Batch audit entire skills directory |
| Validate | `validate-skill.sh` | Check structure and compliance |

---

## Quick Start

### Audit a Single Skill

```bash
./scripts/analyze-skill.sh ~/.claude/skills/my-skill
# Output: Token count, violations, recommendations
```

### Audit All Skills

```bash
./scripts/audit-all-skills.sh ~/.claude/skills
# Generates: audit-report.json with per-skill scores
```

### Validation Checklist

- [ ] **L1**: Description < 1024 chars, includes triggers
- [ ] **L2**: SKILL.md < 500 lines, navigation guide
- [ ] **L3+**: Details in separate files
- [ ] **No deep nesting**: One level from SKILL.md
- [ ] **No voodoo constants**: No explaining what Claude knows

---

## The 3-Level Disclosure Model

| Level | Target | Loaded When | Contains |
|-------|--------|-------------|----------|
| L1: Metadata | ~200 chars | Startup (all skills) | name, description, triggers |
| L2: SKILL.md | <500 lines | Skill triggered | Quick start, workflow overview |
| L3: Nested docs | Variable | Explicitly accessed | API refs, examples, guides |

---

## Optimization Workflow

1. **Measure**: `wc -w SKILL.md` (target: <2000 words)
2. **Identify violations** (see table below)
3. **Apply fixes**
4. **Validate**: `./scripts/validate-skill.sh`

### Common Violations

| Violation | Detection | Fix |
|-----------|-----------|-----|
| Bloated description | >1024 chars | Trim, front-load keywords |
| Voodoo constants | Explains PDF/JSON/API | Delete (Claude knows) |
| Inline code dumps | >50 line blocks | Move to `scripts/` |
| Deep nesting | A→B→C chains | Flatten to one level |

---

## Audit Report Format

```json
{
  "skill": "my-skill",
  "tokenFootprint": { "level1": 180, "level2": 3200, "level3": 15000 },
  "violations": [...],
  "score": 72,
  "grade": "C"
}
```

---

## Related Documentation

- [Disclosure Level Criteria](docs/disclosure-levels.md)
- [Token Counting Guide](docs/token-counting.md)
- [Naming Conventions](docs/naming-conventions.md)
- [Validation Rules](docs/validation-rules.md)
