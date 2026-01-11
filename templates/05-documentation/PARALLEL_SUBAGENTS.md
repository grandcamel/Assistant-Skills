# Parallel Subagent Patterns

For large-scale analysis or coding tasks across multiple skills/components.

---

## Mental Model

Treat subagents as **talented but inexperienced interns**:
- **Worktrees** are separate cubicles so they don't bump into each other
- **Context files** are task sheets explaining exactly what to do
- **Chunked execution** is checking their work hourly, not waiting until Friday
- **File-persisted results** ensure their work survives if they go home early

---

## When to Use Parallel Subagents

| Scenario | Example |
|----------|---------|
| Reviewing all skills for consistency | Check all 14 JIRA skills for documentation gaps |
| Running analysis across components | Analyze token efficiency across all skills |
| Tasks decomposable into independent units | Fix similar issues in multiple files |
| Long-running operations | Operations that risk context exhaustion |

---

## Pattern: File-Persisted Results

**Key principle:** Each subagent writes results to a file, so work is preserved even if the orchestrator session ends.

**Context files per subagent:**

| File | Purpose |
|------|---------|
| `TASK.md` | Task instructions and constraints |
| `log.md` | Observation-Thought-Action trace |
| `commit.md` | Progress summary |
| `SKILL_FIX_PLAN.md` | Final output/deliverable |

---

## Subagent Prompt Template

```markdown
You are reviewing the <skill-name> skill for inconsistencies between its SKILL.md
documentation, CLI commands, and library implementation.

**Your task:**
1. Read the SKILL.md at: <full-path-to-SKILL.md>
2. List all CLI commands mentioned in SKILL.md
3. Check if each CLI command exists and works as documented
4. Identify inconsistencies
5. Write your findings to: <full-path-to-output-file>

Format your output file with:
- ## Summary (one paragraph)
- ## Inconsistencies Found (table: Issue | SKILL.md says | Reality | Fix needed)
- ## Recommended Fixes (prioritized list)
- ## Files to Modify (list)

Do NOT add the file to git.
```

---

## Agent Archetypes

| Archetype | Role | Example Task |
|-----------|------|--------------|
| **Architect** | Designs system patterns | "Design API structure for bulk operations" |
| **Detective** | Debugging and edge cases | "Find all missing error handling" |
| **Craftsman** | Implementation | "Implement fix per plan" |
| **Reviewer** | Verification and QA | "Review for consistency and test coverage" |

---

## Multi-Agent Coordination

### Shared State File

Use `WORKTREE_COORDINATION.md` to track agent status:

```markdown
## Active Tasks
| Task | Agent | Status | Worktree |
|------|-------|--------|----------|
| fix/skill-a | agent-1 | in_progress | .worktrees/skill-a-fix |
| fix/skill-b | agent-2 | completed | .worktrees/skill-b-fix |
| fix/skill-c | agent-3 | pending | - |
```

### TODO-Claim Protocol

1. Read coordination file before starting
2. Claim task by updating file
3. Mark completed when done
4. Back off if already claimed

---

## Git Worktree Pattern

For parallel code changes, use worktrees to isolate each subagent's work.

### Worktree Naming Convention

```bash
# Pattern: .worktrees/<task-type>-<component>--<agent-role>
.worktrees/fix-skill-a--craftsman
.worktrees/fix-skill-b--craftsman
.worktrees/review-skill-c--reviewer
```

### Configuration Guards

Place `.claude/rules.md` in each worktree:

```markdown
## Allowed
- Modify files in skills/<skill-name>/
- Update SKILL.md documentation

## Off-Limits
- Do NOT modify files outside the <skill-name> skill
- Do NOT change shared library code
- Do NOT commit directly to main branch
```

### Coding Subagent Prompt

```markdown
You are implementing fixes for <skill-name> based on SKILL_FIX_PLAN.md.

**Setup:**
1. Create worktree: git worktree add .worktrees/<skill>-fix -b fix/<skill>
2. Change to worktree: cd .worktrees/<skill>-fix

**Task:**
1. Read the fix plan
2. Implement Priority 1 fixes
3. Update SKILL.md documentation
4. Commit: fix(<skill>): <description>
5. Write FIX_SUMMARY.md (do NOT commit)
```

---

## Sequential Rebase Process

After all subagents complete:

```bash
# 1. Start from dev branch
git checkout dev
git pull --rebase origin dev 2>/dev/null || true

# 2. For each skill branch:
cd .worktrees/<skill>-fix
git fetch origin main
git rebase origin/main

# 3. Merge to dev
cd /path/to/main/repo
git checkout dev
git merge fix/<skill> --no-edit

# 4. Push dev
git push origin dev

# 5. Clean up
git worktree remove --force .worktrees/<skill>-fix
git branch -d fix/<skill>

# 6. Repeat for remaining branches

# 7. Run tests
pytest skills/*/tests/ -v

# 8. Create PR when requested
gh pr create --title "<title>" --base main --head dev
```

---

## Recovery from Context Exhaustion

If the orchestrator session ends, results are preserved in files:

```bash
# Check for output files
find skills -name "SKILL_FIX_PLAN.md" -type f

# Review each plan
cat skills/*/SKILL_FIX_PLAN.md

# Check worktree status
git worktree list
```

---

## Best Practices

1. **Write to files** - Always persist results to files
2. **Use absolute paths** - Avoid ambiguity in subagent prompts
3. **Include context** - Mention known issues in prompts
4. **Specify format** - Define exact output structure
5. **Limit scope** - Each subagent should have focused, completable task
6. **Track with TodoWrite** - Track subagent status in orchestrator
7. **Chunked execution** - Ask for "step 1," verify, then proceed
8. **Explicit context injection** - Reference specific filenames and behaviors

---

## Key Lessons Learned

| Lesson | Explanation |
|--------|-------------|
| Merge to dev, not main | Local `main` is read-only |
| Push dev after each merge | So subsequent rebases pick up changes |
| Watch for uncommitted files | Use `--force` when removing worktrees |
| One conflict source | Conflicts occur during rebase, not parallel development |
| Verify with tests before PR | Run full test suite after all merges |
| PR only when requested | Ask for branch name first |

---

## Example: Reviewing All Skills

```markdown
# Orchestrator prompt
Launch 6 parallel subagents to review each skill in skills/ directory:

For each skill, create a subagent with:
- Input: skills/<skill-name>/SKILL.md
- Output: skills/<skill-name>/REVIEW.md
- Task: Check for missing trigger phrases, outdated examples, risk levels

Track progress in REVIEW_COORDINATION.md.
```

---

## Template Files

- `TASK.md.template` - Task instructions template
- `WORKTREE_COORDINATION.md.template` - Coordination file template
- `SKILL_FIX_PLAN.md.template` - Output file template
