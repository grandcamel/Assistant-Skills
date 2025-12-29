# Architecture Design Prompt

## Purpose

Design the skill architecture, shared library components, and project structure based on GAP analysis findings.

## Prerequisites

- Completed GAP analysis document
- Understanding of Claude Code skill patterns
- Decision on initial scope (MVP vs full feature set)

## Placeholders

- `{{API_NAME}}` - Name of the target API
- `{{TOPIC}}` - Lowercase prefix for skills (e.g., "github", "stripe")
- `{{PROJECT_NAME}}` - Full project name (e.g., "GitHub-Assistant-Skills")

---

## Prompt

```
Based on the GAP analysis for {{API_NAME}}, I need to design the architecture for {{PROJECT_NAME}}.

**Context:**
- This is a Claude Code Assistant Skills project
- Skills use progressive disclosure (3-level SKILL.md)
- All skills share a common library
- There's a router meta-skill ({{TOPIC}}-assistant) that routes to specialized skills
- Each skill has its own scripts, tests, and docs

**GAP Analysis Summary:**
<!-- Paste key findings from GAP analysis -->

Please design:

## 1. Skill Decomposition

Identify all skills needed. For each skill:
- Skill name ({{TOPIC}}-{name})
- Purpose (1 sentence)
- Key operations (list of scripts)
- API endpoints used
- Dependencies on other skills

Guidelines:
- Single responsibility per skill
- 5-15 scripts per skill is ideal
- Group by resource or workflow, not by HTTP method
- Consider user mental model

## 2. Router Skill Design

For the {{TOPIC}}-assistant router skill:
- Routing table (user intent → skill)
- Trigger keywords/phrases for each skill
- Multi-skill operation patterns
- Disambiguation logic for overlapping triggers

## 3. Shared Library Components

What utilities should be in `.claude/skills/shared/scripts/lib/`:

Required:
- HTTP client (name, key features)
- Config manager (sources, profile support)
- Error handler (exception hierarchy)
- Validators (what validations needed)
- Formatters (output formats needed)

Optional/API-specific:
- Pagination helper?
- Authentication helper?
- Rate limiter?
- Cache?
- Data format converters?

## 4. Configuration Schema

Design the configuration structure:
- Environment variables
- settings.json structure
- Profile schema (for multi-instance)
- Sensitive vs non-sensitive settings

## 5. Error Handling Strategy

Map API error patterns to skill behavior:
- HTTP status code → Exception class
- Retry conditions
- User-friendly error messages
- Troubleshooting hints per error

## 6. Testing Architecture

- Unit test organization (per skill? per script?)
- Fixtures needed (mock client, sample data)
- Live integration test approach
- Test data management

## 7. Directory Structure

Propose the full directory tree:
```
{{PROJECT_NAME}}/
├── .claude/
│   ├── skills/
│   │   ├── {{TOPIC}}-{skill1}/
│   │   ├── {{TOPIC}}-{skill2}/
│   │   ├── {{TOPIC}}-assistant/
│   │   └── shared/
│   └── settings.json
├── CLAUDE.md
├── README.md
└── ...
```

## 8. Dependency Map

Show which skills depend on which shared components:
- Skills → Shared lib components
- Skills → Other skills (if any)
- Test fixtures → Shared fixtures

Provide a clear architecture that balances:
- Cohesion within skills
- Low coupling between skills
- Reusability of shared components
- Testability of each component
- Progressive disclosure for token efficiency
```

---

## Expected Outputs

After using this prompt, you should have:

1. **Skill inventory** - Complete list of skills with boundaries
2. **Routing table** - How router directs to skills
3. **Shared library design** - Components and their purposes
4. **Configuration schema** - Settings structure
5. **Directory structure** - Full project tree
6. **Dependency diagram** - How components relate

---

## Next Steps

1. Create implementation plan using `04-implementation-plan.md`
2. Begin project scaffolding with `01-project-scaffolding/`
3. Implement shared library first

---

## Architecture Principles

### Skill Design
- **Single Responsibility**: Each skill does one thing well
- **Clear Boundaries**: Obvious when to use which skill
- **Self-Contained**: Skill can function with just shared lib
- **Progressive Disclosure**: SKILL.md loads minimal tokens initially

### Shared Library Design
- **DRY**: Common patterns centralized
- **Composable**: Components work independently
- **Testable**: Each component can be unit tested
- **Extensible**: Easy to add new utilities

### Router Design
- **Exhaustive**: Every API capability routable
- **Unambiguous**: Clear skill selection for each request
- **Composable**: Support multi-skill operations
- **Discoverable**: Users can find capabilities naturally
