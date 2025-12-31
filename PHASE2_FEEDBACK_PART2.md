# Phase 2 Revised Proposal Feedback

**Date:** December 31, 2025
**Author:** Claude (Opus 4.5)
**Re:** Review of `REVISED_PROPOSAL_PHASE2.md` (Gemini AI Agent)

---

## Executive Summary

The revised proposal is a **significant improvement** over the original. It correctly adopts:
- Subcommand CLI pattern (`jira issue get`)
- Scripts remain in plugins (not libraries)
- Additive approach with no breaking changes
- Extended deprecation timeline (6+ months)

**Verdict:** Approve with minor revisions.

The remaining concerns are implementation details, not architectural issues.

---

## What the Proposal Gets Right

| Concern from Part 1 | Resolution in Revised Proposal |
|---------------------|-------------------------------|
| Flat entry points | ✅ Switched to subcommand pattern |
| Scripts in library | ✅ Entry point defined in plugin |
| Skill isolation broken | ✅ Scripts stay in `skills/*/scripts/` |
| Compatibility shim complexity | ✅ Additive approach, no shims |
| Missing test strategy | ✅ CliRunner with mocked scripts |
| Aggressive deprecation | ✅ 6+ month window mentioned |

This demonstrates good responsiveness to feedback.

---

## Remaining Concerns

### 1. Import Path Won't Work

The example code shows:

```python
from skills.jira_issue.scripts.get_issue import main as get_issue_main
```

This will fail because:
- `skills/` is not a Python package (no `__init__.py`)
- Directory uses hyphens (`jira-issue`), not underscores (`jira_issue`)
- Scripts may not be in Python path

**Fix Options:**

**Option A: Subprocess Delegation (Recommended for Phase 1)**
```python
import subprocess
import sys
from pathlib import Path

SKILLS_DIR = Path(__file__).parent.parent.parent.parent / "skills"

@issue.command(name="get")
@click.argument('issue_key')
@click.option('--output', default='text')
def get_issue(issue_key: str, output: str):
    """Get the details of a specific issue."""
    script = SKILLS_DIR / "jira-issue" / "scripts" / "get_issue.py"
    result = subprocess.run(
        [sys.executable, str(script), issue_key, '--output', output],
        capture_output=False
    )
    sys.exit(result.returncode)
```

**Option B: Dynamic Import (Requires script restructuring)**
```python
import importlib.util
from pathlib import Path

def load_script_main(skill_name: str, script_name: str):
    """Dynamically load a script's main function."""
    script_path = SKILLS_DIR / skill_name / "scripts" / f"{script_name}.py"
    spec = importlib.util.spec_from_file_location(script_name, script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.main
```

**Recommendation:** Start with subprocess delegation (Option A). It works immediately without script changes. Migrate to dynamic import later if performance becomes an issue.

---

### 2. sys.argv Manipulation is Fragile

The proposal shows:
```python
original_argv = sys.argv
sys.argv = [sys.argv[0], issue_key, '--output', output]
try:
    get_issue_main()
finally:
    sys.argv = original_argv
```

Problems:
- Not thread-safe
- Breaks if script accesses sys.argv at import time
- Requires careful argument reconstruction

**Better Approach:** Refactor scripts to accept explicit arguments:

```python
# Before (fragile)
def main():
    args = parse_args(sys.argv[1:])
    ...

# After (clean)
def main(argv: list[str] | None = None):
    args = parse_args(argv if argv is not None else sys.argv[1:])
    ...
```

This allows the CLI to call `get_issue_main(['PROJ-123', '--output', 'json'])` directly.

**Recommendation:** Add a prerequisite step to Phase 2: "Refactor all scripts to accept optional argv parameter."

---

### 3. Manual Command Registration Doesn't Scale

The proposal shows each command manually defined:
```python
@issue.command(name="get")
def get_issue(...): ...

@issue.command(name="create")
def create_issue(...): ...
```

For 83+ scripts, this becomes unmaintainable.

**Better Approach: Auto-Discovery Pattern**

Each skill defines its CLI commands in a standard file:

```python
# skills/jira-issue/cli.py
import click

@click.group()
def issue():
    """Issue operations."""
    pass

@issue.command()
@click.argument('key')
def get(key):
    """Get issue details."""
    from .scripts.get_issue import main
    main([key])
```

Main CLI discovers and registers skill CLIs:

