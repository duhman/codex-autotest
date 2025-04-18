import os
import sys
import pytest
from click.testing import CliRunner

# ensure project root is on path for package import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from codex_autotest import cli

@pytest.fixture(autouse=True)
def stub_chat(monkeypatch):
    # Stub OpenAI client
    monkeypatch.setenv('OPENAI_API_KEY', 'testkey')
    monkeypatch.setattr(cli, 'chat_completion', lambda prompt, **kwargs: 'VULNERABILITY at line 1')
    return

def test_audit_security_report(tmp_path, monkeypatch):
    # Setup source directory and file
    monkeypatch.chdir(tmp_path)
    src = tmp_path / 'src'
    src.mkdir()
    f = src / 'vuln.py'
    f.write_text('def foo():\n    pass\n')
    # Run audit-security without apply-fixes
    runner = CliRunner()
    result = runner.invoke(cli.main, ['audit-security', '--path', 'src', '--output', 'report.md'])
    assert result.exit_code == 0
    assert (tmp_path / 'report.md').exists()
    report = (tmp_path / 'report.md').read_text()
    assert '## File: src/vuln.py' in report or 'vuln.py' in report
    assert 'VULNERABILITY at line 1' in report

def test_audit_security_apply_fixes(tmp_path, monkeypatch):
    # Stub chat to return fixed code
    fixed_code = 'def foo():\n    # fixed\n    pass'  # simulate fixed code
    def fake_chat(prompt, **kwargs):
        return fixed_code
    monkeypatch.setenv('OPENAI_API_KEY', 'testkey')
    monkeypatch.setattr(cli, 'chat_completion', fake_chat)
    monkeypatch.chdir(tmp_path)
    src = tmp_path / 'src'
    src.mkdir()
    f = src / 'vuln.py'
    f.write_text('def foo():\n    pass\n')
    runner = CliRunner()
    result = runner.invoke(cli.main, ['audit-security', '--path', 'src', '--apply-fixes'])
    assert result.exit_code == 0
    # Ensure file was updated with fixed code
    updated = (tmp_path / 'src' / 'vuln.py').read_text()
    assert '# fixed' in updated