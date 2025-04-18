---
title: refactor
---

# `codex-autotest refactor`

Refactor source code files based on a specified focus area (e.g., performance, readability).

## Usage

```bash
codex-autotest refactor --path <src_path> --focus <focus> [--language LANG] [--apply]
```

- `--path` specifies the root directory of source files.
- `--focus` describes the refactoring goal (e.g., `performance`, `readability`).
- `--language` overrides the default language (default from config).
- Without `--apply`, shows a unified diff of the proposed changes.
- With `--apply`, writes the refactored code directly into files.

## Examples

Preview refactoring for performance:
```bash
codex-autotest refactor --path src/ --focus performance
```

Apply refactored code:
```bash
codex-autotest refactor --path src/ --focus readability --apply
```