---
name: landing-page
version: 1.0.0
description: Create professional README landing pages for Assistant Skills projects with consistent branding. Use when creating or upgrading project READMEs, generating logos, or ensuring visual consistency across repositories.
category: documentation
tags: [readme, branding, landing-page, documentation, svg, logo]
author: grandcamel
license: MIT
---

# Landing Page Skill

Create professional README landing pages for Assistant Skills projects.

## When to Use

- Create or upgrade a README.md for an Assistant Skills project
- Generate logo SVG files with terminal prompt design (> product_)
- Transform technical READMEs into professional landing pages
- Ensure visual consistency across the Assistant Skills family

## What this skill does

### README Generation
- Analyzes your project structure to extract skills, scripts, and features
- Generates a professional README following the Assistant Skills design pattern
- Includes hero section with stats, badges, and value proposition
- Creates problem/solution comparison sections
- Generates audience-specific content (developers, team leads, ops, etc.)
- Adds architecture diagrams using Mermaid
- Includes trust signals (test coverage, security practices)

### Visual Asset Generation
- Creates logo SVG with terminal prompt design (> product_)
- Generates consistent color gradients matching product identity
- Produces static and animated versions of logos

### Brand Consistency
- Maintains consistent structure across all Assistant Skills projects
- Uses standardized section ordering and formatting
- Ensures uniform badge styling and placement
- Applies consistent Mermaid diagram styling

## Project Analysis

The skill analyzes your project to extract:
- **Product name**: From package name, directory, or README title
- **Skills count**: Number of skill directories in .claude/skills/
- **Scripts count**: Python scripts across all skills
- **Test count**: pytest test files and estimated test count
- **Features**: Key capabilities from SKILL.md files
- **Query language**: JQL, CQL, SPL, or other domain-specific languages

## Templates

### README Template Structure
```
1. Hero Section
   - Centered logo
   - Stats bar (4 columns: efficiency metric, skill count, scripts count, zero-memorization metric)
   - Badge bar (tests, python, skills, license)
   - Tagline and value proposition

2. Problem/Solution
   - Side-by-side comparison (old way vs natural way)
   - Time savings table

3. Quick Start
   - 3-step setup (install, configure, use)

4. What You Can Do
   - Mermaid flow diagram (input → processing → output)
   - Example narrative

5. Skills Overview
   - Table with skill name, purpose, example command

6. Who Is This For?
   - Expandable sections for each persona

7. Architecture
   - Mermaid hub-spoke diagram
   - Technical highlights list

8. Quality & Security
   - Test coverage table
   - Security practices list

9. Documentation & Contributing
10. Roadmap
11. License
```

### Logo Template Parameters
- **product_name**: Short name displayed (jira, confluence, splunk)
- **primary_color**: Main gradient color (e.g., #0052CC for Atlassian blue)
- **accent_color**: Secondary color (e.g., #4a00e0 for purple)
- **cursor_color**: Blinking cursor color (e.g., #00C7E6 for cyan)

## Usage Examples

### Generate README for a new project
```
"Generate an Assistant Skills README for this Confluence project"
```

### Create logo assets
```
"Create a logo SVG for Splunk Assistant Skills using orange #FF6900"
```

### Analyze and upgrade existing README
```
"Upgrade my README to match the JIRA Assistant Skills style"
```

### Full landing page generation
```
"Create a complete landing page for this project including README and logo"
```

## Available Templates

| Template | Description |
|----------|-------------|
| `README_TEMPLATE.md` | Full README structure with placeholders |
| `logo-template.svg` | Terminal prompt logo with customizable colors |
| `logo-static-template.svg` | Non-animated version of logo |
| `stats-bar.md` | Hero section stats component |
| `comparison-section.md` | Problem/solution comparison |
| `audience-section.md` | Role-specific expandable sections |
| `architecture-diagram.md` | Mermaid hub-spoke diagram |

## Color Palettes

### Atlassian Products (JIRA, Confluence)
- Primary: #0052CC (Atlassian Blue)
- Accent: #4a00e0 (Purple)
- Background: #1a1a2e → #16213e

### Splunk
- Primary: #FF6900 (Splunk Orange)
- Accent: #65A637 (Green)
- Background: #1a1a2e → #16213e

### Generic/Custom
- Primary: User-specified
- Accent: Complementary color
- Background: Dark terminal theme

## Scripts

```bash
# Analyze project for README generation
python scripts/analyze_project.py /path/to/project --format json

# Generate logo SVG
python scripts/generate_logo.py --name jira --primary "#0052CC"
```

## Dependencies

- Python 3.8+ (stdlib only, no external packages)
