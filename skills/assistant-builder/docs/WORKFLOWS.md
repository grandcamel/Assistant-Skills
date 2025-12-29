# Workflows

Common workflows for using the assistant-builder skill.

## Workflow 1: Create a New Project

### Step 1: Run the Wizard

```bash
cd ~/projects
python ~/.../assistant-builder/scripts/scaffold_project.py
```

Or with Claude Code:
```
/assistant-builder-setup
```

### Step 2: Answer the Prompts

1. **Project name**: e.g., "Stripe-Assistant-Skills"
2. **Topic prefix**: e.g., "stripe"
3. **API name**: e.g., "Stripe"
4. **Base URL**: e.g., "https://api.stripe.com"
5. **Auth method**: e.g., "api_key"
6. **Initial skills**: e.g., "payments,customers,subscriptions"

### Step 3: Review Generated Structure

```
Stripe-Assistant-Skills/
├── .claude/
│   ├── settings.json
│   └── skills/
│       ├── shared/
│       ├── stripe-assistant/
│       ├── stripe-payments/
│       ├── stripe-customers/
│       └── stripe-subscriptions/
├── CLAUDE.md
├── README.md
└── pyproject.toml
```

### Step 4: Configure Credentials

```bash
cd Stripe-Assistant-Skills

# Create local settings (gitignored)
cat > .claude/settings.local.json << 'EOF'
{
  "stripe": {
    "api_token": "sk_test_..."
  }
}
EOF
```

### Step 5: Implement Shared Library

Follow TDD:
1. Write failing tests for client
2. Implement client
3. Repeat for error_handler, validators, formatters

---

## Workflow 2: Add a Skill to Existing Project

### Step 1: Navigate to Project

```bash
cd ~/projects/Stripe-Assistant-Skills
```

### Step 2: Run add_skill

```bash
python ~/.../assistant-builder/scripts/add_skill.py \
  --name "invoices" \
  --description "Invoice management operations" \
  --scripts crud
```

### Step 3: Implement Following TDD

```bash
# Write failing tests
cd .claude/skills/stripe-invoices
# Edit tests/test_list_invoices.py

# Commit tests
git add -A
git commit -m "test(stripe-invoices): add failing tests for list_invoices"

# Implement
# Edit scripts/list_invoices.py

# Commit implementation
git add -A
git commit -m "feat(stripe-invoices): implement list_invoices (5/5 tests passing)"
```

### Step 4: Update Router Skill

Add new skill to `stripe-assistant/SKILL.md` routing table.

---

## Workflow 3: Learn from Reference Projects

### Step 1: List Available Topics

```bash
python show_reference.py --list-topics
```

### Step 2: View Specific Pattern

```bash
# Shared library pattern from Jira
python show_reference.py --topic shared-library --project jira

# Compare router skills
python show_reference.py --topic router-skill --project all
```

### Step 3: Apply to Your Project

Use the patterns as guidance for your implementation.

---

## Workflow 4: Validate Project Structure

### Step 1: Run Validation

```bash
python validate_project.py ~/projects/MySkills
```

### Step 2: Review Output

```
Validation: /Users/.../MySkills

Errors (2):
  - Missing .claude/settings.json
  - Missing shared library

Warnings (3):
  - my-skill: Missing SKILL.md frontmatter
  - my-skill: No test files found
  - Missing CLAUDE.md

Project Statistics:
  Skills: 2
  Scripts: 5
  Tests: 0
  Docs: 1
```

### Step 3: Fix Issues

Address errors first (required), then warnings (recommended).

---

## Workflow 5: Explore Templates

### Step 1: List All Templates

```bash
python list_templates.py --format tree
```

### Step 2: View Specific Template

```bash
python show_template.py SKILL.md.template --show-placeholders
```

### Step 3: Use Template Content

Copy relevant sections into your project files.

---

## TDD Commit Pattern

Always follow this pattern:

### Commit 1: Failing Tests

```bash
# Write tests that fail
git add -A
git commit -m "test(skill-name): add failing tests for feature_name"
```

### Commit 2: Implementation

```bash
# Implement to pass tests
git add -A
git commit -m "feat(skill-name): implement feature_name (N/N tests passing)"
```

### Example Sequence

```bash
# Tests for list
git commit -m "test(stripe-invoices): add failing tests for list_invoices"
git commit -m "feat(stripe-invoices): implement list_invoices (5/5 tests passing)"

# Tests for get
git commit -m "test(stripe-invoices): add failing tests for get_invoice"
git commit -m "feat(stripe-invoices): implement get_invoice (3/3 tests passing)"

# Tests for create
git commit -m "test(stripe-invoices): add failing tests for create_invoice"
git commit -m "feat(stripe-invoices): implement create_invoice (4/4 tests passing)"
```
