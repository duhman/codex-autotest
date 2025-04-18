---
title: docstring
---

# `codex-autotest docstring`

Generate or apply docstrings for functions, classes, and methods.

## Usage

```bash
codex-autotest docstring --path <src_path> [--apply]
```

- `--path` specifies the root directory to scan for `.py` files.
- Without `--apply`, outputs a unified diff of proposed docstring insertions.
- With `--apply`, writes docstrings directly into source files.

## Examples

Preview docstring changes:
```bash
codex-autotest docstring --path src/
```

Apply docstrings to files:
```bash
codex-autotest docstring --path src/ --apply
```