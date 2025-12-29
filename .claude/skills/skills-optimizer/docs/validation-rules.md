# Validation Rules

## Complete Rule Set

This document defines all validation rules for skill optimization, organized by severity.

---

## Critical Rules (Must Fix)

### C001: Missing YAML Frontmatter

**Rule**: SKILL.md must start with valid YAML frontmatter.

**Check**:
```bash
head -1 SKILL.md | grep -q "^---$"
```

**Valid**:
```yaml
---
name: "My Skill"
description: "Does X. Use when Y."
---
```

**Invalid**:
```markdown
# My Skill
[content without frontmatter]
```

---

### C002: Missing Required Fields

**Rule**: Frontmatter must contain `name` and `description`.

**Check**:
```bash
grep -E "^name:|^description:" SKILL.md | wc -l
# Must equal 2
```

---

### C003: Description Exceeds Limit

**Rule**: Description must be <= 1024 characters.

**Check**:
```bash
# Extract description and count
DESC=$(sed -n '/^description:/,/^[a-z]*:/p' SKILL.md | head -1)
echo ${#DESC}
```

**Severity**: Critical (blocks skill loading)

---

### C004: Name Exceeds Limit

**Rule**: Name must be <= 64 characters.

**Check**:
```bash
NAME=$(grep "^name:" SKILL.md | cut -d'"' -f2)
echo ${#NAME}
```

---

### C005: Invalid Directory Structure

**Rule**: Skill must be directly under `~/.claude/skills/[name]/` or `.claude/skills/[name]/`.

**Invalid Structures**:
```
~/.claude/skills/category/my-skill/     ✗ (nested)
~/.claude/skills/my-skill/sub/SKILL.md  ✗ (SKILL.md not at root)
```

---

## High Severity Rules (Should Fix)

### H001: Missing Trigger Condition

**Rule**: Description should include "use when", "invoke for", or similar trigger phrase.

**Check**:
```bash
grep -qi "use when\|invoke for\|invoke when\|triggers on" SKILL.md
```

**Fix**: Add trigger conditions to description:
```yaml
# Before
description: "Builds REST APIs with Express."

# After
description: "Builds REST APIs with Express. Use when creating new endpoints or scaffolding API projects."
```

---

### H002: SKILL.md Exceeds Size Limit

**Rule**: SKILL.md body should be < 500 lines.

**Check**:
```bash
wc -l SKILL.md
```

**Fix**: Extract content to Level 3 docs.

---

### H003: Deep Reference Nesting

**Rule**: Referenced files should not reference other files.

**Check**:
```bash
# Find markdown links in docs/
grep -r "\[.*\](.*\.md)" docs/
# Should return empty
```

**Fix**: Flatten references to one level from SKILL.md.

---

### H004: Large Inline Code Blocks

**Rule**: Code blocks should be < 50 lines.

**Check**:
```bash
# Find code blocks and count lines between markers
awk '/```/{p=!p; if(!p){print NR-start}; start=NR}' SKILL.md
```

**Fix**: Move large code to `scripts/` or `resources/`.

---

### H005: Voodoo Constant Explanations

**Rule**: Don't explain concepts Claude already knows.

**Patterns to Detect**:
```
"JSON (JavaScript Object Notation)"
"API (Application Programming Interface)"
"what is [common term]"
"[term] stands for"
```

**Check**:
```bash
grep -iE "what is (json|api|rest|http|git|npm|yaml)" SKILL.md
grep -iE "\((javascript object notation|application programming interface)\)" SKILL.md
```

**Fix**: Delete explanations of common concepts.

---

## Medium Severity Rules (Nice to Have)

### M001: Missing Quick Start

**Rule**: SKILL.md should have a Quick Start section.

**Check**:
```bash
grep -qi "quick start\|getting started\|## start" SKILL.md
```

---

### M002: Non-Gerund Directory Name

**Rule**: Action-oriented skills should use gerund form.

**Check**:
```bash
# Directory name should end with -ing or be noun-form
basename "$SKILL_DIR" | grep -E "ing$|reference$|guide$|patterns$"
```

---

### M003: Inconsistent Naming

**Rule**: Directory name and YAML name should correlate.

**Check**:
```bash
DIR_NAME=$(basename "$SKILL_DIR")
YAML_NAME=$(grep "^name:" SKILL.md | cut -d'"' -f2)
# Convert and compare
```

---

### M004: Missing Prerequisites

**Rule**: Skills with dependencies should list prerequisites.

**Check**:
```bash
grep -qi "prerequisite\|requirement\|requires\|needs" SKILL.md
```

---

### M005: No Reference Documentation

**Rule**: Complex skills should link to Level 3 resources.

**Check**:
```bash
# Should have docs/ directory if SKILL.md is substantial
ls docs/ 2>/dev/null
```

---

## Low Severity Rules (Optional)

### L001: Missing Version

**Rule**: Consider adding version to frontmatter.

```yaml
---
name: "My Skill"
description: "..."
version: "1.0.0"
---
```

---

### L002: Trailing Whitespace

**Rule**: Files should not have trailing whitespace.

**Check**:
```bash
grep -n " $" SKILL.md
```

---

### L003: Missing Related Skills

**Rule**: Consider linking to related skills.

---

### L004: No Troubleshooting Section

**Rule**: Complex skills should have troubleshooting guidance.

---

## Validation Script

```bash
#!/bin/bash
# scripts/validate-skill.sh

