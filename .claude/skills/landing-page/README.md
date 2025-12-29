# GitHub Project Promote Skill

Create professional landing pages for Assistant Skills projects with consistent branding.

## Installation

### User-Level (Recommended)

The skill is already installed at `~/.claude/skills/github-project-promote/`.

Claude Code will automatically discover it for all your projects.

### Project-Level

Copy to a specific project:

```bash
cp -r ~/.claude/skills/github-project-promote /path/to/project/.claude/skills/
```

## Usage

### With Claude Code

Just ask Claude to generate a README:

```
"Generate an Assistant Skills README for this project"
"Create a logo for Confluence Assistant Skills"
"Upgrade my README to match the JIRA Assistant Skills style"
```

### Standalone Scripts

#### Analyze a Project

```bash
# Analyze current project
python ~/.claude/skills/github-project-promote/scripts/analyze_project.py .

# Analyze another project
python ~/.claude/skills/github-project-promote/scripts/analyze_project.py ../Confluence-Assistant-Skills

# Output as JSON
python ~/.claude/skills/github-project-promote/scripts/analyze_project.py . --format json
```

Output:
```
Product: Confluence Assistant Skills
Skills: 14
Scripts: 50+
Tests: 200+
Query Language: CQL

Skills: confluence-analytics, confluence-assistant, confluence-attachment, ...

Colors:
  primary: #0052CC
  accent: #36B37E
  cursor: #00C7E6
  badge: 36B37E
```

#### Generate Logo

```bash
# Generate with predefined palette
python ~/.claude/skills/github-project-promote/scripts/generate_logo.py confluence --palette confluence -o logo.svg

# Custom colors
python ~/.claude/skills/github-project-promote/scripts/generate_logo.py splunk --primary "#FF6900" --accent "#65A637" -o logo.svg

# Static (no animation)
python ~/.claude/skills/github-project-promote/scripts/generate_logo.py jira --palette jira --static -o logo-static.svg
```

## Templates

| Template | Description |
|----------|-------------|
| `README_TEMPLATE.md` | Full README with placeholders |
| `logo-template.svg` | Animated terminal prompt logo |
| `logo-static-template.svg` | Static version of logo |
| `audience-section.md` | Role-specific content examples |

## Color Palettes

Pre-configured palettes in `assets/color-palettes.json`:

| Palette | Primary | Accent | Use For |
|---------|---------|--------|---------|
| atlassian | #0052CC | #4a00e0 | JIRA, Confluence, Bitbucket |
| jira | #0052CC | #4a00e0 | JIRA specifically |
| confluence | #0052CC | #36B37E | Confluence specifically |
| splunk | #FF6900 | #65A637 | Splunk |
| github | #238636 | #1f6feb | GitHub |
| gitlab | #FC6D26 | #6E49CB | GitLab |
| datadog | #632CA6 | #FF6B6B | Datadog |
| elastic | #00BFB3 | #F04E98 | Elasticsearch |
| aws | #FF9900 | #232F3E | AWS |
| azure | #0078D4 | #50E6FF | Azure |
| generic | #6366F1 | #8B5CF6 | Custom projects |

## README Structure

The generated README follows this structure:

1. **Hero Section** - Logo, stats bar, badges, tagline
2. **The Difference** - Side-by-side comparison (old way vs natural language)
3. **Quick Start** - 3-step setup guide
4. **What You Can Do** - Mermaid flow diagram + example narrative
5. **Skills Overview** - Table of all skills
6. **Who Is This For?** - Expandable sections by persona
7. **Architecture** - Mermaid hub-spoke diagram
8. **Quality & Security** - Test coverage, security practices
9. **Documentation** - Links to docs
10. **Contributing** - Development setup
11. **Roadmap** - Future plans
12. **License** - MIT

## Examples

### JIRA Assistant Skills

The reference implementation. See the live README at:
https://github.com/grandcamel/jira-assistant-skills

### Creating a New Project README

1. Analyze the project:
   ```bash
   python analyze_project.py ../MyProduct-Assistant-Skills --format json > project.json
   ```

2. Generate logo:
   ```bash
   python generate_logo.py myproduct --palette generic -o ../MyProduct-Assistant-Skills/assets/logo.svg
   ```

3. Ask Claude to generate the README using the template and analysis.

## Contributing

This skill is part of the Assistant Skills ecosystem. Contributions welcome!

## License

MIT
