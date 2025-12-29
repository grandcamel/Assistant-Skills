# Audience Section Templates

Use these templates as the basis for "Who Is This For?" sections in Assistant Skills READMEs.

## Developer Section

```markdown
<details>
<summary><strong>Developers</strong> — Never leave your terminal</summary>

**Stop context-switching to {{PRODUCT_NAME}}.**

You're in your IDE. You just finished a task. Now you need to update {{PRODUCT_NAME}}.

```bash
claude "{{EXAMPLE_DEVELOPER_COMMAND}}"
# Done in 3 seconds, never left your terminal
```

### Developer Cheat Sheet

| Task | Command |
|------|---------|
{{DEVELOPER_COMMANDS_TABLE}}

**Time saved:** ~45 min/week

</details>
```

## Team Lead Section

```markdown
<details>
<summary><strong>Team Leads</strong> — Team visibility in seconds</summary>

**See your team's work without meetings.**

### Morning Check-in (60 Seconds)
```
"Show current sprint progress"
"Who has the most work in progress?"
"What's blocked and why?"
```

### Query Templates

| Need | Command |
|------|---------|
{{TEAM_LEAD_COMMANDS_TABLE}}

**Time saved:** ~4 hours/week

</details>
```

## Ops/Admin Section

```markdown
<details>
<summary><strong>IT/Ops</strong> — {{OPS_HEADLINE}}</summary>

**{{OPS_VALUE_PROP}}**

### Quick Actions
```
"{{OPS_EXAMPLE_1}}"
"{{OPS_EXAMPLE_2}}"
"{{OPS_EXAMPLE_3}}"
```

### Common Operations

| Task | Command |
|------|---------|
{{OPS_COMMANDS_TABLE}}

**Time saved:** Minutes per incident

</details>
```

## Product Manager Section

```markdown
<details>
<summary><strong>Product Managers</strong> — Self-serve product data</summary>

**Focus on product, not administration.**

### Roadmap & Planning
```
"{{PM_EXAMPLE_1}}"
"{{PM_EXAMPLE_2}}"
"{{PM_EXAMPLE_3}}"
```

### Reporting
```
"{{PM_REPORT_1}}"
"{{PM_REPORT_2}}"
```

**Time saved:** ~5 hours/week

</details>
```

---

## Product-Specific Examples

### JIRA

**Developer:**
- "Close PROJ-123 with 'Fixed null pointer', log 30 minutes"
- "What's assigned to me in the current sprint?"
- "Start progress on PROJ-123"

**Team Lead:**
- "Show blockers across all team projects"
- "Who's overloaded? Show assignment counts"
- "Sprint burndown for Team Alpha"

**Ops:**
- "Create urgent incident: Production database unreachable"
- "Show all open incidents by severity"
- "Resolve REQ-789 with 'Password reset completed'"

### Confluence

**Developer:**
- "Create page 'Architecture Decision Record' in DOCS space"
- "Find my recent pages"
- "Add code block to page 12345"

**Team Lead:**
- "Find all pages modified this week in Team space"
- "Show page tree for Project X"
- "Export space content to markdown"

**Ops:**
- "Update runbook page with new procedure"
- "Find all pages with 'deprecated' label"
- "Add label 'reviewed' to pages in KB space"

### Splunk

**Developer:**
- "Search for errors in main index from last hour"
- "Show me error patterns by host"
- "Export search results to CSV"

**Ops:**
- "Show critical alerts from last 24 hours"
- "Search for login failures by user"
- "Create alert for high CPU usage"

**Security:**
- "Find all failed SSH attempts"
- "Show authentication events by user"
- "Search for privilege escalation patterns"
