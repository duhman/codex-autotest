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
    # Stub OpenAI client
    monkeypatch.setenv('OPENAI_API_KEY', 'testkey')
    # Return a complete file defining foo and its test so pytest can import and run it
    def fake_chat(prompt, **kwargs):
        return (
            'def foo():\n'
            '    return 1\n'
            '\n'
            'def test_foo():\n'
            '    assert foo()'
        )
    monkeypatch.setattr(cli, 'chat_completion', fake_chat)
    return

def test_generate_diff(monkeypatch):
    # Use isolated filesystem to prevent leaking generated tests
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create source file
        src = Path('src')
        src.mkdir()
        f = src / 'foo.py'
        f.write_text('def foo():\n    return 1\n')
        result = runner.invoke(cli.main, ['generate-tests', '--path', 'src'])
        assert result.exit_code == 0
        out = result.output
        assert 'Generating tests for' in out
        # diff should show additions for test file
        assert '+++ tests/test_foo.py' in out or '+def test_foo()' in out

def test_generate_apply(monkeypatch):
    runner = CliRunner()
    with runner.isolated_filesystem():
        src = Path('src')
        src.mkdir()
        f = src / 'foo.py'
        f.write_text('def foo():\n    return 1\n')
        result = runner.invoke(cli.main, ['generate-tests', '--path', 'src', '--apply'])
        assert result.exit_code == 0
        out = result.output
        assert 'Wrote tests to' in out
        test_file = Path('tests') / 'test_foo.py'
        assert test_file.exists()
        content = test_file.read_text()
        assert 'def test_foo()' in content