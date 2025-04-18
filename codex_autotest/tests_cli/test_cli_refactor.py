import os
import sys
import pytest
from click.testing import CliRunner
from pathlib import Path

# ensure project root is on path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from codex_autotest import cli

@pytest.fixture(autouse=True)
def stub_chat(monkeypatch):
    # Stub OpenAI client to return modified code
    monkeypatch.setenv('OPENAI_API_KEY', 'testkey')
    def fake_chat(prompt, **kwargs):
        return 'def foo():\n    return 2'
    monkeypatch.setattr(cli, 'chat_completion', fake_chat)
    return

def test_refactor_diff(monkeypatch):
    runner = CliRunner()
    with runner.isolated_filesystem():
        src = Path('src')
        src.mkdir()
        f = src / 'foo.py'
        f.write_text('def foo():\n    return 1\n')
        result = runner.invoke(cli.main, ['refactor', '--path', 'src', '--focus', 'performance'])
        assert result.exit_code == 0
        out = result.output
        assert 'Refactoring' in out
        assert '-    return 1' in out
        assert '+    return 2' in out

def test_refactor_apply(monkeypatch):
    runner = CliRunner()
    with runner.isolated_filesystem():
        src = Path('src')
        src.mkdir()
        f = src / 'foo.py'
        f.write_text('def foo():\n    return 1\n')
        result = runner.invoke(cli.main, ['refactor', '--path', 'src', '--focus', 'performance', '--apply'])
        assert result.exit_code == 0
        out = result.output
        assert 'Wrote refactored code to' in out
        content = f.read_text().splitlines()
        assert 'def foo():' in content[0]
        assert '    return 2' in content[1]