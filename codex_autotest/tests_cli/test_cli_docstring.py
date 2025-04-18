import os
import sys
import pytest
from click.testing import CliRunner

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from codex_autotest import cli

@pytest.fixture(autouse=True)
def stub_chat(monkeypatch):
    # Stub OpenAI client
    monkeypatch.setenv('OPENAI_API_KEY', 'testkey')
    monkeypatch.setattr(cli, 'chat_completion', lambda prompt, **kwargs: 'Generated docstring')
    return

def test_docstring_diff(tmp_path):
    # Create source file with missing docstrings
    src = tmp_path / 'src'
    src.mkdir()
    f = src / 'a.py'
    f.write_text(
        'def foo():\n'
        '    pass\n'
        '\n'
        'class Bar:\n'
        '    def baz(self):\n'
        '        pass\n'
    )
    runner = CliRunner()
    result = runner.invoke(cli.main, ['docstring', '--path', str(src)])
    assert result.exit_code == 0
    out = result.output
    # Expect unified diff with insertions of Generated docstring
    assert 'Generated docstring' in out
    # Should have three insertions: function, class, method
    assert out.count('Generated docstring') == 3

def test_docstring_apply(tmp_path):
    src = tmp_path / 'src'
    src.mkdir()
    f = src / 'b.py'
    f.write_text(
        'def foo():\n'
        '    pass\n'
        '\n'
        'class Bar:\n'
        '    def baz(self):\n'
        '        pass\n'
    )
    runner = CliRunner()
    result = runner.invoke(cli.main, ['docstring', '--path', str(src), '--apply'])
    assert result.exit_code == 0
    content = f.read_text().splitlines()
    # Check top-level function docstring
    assert any('foo' in line for line in content)
    idx = next(i for i, line in enumerate(content) if 'foo' in line)
    assert content[idx + 1].strip() == '"""Generated docstring"""'
    # Check class docstring
    assert any('class Bar' in line for line in content)
    idx_cls = next(i for i, line in enumerate(content) if 'class Bar' in line)
    assert content[idx_cls + 1].strip() == '"""Generated docstring"""'
    # Check method docstring
    idx_m = next(i for i, line in enumerate(content) if 'baz(self)' in line)
    assert content[idx_m + 1].strip() == '"""Generated docstring"""'