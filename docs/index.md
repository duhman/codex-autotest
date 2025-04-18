---
title: Introduction
---

# codex-autotest

`codex-autotest` is a CLI tool that uses OpenAI Codex to automatically generate, review, and maintain test suites for your codebase.

## Key Features

- **init**: Scaffold configuration and tests directory.
- **generate-tests** (alias `generate`): Generate or preview unit and integration tests for source files.
- **review**: Interactively review and regenerate tests.
- **explain**: Explain code snippets or entire files.
- **docstring**: Generate or apply docstrings for functions, classes, and methods.
- **refactor**: Refactor code based on a focus area (e.g., performance, readability).
- **commit**: Generate Conventional Commit messages for staged changes.
- **audit-security**: Audit code for security vulnerabilities and optionally apply fixes.
- **mutate**: Mutation-driven test amplification to kill surviving mutants.

This documentation covers installation, configuration, CLI commands, and development workflows.