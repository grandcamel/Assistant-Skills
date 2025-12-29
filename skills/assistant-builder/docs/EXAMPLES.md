# Examples

Real-world examples of using the assistant-builder skill.

## Example 1: GitHub Assistant Skills

Creating a GitHub integration project.

### Create Project

```bash
python scaffold_project.py \
  --name "GitHub-Assistant-Skills" \
  --topic "github" \
  --api "GitHub" \
  --base-url "https://api.github.com" \
  --skills "issues,repos,users,search,pulls" \
  --auth api_key \
  --pagination link
```

### Generated Structure

```
GitHub-Assistant-Skills/
├── .claude/
│   ├── settings.json
│   └── skills/
│       ├── shared/scripts/lib/
│       ├── github-assistant/
│       ├── github-issues/
│       ├── github-repos/
│       ├── github-users/
│       ├── github-search/
│       └── github-pulls/
├── CLAUDE.md
├── README.md
└── pyproject.toml
```

### settings.json

```json
{
  "github": {
    "default_profile": "production",
    "profiles": {
      "production": {
        "url": "https://api.github.com",
        "timeout": 30
      }
    }
  }
}
```

---

## Example 2: Stripe Assistant Skills

Creating a Stripe payments integration.

### Create Project

```bash
python scaffold_project.py \
  --name "Stripe-Assistant-Skills" \
  --topic "stripe" \
  --api "Stripe" \
  --base-url "https://api.stripe.com/v1" \
  --skills "payments,customers,subscriptions,invoices" \
  --auth api_key \
  --pagination cursor
```

### Add Another Skill Later

```bash
cd Stripe-Assistant-Skills
python add_skill.py \
  --name "products" \
  --description "Product catalog management" \
  --resource "products" \
  --scripts crud
```

---

## Example 3: Slack Assistant Skills

Creating a Slack integration.

### Create Project

```bash
python scaffold_project.py \
  --name "Slack-Assistant-Skills" \
  --topic "slack" \
  --api "Slack" \
  --base-url "https://slack.com/api" \
  --skills "messages,channels,users,files" \
  --auth oauth \
  --pagination cursor
```

### Skill Organization

| Skill | Purpose | Key Scripts |
|-------|---------|-------------|
| slack-messages | Send/read messages | send_message, get_message, list_messages |
| slack-channels | Channel management | list_channels, create_channel, archive |
| slack-users | User lookup | list_users, get_user, update_status |
| slack-files | File sharing | upload_file, list_files, share_file |

---

## Example 4: Twilio Assistant Skills

Creating a Twilio communications integration.

### Create Project

```bash
python scaffold_project.py \
  --name "Twilio-Assistant-Skills" \
  --topic "twilio" \
  --api "Twilio" \
  --base-url "https://api.twilio.com/2010-04-01" \
  --skills "messages,calls,numbers" \
  --auth basic \
  --pagination page
```

---

## Example 5: Custom Scripts

Adding non-CRUD scripts to a skill.

### Add Skill with Custom Scripts

```bash
python add_skill.py \
  --name "analytics" \
  --description "Analytics and reporting" \
  --scripts "generate_report,schedule_report,get_metrics,export_csv"
```

### Generated Scripts

- `generate_report_analytics.py`
- `schedule_report_analytics.py`
- `get_metrics_analytics.py`
- `export_csv_analytics.py`

---

## Example 6: Minimal Project

Just the essentials for a simple API.

### Create Minimal Project

```bash
python scaffold_project.py \
  --name "Simple-API-Skills" \
  --topic "simple" \
  --api "Simple API" \
  --skills "data"
```

### Then Expand As Needed

```bash
python add_skill.py --name "reports" --description "Reporting" --scripts list-get
python add_skill.py --name "config" --description "Configuration" --scripts crud
```

---

## Reference Project Comparison

Stats from existing production projects:

| Project | Skills | Scripts | Tests | Specialty |
|---------|--------|---------|-------|-----------|
| Jira-Assistant-Skills | 14 | 100+ | 560+ | Issue tracking |
| Confluence-Assistant-Skills | 14 | 60+ | 200+ | Content mgmt |
| Splunk-Assistant-Skills | 13 | 50+ | 150+ | Log analytics |

### View Patterns

```bash
# See how Jira organizes shared library
python show_reference.py --topic shared-library --project jira

# Compare router skill patterns
python show_reference.py --topic router-skill --project all

# View testing patterns
python show_reference.py --topic testing-patterns --project confluence
```
