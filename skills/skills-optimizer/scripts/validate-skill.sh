#!/bin/bash
# validate-skill.sh - Validate a skill against progressive disclosure rules

set -e

SKILL_PATH="$1"
VERBOSE="${2:-false}"

if [ -z "$SKILL_PATH" ]; then
  echo "Usage: $0 <skill-path> [verbose]"
  echo "Example: $0 ~/.claude/skills/my-skill"
  echo "         $0 ~/.claude/skills/my-skill true"
  exit 1
fi

SKILL_MD="$SKILL_PATH/SKILL.md"

if [ ! -f "$SKILL_MD" ]; then
  echo "Error: SKILL.md not found in $SKILL_PATH"
  exit 1
fi

SKILL_NAME=$(basename "$SKILL_PATH")

echo "Validating: $SKILL_NAME"
echo "----------------------------------------"

ERRORS=0
WARNINGS=0
INFO=0

log_error() {
  echo "[ERROR] $1"
  ERRORS=$((ERRORS + 1))
}

log_warning() {
  echo "[WARN]  $1"
  WARNINGS=$((WARNINGS + 1))
}

log_info() {
  if [ "$VERBOSE" = "true" ]; then
    echo "[INFO]  $1"
  fi
  INFO=$((INFO + 1))
}

log_pass() {
  if [ "$VERBOSE" = "true" ]; then
    echo "[PASS]  $1"
  fi
}

# ===========================================
# CRITICAL CHECKS (C001-C005)
# ===========================================

# C001: YAML frontmatter exists
if head -1 "$SKILL_MD" | grep -q "^---$"; then
  log_pass "C001: YAML frontmatter present"
else
  log_error "C001: Missing YAML frontmatter (must start with ---)"
fi

# C002: Required fields
if grep -q "^name:" "$SKILL_MD"; then
  log_pass "C002a: 'name' field present"
else
  log_error "C002a: Missing required 'name' field"
fi

if grep -q "^description:" "$SKILL_MD"; then
  log_pass "C002b: 'description' field present"
else
  log_error "C002b: Missing required 'description' field"
fi

