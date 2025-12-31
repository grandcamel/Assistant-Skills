---
name: setup-wizard
description: This skill should be used when the user asks to "set up Assistant Skills", "configure venv", "install dependencies", "run assistant-skills-setup", or needs help with initial plugin configuration. Provides interactive setup for the shared Python virtual environment and shell configuration.
---

# Setup Wizard

Interactive setup for the shared Assistant Skills Python environment.

## Quick Start

Run `/assistant-skills-setup` to start the interactive setup wizard.

## What Gets Configured

| Component | Location | Purpose |
|-----------|----------|---------|
| Shared venv | `~/.assistant-skills-venv/` | Python dependencies for all Assistant Skills plugins |
| Config file | `~/.assistant-skills/config.yaml` | Tracks setup state, installed plugins, requirement hashes |
| Shell function | `~/.bashrc` or `~/.zshrc` | `claude-as` wrapper to run Claude with venv |

## Shell Function

After setup, use `claude-as` instead of `claude` to run with Assistant Skills dependencies:

```bash
claude-as          # Start Claude with venv activated
claude-as -p "..." # Run with prompt
```

The function sets PATH to include the venv without globally activating it:

```bash
claude-as() {
    VIRTUAL_ENV="$HOME/.assistant-skills-venv" \
    PATH="$HOME/.assistant-skills-venv/bin:$PATH" \
    claude "$@"
}
```

## Configuration File

The setup creates `~/.assistant-skills/config.yaml`:

```yaml
venv_path: ~/.assistant-skills-venv
setup_completed_at: 2025-12-30T10:00:00Z
shell_function_added: true
shell_rc_path: ~/.zshrc

installed_plugins:
  - name: assistant-skills
    path: ~/.claude/plugins/assistant-skills
    requirements_hash: a1b2c3d4

combined_requirements_hash: xyz789abc
```

## Environment Variables

Some Assistant Skills plugins require environment variables. The setup wizard:
1. Reads `assistant_skills.env_vars` from each plugin's `plugin.json`
2. Checks which are currently set
3. Offers to add placeholder exports to shell RC

Example plugin.json env_vars definition:

```json
{
  "assistant_skills": {
    "requirements": "requirements.txt",
    "env_vars": [
      {
        "name": "SPLUNK_TOKEN",
        "description": "Splunk HEC token for API access",
        "required": true
      }
    ]
  }
}
```

## Dependency Updates

When a plugin's `requirements.txt` changes:
1. SessionStart hook detects hash mismatch
2. Auto-runs `pip install -r requirements.txt --upgrade`
3. Updates stored hash in config

## Troubleshooting

### Python not found
```bash
# macOS
brew install python@3.11

# Ubuntu/Debian
sudo apt install python3 python3-venv
```

### Venv creation fails
```bash
# Ensure python3-venv is installed (Linux)
sudo apt install python3-venv

# Try creating manually
python3 -m venv ~/.assistant-skills-venv
```

### Dependencies not found in Claude session
Ensure you're using `claude-as` instead of `claude`, or manually activate:
```bash
source ~/.assistant-skills-venv/bin/activate
claude
```

### Re-run setup
```bash
# Remove existing config and venv
rm -rf ~/.assistant-skills ~/.assistant-skills-venv

# Run setup again
/assistant-skills-setup
```
