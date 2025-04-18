---
title: explain
---

# `codex-autotest explain`

Explain the functionality of a code snippet or entire file.

## Usage

```bash
codex-autotest explain <file[:start-end]> [--language LANG] [--model MODEL] [--max-tokens N]
```

- `<file>` can include an optional line range in the form `start-end` to explain only specific lines.
- `--language` overrides the detected language.
- `--model` specifies the OpenAI model (default: gpt-3.5-turbo).
- `--max-tokens` sets the maximum tokens for the explanation output.

## Examples

Explain entire file:
```bash
codex-autotest explain src/module.py
```

Explain lines 10 through 20:
```bash
codex-autotest explain src/module.py:10-20
```