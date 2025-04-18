---
title: review
---

# `codex-autotest review`

Interactively review and regenerate a generated test file.

## Usage

```bash
codex-autotest review <test_file>
```

1. Loads existing test code from `<test_file>`.
2. Opens your default editor (TTY) or prompts for a new prompt template.
3. Renders the prompt with the source code and regenerates test code.
4. Shows the new code and asks to overwrite or edit the prompt again.