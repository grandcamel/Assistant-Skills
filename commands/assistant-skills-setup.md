---
description: Set up the shared Python virtual environment and shell configuration for Assistant Skills plugins
---

# Assistant Skills Setup Wizard

Guide the user through setting up the shared Assistant Skills environment. Follow these steps carefully:

## Step 1: Check Python Version

Run `python3 --version` to verify Python 3.8+ is installed. If Python is missing or too old:
- macOS: Suggest `brew install python@3.11` or download from python.org
- Linux: Suggest `sudo apt install python3` or equivalent for their distro

## Step 2: Detect Existing Virtual Environments

Check for existing venvs in this order:
1. `$VIRTUAL_ENV` environment variable (currently active venv)
2. `~/.assistant-skills-venv/` (shared Assistant Skills venv)
3. `.venv/` in current directory
4. `venv/` in current directory
5. `env/` in current directory

Use `AskUserQuestion` to ask the user:
- If existing venv found: "Found existing virtual environment at [path]. Would you like to reuse it or create the shared Assistant Skills venv?"
  - Options: [Reuse existing], [Create shared venv at ~/.assistant-skills-venv]
- If no venv found: Proceed to create shared venv

## Step 3: Create/Validate Virtual Environment

If creating new:
```bash
python3 -m venv ~/.assistant-skills-venv
```

If reusing existing, validate it has Python 3.8+:
```bash
[venv-path]/bin/python --version
```

## Step 4: Install Dependencies

Collect requirements from all installed Assistant Skills plugins. For now, install from this plugin's requirements.txt:

```bash
~/.assistant-skills-venv/bin/pip install --upgrade pip
~/.assistant-skills-venv/bin/pip install -r ${CLAUDE_PLUGIN_ROOT}/requirements.txt
```

Show installation progress to the user.

## Step 5: Check Environment Variables

Read `assistant_skills.env_vars` from each installed plugin's plugin.json. For each required env var:
1. Check if it's currently set in the environment
2. If missing, note it for the shell RC update step

This plugin has no required env vars, but other plugins (Splunk, Confluence, JIRA) may have them.

## Step 6: Shell Function Setup

Detect the user's shell from `$SHELL`:
- If contains "zsh": use `~/.zshrc`
- If contains "bash": use `~/.bashrc`

Use `AskUserQuestion` to ask:
"Would you like to add the `claude-as` function to your shell configuration? This lets you run Claude with Assistant Skills dependencies without activating the venv globally."

Options: [Add to shell config], [Show manual setup]

If they choose to add, append this to their shell RC file:

```bash

# Assistant Skills - Claude Code wrapper function
# Runs Claude with the Assistant Skills venv activated
claude-as() {
    VIRTUAL_ENV="$HOME/.assistant-skills-venv" \
    PATH="$HOME/.assistant-skills-venv/bin:$PATH" \
    claude "$@"
}
```

If there are missing environment variables, also add placeholders:

```bash
# Assistant Skills - Required environment variables
# export SPLUNK_TOKEN=""  # Required for: splunk-query, splunk-alert
# export CONFLUENCE_API_KEY=""  # Required for: confluence-search
```

## Step 7: Write Configuration

Create the config directory and file:

```bash
mkdir -p ~/.assistant-skills
```

Write `~/.assistant-skills/config.yaml`:

```yaml
venv_path: ~/.assistant-skills-venv
setup_completed_at: [current ISO timestamp]
shell_function_added: [true/false]
shell_rc_path: [path to modified RC file]

installed_plugins:
  - name: assistant-skills
    path: [CLAUDE_PLUGIN_ROOT]
    requirements_hash: [md5 hash of requirements.txt]

combined_requirements_hash: [hash]
```

## Step 8: Final Instructions

Show the user:
1. "Setup complete!"
2. If shell RC was modified: "Run `source ~/.zshrc` (or restart your terminal) to load the changes"
3. "Use `claude-as` to run Claude with Assistant Skills dependencies"
4. If there are missing env vars: "Remember to set your environment variables before using skills that require them"

## Important Notes

- Always use `AskUserQuestion` for user choices - never assume
- Show progress for long operations (pip install)
- If any step fails, provide clear error message and recovery steps
- The venv path must be `~/.assistant-skills-venv` for the shared setup
