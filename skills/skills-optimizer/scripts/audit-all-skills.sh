#!/bin/bash
# audit-all-skills.sh - Audit all skills in a directory for token efficiency

set -e

SKILLS_DIR="${1:-$HOME/.claude/skills}"
OUTPUT_FILE="${2:-audit-report.json}"

if [ ! -d "$SKILLS_DIR" ]; then
  echo "Error: Skills directory not found: $SKILLS_DIR"
  exit 1
fi

echo "=========================================="
echo "  Skills Audit Report"
echo "  Directory: $SKILLS_DIR"
echo "=========================================="
echo ""

# Initialize counters
TOTAL_SKILLS=0
TOTAL_TOKENS=0
CRITICAL_COUNT=0
WARNING_COUNT=0

# JSON output start
echo "[" > "$OUTPUT_FILE"
FIRST=true

# Process each skill
for SKILL_PATH in "$SKILLS_DIR"/*/; do
  if [ ! -f "$SKILL_PATH/SKILL.md" ]; then
    continue
  fi

  SKILL_NAME=$(basename "$SKILL_PATH")
  SKILL_MD="$SKILL_PATH/SKILL.md"

  ((TOTAL_SKILLS++))

  # Extract metrics
  YAML_END=$(grep -n "^---$" "$SKILL_MD" | sed -n '2p' | cut -d: -f1 2>/dev/null || echo "3")
  if [ -z "$YAML_END" ]; then YAML_END=3; fi

  DESC=$(grep "^description:" "$SKILL_MD" | sed 's/description: *"\(.*\)"/\1/' | head -1)
  DESC_LEN=${#DESC}

  TOTAL_LINES=$(wc -l < "$SKILL_MD")
  BODY_LINES=$((TOTAL_LINES - YAML_END))
  WORD_COUNT=$(tail -n +$((YAML_END + 1)) "$SKILL_MD" | wc -w)
  EST_TOKENS=$((WORD_COUNT * 4 / 3))

  TOTAL_TOKENS=$((TOTAL_TOKENS + EST_TOKENS))

  # Check violations
  VIOLATIONS=""
  SCORE=100

  # Critical checks
  if [ "$DESC_LEN" -gt 1024 ]; then
    VIOLATIONS="$VIOLATIONS,\"description_too_long\""
    SCORE=$((SCORE - 50))
    ((CRITICAL_COUNT++))
  fi

  # High severity checks
  if ! echo "$DESC" | grep -qiE "use when|invoke for|invoke when"; then
    VIOLATIONS="$VIOLATIONS,\"missing_trigger\""
    SCORE=$((SCORE - 10))
    ((WARNING_COUNT++))
  fi

  if [ "$BODY_LINES" -gt 500 ]; then
    VIOLATIONS="$VIOLATIONS,\"body_too_long\""
    SCORE=$((SCORE - 10))
    ((WARNING_COUNT++))
  fi

  # Medium checks
  if ! grep -qi "quick start" "$SKILL_MD"; then
    VIOLATIONS="$VIOLATIONS,\"no_quickstart\""
    SCORE=$((SCORE - 5))
  fi

  if [ "$EST_TOKENS" -gt 4000 ]; then
    VIOLATIONS="$VIOLATIONS,\"high_tokens\""
    SCORE=$((SCORE - 5))
  fi

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

  # Remove leading comma from violations
  VIOLATIONS="${VIOLATIONS#,}"
  if [ -z "$VIOLATIONS" ]; then
    VIOLATIONS="[]"
  else
    VIOLATIONS="[$VIOLATIONS]"
  fi

  # Print summary line
  printf "%-35s %4d tokens  %3d/100 (%s)\n" "$SKILL_NAME" "$EST_TOKENS" "$SCORE" "$GRADE"

  # Append to JSON
  if [ "$FIRST" = true ]; then
    FIRST=false
  else
    echo "," >> "$OUTPUT_FILE"
  fi

  cat >> "$OUTPUT_FILE" << EOF
  {
    "skill": "$SKILL_NAME",
    "path": "$SKILL_PATH",
    "metrics": {
      "descriptionLength": $DESC_LEN,
      "bodyLines": $BODY_LINES,
      "wordCount": $WORD_COUNT,
      "estimatedTokens": $EST_TOKENS
    },
    "violations": $VIOLATIONS,
    "score": $SCORE,
    "grade": "$GRADE"
  }
EOF

done

# Close JSON array
echo "]" >> "$OUTPUT_FILE"

echo ""
echo "=========================================="
echo "  Summary"
echo "=========================================="
echo ""
echo "Total Skills Analyzed: $TOTAL_SKILLS"
echo "Total Estimated Tokens: $TOTAL_TOKENS"
echo "Average Tokens/Skill: $((TOTAL_TOKENS / TOTAL_SKILLS))"
echo ""
echo "Critical Issues: $CRITICAL_COUNT"
echo "Warnings: $WARNING_COUNT"
echo ""
echo "Report saved to: $OUTPUT_FILE"

# Calculate overall score
if [ "$CRITICAL_COUNT" -eq 0 ] && [ "$WARNING_COUNT" -le 5 ]; then
  echo "Overall Status: HEALTHY"
elif [ "$CRITICAL_COUNT" -eq 0 ]; then
  echo "Overall Status: NEEDS ATTENTION"
else
  echo "Overall Status: CRITICAL ISSUES FOUND"
fi
