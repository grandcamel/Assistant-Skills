# Token Counting Guide

## Overview

Accurate token measurement is critical for optimizing skill context usage. This guide covers measurement techniques and budgets.

---

## Quick Estimation

### Rule of Thumb
- **1 token ~ 4 characters** (English text)
- **1 token ~ 0.75 words**
- **Code**: ~1.5x more tokens than prose (syntax overhead)

### Fast Commands

```bash
# Word count (multiply by 1.33 for token estimate)
wc -w SKILL.md

# Character count (divide by 4 for token estimate)
wc -c SKILL.md

# Line count (sanity check)
wc -l SKILL.md
```

---

## Accurate Token Counting

### Using tiktoken (Recommended)

```bash
# Install
pip install tiktoken

# Count tokens
python3 -c "
import tiktoken
enc = tiktoken.get_encoding('cl100k_base')
with open('SKILL.md') as f:
    tokens = enc.encode(f.read())
print(f'Tokens: {len(tokens)}')
"
```

### Using Node.js

```javascript
// npm install gpt-tokenizer
const { encode } = require('gpt-tokenizer');
const fs = require('fs');

const content = fs.readFileSync('SKILL.md', 'utf8');
console.log('Tokens:', encode(content).length);
```

### Batch Analysis Script

```bash
#!/bin/bash
# scripts/count-tokens.sh

for skill in ~/.claude/skills/*/SKILL.md; do
  name=$(dirname "$skill" | xargs basename)
  words=$(wc -w < "$skill")
  tokens=$((words * 4 / 3))  # Rough estimate
  echo "$name: ~$tokens tokens"
done | sort -t: -k2 -n -r
```

---

## Token Budgets

### Level 1 (Metadata)

| Component | Target | Max |
|-----------|--------|-----|
| name | 10-20 tokens | 30 tokens |
| description | 50-150 tokens | 250 tokens |
| **Total per skill** | 60-170 tokens | 280 tokens |

**At scale**:
- 50 skills: ~3,000-8,500 tokens
- 100 skills: ~6,000-17,000 tokens
- 200 skills: ~12,000-34,000 tokens

### Level 2 (SKILL.md Body)

| Content Type | Target | Max |
|--------------|--------|-----|
| Overview | 100-200 tokens | 400 tokens |
| Prerequisites | 50-100 tokens | 200 tokens |
| Quick Start | 200-400 tokens | 600 tokens |
| Core Workflow | 500-1000 tokens | 2000 tokens |
| References | 50-100 tokens | 200 tokens |
| **Total** | 1000-2000 tokens | 4000 tokens |

### Level 3 (Nested Resources)

No hard limits - loaded on demand. However:
- Single file read: Prefer < 50KB
- Claude may preview large files (head -100)
- Split very large docs into focused sections

---

## Identifying Token Waste

### High-Token Anti-Patterns

| Pattern | Token Cost | Fix |
|---------|------------|-----|
| Inline 100-line code block | ~500 tokens | Move to scripts/ |
| Explaining "what is JSON" | ~100 tokens | Delete |
| Verbose step descriptions | ~200 tokens | Use bullet points |
| Redundant examples | ~300 tokens | Keep 1-2, link rest |
| ASCII art diagrams | ~100-300 tokens | Use text or omit |

### Token Audit Checklist

```markdown
## Token Audit for [Skill Name]

### Measurements
- [ ] Total SKILL.md tokens: ____
- [ ] Description tokens: ____
- [ ] Largest code block: ____ tokens
- [ ] Total inline code: ____ tokens

### Violations
- [ ] SKILL.md > 4000 tokens
- [ ] Description > 250 tokens
- [ ] Code block > 200 tokens
- [ ] Contains "what is X" explanations
- [ ] Redundant examples

### Savings Identified
- [ ] Move code block X: -____ tokens
- [ ] Delete explanation Y: -____ tokens
- [ ] Consolidate examples: -____ tokens

### Projected After Optimization
- Current: ____ tokens
- Target: ____ tokens
- Savings: ____% reduction
```

---

## Context Window Considerations

### Claude's Context Limits

| Model | Context Window |
|-------|----------------|
| Claude 3.5 Sonnet | 200K tokens |
| Claude 3 Opus | 200K tokens |
| Claude 3 Haiku | 200K tokens |

### Effective Available Context

```
Total Context Window: 200,000 tokens
- System Prompt:        ~2,000 tokens
- Skill Metadata (L1):  ~5,000 tokens (50 skills)
- Active Skill (L2):    ~3,000 tokens
- Conversation History: ~50,000+ tokens
- User Request:         ~1,000 tokens
- Response Space:       ~10,000 tokens
------------------------
Available for work:     ~128,000 tokens
```

**Key insight**: Every token wasted on skill metadata is stolen from conversation history or response quality.

---

## Optimization Strategies

### 1. Aggressive Description Trimming

**Before** (312 tokens):
```yaml
description: "This skill provides a comprehensive framework for analyzing, optimizing, and restructuring existing Claude Code skills to ensure they follow the progressive disclosure pattern, minimize token usage, and maximize context efficiency across all surfaces including Claude.ai, Claude Code CLI, and the Claude API."
```

**After** (89 tokens):
```yaml
description: "Audit and optimize skills for token efficiency. Use when analyzing skill footprint, reformatting verbose skills, or ensuring 3-level disclosure compliance."
```

### 2. Code Block Extraction

**Before** (in SKILL.md):
```markdown
## Setup Script
```python
#!/usr/bin/env python3
import os
import sys
import json
from pathlib import Path
# ... 80 more lines
```

**After** (in SKILL.md):
```markdown
## Setup
Run: `python3 scripts/setup.py`
```

### 3. Reference Consolidation

**Before**:
```markdown
See [Part 1](docs/part1.md)
See [Part 2](docs/part2.md)
See [Part 3](docs/part3.md)
See [Part 4](docs/part4.md)
```

**After**:
```markdown
See [Complete Guide](docs/guide.md) for all details.
```

---

## Measurement Script

```bash
#!/bin/bash
# scripts/measure-tokens.sh

SKILL_PATH="$1"

if [ -z "$SKILL_PATH" ]; then
  echo "Usage: $0 <skill-path>"
  exit 1
fi

SKILL_MD="$SKILL_PATH/SKILL.md"

if [ ! -f "$SKILL_MD" ]; then
  echo "Error: SKILL.md not found in $SKILL_PATH"
  exit 1
fi

# Extract description
DESC=$(sed -n '/^---$/,/^---$/p' "$SKILL_MD" | grep "description:" | cut -d'"' -f2)
DESC_CHARS=${#DESC}
DESC_TOKENS=$((DESC_CHARS / 4))

# Body metrics
BODY=$(sed -n '/^---$/,/^---$/d; p' "$SKILL_MD")
BODY_WORDS=$(echo "$BODY" | wc -w)
BODY_TOKENS=$((BODY_WORDS * 4 / 3))

# Code block analysis
CODE_LINES=$(grep -c '```' "$SKILL_MD")
CODE_BLOCKS=$((CODE_LINES / 2))

echo "=== Token Analysis: $(basename $SKILL_PATH) ==="
echo ""
echo "Level 1 (Description):"
echo "  Characters: $DESC_CHARS / 1024"
echo "  Est. Tokens: ~$DESC_TOKENS"
echo ""
echo "Level 2 (Body):"
echo "  Words: $BODY_WORDS"
echo "  Est. Tokens: ~$BODY_TOKENS"
echo "  Code Blocks: $CODE_BLOCKS"
echo ""
echo "Total Est. Tokens: $((DESC_TOKENS + BODY_TOKENS))"
```
