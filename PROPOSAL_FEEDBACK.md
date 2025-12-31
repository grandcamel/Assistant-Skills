# Refactoring Proposal: Centralizing Assistant-Skills Libraries and Scripts

**Original Author:** Gemini AI Agent
**Feedback Author:** Claude (Opus 4.5)
**Date:** December 31, 2025
**Status:** DRAFT - WITH FEEDBACK INCORPORATED

---

## 1. Abstract

The `Assistant-Skills` ecosystem currently comprises several projects, each with its own Python library (`...-lib`). This has led to significant code duplication, particularly for common functionalities like configuration management, error handling, and input validation. Furthermore, the skill execution model relies on invoking Python scripts via their full file path, creating a brittle coupling to the filesystem layout.

This proposal outlines a **three-phase** refactoring plan to address these issues.

* **Phase 0** (NEW) will audit all duplicated modules across libraries to document exact divergence and guide refactoring decisions.
* **Phase 1** will consolidate all duplicated, non-domain-specific code from the `jira-`, `confluence-`, and `splunk-assistant-skills-lib` projects into the central `assistant-skills-lib`.
* **Phase 2** will transform the skill scripts into formal command-line entry points distributed by their respective Python packages, decoupling skill execution from the file system.

This effort will drastically reduce code duplication, improve long-term maintainability, and align the projects with standard Python packaging and distribution practices.

---

## 2. Background & Problem Statement

The `Assistant-Skills` architecture is a "factory" model where the `Assistant-Skills` project provides templates and tools to create service-specific plugins (e.g., `Jira-Assistant-Skills`). While this has successfully standardized the project structure, it has led to two significant technical debts.

### Problem A: Systemic Code Duplication Across Libraries

The service-specific libraries (`confluence-lib`, `jira-lib`, `splunk-lib`) were developed independently and contain large amounts of functionally similar code.

**Evidence of Duplication (Validated via Codebase Analysis):**

| Common Module | `assistant-skills-lib` | `confluence-lib` | `splunk-lib` | Divergence Status |
| :--- | :---: | :---: | :---: | :--- |
| `error_handler.py` | 11.4KB | 10.8KB | 10.2KB | **DIVERGED** - Different exception hierarchies |
| `formatters.py` | 6.4KB | 16.3KB | 13.2KB | **EXTENDED** - Service libs 2-3x larger |
| `validators.py` | 8.4KB | 18.0KB | 13.3KB | **EXTENDED** - Domain-specific validation added |
| `config_manager.py` | ❌ | 11.1KB | 11.8KB | **MISSING FROM BASE** |
| `cache.py` | 12.4KB | 11.9KB | ❌ | Partial duplication |

> **FEEDBACK NOTE:** The original proposal presented these as simple duplicates. Analysis reveals they have **diverged with service-specific customizations**. A "delete and import from base" approach will not work without careful refactoring using inheritance/extension patterns.

**Key Divergence Example - Error Handlers:**
```python
# Base lib uses:
class APIError(Exception): ...

# Splunk lib has diverged to:
class SplunkError(Exception): ...
class SearchQuotaError(SplunkError): ...
class JobFailedError(SplunkError): ...
```

This duplication means that:
* Fixing a bug in the error handling logic for Jira requires manually porting the fix to Confluence and Splunk.
* The overall maintenance burden is 3x higher than it needs to be for common code.
* There is a high risk of further divergence, where subtle differences can emerge over time, leading to inconsistent behavior across the different `Assistant-Skills` projects.

### Problem B: Brittle Filesystem-Coupled Skill Execution

Currently, `SKILL.md` files trigger functionality by invoking a Python script directly via its path:
```bash
# Example from current SKILL.md files
python skills/e2e-testing/scripts/setup_e2e.py /path/to/project
```

This approach is problematic because:
* It is tightly coupled to the project's directory structure.
* It is not a standard or professional way to distribute and execute code within a Python package.
* It makes the scripts less portable and harder to test or execute outside the specific context of the Claude Code runner.

### Problem C: Incomplete Library Extraction (NEW)