# C003: Description length
DESC=$(grep "^description:" "$SKILL_MD" | sed 's/description: *"\(.*\)"/\1/' | head -1)
DESC_LEN=${#DESC}
if [ "$DESC_LEN" -le 1024 ]; then
  log_pass "C003: Description length OK ($DESC_LEN/1024)"
else
  log_error "C003: Description exceeds 1024 chars ($DESC_LEN)"
fi

# C004: Name length
NAME=$(grep "^name:" "$SKILL_MD" | sed 's/name: *"\(.*\)"/\1/' | head -1)
NAME_LEN=${#NAME}
if [ "$NAME_LEN" -le 64 ]; then
  log_pass "C004: Name length OK ($NAME_LEN/64)"
else
  log_error "C004: Name exceeds 64 chars ($NAME_LEN)"
fi

# C005: Directory structure (SKILL.md at skill root)
if [ -f "$SKILL_PATH/SKILL.md" ]; then
  log_pass "C005: SKILL.md at correct location"
else
  log_error "C005: SKILL.md not at skill root"
fi

# ===========================================
# HIGH SEVERITY CHECKS (H001-H005)
# ===========================================

# H001: Trigger condition in description
if echo "$DESC" | grep -qiE "use when|invoke for|invoke when|triggers on"; then
  log_pass "H001: Trigger condition present"
else
  log_warning "H001: Missing trigger condition (add 'Use when...')"
fi

# H002: SKILL.md size
TOTAL_LINES=$(wc -l < "$SKILL_MD")
YAML_END=$(grep -n "^---$" "$SKILL_MD" | sed -n '2p' | cut -d: -f1 2>/dev/null || echo "3")
if [ -z "$YAML_END" ]; then YAML_END=3; fi
BODY_LINES=$((TOTAL_LINES - YAML_END))

if [ "$BODY_LINES" -le 500 ]; then
  log_pass "H002: Body size OK ($BODY_LINES/500 lines)"
else
  log_warning "H002: Body exceeds 500 lines ($BODY_LINES)"
fi

# H003: Deep nesting
if [ -d "$SKILL_PATH/docs" ]; then
  NESTED_FILES=$(grep -l "\[.*\](.*\.md)" "$SKILL_PATH/docs/"*.md 2>/dev/null || true)
  if [ -z "$NESTED_FILES" ]; then
    log_pass "H003: No deep nesting in docs/"
  else
    log_warning "H003: Deep nesting detected - docs reference other docs"
    if [ "$VERBOSE" = "true" ]; then
      echo "$NESTED_FILES" | while read f; do
        echo "        -> $(basename "$f")"
      done
    fi
  fi
else
  log_info "H003: No docs/ directory to check"
fi

# H004: Large inline code blocks
LARGE_BLOCKS=0
IN_BLOCK=false
BLOCK_LINES=0
while IFS= read -r line; do
  if echo "$line" | grep -q '```'; then
    if [ "$IN_BLOCK" = true ]; then
      if [ "$BLOCK_LINES" -gt 50 ]; then
        ((LARGE_BLOCKS++))
      fi
      IN_BLOCK=false
      BLOCK_LINES=0
    else
      IN_BLOCK=true
    fi
  elif [ "$IN_BLOCK" = true ]; then
    ((BLOCK_LINES++))
  fi
done < "$SKILL_MD"

if [ "$LARGE_BLOCKS" -eq 0 ]; then
  log_pass "H004: No large code blocks (>50 lines)"
else
  log_warning "H004: Found $LARGE_BLOCKS code block(s) exceeding 50 lines"
fi

# H005: Voodoo constants
VOODOO=$(grep -ciE "what is (json|api|rest|http|git|npm|yaml|pdf|csv)|javascript object notation|application programming interface" "$SKILL_MD" 2>/dev/null | head -1 || echo "0")
if [ -z "$VOODOO" ]; then VOODOO=0; fi
if [ "$VOODOO" -eq 0 ]; then
  log_pass "H005: No voodoo constants detected"
else
  log_warning "H005: Found $VOODOO potential voodoo constant(s)"
fi

# ===========================================
# ROUTER SKILL CHECKS (R001-R005)
# ===========================================

# Detect if this is a router/hub skill
IS_ROUTER=false
if grep -qiE "hub|router|routes to.*skills|routing|specialized skills" "$SKILL_MD"; then
  IS_ROUTER=true
  log_info "Detected router/hub skill - running router checks"
fi

if [ "$IS_ROUTER" = true ]; then
  # R001: Quick Reference table with Risk column
  if grep -qE "\| Risk \||\|:---*:\|" "$SKILL_MD" && grep -q "I want to" "$SKILL_MD"; then
    log_pass "R001: Quick Reference table with Risk column present"
  else
    log_warning "R001: Router missing Quick Reference table with Risk levels"
  fi

  # R002: Risk legend
  if grep -qiE "risk legend|read-only.*safe.*destructive|⚠️.*high-risk" "$SKILL_MD"; then
    log_pass "R002: Risk legend present"
  else
    log_warning "R002: Router missing Risk Legend (add: **Risk Legend**: - Read-only | ⚠️ Destructive | ⚠️⚠️ High-risk)"
  fi

  # R003: Negative triggers table
  if grep -qiE "negative trigger|does not handle|route to instead" "$SKILL_MD"; then
    log_pass "R003: Negative triggers documented"
  else
    log_warning "R003: Router missing Negative Triggers section"
  fi

  # R004: Disambiguation examples
  if grep -qiE "disambiguation|could mean|clarif|ask:.*\"" "$SKILL_MD"; then
    log_pass "R004: Disambiguation examples present"
  else
    log_warning "R004: Router missing disambiguation examples"
  fi

  # R005: Context awareness
  if grep -qiE "pronoun|context|\"it\"|\"that\"|\"them\"" "$SKILL_MD"; then
    log_pass "R005: Context awareness documented"
  else
    log_info "R005: Consider documenting context awareness (pronoun resolution)"
  fi
fi

# ===========================================
# RISK LEVEL CHECKS (K001-K003) - For all skills with scripts
# ===========================================

# K001: Destructive scripts have risk indicators
if [ -d "$SKILL_PATH/scripts" ]; then
  HAS_DESTRUCTIVE=$(ls "$SKILL_PATH/scripts/" 2>/dev/null | grep -ciE "delete|remove|bulk|purge" || echo "0")
  if [ "$HAS_DESTRUCTIVE" -gt 0 ]; then
    if grep -q "⚠️" "$SKILL_MD"; then
      log_pass "K001: Risk indicators present for destructive operations"
    else
      log_warning "K001: Destructive scripts found but no risk indicators (⚠️) in SKILL.md"
    fi
  else
    log_pass "K001: No destructive scripts detected"
  fi

  # K002: Bulk operations marked as high-risk
  HAS_BULK=$(ls "$SKILL_PATH/scripts/" 2>/dev/null | grep -ciE "bulk" || echo "0")
  if [ "$HAS_BULK" -gt 0 ]; then
    if grep -q "⚠️⚠️" "$SKILL_MD"; then
      log_pass "K002: Bulk operations marked as high-risk (⚠️⚠️)"
    else
      log_warning "K002: Bulk scripts found but not marked as high-risk (⚠️⚠️)"
    fi
  else
    log_pass "K002: No bulk operations detected"
  fi

  # K003: Dry-run mentioned for high-risk operations
  if grep -q "⚠️⚠️" "$SKILL_MD"; then
    if grep -qiE "dry.run|--dry-run|preview" "$SKILL_MD"; then
      log_pass "K003: Dry-run documented for high-risk operations"
    else
      log_warning "K003: High-risk operations should document --dry-run option"
    fi
  fi
fi

# ===========================================
# MEDIUM SEVERITY CHECKS (M001-M005)
# ===========================================

# M001: Quick Start section
if grep -qi "quick start\|## start\|getting started" "$SKILL_MD"; then
  log_pass "M001: Quick Start section present"
else
  log_info "M001: Consider adding Quick Start section"
fi

# M002: Gerund directory name
DIR_NAME=$(basename "$SKILL_PATH")
if echo "$DIR_NAME" | grep -qE "ing$|ing-|reference$|guide$|patterns$"; then
  log_pass "M002: Directory name follows conventions"
else
  log_info "M002: Consider gerund form for directory name (e.g., analyzing-x)"
fi

# M003: Prerequisites (for non-trivial skills)
if [ "$BODY_LINES" -gt 100 ]; then
  if grep -qi "prerequisite\|requirements\|## requirements" "$SKILL_MD"; then
    log_pass "M003: Prerequisites section present"
  else
    log_info "M003: Consider adding Prerequisites section"
  fi
fi

# M004: Reference documentation
if [ "$BODY_LINES" -gt 200 ]; then
  if [ -d "$SKILL_PATH/docs" ]; then
    log_pass "M004: Has docs/ for reference content"
  else
    log_info "M004: Consider extracting content to docs/"
  fi
fi

# ===========================================
# SUMMARY
# ===========================================

echo ""
echo "=========================================="
echo "  Validation Summary"
echo "=========================================="
echo ""
echo "Errors:   $ERRORS"
echo "Warnings: $WARNINGS"
if [ "$VERBOSE" = "true" ]; then
  echo "Info:     $INFO"
fi
echo ""

if [ "$ERRORS" -gt 0 ]; then
  echo "Status: FAILED"
  echo "Fix critical errors before publishing."
  exit 1
elif [ "$WARNINGS" -gt 0 ]; then
  echo "Status: PASSED (with warnings)"
  echo "Consider addressing warnings for optimal performance."
  exit 0
else
  echo "Status: PASSED"
  echo "Skill is optimized for progressive disclosure."
  exit 0
fi
