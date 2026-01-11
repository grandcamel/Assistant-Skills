# Risk Level Marking Pattern

A standardized approach for marking operation risk in Claude Code skills.

---

## Purpose

Risk levels teach Claude which operations require additional safeguards:
- Read-only operations can proceed without confirmation
- Destructive operations should request confirmation
- High-risk operations require confirmation AND dry-run preview

---

## Risk Level Definitions

### `-` (Dash) - Read-only / Safe

Operations with no side effects that can be safely repeated.

**Characteristics**:
- No data modification
- No state changes
- Idempotent
- Can be undone by simply not using the result

**Examples**:
- `search_items.py` - Search with query
- `list_resources.py` - List all resources
- `get_item.py` - Get single item details
- `export_data.py` - Export to file
- `validate_input.py` - Validate without executing

**Safeguards**: None required

---

### `⚠️` (Single Warning) - Destructive Operations

Operations that modify data but are recoverable or affect single items.

**Characteristics**:
- Creates, updates, or deletes data
- Affects single items or small sets
- Potentially reversible (can be undone manually)
- State changes that could be unintended

**Examples**:
- `create_item.py` - Create new item
- `update_item.py` - Update single item fields
- `delete_item.py` - Delete single item
- `transition_status.py` - Change item status
- `assign_user.py` - Change assignment

**Safeguards**:
1. Confirm before destructive action
2. Show what will be affected
3. Offer to cancel

**Confirmation Pattern**:
```
About to delete ITEM-123 "Feature request".
This action cannot be undone.

Proceed? [y/N]
```

---

### `⚠️⚠️` (Double Warning) - High-Risk Operations

Operations with significant blast radius or irreversible consequences.

**Characteristics**:
- Affects many items at once (bulk operations)
- Admin-level changes (permissions, settings)
- Irreversible or expensive to reverse
- Could cause significant disruption if wrong

**Examples**:
- `bulk_delete.py` - Delete multiple items
- `bulk_update.py` - Update 10+ items
- `change_permissions.py` - Modify access controls
- `delete_project.py` - Delete container with contents
- `purge_old_data.py` - Permanent data removal
- `automation_rule_create.py` - Create automated actions

**Safeguards**:
1. Require explicit confirmation
2. **Always offer dry-run first**
3. Show summary of what will be affected
4. Consider requiring explicit `--force` flag

**Confirmation Pattern**:
```
About to update 47 items matching "project = ABC AND status = Open".

Changes:
  - priority: High → Medium
  - assignee: (unchanged)

This will affect 47 items. Run with --dry-run first? [Y/n]

Dry-run complete. 47 items would be updated:
  - ABC-101: priority High → Medium
  - ABC-102: priority High → Medium
  ... (45 more)

Proceed with actual update? [y/N]
```

---

## Implementation in SKILL.md

### Quick Reference Table Format

```markdown
## Quick Reference

| I want to... | Use this skill | Risk |
|--------------|----------------|:----:|
| Search with queries | topic-search | - |
| Create a single item | topic-issue | ⚠️ |
| Update 10+ items at once | topic-bulk | ⚠️⚠️ |

**Risk Legend**: `-` Read-only/safe | `⚠️` Destructive (confirm) | `⚠️⚠️` High-risk (confirm + dry-run)
```

### Per-Script Documentation

```markdown
## Available Scripts

### create_item.py ⚠️

Creates a new item in the specified project.

**Risk**: This creates data. Confirm project and type before executing.

### bulk_delete.py ⚠️⚠️

Deletes multiple items matching criteria.

**Risk**: This permanently deletes data. Always run with `--dry-run` first.

```bash
# Preview what will be deleted
python bulk_delete.py --query "status = Obsolete" --dry-run

# Execute after confirming
python bulk_delete.py --query "status = Obsolete" --confirm
```
```

---

## Risk Assessment Criteria

Use this matrix to determine risk level:

| Factor | `-` Safe | `⚠️` Destructive | `⚠️⚠️` High-Risk |
|--------|----------|------------------|------------------|
| **Data modification** | None | Single item | Multiple items |
| **Reversibility** | N/A | Easy to undo | Hard/impossible |
| **Blast radius** | 0 items | 1-10 items | 10+ items |
| **Permission level** | Read | Write | Admin |
| **Frequency of regret** | Never | Sometimes | Often |

### Decision Tree

```
Is data modified?
├── No → Risk: -
└── Yes → How many items affected?
    ├── 1 item → Risk: ⚠️
    └── Multiple items → Is it reversible?
        ├── Yes (easy) → Risk: ⚠️
        └── No or hard → Risk: ⚠️⚠️
```

---

## Script Implementation Patterns

### Safe Operations (Risk: -)

```python
def main():
    # No special handling needed
    results = search_items(query)
    print_results(results)
```

### Destructive Operations (Risk: ⚠️)

```python
def main():
    item = get_item(item_id)

    # Show what will be affected
    print(f"About to delete: {item['key']} - {item['summary']}")

    # Confirm unless --force
    if not args.force:
        confirm = input("Proceed? [y/N] ")
        if confirm.lower() != 'y':
            print("Cancelled.")
            return

    delete_item(item_id)
    print(f"Deleted {item['key']}")
```

### High-Risk Operations (Risk: ⚠️⚠️)

```python
def main():
    items = search_items(query)

    # Always show summary
    print(f"Found {len(items)} items matching query.")

    # Dry-run by default or when requested
    if args.dry_run or not args.confirm:
        print("\nDry-run preview:")
        for item in items[:10]:
            print(f"  Would delete: {item['key']}")
        if len(items) > 10:
            print(f"  ... and {len(items) - 10} more")

        if not args.confirm:
            print("\nRun with --confirm to execute.")
            return

    # Require explicit confirmation for actual execution
    if args.confirm:
        confirm = input(f"Delete {len(items)} items? [y/N] ")
        if confirm.lower() != 'y':
            print("Cancelled.")
            return

        for item in items:
            delete_item(item['id'])
        print(f"Deleted {len(items)} items.")
```

---

## Common Mistakes

### 1. Missing Risk Indicator
**Bad**: No indication that operation modifies data
**Good**: Clear risk level in table and script docs

### 2. No Dry-Run for Bulk Operations
**Bad**: Bulk delete with only a confirmation prompt
**Good**: Dry-run preview showing exactly what will be affected

### 3. Inconsistent Risk Assessment
**Bad**: Similar operations with different risk levels
**Good**: Consistent criteria applied across all skills

### 4. Risk Level Inflation
**Bad**: Marking read-only operations as ⚠️
**Good**: Reserve warnings for actual destructive operations

### 5. Risk Level Deflation
**Bad**: Marking bulk deletes as ⚠️ instead of ⚠️⚠️
**Good**: Acknowledge the blast radius in risk assessment

---

## Validation Checklist

For router skills:
- [ ] All skills in Quick Reference have risk levels
- [ ] Risk legend is included below the table
- [ ] High-risk skills (⚠️⚠️) have dry-run documentation
- [ ] Destructive skills (⚠️) have confirmation patterns

For individual skills:
- [ ] Scripts with side effects are marked with risk level
- [ ] Confirmation patterns are documented
- [ ] Dry-run flag is available for bulk operations
- [ ] Error messages suggest recovery options