> **FEEDBACK NOTE:** The `jira-assistant-skills-lib` does not yet exist as a standalone package. The Jira project still uses `skills/shared/scripts/lib/` internally. This affects Phase 1 scope and sequencing.

---

## 3. Proposed Solution

This refactoring will be executed in **three** distinct phases.

### Phase 0: Comprehensive Audit (NEW)

**Goal:** Document the exact state of all duplicated code before making changes.

**Detailed Steps:**

1. **Generate Module Comparison Report:**
   * For each duplicated module (`error_handler.py`, `formatters.py`, `validators.py`, `config_manager.py`, `cache.py`), generate a diff report across all libraries.
   * Categorize each function/class as: IDENTICAL, EXTENDED, or DIVERGED.

2. **Capture Baseline Outputs:**
   * Run all scripts with sample inputs and record outputs.
   * These outputs serve as regression tests after refactoring.

3. **Document Extension Points:**
   * Identify which service-specific additions should become part of the base lib.
   * Identify which should remain as service-specific extensions.

4. **Create Dependency Graph:**
   * Map which modules depend on which across all libraries.
   * Identify potential circular dependency risks.

**Deliverables:**
* `docs/audit/module-comparison.md` - Side-by-side function comparison
* `docs/audit/divergence-report.md` - Categorized list of identical/extended/diverged code
* `docs/audit/baseline-outputs/` - Recorded script outputs for regression testing

---

### Phase 1: Library Consolidation & Centralization

**Goal:** Establish the base `assistant-skills-lib` as the single source of truth for all common, non-domain-specific code.

> **FEEDBACK NOTE:** Split into Phase 1a and 1b for safer incremental delivery.

#### Phase 1a: Add Missing Base Functionality

1. **Create `BaseConfigManager` in Base Library:**
   * Handle universal logic: finding `.claude` directory, loading/merging `settings.json` and `settings.local.json`, managing profiles.
   * Design as an abstract base class that service-specific managers extend.

2. **Consolidate `cache.py`:**
   * Merge the best implementation into the base library.
   * Service libs remove their copies and import from base.

3. **Update Base Library Version:**
   * Bump `assistant-skills-lib` to version `0.2.0`.
   * Publish to PyPI.

#### Phase 1b: Implement Extension Patterns

1. **Refactor Error Handling with Inheritance:**
   ```python
   # assistant_skills_lib/error_handler.py
   class BaseAPIError(Exception):
       """Base exception for all API-related errors."""
       def __init__(self, message: str, status_code: Optional[int] = None,
                    operation: Optional[str] = None):
           self.message = message
           self.status_code = status_code
           self.operation = operation
           super().__init__(self.format_message())

       def format_message(self) -> str:
           parts = []
           if self.operation:
               parts.append(f"[{self.operation}]")
           if self.status_code:
               parts.append(f"({self.status_code})")
           parts.append(self.message)
           return " ".join(parts)

   class AuthenticationError(BaseAPIError): ...
   class AuthorizationError(BaseAPIError): ...
   class RateLimitError(BaseAPIError): ...
   class NotFoundError(BaseAPIError): ...
   class ValidationError(BaseAPIError): ...
   class ServerError(BaseAPIError): ...
   ```

   ```python
   # splunk_assistant_skills_lib/error_handler.py
   from assistant_skills_lib.error_handler import (
       BaseAPIError, AuthenticationError, AuthorizationError,
       RateLimitError, NotFoundError, ValidationError, ServerError
   )

   class SplunkError(BaseAPIError):
       """Splunk-specific base exception."""
       pass

   class SearchQuotaError(SplunkError):
       """Splunk search quota exceeded."""
       pass

   class JobFailedError(SplunkError):
       """Splunk search job failed."""
       pass
   ```

