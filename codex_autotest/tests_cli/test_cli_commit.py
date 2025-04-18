import os
import sys
import pytest
import subprocess
from click.testing import CliRunner

# ensure project root is on path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from codex_autotest import cli

class FakeResult:
    def __init__(self, returncode=0, stdout='', stderr=''):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr

@pytest.fixture(autouse=True)
def stub_chat(monkeypatch):
    # Stub OpenAI client
    monkeypatch.setenv('OPENAI_API_KEY', 'testkey')
    monkeypatch.setattr(cli, 'chat_completion', lambda prompt, **kwargs: 'feat: add foo feature')
    return

def test_commit_no_staged():
    runner = CliRunner()
    result = runner.invoke(cli.main, ['commit'])
    assert result.exit_code == 0
    assert 'Please specify --staged' in result.output

def test_commit_no_changes(monkeypatch):
    # Stub git diff returning no changes
    monkeypatch.setattr(subprocess, 'run', lambda *args, **kwargs: FakeResult(returncode=0, stdout=''))
    runner = CliRunner()
    result = runner.invoke(cli.main, ['commit', '--staged'])
    assert result.exit_code == 0
    assert 'No staged changes detected.' in result.output

def test_commit_git_error(monkeypatch):
    # Stub git diff error
    err = 'fatal: not a git repository'
    monkeypatch.setattr(subprocess, 'run', lambda *args, **kwargs: FakeResult(returncode=1, stderr=err))
    runner = CliRunner()
    result = runner.invoke(cli.main, ['commit', '--staged'])
    assert result.exit_code == 0
    assert 'Error getting staged diff' in result.output

def test_commit_success(monkeypatch):
    # Stub git diff with example diff
    diff_text = 'diff --git a/foo.py b/foo.py\n+print(\"foo\")'
    monkeypatch.setattr(subprocess, 'run', lambda *args, **kwargs: FakeResult(returncode=0, stdout=diff_text))
    runner = CliRunner()
    result = runner.invoke(cli.main, ['commit', '--staged'])
    assert result.exit_code == 0
    # chat_completion stub returns commit message
    assert 'feat: add foo feature' in result.output