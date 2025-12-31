# Jira Assistant Skills Setup Integration

Run this prompt in the Jira-Assistant-Skills project to integrate with the universal setup system.

---

## Prompt

```
Integrate this Jira-Assistant-Skills project with the Assistant Skills universal setup system.

## 1. Update plugin.json

Add the `assistant_skills` section to `.claude-plugin/plugin.json`:

```json
{
  "assistant_skills": {
    "requirements": "requirements.txt",
    "env_vars": [
      {
        "name": "JIRA_URL",
        "description": "Jira instance base URL (e.g., https://company.atlassian.net)",
        "required": true
      },
      {
        "name": "JIRA_USERNAME",
        "description": "Atlassian account email for authentication",
        "required": true
      },
      {
        "name": "JIRA_API_TOKEN",
        "description": "Atlassian API token (generate at id.atlassian.com/manage-profile/security/api-tokens)",
        "required": true
      },
      {
        "name": "JIRA_PROJECT_KEY",
        "description": "Default project key for operations (optional, can be specified per-request)",
        "required": false
      }
    ]
  }
}
```

Review the actual environment variables used in this project's scripts and adjust if needed.

## 2. Update README.md

Add this section after the installation instructions:

---

### Setup

After installing the plugin, run the setup wizard from the main Assistant-Skills plugin:
```
/assistant-skills-setup
```

This configures:
- Shared Python venv at `~/.assistant-skills-venv/`
- Required dependencies from `requirements.txt`
- Environment variables (prompts you to configure Jira credentials)
- `claude-as` shell function for running Claude with dependencies

After setup, use `claude-as` instead of `claude`:
```bash
claude-as  # Runs Claude with Assistant Skills venv activated
```

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `JIRA_URL` | Yes | Jira instance base URL (e.g., `https://company.atlassian.net`) |
| `JIRA_USERNAME` | Yes | Atlassian account email for authentication |
| `JIRA_API_TOKEN` | Yes | Atlassian API token ([generate here](https://id.atlassian.com/manage-profile/security/api-tokens)) |
| `JIRA_PROJECT_KEY` | No | Default project key for operations |

### Getting Your API Token

1. Go to [Atlassian API Tokens](https://id.atlassian.com/manage-profile/security/api-tokens)
2. Click "Create API token"
3. Give it a descriptive label (e.g., "Claude Code Jira")
4. Copy the token and add it to your shell config:
   ```bash
   export JIRA_API_TOKEN="your-token-here"
   ```

---

## 3. Review hooks compatibility

Check `hooks/hooks.json` - if there's a SessionStart hook, ensure it doesn't conflict with the main Assistant Skills health check. The main plugin will check for required env vars automatically.

## 4. Create commits

Create these commits:
1. `feat(plugin): add assistant_skills config for universal setup`
2. `docs(readme): add setup section with Jira environment variables`

Push when done.
```

---

## Expected Changes

### plugin.json
```json
{
  "name": "jira-assistant-skills",
  "version": "...",
  ...
  "assistant_skills": {
    "requirements": "requirements.txt",
    "env_vars": [
      {
        "name": "JIRA_URL",
        "description": "Jira instance base URL",
        "required": true
      },
      {
        "name": "JIRA_USERNAME",
        "description": "Atlassian account email",
        "required": true
      },
      {
        "name": "JIRA_API_TOKEN",
        "description": "Atlassian API token",
        "required": true
      },
      {
        "name": "JIRA_PROJECT_KEY",
        "description": "Default project key",
        "required": false
      }
    ]
  }
}
```
