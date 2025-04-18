---
title: commit
---

# `codex-autotest commit`

Generate a Conventional Commit message for staged changes using OpenAI Codex.

## Usage

```bash
codex-autotest commit --staged [--model MODEL] [--max-tokens N]
```

- `--staged` (required) reads the current git staged diff.
- `--model` overrides the OpenAI model (default from config).
- `--max-tokens` sets the maximum tokens for the generated commit message.

## Examples

Generate a commit message for staged changes:
```bash
git add file1.py file2.js
codex-autotest commit --staged
```