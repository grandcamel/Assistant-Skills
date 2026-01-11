---
name: skills-optimizer
description: Audit and optimize skills for token efficiency and progressive disclosure compliance. Use when user wants to "analyze skill tokens", "audit skills", "optimize skill size", "check token efficiency", or "validate progressive disclosure".
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

## Router Skill Checks (R001-R005)

Automatically detected for skills mentioning "hub", "router", or "routes to...skills":

| Check | Description | Severity |
|-------|-------------|----------|
| R001 | Quick Reference table with Risk column | Warning |
| R002 | Risk Legend present | Warning |
| R003 | Negative Triggers documented | Warning |
| R004 | Disambiguation examples | Warning |
| R005 | Context awareness (pronoun resolution) | Info |

---

## Risk Level Checks (K001-K003)

Applied to skills with `scripts/` directory:

| Check | Description | Severity |
|-------|-------------|----------|
| K001 | Destructive scripts have ⚠️ indicators | Warning |
| K002 | Bulk operations marked as ⚠️⚠️ | Warning |
| K003 | High-risk ops document --dry-run | Warning |

### Risk Level Reference

| Risk | Symbol | Operations | Required Safeguards |
|------|:------:|------------|---------------------|
| Safe | `-` | search, list, get, export | None |
| Destructive | `⚠️` | create, update, delete | Confirm |
| High-risk | `⚠️⚠️` | bulk ops, admin changes | Confirm + dry-run |

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
