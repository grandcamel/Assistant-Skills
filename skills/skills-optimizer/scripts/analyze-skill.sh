#!/bin/bash
# analyze-skill.sh - Analyze a single skill for token efficiency and progressive disclosure compliance

set -e

SKILL_PATH="$1"

if [ -z "$SKILL_PATH" ]; then
  echo "Usage: $0 <skill-path>"
  echo "Example: $0 ~/.claude/skills/my-skill"
  exit 1
fi

SKILL_MD="$SKILL_PATH/SKILL.md"

if [ ! -f "$SKILL_MD" ]; then
  echo "Error: SKILL.md not found in $SKILL_PATH"
  exit 1
fi

SKILL_NAME=$(basename "$SKILL_PATH")

echo "=========================================="
echo "  Skill Analysis: $SKILL_NAME"
echo "=========================================="
echo ""

# Extract YAML frontmatter
YAML_START=$(grep -n "^---$" "$SKILL_MD" | head -1 | cut -d: -f1)
YAML_END=$(grep -n "^---$" "$SKILL_MD" | sed -n '2p' | cut -d: -f1)

if [ -z "$YAML_START" ] || [ -z "$YAML_END" ]; then
  echo "[CRITICAL] No valid YAML frontmatter found!"
  exit 1
fi

# Extract name and description
NAME=$(sed -n "${YAML_START},${YAML_END}p" "$SKILL_MD" | grep "^name:" | sed 's/name: *"\(.*\)"/\1/' | head -1)
DESC=$(sed -n "${YAML_START},${YAML_END}p" "$SKILL_MD" | grep "^description:" | sed 's/description: *"\(.*\)"/\1/' | head -1)

# If description spans multiple lines, try alternate extraction
if [ -z "$DESC" ]; then
  DESC=$(sed -n "${YAML_START},${YAML_END}p" "$SKILL_MD" | grep -A5 "^description:" | tr '\n' ' ' | sed 's/description: *"\([^"]*\)".*/\1/')
fi

