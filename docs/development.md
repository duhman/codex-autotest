---
title: Development
---

# Development Guide

## Project Layout

```
.
├── codex_autotest/
│   ├── cli.py             # Main CLI commands
│   ├── config.py          # Configuration loader/writer
│   └── openai_client.py   # OpenAI API wrapper (caching & retries)
├── docs/                  # Fumadocs documentation source
├── tests/                 # pytest test suite
├── dev-requirements.txt   # Developer dependencies (mutmut, hypothesis)
├── requirements.txt       # Runtime dependencies
├── setup.py               # Packaging and extras_require
└── README.md
```

## Running Tests

```bash
pytest
```

## Linting and Formatting

Use your preferred tools (e.g., `flake8`, `black`) to maintain code quality.

## Contributing

1. Fork the repository on GitHub.
2. Create a feature branch: `git checkout -b feature/XYZ`.
3. Write tests for new functionality.
4. Implement your changes.
5. Run tests and ensure everything passes.
6. Submit a pull request against `main`.