2. **Refactor Formatters with Mixins/Inheritance:**
   ```python
   # assistant_skills_lib/formatters.py
   class BaseFormatter:
       """Core formatting utilities."""
       def format_table(self, data, headers): ...
       def format_tree(self, data): ...
       def colorize(self, text, color): ...

   # splunk_assistant_skills_lib/formatters.py
   from assistant_skills_lib.formatters import BaseFormatter

   class SplunkFormatter(BaseFormatter):
       """Splunk-specific formatters."""
       def format_search_results(self, results): ...
       def format_job_status(self, job): ...
   ```

3. **Refactor Validators Similarly:**
   * Base lib provides: `validate_url`, `validate_path`, `validate_name`, `sanitize_input`
   * Service libs extend with: `validate_jql`, `validate_spl`, `validate_cql`

4. **Update Service Library Dependencies:**
   ```toml
   # Service lib pyproject.toml
   [project]
   dependencies = [
       "assistant-skills-lib>=0.2.0",
   ]
   ```

5. **Create Jira Library Package:**
   * Extract `Jira-Assistant-Skills/skills/shared/scripts/lib/` into `jira-assistant-skills-lib`
   * Follow the same structure as confluence and splunk libs
   * Apply the extension patterns from the start

---

### Phase 2: Script-to-Entry-Point Refactoring

**Goal:** Decouple skill execution from the filesystem by converting skill scripts into standard Python package command-line entry points.

> **FEEDBACK NOTE:** Prerequisites must be validated before proceeding.

#### Phase 2 Prerequisites (NEW)

1. **Verify Claude Code Entry Point Discovery:**
   * Test how Claude Code's sandbox discovers and executes pip-installed entry points.
   * Confirm that `pip install jira-assistant-skills-lib` makes entry points available.
   * Document any sandbox restrictions that affect entry point execution.

2. **Create Compatibility Shim:**
   * During transition, support BOTH execution methods:
     ```bash
     # Old method (deprecated but still works)
     python skills/jira-issue/scripts/get_issue.py PROJ-123

     # New method (preferred)
     jira-get-issue PROJ-123
     ```
   * The old script becomes a thin wrapper that calls the entry point logic.

#### Phase 2 Implementation

1. **Move Scripts into Library Source Tree:**
   ```
   # Before
   Jira-Assistant-Skills/
   └── skills/jira-issue/scripts/get_issue.py

   # After
   jira-assistant-skills-lib/
   └── src/jira_assistant_skills_lib/
       └── cli/
           ├── __init__.py
           └── get_issue.py  # Contains main() function
   ```

2. **Define Entry Points in `pyproject.toml`:**
   ```toml
   [project.scripts]
   jira-get-issue = "jira_assistant_skills_lib.cli.get_issue:main"
   jira-create-issue = "jira_assistant_skills_lib.cli.create_issue:main"
   jira-search = "jira_assistant_skills_lib.cli.search:main"
   jira-transition = "jira_assistant_skills_lib.cli.transition:main"
   # ... all other scripts
   ```

3. **Update `SKILL.md` Files:**
   ```markdown
   ## Quick Start

   Get issue details:
   ```bash
   jira-get-issue PROJ-123 --output json
   ```
   ```

4. **Naming Convention Decision:**

   > **RECOMMENDATION:** Use `{service}-{verb}-{noun}` pattern for maximum clarity.

   | Pattern | Example | Pros | Cons |
   |---------|---------|------|------|
   | `jira-get-issue` | `jira-get-issue PROJ-123` | Clear, discoverable | Longer to type |
   | `jas-get-issue` | `jas-get-issue PROJ-123` | Shorter | Opaque, requires learning |
   | `jira issue get` | `jira issue get PROJ-123` | Git-like subcommands | More complex CLI framework |

   **Decision:** Use `jira-get-issue` pattern. Tab completion negates typing length concerns, and clarity aids adoption.

5. **Deprecation Timeline:**
   * **v1.0:** Both methods work, new method documented as preferred
   * **v1.1:** Old method emits deprecation warning
   * **v2.0:** Old method removed

---

## 4. Benefits

