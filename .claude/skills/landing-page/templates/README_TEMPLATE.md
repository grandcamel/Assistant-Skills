<p align="center">
  <img src="{{LOGO_PATH}}" alt="{{PRODUCT_NAME}} Assistant Skills" width="140">
</p>

<h1 align="center">{{PRODUCT_NAME}} Assistant Skills</h1>

<table align="center">
<tr>
<td align="center">
<h2>{{EFFICIENCY_METRIC}}</h2>
<sub>{{EFFICIENCY_DESCRIPTION}}</sub>
</td>
<td align="center">
<h2>{{SKILL_COUNT}}</h2>
<sub>Specialized skills<br>one conversation</sub>
</td>
<td align="center">
<h2>{{SCRIPT_COUNT}}+</h2>
<sub>Production-ready<br>Python scripts</sub>
</td>
<td align="center">
<h2>0</h2>
<sub>{{QUERY_LANGUAGE}} syntax<br>to memorize</sub>
</td>
</tr>
</table>

<p align="center">
  <img src="https://img.shields.io/badge/tests-{{TEST_COUNT}}%2B%20passing-brightgreen?logo=pytest" alt="Tests">
  <img src="https://img.shields.io/badge/python-3.8+-3776AB?logo=python&logoColor=white" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/skills-{{SKILL_COUNT}}-{{BADGE_COLOR}}" alt="Skills">
  <img src="https://img.shields.io/github/stars/{{GITHUB_ORG}}/{{GITHUB_REPO}}?style=social" alt="GitHub Stars">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="MIT License">
</p>

<p align="center">
  <strong>{{TAGLINE}}</strong><br>
  <sub>{{SUBTITLE}}</sub>
</p>

<div align="center">

```
{{DEMO_BLOCK}}
```

</div>

<p align="center">
  <a href="#quick-start"><strong>Get Started</strong></a> &bull;
  <a href="#skills-overview">Skills</a> &bull;
  <a href="#who-is-this-for">Use Cases</a> &bull;
  <a href="#architecture">Architecture</a>
</p>

---

## The Difference

<table>
<tr>
<td width="50%">

### The {{QUERY_LANGUAGE}} Way
```{{QUERY_LANGUAGE_LOWER}}
{{COMPLEX_QUERY_EXAMPLE}}
```
*Hope you remembered the syntax...*

</td>
<td width="50%">

### The Natural Way
```
"{{SIMPLE_QUERY_EXAMPLE}}"
```
*Just ask.*

</td>
</tr>
</table>

### Time Saved

| Task | Traditional {{PRODUCT_NAME}} | {{PRODUCT_NAME}} Assistant | Saved |
|------|------------------|----------------|-------|
{{TIME_SAVINGS_ROWS}}

**Typical user:** Save {{WEEKLY_TIME_SAVED}} per week.

---

## Quick Start

### 1. Install Dependencies

```bash
pip install -r .claude/skills/shared/scripts/lib/requirements.txt
```

### 2. Get API Token

{{AUTH_INSTRUCTIONS}}

### 3. Configure

```bash
{{ENV_VARIABLES}}
```

### 4. Start Using

```bash
{{USAGE_EXAMPLES}}
```

**That's it.** Claude now has full {{PRODUCT_NAME}} access.

<p align="center">
  <a href="docs/quick-start.md"><strong>Full Setup Guide</strong></a>
</p>

---

## What You Can Do

```mermaid
flowchart LR
    subgraph Input["You Say"]
{{FLOW_INPUT_NODES}}
    end

    subgraph Processing["Claude Understands"]
{{FLOW_PROCESSING_NODES}}
    end

    subgraph Output["You Get"]
{{FLOW_OUTPUT_NODES}}
    end

{{FLOW_CONNECTIONS}}
```

<details>
<summary><strong>Example: {{EXAMPLE_PERSONA}}'s {{EXAMPLE_TIME}}</strong></summary>

**Before {{PRODUCT_NAME}} Assistant ({{BEFORE_TIME}})**
{{BEFORE_STEPS}}

**After {{PRODUCT_NAME}} Assistant ({{AFTER_TIME}})**
> {{EXAMPLE_PERSONA}}: "{{EXAMPLE_QUERY}}"

Claude provides a formatted summary with everything they need.

**Time saved:** {{TIME_CALCULATION}}

</details>

---

## Skills Overview

| Skill | Purpose | Example Command |
|-------|---------|-----------------|
{{SKILLS_TABLE_ROWS}}

<p align="center">
  <a href="docs/scripts-reference.md"><strong>Full Scripts Reference</strong></a>
</p>

---

## Who Is This For?

{{AUDIENCE_SECTIONS}}

---

## Architecture

```mermaid
flowchart TD
    U["User Request"] --> CC["Claude Code"]
    CC --> HA["{{ASSISTANT_SKILL_NAME}}<br/>Meta-Router"]

{{ARCHITECTURE_ROUTES}}

{{ARCHITECTURE_SHARED}}
```

### Technical Highlights

{{TECHNICAL_HIGHLIGHTS}}

---

## Quality & Security

### Test Coverage

| Category | Tests | Description |
|----------|------:|-------------|
{{TEST_COVERAGE_ROWS}}

> Tests run against live {{PRODUCT_NAME}} instances to ensure real-world reliability.

### Security

{{SECURITY_PRACTICES}}

---

## Try It

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/{{GITHUB_ORG}}/{{GITHUB_REPO}})

One-click cloud environment with all dependencies pre-installed.

---

## Documentation

| Resource | Description |
|----------|-------------|
| [Quick Start Guide](docs/quick-start.md) | Get up and running in 5 minutes |
| [Configuration Guide](docs/configuration.md) | Multi-profile setup and options |
| [Scripts Reference](docs/scripts-reference.md) | Complete CLI documentation |
| [Troubleshooting](docs/troubleshooting.md) | Common issues and solutions |

### Need Help?

- [GitHub Discussions](https://github.com/{{GITHUB_ORG}}/{{GITHUB_REPO}}/discussions)
- [Report Issues](https://github.com/{{GITHUB_ORG}}/{{GITHUB_REPO}}/issues)

---

## Contributing

Contributions are welcome! See our [Contributing Guide](CONTRIBUTING.md).

```bash
# Clone the repository
git clone https://github.com/{{GITHUB_ORG}}/{{GITHUB_REPO}}.git
cd {{GITHUB_REPO}}

# Install dependencies
pip install -r .claude/skills/shared/scripts/lib/requirements.txt

# Run tests
pytest .claude/skills/*/tests/ -v
```

---

## Roadmap

{{ROADMAP_ITEMS}}

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  <strong>{{CLOSING_TAGLINE}}</strong>
  <br>
  <sub>Built for Claude Code by developers who were tired of {{PAIN_POINT}}.</sub>
</p>
