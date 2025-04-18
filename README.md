# codex-autotest

`codex-autotest` is a CLI tool that uses OpenAI Codex to automatically generate and review test suites for your codebase.

## Features
- Initialize test configuration and scaffolding (`init`)
- Generate unit and integration tests (`generate`)
- Interactive review of generated tests (`review`)

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

# Generate tests for source directory
codex-autotest generate --path src/

# Review a generated test file
codex-autotest review tests/test_module.py

# Mutation-driven test amplification (requires mutmut)
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