---
title: generate (deprecated)
---

---
# `codex-autotest generate` (DEPRECATED)

This command is deprecated. Please use `codex-autotest generate-tests --apply` instead.
Refer to [generate-tests documentation](generate-tests.md) for details.

## Usage

```bash
codex-autotest generate --path <src_path> [--language <lang>] [--framework <fw>]
```

1. Scans `<src_path>` (or configured `src_path`) for `.py` or `.js` files.
2. Renders the `unit_test` prompt template with each file’s source code.
3. Calls OpenAI ChatCompletion (with caching & retry logic).
4. Writes generated test files under `tests/`, prefixing filenames with `test_`.

## Examples

Generate pytest tests for Python code:
```bash
codex-autotest generate --path src/ --language python --framework pytest
```