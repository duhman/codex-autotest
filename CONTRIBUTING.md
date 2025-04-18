# Contributing to Codex-Autotest

Thank you for your interest in contributing! We welcome issues, pull requests, and feedback.

## Getting Started
1. Fork the repository and clone your fork.
2. Install dependencies:
   ```bash
   pip install -e .[dev]
   npm ci
   ```
3. Set your OpenAI API key:
   ```bash
   export OPENAI_API_KEY=YOUR_KEY
   ```

## Development Workflow
1. Create a new branch for your work.
2. Run formatting and lint checks:
   ```bash
   pre-commit run --all-files
   ```
3. Run tests:
   ```bash
   pytest
   ```
4. Build docs:
   ```bash
   npm run docs:build
   ```
5. Commit your changes and open a pull request.

## Code Style
- Python: black, isort, flake8, mypy
- Markdown: adhere to existing project style

## Reporting Issues
Please file issues on GitHub with a clear description and, if possible, a minimal reproducible example.