```python
# src/jira_assistant_skills/cli/main.py
import click
from pathlib import Path
import importlib.util

@click.group()
def cli():
    """Jira Assistant Skills CLI."""
    pass

def discover_skill_clis():
    """Auto-discover CLI definitions from skills."""
    skills_dir = Path(__file__).parent.parent.parent.parent / "skills"
    for skill_dir in skills_dir.iterdir():
        cli_file = skill_dir / "cli.py"
        if cli_file.exists():
            # Load and register the skill's CLI group
            spec = importlib.util.spec_from_file_location("skill_cli", cli_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            # Find Click groups in the module and register them
            for name in dir(module):
                obj = getattr(module, name)
                if isinstance(obj, click.core.Group):
                    cli.add_command(obj)

discover_skill_clis()
```

**Recommendation:** Adopt auto-discovery pattern to scale gracefully.

---

### 4. Plugin Package Structure Unclear

The proposal assumes:
```
Jira-Assistant-Skills/
└── src/jira_assistant_skills/
    └── cli/main.py
```

But current structure is likely:
```
Jira-Assistant-Skills/
├── skills/
│   └── jira-issue/
└── (no src/ directory)
```

**Questions:**
- Does `Jira-Assistant-Skills` already have a `src/` layout?
- Is it already pip-installable?
- If not, what's the migration plan?

**Recommendation:** Add a section clarifying plugin package structure requirements and any needed restructuring.

---

### 5. Test Location Non-Standard

The proposal places tests in:
```
src/jira_assistant_skills/tests/test_cli.py
```

Standard Python convention is:
```
tests/test_cli.py  # Top-level tests directory
```

Or for pytest with src layout:
```
tests/
└── test_cli.py

pyproject.toml:
[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
```

**Recommendation:** Use standard `tests/` directory at project root, consistent with existing test infrastructure.

---

### 6. Click vs Typer vs Argparse

The proposal specifies `click>=8.0`. Alternatives:

| Framework | Pros | Cons |
|-----------|------|------|
| **Click** | Mature, widely used, excellent docs | Decorator-heavy syntax |
| **Typer** | Type hint-based, less boilerplate | Requires Python 3.7+, newer |
| **Argparse** | Stdlib, no dependencies | Verbose, less ergonomic |

**Recommendation:** Click is fine. Typer would also work well. Document the choice rationale.

---

### 7. Non-Python Scripts

Some skills may have bash scripts. How are these exposed?

**Recommendation:** Add clarification that non-Python scripts can be wrapped with a subprocess call:

```python
@cli.command()
@click.argument('args', nargs=-1)
def legacy_bash_tool(args):
    """Run legacy bash tool."""
    script = SKILLS_DIR / "some-skill" / "scripts" / "tool.sh"
    subprocess.run(["bash", str(script)] + list(args))
```

---

## Minor Suggestions

### 1. Pilot Skill

> "Start with `jira-issue` as the pilot skill before scaling to all 83+ scripts."

Add explicit pilot phase:
1. Implement CLI for `jira-issue` skill only
2. Run E2E tests
3. Gather feedback
4. Scale to remaining skills

### 2. Help Text Quality

Ensure help text is useful:

```
$ jira --help
Usage: jira [OPTIONS] COMMAND [ARGS]...

  Jira Assistant Skills CLI.

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  issue   Work with Jira issues (get, create, update, delete)
  search  Search Jira using JQL
  sprint  Sprint management commands
```

### 3. Shell Completion

Click supports shell completion. Add to docs:

```bash
# Enable bash completion
eval "$(_JIRA_COMPLETE=bash_source jira)"

# Enable zsh completion
eval "$(_JIRA_COMPLETE=zsh_source jira)"
```

---

## Updated Decision Log

| Aspect | Original Proposal | Revised Proposal | My Recommendation |
|--------|-------------------|------------------|-------------------|
| CLI Pattern | Flat | Subcommand | ✅ Approved |
| Script Location | Library | Plugin | ✅ Approved |
| Import Method | Direct import | Direct import | ⚠️ Use subprocess initially |
| Command Registration | Manual | Manual | ⚠️ Use auto-discovery |
| Test Location | `src/.../tests/` | `src/.../tests/` | ⚠️ Use `tests/` at root |

---

## Conclusion

The revised proposal addresses all critical architectural concerns. The remaining issues are implementation details that can be resolved during development:

1. Use subprocess delegation initially (simpler, works immediately)
2. Add auto-discovery for scalability
3. Clarify plugin package structure
4. Use standard test directory layout
5. Start with a pilot skill before scaling

**Recommendation:** Approve with the understanding that implementation details will be refined during the pilot phase.

---

## Suggested Next Steps

1. **Conduct sandbox prerequisite test** (Section 3.1)
2. **Choose pilot skill** (recommend `jira-issue` - has good test coverage)
3. **Implement CLI for pilot skill** using subprocess delegation
4. **Run E2E tests** with new CLI syntax
5. **Document findings** and refine approach
6. **Scale to remaining skills** with auto-discovery pattern

This incremental approach minimizes risk while delivering value quickly.
