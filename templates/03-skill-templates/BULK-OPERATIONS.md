# Bulk Operations Patterns

Safe patterns for high-risk bulk operations with dry-run, batching, and checkpointing.

---

## Core Flags

| Flag | Purpose | Default |
|------|---------|---------|
| `--dry-run` | Preview without executing | Off |
| `--batch-size N` | Items per batch | 50 |
| `--batch-delay N` | Seconds between batches | 1.0 |
| `--enable-checkpoint` | Save progress for resume | Off |
| `--resume FILE` | Continue from checkpoint | - |
| `--confirm` | Skip confirmation prompt | Off |

---

## Required Workflow

### Step 1: Always Preview First

```bash
# Preview what will be affected
python bulk_update.py --query "status=active" --set-field priority=high --dry-run
```

Output:
```
Found 47 issues to update
Updates: {'priority': 'high'}

[DRY RUN] Preview of changes:
  Would update: PROJ-101 - Fix login bug
  Would update: PROJ-102 - Add dark mode
  ... and 45 more

[DRY RUN] Would update 47 issue(s)
Run without --dry-run to execute
```

### Step 2: Execute with Safeguards

```bash
# Small batch with rate limiting
python bulk_update.py --query "status=active" --set-field priority=high \
    --batch-size 10 --batch-delay 2
```

### Step 3: For Large Operations, Enable Checkpointing

```bash
# Enable checkpoint for resumability
python bulk_update.py --query "status=active" --set-field priority=high \
    --enable-checkpoint
```

### Step 4: Resume if Interrupted

```bash
# Resume from last checkpoint
python bulk_update.py --resume .checkpoints/checkpoint_20240101_120000.json
```

---

## Checkpoint File Format

```json
{
  "query": "status=active",
  "fields": ["priority=high"],
  "remaining_ids": ["PROJ-145", "PROJ-146", "PROJ-147"],
  "success_count": 44,
  "error_count": 0,
  "errors": [],
  "timestamp": "2024-01-01T12:30:00"
}
```

---

## Batch Processing Pattern

```python
for i in range(0, total, batch_size):
    batch = items[i:i + batch_size]

    for item in batch:
        try:
            process(item)
            success_count += 1
        except Exception as e:
            error_count += 1
            errors.append({'id': item['id'], 'error': str(e)})

    # Save checkpoint after each batch
    if enable_checkpoint:
        save_checkpoint(remaining_items)

    # Rate limit between batches
    if more_batches_remaining:
        time.sleep(batch_delay)
```

---

## Error Handling

### Partial Failure Strategy

When some items fail:
1. Continue processing remaining items
2. Collect all errors
3. Report summary at end
4. Save failed items for retry

```python
# Summary output
print(f"Success: {success_count}")
print(f"Errors:  {error_count}")

if errors:
    print("Failed items:")
    for err in errors:
        print(f"  {err['id']}: {err['error']}")

    # Save failed items for retry
    save_failed_items(errors)
```

### Retry Failed Items

```bash
# Retry only failed items
python bulk_update.py --ids PROJ-101 PROJ-102 PROJ-103 --set-field priority=high
```

---

## Risk Level Integration

### In SKILL.md Quick Reference

```markdown
| Operation | Script | Risk |
|-----------|--------|:----:|
| Bulk update | `bulk_update.py` | ⚠️⚠️ |
| Bulk delete | `bulk_delete.py` | ⚠️⚠️ |
```

### In Script Documentation

```markdown
### bulk_update.py ⚠️⚠️

Bulk update items matching criteria.

**Risk**: High - affects multiple items. Always use `--dry-run` first.

**Required workflow**:
1. Preview: `--dry-run`
2. Execute with small batches: `--batch-size 10`
3. For large operations: `--enable-checkpoint`
```

---

## Implementation Checklist

For bulk operation scripts:

- [ ] `--dry-run` flag shows preview without executing
- [ ] `--batch-size` controls items per batch
- [ ] `--batch-delay` adds delay between batches
- [ ] `--enable-checkpoint` saves progress after each batch
- [ ] `--resume` continues from checkpoint file
- [ ] Confirmation required before execution
- [ ] Partial failures collected and reported
- [ ] Failed items saved for retry
- [ ] Progress shown during execution

---

## Example Output

```
Found 150 issues to update
Updates: {'priority': 'high'}
Batch size: 25

Update 150 issue(s)? [y/N]: y

Processing batch 1/6 (25 items)
  Checkpoint saved: .checkpoints/checkpoint_20240101_120000.json
  Waiting 1.0s before next batch...

Processing batch 2/6 (25 items)
  Failed: PROJ-127 - Permission denied
  Checkpoint saved: .checkpoints/checkpoint_20240101_120000.json
  Waiting 1.0s before next batch...

...

==================================================
Bulk update complete
  Success: 149
  Errors:  1

Failed items:
  PROJ-127: Permission denied

1 errors occurred. Review and retry failed items.
Resume with: python bulk_update.py --resume .checkpoints/checkpoint_20240101_120000.json
```