SKILL_PATH="$1"
ERRORS=0
WARNINGS=0

echo "=== Validating: $SKILL_PATH ==="
echo ""

# C001: YAML frontmatter
if ! head -1 "$SKILL_PATH/SKILL.md" | grep -q "^---$"; then
  echo "[CRITICAL] C001: Missing YAML frontmatter"
  ((ERRORS++))
fi

# C002: Required fields
if ! grep -q "^name:" "$SKILL_PATH/SKILL.md"; then
  echo "[CRITICAL] C002: Missing 'name' field"
  ((ERRORS++))
fi
if ! grep -q "^description:" "$SKILL_PATH/SKILL.md"; then
  echo "[CRITICAL] C002: Missing 'description' field"
  ((ERRORS++))
fi

# C003: Description length
DESC=$(sed -n 's/^description: *"\(.*\)"$/\1/p' "$SKILL_PATH/SKILL.md" | head -1)
if [ ${#DESC} -gt 1024 ]; then
  echo "[CRITICAL] C003: Description exceeds 1024 chars (${#DESC})"
  ((ERRORS++))
fi

# H001: Trigger condition
if ! echo "$DESC" | grep -qiE "use when|invoke for|invoke when"; then
  echo "[HIGH] H001: Missing trigger condition in description"
  ((WARNINGS++))
fi

# H002: File size
LINES=$(wc -l < "$SKILL_PATH/SKILL.md")
if [ "$LINES" -gt 500 ]; then
  echo "[HIGH] H002: SKILL.md exceeds 500 lines ($LINES)"
  ((WARNINGS++))
fi

# H003: Deep nesting
if ls "$SKILL_PATH/docs/"*.md 2>/dev/null | xargs grep -l "\[.*\](.*\.md)" 2>/dev/null; then
  echo "[HIGH] H003: Deep reference nesting detected"
  ((WARNINGS++))
fi

# M001: Quick Start
if ! grep -qi "quick start" "$SKILL_PATH/SKILL.md"; then
  echo "[MEDIUM] M001: Missing Quick Start section"
fi

# M004: Prerequisites
SKILL_LINES=$(wc -l < "$SKILL_PATH/SKILL.md")
if [ "$SKILL_LINES" -gt 100 ] && ! grep -qi "prerequisite" "$SKILL_PATH/SKILL.md"; then
  echo "[MEDIUM] M004: Consider adding Prerequisites section"
fi

echo ""
echo "=== Results ==="
echo "Critical Errors: $ERRORS"
echo "Warnings: $WARNINGS"

if [ "$ERRORS" -gt 0 ]; then
  echo "Status: FAILED"
  exit 1
else
  echo "Status: PASSED"
  exit 0
fi
```

---

## Validation Report Format

```json
{
  "skill": "my-skill",
  "path": "/Users/x/.claude/skills/my-skill",
  "timestamp": "2025-01-15T10:30:00Z",
  "status": "failed",
  "summary": {
    "critical": 1,
    "high": 2,
    "medium": 3,
    "low": 1
  },
  "violations": [
    {
      "code": "C003",
      "severity": "critical",
      "message": "Description exceeds 1024 chars",
      "current": 1847,
      "limit": 1024,
      "location": "frontmatter.description"
    },
    {
      "code": "H001",
      "severity": "high",
      "message": "Missing trigger condition",
      "suggestion": "Add 'Use when...' clause to description"
    },
    {
      "code": "H002",
      "severity": "high",
      "message": "SKILL.md exceeds 500 lines",
      "current": 687,
      "limit": 500,
      "suggestion": "Extract content to docs/"
    }
  ],
  "score": 45,
  "grade": "F"
}
```

---

## Scoring System

| Grade | Score | Criteria |
|-------|-------|----------|
| A+ | 95-100 | 0 critical, 0 high, <= 2 medium |
| A | 90-94 | 0 critical, 0 high, <= 4 medium |
| B | 80-89 | 0 critical, <= 2 high |
| C | 70-79 | 0 critical, <= 4 high |
| D | 60-69 | 0 critical, > 4 high |
| F | 0-59 | Any critical violations |

### Score Calculation

```
Base Score: 100

Deductions:
- Critical violation: -50 each
- High violation: -10 each
- Medium violation: -5 each
- Low violation: -2 each

Minimum score: 0
```