* **Drastically Reduced Maintenance:** A bug fix in `error_handler.py` is made in one place and instantly benefits all three service projects.
* **Code Simplification:** The service-specific libraries will become significantly smaller and focused only on their core domain logic.
* **Improved Robustness & Consistency:** All projects will share the exact same implementation for configuration, validation, and error handling.
* **Professional Packaging:** Adopts the standard, modern Python practice for distributing command-line tools, making the projects easier to understand, install, and use.
* **Future-Proofing:** Establishes a clean, DRY (Don't Repeat Yourself) architecture that makes it trivial to create new, high-quality `*-Assistant-Skills` projects in the future.
* **Clear Extension Points (NEW):** Service-specific functionality is cleanly separated via inheritance, making it obvious where to add new domain-specific features.

---

## 5. Risks & Mitigation Strategy

### Original Risks

* **Risk:** The scale of the refactoring could introduce regressions.
  * **Mitigation:** The phased approach isolates changes. Phase 0 baseline outputs serve as regression tests. No change is complete until all unit, integration (`live_integration`), and end-to-end (`e2e`) tests pass.

* **Risk:** Modifying imports across hundreds of files is potentially error-prone.
  * **Mitigation:** Changes performed using IDE tooling and `grep`/`sed` for batch replacements, followed by validation via static analysis (`mypy`) and test suites.

### Additional Risks Identified (NEW)

* **Risk:** Circular Dependency
  * **Description:** If service libs depend on base lib, but base lib is updated to include patterns extracted from service libs, version coordination becomes critical.
  * **Mitigation:** Strict semantic versioning. Base lib never imports from service libs. All shared code flows one direction only.

* **Risk:** Jira Library Doesn't Exist Yet
  * **Description:** The `jira-assistant-skills-lib` package hasn't been extracted yet, unlike Confluence and Splunk.
  * **Mitigation:** Add "Extract Jira lib" as first task in Phase 1b. Use the `library-publisher` skill in Assistant-Skills to scaffold it consistently.

* **Risk:** Claude Code Sandbox Compatibility
  * **Description:** Entry points require packages to be pip-installed. Claude Code's sandbox behavior with entry points is unverified.
  * **Mitigation:** Phase 2 Prerequisites include explicit verification. Create fallback to script-based execution if needed.

* **Risk:** Documentation Update Burden
  * **Description:** All SKILL.md files across 4+ projects (40+ skills) need updating for Phase 2.
  * **Mitigation:** Create automated script to update SKILL.md files. Run as part of Phase 2 implementation.

* **Risk:** Breaking Existing Users
  * **Description:** Changing execution patterns breaks existing workflows.
  * **Mitigation:** Compatibility shim supports both methods during transition. Clear deprecation timeline communicated.

---

## 6. Testing & Validation

### Phase 0 Validation
* Audit outputs reviewed and approved before proceeding.
* Baseline outputs captured for all scripts.

### Phase 1 Validation
1. After each sub-phase (1a, 1b), run full test suite for affected libraries.
2. Compare script outputs against Phase 0 baselines to detect behavioral changes.
3. Verify import paths resolve correctly with `mypy --strict`.
4. Run E2E tests for one service project (recommend Jira as pilot) before applying to others.

### Phase 2 Validation
1. Verify entry points are discoverable in Claude Code sandbox.
2. Run E2E test suite (`run-e2e-tests.sh`) with new entry point commands.
3. Test backwards compatibility shim works correctly.
4. Validate deprecation warnings appear for old method.

---

## 7. Implementation Timeline

> **NOTE:** Per project guidelines, no time estimates are provided. This shows sequencing only.

```
Phase 0: Audit
├── Generate module comparison report
├── Capture baseline outputs
├── Document extension points
└── Create dependency graph

Phase 1a: Add Missing Base Functionality
├── Create BaseConfigManager
├── Consolidate cache.py
└── Publish assistant-skills-lib v0.2.0

Phase 1b: Implement Extension Patterns
├── Extract jira-assistant-skills-lib
├── Refactor error_handler with inheritance
├── Refactor formatters with inheritance
├── Refactor validators with inheritance
├── Update all service lib dependencies
└── Run full test suites

Phase 2: Entry Points
├── Verify Claude Code sandbox compatibility
├── Create compatibility shim
├── Move scripts to library cli/ directory
├── Define entry points in pyproject.toml
├── Update all SKILL.md files
├── Publish v1.0 of all service libs
└── Document deprecation timeline
```

---

## 8. Decision Log

| Question | Decision | Rationale |
|----------|----------|-----------|
| Naming convention for entry points? | `{service}-{verb}-{noun}` (e.g., `jira-get-issue`) | Clarity over brevity; tab completion negates typing concerns |
| How to handle diverged error handlers? | Inheritance pattern with `BaseAPIError` | Allows service-specific exceptions while sharing common logic |
| How to handle extended formatters/validators? | Mixin/inheritance with base classes | Service libs extend rather than duplicate |
| Which project to pilot Phase 2? | Jira-Assistant-Skills | Most comprehensive (14 skills), already has strong test coverage |
| Backwards compatibility approach? | Shim + deprecation timeline | Minimizes disruption to existing users |

---

## 9. Appendix: Module Comparison Summary

### error_handler.py

| Function/Class | Base | Confluence | Splunk | Action |
|----------------|------|------------|--------|--------|
| `BaseAPIError` / `APIError` | `APIError` | `ConfluenceError` | `SplunkError` | Create abstract `BaseAPIError`, services extend |
| `AuthenticationError` | ✅ | ✅ | ✅ | Move to base, services inherit |
| `AuthorizationError` | ✅ | ✅ | ✅ | Move to base, services inherit |
| `RateLimitError` | ✅ | ✅ | ✅ | Move to base, services inherit |
| `NotFoundError` | ✅ | ✅ | ✅ | Move to base, services inherit |
| `SearchQuotaError` | ❌ | ❌ | ✅ | Keep in Splunk lib only |
| `JobFailedError` | ❌ | ❌ | ✅ | Keep in Splunk lib only |
| `ContentError` | ❌ | ✅ | ❌ | Keep in Confluence lib only |
| `handle_errors` decorator | ✅ | ✅ | ✅ | Consolidate in base |
| `print_error` | ✅ | ✅ | ✅ | Consolidate in base |

### formatters.py

| Function/Class | Base | Confluence | Splunk | Action |
|----------------|------|------------|--------|--------|
| `format_table` | ✅ | ✅ | ✅ | Consolidate in base |
| `format_tree` | ✅ | ✅ | ✅ | Consolidate in base |
| `colorize` | ✅ | ✅ | ✅ | Consolidate in base |
| `format_page` | ❌ | ✅ | ❌ | Keep in Confluence lib |
| `format_adf` | ❌ | ✅ | ❌ | Keep in Confluence lib |
| `format_search_results` | ❌ | ❌ | ✅ | Keep in Splunk lib |
| `format_job_status` | ❌ | ❌ | ✅ | Keep in Splunk lib |

### validators.py

| Function/Class | Base | Confluence | Splunk | Action |
|----------------|------|------------|--------|--------|
| `validate_url` | ✅ | ✅ | ✅ | Consolidate in base |
| `validate_path` | ✅ | ✅ | ✅ | Consolidate in base |
| `validate_name` | ✅ | ✅ | ✅ | Consolidate in base |
| `sanitize_input` | ✅ | ✅ | ✅ | Consolidate in base |
| `validate_cql` | ❌ | ✅ | ❌ | Keep in Confluence lib |
| `validate_space_key` | ❌ | ✅ | ❌ | Keep in Confluence lib |
| `validate_spl` | ❌ | ❌ | ✅ | Keep in Splunk lib |
| `validate_time_range` | ❌ | ❌ | ✅ | Keep in Splunk lib |

---

## 10. Stakeholder Sign-off

| Role | Name | Approval | Date |
|------|------|----------|------|
| Proposal Author | Gemini AI Agent | ✅ | 2025-12-30 |
| Technical Reviewer | Claude (Opus 4.5) | ✅ Feedback Incorporated | 2025-12-31 |
| Project Owner | | ⬜ Pending | |
| Lead Developer | | ⬜ Pending | |
