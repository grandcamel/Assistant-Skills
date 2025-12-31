# Setup Wizard Reference

## Plugin Manifest Schema

The `assistant_skills` section in plugin.json:

```json
{
  "assistant_skills": {
    "requirements": "requirements.txt",
    "env_vars": [
      {
        "name": "ENV_VAR_NAME",
        "description": "Description of what this variable is for",
        "required": true,
        "used_by": ["skill-1", "skill-2"]
      }
    ]
  }
}
```

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `requirements` | string | Yes | Path to requirements.txt relative to plugin root |
| `env_vars` | array | No | List of environment variable definitions |

### Environment Variable Definition

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Environment variable name (e.g., `SPLUNK_TOKEN`) |
| `description` | string | Yes | Human-readable description |
| `required` | boolean | No | If true, warns user when missing. Default: false |
| `used_by` | array | No | List of skill names that use this variable |

## Configuration File Schema

Location: `~/.assistant-skills/config.yaml`

```yaml
# Shared virtual environment path
venv_path: ~/.assistant-skills-venv

# ISO 8601 timestamp of setup completion
setup_completed_at: 2025-12-30T10:00:00Z

# Whether claude-as function was added to shell RC
shell_function_added: true

# Path to modified shell RC file
shell_rc_path: ~/.zshrc

# List of installed Assistant Skills plugins
installed_plugins:
  - name: assistant-skills
    path: /path/to/plugin
    requirements_hash: md5-hash-of-requirements-txt

# Combined hash of all requirements (for change detection)
combined_requirements_hash: combined-md5-hash
```

## Shell Function

The `claude-as` function added to shell RC:

```bash
# Assistant Skills - Claude Code wrapper function
# Runs Claude with the Assistant Skills venv activated
claude-as() {
    VIRTUAL_ENV="$HOME/.assistant-skills-venv" \
    PATH="$HOME/.assistant-skills-venv/bin:$PATH" \
    claude "$@"
}
```

### How It Works

1. Sets `VIRTUAL_ENV` environment variable (standard Python convention)
2. Prepends venv's `bin/` directory to `PATH`
3. Runs `claude` with these environment modifications
4. Child processes (Bash tool calls) inherit the modified PATH
5. Python scripts find the correct interpreter automatically

### Why Not Global Activation?

- User's default shell environment stays clean
- No interference with other Python projects
- Explicit opt-in when using Assistant Skills
- Works consistently across all projects

## Dependency Update Flow

```
SessionStart Hook
       │
       ▼
┌─────────────────────────────┐
│ Compute hash of all         │
│ requirements.txt files      │
└─────────────────────────────┘
       │
       ▼
┌─────────────────────────────┐
│ Compare with stored hash    │
│ in config.yaml              │
└─────────────────────────────┘
       │
       ├─── Match ──► No action
       │
       ▼ Mismatch
┌─────────────────────────────┐
│ Auto-run pip install        │
│ --upgrade --quiet           │
└─────────────────────────────┘
       │
       ▼
┌─────────────────────────────┐
│ Update hash in config.yaml  │
│ Notify user: "Updated"      │
└─────────────────────────────┘
```

## Multiple Plugin Support

When multiple Assistant Skills plugins are installed:

1. Each plugin's `requirements.txt` is collected
2. All requirements are combined and installed in the shared venv
3. Combined hash is stored for change detection
4. Each plugin's individual hash is also stored for granular tracking

### Hash Computation

```bash
# Single file hash
md5sum requirements.txt | cut -d' ' -f1

# Combined hash (sorted for consistency)
cat plugin1/requirements.txt plugin2/requirements.txt | sort | md5sum | cut -d' ' -f1
```

## Platform Notes

### macOS

- Default shell: zsh (`~/.zshrc`)
- Python: Often via Homebrew (`brew install python@3.11`)
- Venv module: Included with Python

### Linux (Ubuntu/Debian)

- Default shell: bash (`~/.bashrc`)
- Python: System package (`sudo apt install python3`)
- Venv module: Separate package (`sudo apt install python3-venv`)

### Linux (RHEL/CentOS/Fedora)

- Default shell: bash (`~/.bashrc`)
- Python: System package (`sudo dnf install python3`)
- Venv module: Usually included

## Troubleshooting Commands

```bash
# Check Python version
python3 --version

# Check if venv exists
ls -la ~/.assistant-skills-venv/

# Check if assistant-skills-lib is installed
~/.assistant-skills-venv/bin/pip show assistant-skills-lib

# Check current PATH
echo $PATH | tr ':' '\n' | grep assistant-skills

# Check VIRTUAL_ENV
echo $VIRTUAL_ENV

# Manually activate venv
source ~/.assistant-skills-venv/bin/activate

# Reinstall all dependencies
~/.assistant-skills-venv/bin/pip install -r requirements.txt --upgrade

# View config
cat ~/.assistant-skills/config.yaml
```
