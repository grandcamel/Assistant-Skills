---
name: safe-mode
description: This skill should be used when the user wants to run Claude with risk-based permission enforcement, configure safe mode settings, create permission blocks for SAFEGUARDS.md files, or understand how to restrict CLI operations based on risk levels. Use when asked about "safe mode", "permission enforcement", "risk levels", "claude-safe", or "restricting dangerous commands".
---

# Safe Mode

Risk-based permission enforcement wrapper for Claude CLI. Restricts CLI operations based on configurable risk thresholds by parsing permission blocks from plugin SAFEGUARDS.md files.

## Quick Start

```bash
# Run with auto-discovery at safe level (read-only operations only)
claude-safe -d

# Run at caution level (allows creates/updates)
claude-safe -d -l caution

# Preview permissions without running (dry-run)
claude-safe -d -n -v

# Specify plugins manually
claude-safe -l warning -p "/path/to/plugin1:/path/to/plugin2"
```

## Risk Levels

Operations are classified into four cumulative risk levels:

| Level | Value | Description | Typical Operations |
|-------|:-----:|-------------|-------------------|
| `safe` | 0 | Read-only, no data modification | search, list, get, view, status |
| `caution` | 1 | Modifiable but easily reversible | create, update, enable, disable |
| `warning` | 2 | Destructive but potentially recoverable | delete (single items) |
| `danger` | 3 | **IRREVERSIBLE** data loss | bulk delete, drop, purge, uninstall |

**Threshold Logic**: Operations with `risk_value <= threshold` go to `allow[]`, operations with `risk_value > threshold` go to `deny[]`.

## CLI Reference

```
claude-safe [OPTIONS] [-- CLAUDE_ARGS...]

Options:
  -d, --discover        Auto-discover plugins from ~/.claude/plugins/cache/
  -l, --level LEVEL     Risk level: safe|caution|warning|danger (default: safe)
  -p, --plugins DIRS    Colon-separated plugin directories
  -n, --dry-run         Preview permissions without running claude
  -v, --verbose         Debug output
  -h, --help            Show help message

Environment Variables:
  CLAUDE_SAFE_LEVEL     Default risk level (overridden by -l)
  CLAUDE_SAFE_PLUGINS   Default plugin directories (overridden by -p)
  CLAUDE_HOME           Claude config directory (default: ~/.claude)
```

## Adding Permission Blocks

Add a YAML permission block to your plugin's SAFEGUARDS.md file:

```markdown
<!-- PERMISSIONS
permissions:
  cli: your-cli-name
  operations:
    - pattern: "your-cli list *"
      risk: safe
    - pattern: "your-cli create *"
      risk: caution
    - pattern: "your-cli delete *"
      risk: warning
    - pattern: "your-cli drop *"
      risk: danger
-->
```

**SAFEGUARDS.md Search Order**:
1. `{plugin}/skills/shared/docs/SAFEGUARDS.md`
2. `{plugin}/docs/SAFEGUARDS.md`
3. `{plugin}/.claude/SAFEGUARDS.md`
4. `{plugin}/SAFEGUARDS.md`

## Pattern Format

Patterns use simple wildcards and convert to Bash() permission format:

| Pattern | Converted To |
|---------|--------------|
| `splunk-as search *` | `Bash(splunk-as search *)` |
| `glab mr list *` | `Bash(glab mr list *)` |
| `confluence page delete *` | `Bash(confluence page delete *)` |

## Usage Examples

### Production Safety (Default)
```bash
# Only allow read operations
claude-safe -d
```

### Development Mode
```bash
# Allow creates and updates
claude-safe -d -l caution
```

### Testing Mode
```bash
# Allow deletes (but not bulk/purge)
claude-safe -d -l warning
```

### Full Access (Use with Caution)
```bash
# Allow all operations including dangerous ones
claude-safe -d -l danger
```

### Preview Before Running
```bash
# See what would be allowed/denied
claude-safe -d -n -v -l caution
```

### Pass Arguments to Claude
```bash
# Use specific model
claude-safe -d -l caution -- --model sonnet

# Start with a prompt
claude-safe -d -- "Help me search for errors"
```

## Dependencies

- bash 4.0+
- yq (YAML parser)
- jq (JSON processor)

Install on macOS:
```bash
brew install yq jq
```

## Integration with Existing Plugins

The following plugins have permission blocks in their SAFEGUARDS.md:

| Plugin | CLI | Safe Ops | Danger Ops |
|--------|-----|----------|------------|
| Splunk-Assistant-Skills | `splunk-as` | search, metadata, list | app uninstall, kvstore drop |
| Jira-Assistant-Skills | `jira-as` | issue get, search | bulk delete, project delete |
| GitLab-Assistant-Skills | `glab` | mr list, issue view | repo delete |
| Confluence-Assistant-Skills | `confluence` | page get, search | space delete, purge |

## See Also

- [Permission Block Template](docs/PERMISSION_TEMPLATE.md) - Copy-paste template for new plugins
- [Risk Level Guidelines](docs/RISK_GUIDELINES.md) - How to classify operations
