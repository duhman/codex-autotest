---
title: mutate
---

# `codex-autotest mutate`

Mutation-driven test amplification: automatically generate tests that kill surviving mutants.

## Usage

```bash
codex-autotest mutate --path <src_path> [--language <lang>] [--framework <fw>]
```

1. Runs `mutmut run --paths-to-mutate <src_path>` to execute mutation testing.
2. Retrieves surviving mutants via `mutmut results --json`.
3. For each surviving mutant, obtains the diff with `mutmut show <id>`.
4. Renders the `kill_mutant` prompt with the diff and calls OpenAI to generate a kill test.
5. Writes kill tests under `tests/test_mutant_<module>_<id>.py`.

## Requirements
- Requires [mutmut](https://github.com/boxed/mutmut) installed in your environment.