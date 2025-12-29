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

Generate professional README landing pages and logo assets for Assistant Skills projects.

## Quick Start

```bash
# Analyze project
python scripts/analyze_project.py /path/to/project --format json

# Generate logo
python scripts/generate_logo.py --name jira --primary "#0052CC"
```

## Usage Examples

```
"Generate an Assistant Skills README for this Confluence project"
"Create a logo SVG for Splunk using orange #FF6900"
"Upgrade my README to match the JIRA Assistant Skills style"
```

## Templates

| File | Purpose |
|------|---------|
| `README_TEMPLATE.md` | Full landing page with placeholders |
| `logo-template.svg` | Animated terminal prompt logo |
| `logo-static-template.svg` | Static logo version |
| `audience-section.md` | Role-specific expandable sections |

### README Structure

1. Hero (logo, stats bar, badges, tagline)
2. Problem/Solution comparison
3. Quick Start (3-step setup)
4. What You Can Do (Mermaid flow)
5. Skills Overview table
6. Who Is This For? (personas)
7. Architecture diagram
8. Quality & Security
9. Documentation & Contributing
10. Roadmap & License

## Logo Parameters

| Parameter | Example | Description |
|-----------|---------|-------------|
| `--name` | jira | Product name in prompt |
| `--primary` | #0052CC | Main gradient color |
| `--accent` | #4a00e0 | Secondary color |
| `--cursor` | #00C7E6 | Blinking cursor color |

Color palettes for known products in `assets/color-palettes.json`.

## Scripts Reference

```bash
python scripts/analyze_project.py --help
python scripts/generate_logo.py --help
```
