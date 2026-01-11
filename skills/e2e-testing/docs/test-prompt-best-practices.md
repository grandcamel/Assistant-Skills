# Test Prompt Best Practices

Well-designed test prompts complete in fewer turns and produce consistent results.

## Avoid Exploration Triggers

Prompts that trigger file exploration can exhaust turns before producing output:

```yaml
# BAD - May cause Claude to read files for multiple turns
prompt: "What templates are available for this project?"
prompt: "Analyze the shared library structure"
prompt: "What are the main dependencies?"

# GOOD - Direct questions that don't require file exploration
prompt: "Without reading files, what templates are typically used for Assistant Skills projects?"
prompt: "Without reading files, describe typical Python package dependencies for plugins."
prompt: "Briefly explain what a landing-page skill typically does."
```

## Use Flexible Expectations

Test validation should be lenient to handle Claude's varied responses:

```yaml
# BAD - Exact match is fragile
expect:
  output_contains:
    - "assistant-skills-lib"

# GOOD - Any of these terms indicates success
expect:
  output_contains_any:
    - "skill"
    - "plugin"
    - "SKILL"
    - "claude"
  no_crashes: true  # More lenient than no_errors
```

## Prompt Design Patterns

| Pattern | Example | Purpose |
|---------|---------|---------|
| Prefix constraint | "Without reading files, ..." | Prevents file exploration |
| Direct question | "What is X?" vs "Analyze X" | Faster response |
| Conceptual focus | "What does X typically do?" | Avoids project-specific exploration |
| Flexible terms | Multiple synonyms in `output_contains_any` | Handles response variation |
