---
title: Configuration
---

# Configuration

`codex-autotest` reads configuration from `.codex-autotest.yaml` in the project root.

Example configuration:
```yaml
src_path: src          # root path of your source code directory
language: python      # language of source files
framework: pytest     # test framework to target
prompts:
  unit_test: "Write {framework} tests for the following {language} function, including edge cases:\n{code}"
  kill_mutant: "Write {framework} tests to kill the following mutant in {language} code:\n{diff}"
```

| Field        | Description                                         |
|--------------|-----------------------------------------------------|
| src_path     | Root path for source files (relative to CWD)       |
| language     | Programming language (e.g., python, javascript)     |
| framework    | Test framework (e.g., pytest, mocha)               |
| prompts.unit_test | Template for unit test generation            |
| prompts.kill_mutant | Template for mutation kill tests (diff)    |