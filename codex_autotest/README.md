# Codex-Autotest

Codex-Autotest is a CLI tool that leverages OpenAI Codex to automate common development tasks: generating tests, writing docstrings, explaining code, refactoring, crafting commit messages, and auditing security.

## Installation

Clone the repository and install the package:
```
git clone https://github.com/your_org/codex-autotest.git
cd codex-autotest
pip install -e .
```

Ensure you set your OpenAI API key:
```
export OPENAI_API_KEY=your_api_key
```

## Commands

All commands are invoked via `codex-autotest <command> [options]`:

- `init [--template <name>]`
  Initialize a `.codex-autotest.yaml` config and `tests/` directory.
- `explain <file[:start-end]> [--language LANG] [--model MODEL] [--max-tokens N]`
  Returns a detailed explanation of the specified code snippet or file.
- `docstring [--path PATH] [--apply]`
  Generates or previews docstrings for functions, classes, and methods.
- `generate-tests [--path PATH] [--language LANG] [--framework FW] [--apply]`
  Generates or previews unit tests for source files. The `generate` command is a deprecated alias for `generate-tests --apply`.
- `refactor [--path PATH] [--focus FOCUS] [--language LANG] [--apply]`
  Refactors code based on a focus (e.g. performance, readability).
- `commit --staged [--model MODEL] [--max-tokens N]`
  Produces a Conventional Commit message for staged changes.
- `audit-security [--path PATH] [--language LANG] [--output FILE] [--apply-fixes]`
  Audits code for security issues and optionally applies fixes.
- `review <test_file>`
  Regenerates or reviews tests interactively.
- `mutate [--path PATH] [--language LANG] [--framework FW]`
  Generates tests to kill surviving mutants using `mutmut`.

Run `codex-autotest <command> --help` for detailed options.

## Configuration

Configuration is stored in `.codex-autotest.yaml`. Example defaults:
```yaml
src_path: src
language: python
framework: pytest
prompts:
  unit_test: |
    Write {framework} tests for the following {language} function, including edge cases:

    {code}
  kill_mutant: |
    Write {framework} tests to kill the following mutant in {language} code:

    {diff}
  commit: |
    Write a conventional commit message (type, scope, subject) for the following diff, following Conventional Commits format:

    {diff}
  refactor: |
    Refactor the following {language} code focusing on {focus}. Provide the entire updated code without extra commentary:

    {code}
  audit_security: |
    Audit the following {language} code for security vulnerabilities. List each issue with line numbers, a description, and a suggested fix:

    {code}
```

## Tests

Run the test suite with:
```
pytest
```

---
Powered by OpenAI Codex via the OpenAI API.