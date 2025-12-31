# Add Assistant Skills Setup Integration

Use this prompt to integrate an existing Assistant Skills project with the universal setup system from the main Assistant-Skills plugin.

---

## Prompt

```
I need to integrate this project with the Assistant Skills universal setup system. Please make the following updates:

## 1. Update plugin.json

Add the `assistant_skills` section to `.claude-plugin/plugin.json`:

```json
{
  "assistant_skills": {
    "requirements": "requirements.txt",
    "env_vars": [
      {
        "name": "ENV_VAR_NAME",
        "description": "Description of what this variable is for",
        "required": true
      }
    ]
  }
}
```

Analyze this project's requirements.txt and any environment variables used by skills to populate this section accurately.

## 2. Update README.md

Add a "Setup" section after the installation instructions:

### Setup

After installing the plugin, run the setup wizard:
```
/assistant-skills-setup
```

This configures:
- Shared Python venv at `~/.assistant-skills-venv/`
- Required dependencies from `requirements.txt`
- Environment variables (prompts you to set: `ENV_VAR_1`, `ENV_VAR_2`, etc.)
- `claude-as` shell function for running Claude with dependencies

After setup, use `claude-as` instead of `claude`:
```bash
claude-as  # Runs Claude with Assistant Skills venv activated
```

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ENV_VAR_1` | Yes | Description... |
| `ENV_VAR_2` | No | Description... |

## 3. Update any SessionStart hooks

If this project has custom SessionStart hooks in `hooks/hooks.json`, ensure they:
- Don't conflict with the main Assistant Skills health check
- Use `${CLAUDE_PLUGIN_ROOT}` for paths
- Assume the venv may be activated via `claude-as`

## 4. Review script paths

Ensure all Python script invocations in commands and skills use relative paths that work when:
- The venv is activated via `claude-as`
- Scripts are run from any directory

## 5. Create logical commits

Create separate commits for:
1. `feat(plugin): add assistant_skills config for universal setup`
2. `docs(readme): add setup section with environment variables`
3. Any hook updates if needed

---

Please analyze this project and implement these changes. List the environment variables this project requires and add them to the plugin.json.
```

---

## Example: Splunk-Assistant-Skills

After running this prompt on Splunk-Assistant-Skills, you'd expect:

**plugin.json additions:**
```json
{
  "assistant_skills": {
    "requirements": "requirements.txt",
    "env_vars": [
      {
        "name": "SPLUNK_HOST",
        "description": "Splunk instance hostname",
        "required": true
      },
      {
        "name": "SPLUNK_TOKEN",
        "description": "Splunk HEC token for API access",
        "required": true
      },
      {
        "name": "SPLUNK_PORT",
        "description": "Splunk management port (default: 8089)",
        "required": false
      }
    ]
  }
}
```

**README.md additions:**
```markdown
### Setup

After installing the plugin, run the setup wizard:
```
/assistant-skills-setup
```

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `SPLUNK_HOST` | Yes | Splunk instance hostname (e.g., `splunk.company.com`) |
| `SPLUNK_TOKEN` | Yes | Splunk HEC token for API authentication |
| `SPLUNK_PORT` | No | Management port (default: 8089) |
```

---

## Projects to Update

- [ ] Splunk-Assistant-Skills
- [ ] Confluence-Assistant-Skills
- [ ] Jira-Assistant-Skills

---

## Notes

- The `/assistant-skills-setup` command comes from the main Assistant-Skills plugin
- Projects don't need their own setup command, just the `assistant_skills` config
- The SessionStart hook in Assistant-Skills checks env vars from all installed plugins
- Users install the main plugin first, then project-specific plugins
