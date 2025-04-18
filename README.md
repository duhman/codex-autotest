# [![PyPI version](https://img.shields.io/pypi/v/codex-autotest.svg)](https://pypi.org/project/codex-autotest)
# [![CI](https://github.com/your_org/codex-autotest/actions/workflows/ci.yml/badge.svg)](https://github.com/your_org/codex-autotest/actions/workflows/ci.yml)
#
# # codex-autotest

`codex-autotest` is a CLI tool that uses OpenAI Codex to automatically generate and review test suites for your codebase.

## Features
* Initialize test configuration and scaffolding (`init`)
* Generate or apply unit and integration tests (`generate-tests`, alias `generate`)
* Interactive review of generated tests (`review`)
* Explain code snippets or files (`explain`)
* Generate or apply docstrings (`docstring`)
* Refactor code focused on a given concern (`refactor`)
* Generate conventional commit messages (`commit`)
* Audit code for security issues and optionally apply fixes (`audit-security`)
* Mutation-driven test amplification (`mutate`)

## Installation
```sh
# Install from PyPI
pip install codex-autotest
# (Optional) For mutate command: install mutmut
pip install mutmut

git clone https://github.com/yourusername/codex-autotest.git
# Local development
git clone https://github.com/yourusername/codex-autotest.git
cd codex-autotest
pip install -e .
# (Optional) For development tasks (mutation testing, property tests)
pip install -r dev-requirements.txt
```

## Usage
```sh
# Initialize in your repository
codex-autotest init

# Generate tests (preview diff):
codex-autotest generate-tests --path src/

# Generate and write tests:
codex-autotest generate-tests --path src/ --apply
 # or using deprecated alias:
codex-autotest generate --path src/

# Review a generated test file:
codex-autotest review tests/test_module.py

# Explain code or snippet:
codex-autotest explain path/to/file.py[:start-end]

# Generate docstrings (preview):
codex-autotest docstring --path src/

# Apply docstrings:
codex-autotest docstring --path src/ --apply

# Refactor code:
codex-autotest refactor --path src/ --focus performance
codex-autotest refactor --path src/ --focus performance --apply

# Generate commit message:
codex-autotest commit --staged

# Audit security (preview report):
codex-autotest audit-security --path src/

# Audit security and apply fixes:
codex-autotest audit-security --path src/ --apply-fixes

# Mutation-driven test amplification (requires mutmut):
codex-autotest mutate --path src/
``` 

## Configuration
The `.codex-autotest.yaml` file supports options:
```yaml
src_path: src          # root path of your source code directory
language: python        # language of source files
framework: pytest       # test framework to target
prompts:
  unit_test: "Write {framework} tests for the following {language} function, including edge cases:\n{code}"
  # Test templates for surviving mutants (diff placeholder)
  kill_mutant: "Write {framework} tests to kill the following mutant in {language} code:\n{diff}"
```

## Development
Refer to [PRD.md] for detailed requirements, roadmap, and design.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
```

## Documentation

The full documentation is available in the `docs/` directory. You can preview it locally via Fumadocs:

To preview documentation locally, simply run:
```bash
npm run docs:dev
```
or directly with npx:
```bash
npx fumadocs@latest dev
```