NAME_LEN=${#NAME}
DESC_LEN=${#DESC}

echo "=== Level 1: Metadata ==="
echo ""
echo "Name: \"$NAME\""
echo "  Length: $NAME_LEN / 64 chars"
if [ "$NAME_LEN" -gt 64 ]; then
  echo "  [WARNING] Exceeds limit!"
elif [ "$NAME_LEN" -gt 50 ]; then
  echo "  [OK] Near limit"
else
  echo "  [GOOD] Within limit"
fi
echo ""

echo "Description: \"${DESC:0:80}...\""
echo "  Length: $DESC_LEN / 1024 chars"
if [ "$DESC_LEN" -gt 1024 ]; then
  echo "  [CRITICAL] Exceeds limit!"
elif [ "$DESC_LEN" -gt 800 ]; then
  echo "  [WARNING] Near limit"
else
  echo "  [GOOD] Within limit"
fi

# Check for trigger condition
if echo "$DESC" | grep -qiE "use when|invoke for|invoke when|triggers on"; then
  echo "  [GOOD] Has trigger condition"
else
  echo "  [WARNING] Missing trigger condition (add 'Use when...')"
fi
echo ""

# Level 2 Analysis
echo "=== Level 2: SKILL.md Body ==="
echo ""

TOTAL_LINES=$(wc -l < "$SKILL_MD")
BODY_LINES=$((TOTAL_LINES - YAML_END))
WORD_COUNT=$(tail -n +$((YAML_END + 1)) "$SKILL_MD" | wc -w)
EST_TOKENS=$((WORD_COUNT * 4 / 3))

echo "Total Lines: $TOTAL_LINES"
echo "Body Lines: $BODY_LINES / 500 max"
if [ "$BODY_LINES" -gt 500 ]; then
  echo "  [WARNING] Exceeds recommended limit"
elif [ "$BODY_LINES" -gt 300 ]; then
  echo "  [OK] Approaching limit"
else
  echo "  [GOOD] Within limit"
fi
echo ""

echo "Word Count: $WORD_COUNT"
echo "Est. Tokens: ~$EST_TOKENS"
if [ "$EST_TOKENS" -gt 4000 ]; then
  echo "  [WARNING] High token count - consider extracting content"
elif [ "$EST_TOKENS" -gt 2000 ]; then
  echo "  [OK] Moderate token count"
else
  echo "  [GOOD] Efficient token usage"
fi
echo ""

# Code block analysis
CODE_BLOCKS=$(grep -c '```' "$SKILL_MD" 2>/dev/null || echo 0)
CODE_BLOCKS=$((CODE_BLOCKS / 2))
echo "Code Blocks: $CODE_BLOCKS"
if [ "$CODE_BLOCKS" -gt 10 ]; then
  echo "  [WARNING] Many code blocks - consider extracting to scripts/"
fi
echo ""

# Check for Quick Start
if grep -qi "quick start" "$SKILL_MD"; then
  echo "[GOOD] Has Quick Start section"
else
  echo "[SUGGESTION] Add Quick Start section"
fi

# Check for Prerequisites
if grep -qi "prerequisite" "$SKILL_MD"; then
  echo "[GOOD] Has Prerequisites section"
else
  echo "[SUGGESTION] Consider adding Prerequisites"
fi
echo ""

# Level 3 Analysis
echo "=== Level 3: Nested Resources ==="
echo ""

if [ -d "$SKILL_PATH/docs" ]; then
  DOC_COUNT=$(ls "$SKILL_PATH/docs/"*.md 2>/dev/null | wc -l)
  echo "Documentation files: $DOC_COUNT"
  ls "$SKILL_PATH/docs/"*.md 2>/dev/null | while read f; do
    echo "  - $(basename "$f")"
  done
else
  echo "No docs/ directory"
fi
echo ""

if [ -d "$SKILL_PATH/scripts" ]; then
  SCRIPT_COUNT=$(ls "$SKILL_PATH/scripts/"* 2>/dev/null | wc -l)
  echo "Script files: $SCRIPT_COUNT"
  ls "$SKILL_PATH/scripts/"* 2>/dev/null | while read f; do
    echo "  - $(basename "$f")"
  done
else
  echo "No scripts/ directory"
fi
echo ""

if [ -d "$SKILL_PATH/resources" ]; then
  echo "Resources directory: Present"
  find "$SKILL_PATH/resources" -type f | head -5 | while read f; do
    echo "  - ${f#$SKILL_PATH/}"
  done
else
  echo "No resources/ directory"
fi
echo ""

# Deep nesting check
echo "=== Deep Nesting Check ==="
if [ -d "$SKILL_PATH/docs" ]; then
  NESTED=$(grep -l "\[.*\](.*\.md)" "$SKILL_PATH/docs/"*.md 2>/dev/null || true)
  if [ -n "$NESTED" ]; then
    echo "[WARNING] Deep nesting detected in:"
    echo "$NESTED" | while read f; do
      echo "  - $(basename "$f")"
    done
  else
    echo "[GOOD] No deep nesting found"
  fi
else
  echo "[OK] No docs to check"
fi
echo ""

# Voodoo constant check
echo "=== Voodoo Constants Check ==="
VOODOO=$(grep -iE "what is (json|api|rest|http|git|npm|yaml|pdf|csv)|javascript object notation|application programming interface" "$SKILL_MD" 2>/dev/null || true)
if [ -n "$VOODOO" ]; then
  echo "[WARNING] Potential voodoo constants (concepts Claude already knows):"
  echo "$VOODOO" | head -3 | while read line; do
    echo "  - ${line:0:60}..."
  done
else
  echo "[GOOD] No obvious voodoo constants"
fi
echo ""

# Calculate score
SCORE=100

# Critical deductions
if [ "$DESC_LEN" -gt 1024 ]; then SCORE=$((SCORE - 50)); fi
if [ "$NAME_LEN" -gt 64 ]; then SCORE=$((SCORE - 50)); fi

# High deductions
if ! echo "$DESC" | grep -qiE "use when|invoke for"; then SCORE=$((SCORE - 10)); fi
if [ "$BODY_LINES" -gt 500 ]; then SCORE=$((SCORE - 10)); fi
if [ -n "$NESTED" ]; then SCORE=$((SCORE - 10)); fi
if [ -n "$VOODOO" ]; then SCORE=$((SCORE - 10)); fi

# Medium deductions
if ! grep -qi "quick start" "$SKILL_MD"; then SCORE=$((SCORE - 5)); fi
if [ "$EST_TOKENS" -gt 4000 ]; then SCORE=$((SCORE - 5)); fi

# Ensure minimum 0
if [ "$SCORE" -lt 0 ]; then SCORE=0; fi

# Determine grade
if [ "$SCORE" -ge 95 ]; then GRADE="A+"
elif [ "$SCORE" -ge 90 ]; then GRADE="A"
elif [ "$SCORE" -ge 80 ]; then GRADE="B"
elif [ "$SCORE" -ge 70 ]; then GRADE="C"
elif [ "$SCORE" -ge 60 ]; then GRADE="D"
else GRADE="F"
fi

echo "=========================================="
echo "  FINAL SCORE: $SCORE / 100 ($GRADE)"
echo "=========================================="
