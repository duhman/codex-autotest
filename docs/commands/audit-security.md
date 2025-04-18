---
title: audit-security
---

# `codex-autotest audit-security`

Audit source code for security vulnerabilities and optionally apply suggested fixes.

## Usage

```bash
codex-autotest audit-security --path <src_path> [--language LANG] [--output FILE] [--apply-fixes]
```

- `--path` specifies the root directory of source files.
- `--language` overrides the default language (default from config).
- `--output` sets the report filename (default: `security_audit_report.md`).
- Without `--apply-fixes`, generates an audit report only.
- With `--apply-fixes`, also applies suggested fixes to source files.

## Examples

Generate security audit report:
```bash
codex-autotest audit-security --path src/ --output audit.md
```

Generate and apply fixes:
```bash
codex-autotest audit-security --path src/ --apply-fixes
```