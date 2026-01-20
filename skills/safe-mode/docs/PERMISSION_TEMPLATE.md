# Permission Block Template

Copy this template to your plugin's SAFEGUARDS.md file and customize for your CLI.

## Template

```markdown
<!-- PERMISSIONS
permissions:
  cli: your-cli-name
  operations:
    # Safe - Read-only operations
    - pattern: "your-cli list *"
      risk: safe
    - pattern: "your-cli get *"
      risk: safe
    - pattern: "your-cli view *"
      risk: safe
    - pattern: "your-cli search *"
      risk: safe
    - pattern: "your-cli status *"
      risk: safe

    # Caution - Modifiable but easily reversible
    - pattern: "your-cli create *"
      risk: caution
    - pattern: "your-cli update *"
      risk: caution
    - pattern: "your-cli enable *"
      risk: caution
    - pattern: "your-cli disable *"
      risk: caution

    # Warning - Destructive but potentially recoverable
    - pattern: "your-cli delete *"
      risk: warning
    - pattern: "your-cli remove *"
      risk: warning

    # Danger - IRREVERSIBLE operations
    - pattern: "your-cli purge *"
      risk: danger
    - pattern: "your-cli drop *"
      risk: danger
    - pattern: "your-cli force-delete *"
      risk: danger
-->
```

## Guidelines

### Safe (risk: safe)
- Read-only operations that never modify data
- List, get, view, search, status, export
- No confirmation needed

### Caution (risk: caution)
- Operations that modify data but are easily reversible
- Create, update, enable, disable, upload
- Optional confirmation

### Warning (risk: warning)
- Destructive operations on single items
- Delete, remove, cancel (where data can potentially be recovered)
- Recommended confirmation

### Danger (risk: danger)
- Irreversible operations
- Bulk delete, purge, drop, force-delete, uninstall
- **Required confirmation and dry-run**

## Placement

Add the permission block at the **end** of your SAFEGUARDS.md file, after all other content.

The block is parsed as YAML within HTML comments, so it won't affect the rendered markdown.

## Validation

Test your permission block:

```bash
# Preview with verbose output
claude-safe -n -v -l safe -p "/path/to/your/plugin"
```

Check that:
1. All patterns are parsed correctly
2. Risk levels are assigned as expected
3. Allow/deny lists match your intent
