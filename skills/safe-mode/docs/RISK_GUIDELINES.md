# Risk Level Guidelines

How to classify CLI operations by risk level for the claude-safe permission system.

## Risk Level Definitions

| Level | Value | Recovery | User Impact | Examples |
|-------|:-----:|----------|-------------|----------|
| **safe** | 0 | N/A (read-only) | None | list, get, search, view |
| **caution** | 1 | Easy undo | Minimal | create, update, enable |
| **warning** | 2 | From backup/trash | Moderate | delete single item |
| **danger** | 3 | **None** | Severe | bulk delete, drop, purge |

## Decision Tree

```
Is the operation read-only?
├── Yes → safe
└── No → Does it create/modify data?
    ├── Yes → Is it easily reversible?
    │   ├── Yes → caution
    │   └── No → warning
    └── No → Does it delete data?
        ├── Single item with recovery option → warning
        ├── Single item, no recovery → danger
        └── Bulk/all items → danger
```

## Classification by Operation Type

### Safe Operations
Operations that **never** modify state:

| Operation | Pattern Examples |
|-----------|-----------------|
| List/enumerate | `list *`, `ls *` |
| Read single | `get *`, `view *`, `show *` |
| Search/query | `search *`, `query *`, `find *` |
| Status check | `status *`, `info *`, `health *` |
| Export/download | `export *`, `download *` |
| Validate | `validate *`, `check *`, `lint *` |

### Caution Operations
Operations that modify state but are **easily reversible**:

| Operation | Pattern Examples | Recovery |
|-----------|-----------------|----------|
| Create new | `create *`, `add *`, `new *` | Delete the created item |
| Update existing | `update *`, `edit *`, `set *` | Update again with old value |
| Enable/disable | `enable *`, `disable *` | Toggle back |
| Upload/import | `upload *`, `import *` | Re-upload original |
| Assign/unassign | `assign *`, `unassign *` | Reassign |
| Move/rename | `move *`, `rename *` | Move/rename back |

### Warning Operations
Operations that are **destructive but potentially recoverable**:

| Operation | Pattern Examples | Recovery |
|-----------|-----------------|----------|
| Delete single | `delete *`, `remove *` | Restore from trash/backup |
| Cancel job | `cancel *` | Re-run the job |
| Close/archive | `close *`, `archive *` | Reopen/unarchive |
| Revoke access | `revoke *` | Re-grant access |
| Merge (with history) | `merge *` | Revert merge commit |

### Danger Operations
Operations that are **IRREVERSIBLE**:

| Operation | Pattern Examples | Why Irreversible |
|-----------|-----------------|------------------|
| Bulk delete | `bulk delete *` | Too many items to restore |
| Purge/permanent delete | `purge *`, `force-delete *` | Bypasses trash |
| Drop collection/table | `drop *` | All data lost |
| Uninstall | `uninstall *` | Config and data removed |
| Delete project/space | `project delete *`, `space delete *` | Contains many sub-items |
| Wipe/reset | `wipe *`, `reset *` | Clears all data |

## Edge Cases

### Operations That May Vary

Some operations may be different risk levels depending on context:

| Operation | Lower Risk When | Higher Risk When |
|-----------|-----------------|------------------|
| `delete` | Single item, has trash | Bulk, no trash |
| `update` | Single field | Bulk update |
| `disable` | Single item | All items |
| `export` | To local file | To external service |

### CLI-Specific Considerations

Different CLIs may have different recovery mechanisms:

| Platform | Trash/Recovery | Audit Log | Backup |
|----------|---------------|-----------|--------|
| JIRA | 30-day trash | Yes | Manual |
| Confluence | 30-day trash | Yes | Manual |
| GitLab | Some recovery | Yes | Git history |
| Splunk | No trash | Audit index | Manual |

## Best Practices

1. **When in doubt, go higher** - It's safer to require more confirmation
2. **Consider the blast radius** - Bulk operations should always be higher risk
3. **Check for recovery mechanisms** - If the platform has trash/undo, use warning instead of danger
4. **Document exceptions** - If an operation seems miscategorized, add a comment explaining why
5. **Test with dry-run** - Always verify patterns work as expected before deploying
