# Naming Conventions

## Directory Names

### Gerund Form (Recommended)

Use present participle (-ing) form for action-oriented skills:

| Good | Bad |
|------|-----|
| `analyzing-spreadsheets` | `spreadsheet-analyzer` |
| `generating-apis` | `api-generator` |
| `optimizing-performance` | `performance-optimizer` |
| `building-components` | `component-builder` |

**Why gerunds?**
- Emphasizes the action Claude performs
- Consistent pattern recognition
- Matches user intent phrasing ("I need help analyzing...")

### Noun Form (Acceptable)

Use for static reference skills:

| Good | Bad |
|------|-----|
| `api-reference` | `apis` |
| `style-guide` | `styles` |
| `architecture-patterns` | `architectures` |

### Formatting Rules

```
skill-name-here
│
├── lowercase only
├── hyphens between words (no underscores)
├── no special characters
├── no version numbers
└── 3-5 words max
```

**Valid**:
- `optimizing-skills-performance`
- `github-workflow-automation`
- `react-component-generator`

**Invalid**:
- `Optimizing_Skills` (uppercase, underscores)
- `skill-v2.0` (version number)
- `my-awesome-super-cool-skill-for-everything` (too long)

---

## Skill Names (YAML)

### Title Case Convention

```yaml
name: "Skills Performance Optimizer"  # Title Case
name: "API Documentation Generator"   # Title Case
name: "React Component Builder"        # Title Case
```

### Length Guidelines

| Length | Assessment |
|--------|------------|
| 1-3 words | Excellent |
| 4-5 words | Good |
| 6+ words | Too long, trim it |

### Avoid

```yaml
# Too generic
name: "Helper"
name: "Utility"
name: "Tool"

# Too verbose
name: "A Comprehensive Tool for Building and Deploying APIs"

# Unclear
name: "XYZ Processor v2"
```

---

## Description Keywords

### Front-Load Action Verbs

Place the most important keywords at the start:

**Good** (action first):
```yaml
description: "Generate OpenAPI docs from Express routes. Use when..."
description: "Analyze code quality and suggest improvements. Use when..."
description: "Build React components with TypeScript. Use when..."
```

**Bad** (buried action):
```yaml
description: "This skill helps developers by providing tools to generate..."
description: "A comprehensive solution for those who need to analyze..."
```

### Trigger Keyword Patterns

Include these patterns for reliable matching:

```yaml
# Pattern: "Use when [trigger condition]"
description: "... Use when creating new projects."
description: "... Use when debugging performance issues."
description: "... Use when refactoring legacy code."

# Pattern: "Invoke for [use case]"
description: "... Invoke for API documentation tasks."

# Pattern: "Triggers on [condition]"
description: "... Triggers on requests for code review."
```

### Power Keywords

These keywords improve matching:

| Category | Keywords |
|----------|----------|
| Creation | generate, create, build, scaffold, initialize |
| Analysis | analyze, audit, review, inspect, evaluate |
| Transformation | convert, migrate, refactor, transform, optimize |
| Documentation | document, describe, explain, annotate |
| Testing | test, validate, verify, check, assert |
| Deployment | deploy, publish, release, ship |

---

## File Naming

### SKILL.md (Required)

Always uppercase, always `.md`:
```
SKILL.md    ✓
skill.md    ✗
Skill.MD    ✗
README.md   ✗ (not the main skill file)
```

### Documentation Files

```
docs/
├── getting-started.md      # Lowercase, hyphens
├── api-reference.md        # Descriptive names
├── advanced-config.md      # Topic-focused
└── troubleshooting.md      # Action-oriented
```

### Script Files

```
scripts/
├── setup.sh               # Verb-first
├── validate.js            # Action names
├── generate-report.py     # Hyphenated actions
└── analyze-skill.sh       # Clear purpose
```

### Resource Files

```
resources/
├── templates/
│   ├── component.tsx.template    # .template suffix
│   └── api-route.js.template
├── examples/
│   ├── basic-usage/              # Descriptive folders
│   └── advanced-config/
└── schemas/
    └── config.schema.json        # .schema suffix
```

---

## Mapping Directory to Name

### Conversion Pattern

| Directory Name | YAML Name |
|---------------|-----------|
| `analyzing-spreadsheets` | "Spreadsheet Analyzer" |
| `github-workflow-automation` | "GitHub Workflow Automation" |
| `react-component-generator` | "React Component Generator" |
| `api-docs-builder` | "API Documentation Builder" |

### Transformation Rules

1. **Replace hyphens with spaces**
2. **Apply Title Case**
3. **Expand abbreviations** (api -> API, github -> GitHub)
4. **Adjust gerunds if needed** (analyzing -> Analyzer OR keep as Analyzing)

---

## Anti-Patterns

### Directory Names

```
# Version numbers
my-skill-v2/          ✗
skill-2.0/            ✗

# Underscores
my_skill/             ✗

# Mixed case
MySkill/              ✗
mySkill/              ✗

# Special characters
skill@2.0/            ✗
skill+plus/           ✗

# Spaces
my skill/             ✗
```

### YAML Names

```yaml
# All lowercase
name: "api builder"           ✗

# All uppercase
name: "API BUILDER"           ✗

# With version
name: "API Builder v2.0"      ✗

# Generic
name: "Skill"                 ✗
name: "Tool"                  ✗
name: "Helper"                ✗
```

### Descriptions

```yaml
# Starting with "This skill..."
description: "This skill helps you..."    ✗

# Starting with "A tool for..."
description: "A tool for building..."     ✗

# No trigger condition
description: "Builds APIs with Express."  ✗

# Too vague
description: "Helps with development."    ✗
```

---

## Validation Regex

```javascript
// Directory name validation
const validDirName = /^[a-z][a-z0-9]*(-[a-z0-9]+)*$/;

// YAML name validation
const validYamlName = /^[A-Z][A-Za-z0-9\s]+$/;

// Description validation (has "use when" or similar)
const hasTrigger = /(use when|invoke for|triggers on|invoke when)/i;
```

---

## Quick Reference Card

```
DIRECTORY NAME:
  Format:     lowercase-hyphen-separated
  Length:     3-5 words
  Example:    optimizing-skills-performance

YAML NAME:
  Format:     Title Case With Spaces
  Length:     2-5 words
  Example:    "Skills Performance Optimizer"

DESCRIPTION:
  Format:     [Action verb] [what]. Use when [trigger].
  Length:     50-200 words
  Example:    "Audit skills for token efficiency. Use when optimizing skill footprint."

FILES:
  Main:       SKILL.md (uppercase)
  Docs:       lowercase-hyphen.md
  Scripts:    action-name.sh/js/py
```
