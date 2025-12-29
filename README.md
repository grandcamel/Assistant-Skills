# Assistant Skills Templates

A comprehensive collection of prompt templates for building Claude Code Assistant Skills projects with Test-Driven Development (TDD) practices.

## Overview

These templates guide you through the complete lifecycle of creating an Assistant Skills project for any REST API, from initial research through production-ready implementation.

**Key Techniques:**
- **TDD (Test-Driven Development)** - Write failing tests first, implement to pass
- **Progressive Disclosure** - 3-level SKILL.md structure minimizes context token usage
- **GAP Analysis** - Comprehensive API research before implementation
- **Phased Implementation** - Milestone-based plans with regression checkpoints
- **Router Meta-Skill** - Central hub pattern for skill routing

## Quick Start

```bash
# 1. Copy templates to your project location
cp -r Assistant-Skills-Templates/ ~/projects/my-api-skills-templates/

# 2. Start with API research
# Open 00-project-lifecycle/01-api-research-prompt.md
# Use with Claude Code to research your target API

# 3. Create GAP analysis
# Use 00-project-lifecycle/02-gap-analysis-template.md

# 4. Initialize project
# Use 01-project-scaffolding/project-init-prompt.md
```

## Template Categories

| Folder | Purpose | When to Use |
|--------|---------|-------------|
| `00-project-lifecycle/` | Full lifecycle guidance | Starting a new project from scratch |
| `01-project-scaffolding/` | Initial project setup | Creating directory structure, configs |
| `02-shared-library/` | Common utilities | Building reusable client, error handling |
| `03-skill-templates/` | Individual skills | Adding new skills to existing project |
| `04-testing/` | TDD and testing | Writing unit and integration tests |
| `05-documentation/` | Documentation patterns | Creating user and developer docs |
| `06-git-and-ci/` | Version control, CI/CD | Setting up commits, GitHub Actions |
| `examples/` | Filled-in examples | Reference for template completion |

## Project Lifecycle

```
┌─────────────────────────────────────────────────────────────────────┐
│                        PROJECT LIFECYCLE                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  1. API RESEARCH          2. GAP ANALYSIS         3. ARCHITECTURE   │
│  ┌──────────────┐         ┌──────────────┐        ┌──────────────┐  │
│  │ Discover     │         │ Inventory    │        │ Design       │  │
│  │ endpoints,   │────────▶│ capabilities │───────▶│ skills,      │  │
│  │ auth, limits │         │ vs. needs    │        │ shared lib   │  │
│  └──────────────┘         └──────────────┘        └──────────────┘  │
│                                                          │           │
│  ┌───────────────────────────────────────────────────────┘           │
│  ▼                                                                   │
│  4. IMPLEMENTATION PLAN   5. TDD CYCLE            6. COMPLETION     │
│  ┌──────────────┐         ┌──────────────┐        ┌──────────────┐  │
│  │ Phases,      │         │ Failing test │        │ Full test    │  │
│  │ milestones,  │────────▶│ ──▶ Implement│───────▶│ suite, docs, │  │
│  │ test targets │         │ ──▶ Pass     │        │ release      │  │
│  └──────────────┘         └──────────────┘        └──────────────┘  │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## Template Usage

Each template follows a consistent format:

```markdown
# Template Name

## Purpose
What this template accomplishes.

## Prerequisites
What you need before using this template.

## Placeholders
- `{{PLACEHOLDER}}` - Description of what to fill in

## Prompt
The actual prompt to use with Claude Code.

## Expected Outputs
What files/artifacts this creates.

## Next Steps
What template to use after this one.
```

## Progressive Disclosure (3 Levels)

SKILL.md files use 3 levels to minimize boot context:

| Level | Content | Token Impact |
|-------|---------|--------------|
| **L1: Discovery** | YAML frontmatter (name, description, triggers) | ~50 tokens |
| **L2: Quick Reference** | Tables, examples, common patterns | ~200-500 tokens |
| **L3: Deep Documentation** | Linked files (workflows, subsystems, API details) | Loaded on demand |

## TDD Commit Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                     TDD TWO-COMMIT PATTERN                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  COMMIT 1: Add failing tests                                     │
│  ────────────────────────────────────────────────────────────   │
│  test(skill-name): add failing tests for feature_name           │
│                                                                  │
│  - Tests define expected behavior                                │
│  - All tests should FAIL at this point                          │
│  - Commit captures test specification                            │
│                                                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  COMMIT 2: Implement to pass tests                               │
│  ────────────────────────────────────────────────────────────   │
│  feat(skill-name): implement feature_name (N/N tests passing)   │
│                                                                  │
│  - Implement minimum code to pass tests                          │
│  - Include test count in commit message                          │
│  - Run regression suite before committing                        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Best Practices

### Do
- Complete GAP analysis before writing code
- Write failing tests before implementation
- Run full test suite before each phase transition
- Update implementation plan after each milestone
- Use conventional commits with test counts

### Don't
- Skip API research phase
- Implement without tests
- Batch multiple features in one commit
- Forget regression testing between phases
- Leave implementation plan outdated

## Reference Projects

These templates are derived from production implementations:

| Project | Skills | Scripts | Tests |
|---------|--------|---------|-------|
| Jira-Assistant-Skills | 14 | 100+ | 560+ |
| Confluence-Assistant-Skills | 14 | 60+ | 200+ |
| Splunk-Assistant-Skills | 13 | 50+ | 150+ |

## License

MIT License - Use freely for your own Assistant Skills projects.
