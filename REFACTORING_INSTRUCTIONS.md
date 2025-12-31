# Refactoring Instructions: `Assistant-Skills` (Phase 2)

**Engineer:** Core Team

This document outlines the specific steps for the `Assistant-Skills` project, which primarily involves creating the sandbox test package and potentially updating any core E2E testing infrastructure.

## P2a.3: Sandbox Compatibility Test

This is the main task for this project. The goal is to create a small, temporary package to verify how `pip`-installed entry points behave in the Claude Code sandbox environment.

1.  **Create Test Package Directory**:
    -   Create a directory named `test_entrypoint` at the root of the `Assistant-Skills` project.

2.  **Create `pyproject.toml`**:
    -   Inside `test_entrypoint`, create a `pyproject.toml` file with the following content:
        ```toml
        [build-system]
        requires = ["setuptools"]
        build-backend = "setuptools.build_meta"

        [project]
        name = "test-claude-entrypoint"
        version = "0.1.0"

        [project.scripts]
        test-claude-ep = "test_entrypoint:main"
        ```

3.  **Create Test Script**:
    -   Inside `test_entrypoint`, create a `test_entrypoint.py` file with the following content:
        ```python
        import sys

        def main():
            print("""---
        ENTRY POINT EXECUTION SUCCESSFUL
        ---""")
            print(f"Executable: {sys.executable}")
            print(f"Arguments: {sys.argv}")

        if __name__ == "__main__":
            main()
        ```

4.  **Install the Test Package**:
    -   From within the `Assistant-Skills/test_entrypoint` directory, run `pip install -e .`. This should install the package and make the `test-claude-ep` command available in the environment's `PATH`.

5.  **Execute and Validate**:
    -   Run the following commands and verify the output:
        -   `which test-claude-ep`: Should return a path to the executable in your environment's `bin` directory.
        -   `test-claude-ep --test-arg`: Should execute the script and print the success message and arguments.
        -   `python -m test_entrypoint --test-arg-module`: Should also execute the script successfully.

6.  **Communicate Results**:
    -   Document the results of these tests and share with the other teams. The success of direct entry point invocation is the primary outcome. If it fails, the `python -m` fallback will be the new standard.

## E2E Test Infrastructure Review (If Applicable)

-   Review the core E2E test runner (`claude_runner` or similar components) if it lives in this repository.
-   Ensure that the test runner's environment will have the new `pip`-installed packages (`jira-assistant-skills`, `confluence-assistant-skills`, etc.) available during test runs. This may involve updating a `requirements.txt` file for the E2E test setup or modifying a Dockerfile to include an installation step.

This project's role is foundational. Completing the sandbox test unblocks all other teams from proceeding with the CLI implementation.
