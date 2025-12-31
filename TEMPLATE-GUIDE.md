# Template Guide

How to effectively use these templates to build your Assistant Skills project.

## Template Conventions

### Placeholder Syntax

All templates use double curly braces for placeholders:

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `{{API_NAME}}` | Name of the target API | `GitHub`, `Stripe`, `Twilio` |
| `{{TOPIC}}` | Lowercase topic prefix | `github`, `stripe`, `twilio` |
| `{{SKILL_NAME}}` | Specific skill name | `issues`, `payments`, `messages` |
| `{{ENDPOINT}}` | API endpoint path | `/repos/{owner}/{repo}/issues` |
| `{{BASE_URL}}` | API base URL | `https://api.github.com` |

### Section Markers

Templates include section markers for navigation:

```markdown
<!-- SECTION: Overview -->
<!-- SECTION: Implementation -->
<!-- SECTION: Testing -->
```

### Conditional Sections

Some templates have optional sections:

```markdown
<!-- IF: Has Pagination -->
## Pagination Handling
...
<!-- ENDIF -->
```

## Workflow: New Project from Scratch

### Phase 1: Research (1-2 hours)

```
templates/00-project-lifecycle/
├── 01-api-research-prompt.md      ◄── START HERE
└── 02-gap-analysis-template.md    ◄── Create this document
```

1. **API Research**: Use `01-api-research-prompt.md` with Claude Code
   - Discover all endpoints
   - Understand authentication
   - Document rate limits and pagination

2. **GAP Analysis**: Fill in `02-gap-analysis-template.md`
   - Inventory all API capabilities
   - Map features to endpoints
   - Identify limitations and workarounds

### Phase 2: Architecture (30 minutes)

```
templates/00-project-lifecycle/
├── 03-architecture-prompt.md      ◄── Design your skills
└── 04-implementation-plan.md      ◄── Create TDD plan
```

1. **Architecture Design**: Use `03-architecture-prompt.md`
   - Define skill boundaries
   - Plan shared library components
   - Design router skill

2. **Implementation Plan**: Fill in `04-implementation-plan.md`
   - Define phases and milestones
   - Set test coverage targets
   - Plan regression checkpoints

### Phase 3: Scaffolding (15 minutes)

```
templates/01-project-scaffolding/
├── project-init-prompt.md         ◄── Initialize project
├── CLAUDE.md.template
├── README.md.template
└── settings.json.template
```

1. **Project Initialization**: Use `project-init-prompt.md`
   - Creates directory structure
   - Generates CLAUDE.md
   - Sets up configuration

### Phase 4: Shared Library (1-2 hours)

```
templates/02-shared-library/
├── shared-lib-prompt.md           ◄── Create shared utilities
├── client.py.template
├── config_manager.py.template
├── error_handler.py.template
├── validators.py.template
└── formatters.py.template
```

1. **Shared Library**: Use `shared-lib-prompt.md`
   - HTTP client with retry logic
   - Configuration management
   - Error handling hierarchy
   - Input validation
   - Output formatting

### Phase 5: Skills Implementation (varies)

```
templates/03-skill-templates/
├── skill-creation-prompt.md       ◄── For each skill
├── SKILL.md.template
├── script.py.template
└── router-skill/
    └── router-skill-prompt.md     ◄── Create router last
```

For each skill:
1. Create skill structure with `skill-creation-prompt.md`
2. Write failing tests (see `templates/04-testing/`)
3. Implement scripts
4. Create SKILL.md with progressive disclosure

### Phase 6: Testing Throughout

```
templates/04-testing/
├── tdd-workflow-prompt.md         ◄── TDD guidance
├── unit-test.py.template
├── conftest.py.template
└── live-integration.py.template
```

Use TDD workflow:
1. Write failing tests first
2. Implement to pass
3. Refactor if needed
4. Run regression suite

### Phase 7: Documentation

```
templates/05-documentation/
├── WORKFLOWS.md.template
├── QUICK-REFERENCE.md.template
└── TROUBLESHOOTING.md.template
```

Create user documentation:
1. Step-by-step workflows
2. Command quick reference
3. Troubleshooting guide

### Phase 8: CI/CD Setup

```
templates/06-git-and-ci/
├── conventional-commits.md
├── tdd-commit-workflow.md
└── github-workflows/
    └── test.yml.template
```

Set up version control:
1. Configure commit conventions
2. Set up GitHub Actions
3. Create release workflow

---

## Workflow: Adding a Skill to Existing Project

If you already have a project and want to add a new skill:

```
1. templates/03-skill-templates/skill-creation-prompt.md
2. templates/04-testing/tdd-workflow-prompt.md
3. templates/04-testing/unit-test.py.template
4. templates/03-skill-templates/SKILL.md.template
5. Run regression tests
6. Commit with TDD pattern
```

---

## Workflow: Creating Router Skill

The router skill should be created after other skills exist:

```
1. Review all existing skills
2. templates/03-skill-templates/router-skill/router-skill-prompt.md
3. Define routing tables
4. Test skill invocation
5. Document multi-skill operations
```

---

## Template Customization

### API-Specific Adaptations

Templates are generic but may need adaptation:

| API Pattern | Customization Needed |
|-------------|---------------------|
| OAuth 2.0 | Add token refresh logic to client |
| API Keys | Simplify auth in config_manager |
| GraphQL | Modify client for query/mutation pattern |
| WebSocket | Add connection management to client |
| Pagination (cursor) | Implement cursor-based iteration |
| Pagination (offset) | Implement offset-based iteration |

### Adding Custom Utilities

If your API needs utilities not in templates:

1. Add to `shared/scripts/lib/`
2. Follow existing patterns (docstrings, error handling)
3. Add corresponding unit tests
4. Update shared-lib documentation

---

## Checklist: Project Completion

Before considering a project complete:

### Research & Planning
- [ ] API research completed
- [ ] GAP analysis document created
- [ ] Architecture designed
- [ ] Implementation plan with phases

### Core Implementation
- [ ] Shared library implemented and tested
- [ ] All planned skills implemented
- [ ] Router skill routes to all skills
- [ ] All scripts support `--help`

### Testing
- [ ] Unit tests for all scripts
- [ ] Live integration tests exist
- [ ] Test coverage meets targets
- [ ] Full regression suite passes

### Documentation
- [ ] CLAUDE.md complete
- [ ] README.md user-friendly
- [ ] All SKILL.md files have 3 levels
- [ ] Troubleshooting guide exists

### Version Control
- [ ] Conventional commits used
- [ ] TDD commit pattern followed
- [ ] CI/CD configured
- [ ] .gitignore includes credentials

---

## Tips for Success

### 1. Complete Research First
Resist the urge to start coding. A thorough GAP analysis prevents rework.

### 2. Small Skills, Clear Boundaries
Better to have 10 focused skills than 3 bloated ones.

### 3. Test Coverage is Non-Negotiable
Aim for 80%+ unit test coverage, 100% happy path integration.

### 4. Progressive Disclosure Saves Tokens
Keep SKILL.md Level 1+2 under 500 tokens. Link to Level 3.

### 5. Update Plans as You Go
The implementation plan is a living document. Update after each milestone.

### 6. Commit Often with TDD Pattern
Small, focused commits with test counts are easier to review and revert.
