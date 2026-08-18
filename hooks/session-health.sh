#!/usr/bin/env bash
# SessionStart health check — command-type port of the former prompt hook.
# Prompt-type hooks are not supported for SessionStart (no conversation
# context exists at startup), so the five checks run as shell tests here.
# Prints nothing when healthy; stdout becomes session context on issues.
set -u

CFG="$HOME/.assistant-skills/config.yaml"
VENV="$HOME/.assistant-skills-venv"
VPY="$VENV/bin/python"
out=""
note() { out="${out}- $1\n"; }

# 1. No config = this machine never opted into the shared-venv workflow.
# Stay completely quiet; /assistant-skills-setup and the plugin docs cover
# discovery, and a per-session nag on non-opted-in machines is just noise.
if [ ! -f "$CFG" ]; then
  exit 0
fi

# 2. Shared venv present
if [ ! -x "$VPY" ]; then
  note "Shared venv missing. Run /assistant-skills-setup to recreate."
fi

# 3. claude-as PATH tip
case ":$PATH:" in
  *":$VENV/bin:"*) : ;;
  *) note "Tip: Use claude-as instead of claude to run with Assistant Skills dependencies." ;;
esac

# 4. Library importable (via the shared venv; check 2 already covers a missing venv)
if [ -x "$VPY" ] && ! "$VPY" -c 'import assistant_skills_lib' >/dev/null 2>&1; then
  note "assistant_skills_lib is not importable. Run /assistant-skills-setup."
fi

# 5. Requirements drift → auto-update, then record the new hash
REQ="${CLAUDE_PLUGIN_ROOT:-}/requirements.txt"
if [ -f "$REQ" ] && [ -f "$CFG" ] && [ -x "$VENV/bin/pip" ]; then
  if command -v md5 >/dev/null 2>&1; then
    have=$(md5 -q "$REQ")
  else
    have=$(md5sum "$REQ" | cut -d' ' -f1)
  fi
  want=$(sed -n 's/^combined_requirements_hash:[[:space:]]*//p' "$CFG" | head -1)
  if [ "$have" != "$want" ]; then
    if "$VENV/bin/pip" install -r "$REQ" --upgrade --quiet >/dev/null 2>&1; then
      if grep -q '^combined_requirements_hash:' "$CFG"; then
        sed "s|^combined_requirements_hash:.*|combined_requirements_hash: $have|" "$CFG" > "$CFG.tmp" \
          && mv "$CFG.tmp" "$CFG"
      else
        printf 'combined_requirements_hash: %s\n' "$have" >> "$CFG"
      fi
      note "Dependencies updated automatically."
    else
      note "Dependency update failed. Run /assistant-skills-setup."
    fi
  fi
fi

if [ -n "$out" ]; then
  printf 'Assistant Skills health check:\n%b' "$out"
fi
exit 0
