import os
import sys
import pytest
from click.testing import CliRunner

# ensure parent of project directory is on path for package import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from codex_autotest import cli

@pytest.fixture(autouse=True)
def stub_chat(monkeypatch):
    # Ensure API key is set and stub out OpenAI calls
    monkeypatch.setenv('OPENAI_API_KEY', 'testkey')
    monkeypatch.setattr(cli, 'chat_completion', lambda prompt, **kwargs: 'Mock explanation')
    return

def test_explain_file_not_found():
    runner = CliRunner()
    result = runner.invoke(cli.main, ['explain', 'nofile.py'])
    assert result.exit_code == 0
    assert 'File not found' in result.output

def test_explain_invalid_range(tmp_path):
    f = tmp_path / 'f.py'
    f.write_text('a=1\nb=2\n')
    runner = CliRunner()
    result = runner.invoke(cli.main, ['explain', str(f) + ':3-1'])
    assert result.exit_code == 0
    assert 'Invalid line range' in result.output

def test_explain_success_whole_file(tmp_path):
    f = tmp_path / 'foo.py'
    f.write_text('x=1\n')
    runner = CliRunner()
    result = runner.invoke(cli.main, ['explain', str(f)])
    assert result.exit_code == 0
    assert 'Mock explanation' in result.output

def test_explain_success_range(tmp_path):
    f = tmp_path / 'foo.py'
    f.write_text('x=1\ny=2\n')
    runner = CliRunner()
    result = runner.invoke(cli.main, ['explain', str(f) + ':1-1'])
    assert result.exit_code == 0
    assert 'Mock explanation' in result.output