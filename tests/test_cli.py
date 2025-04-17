import os
import yaml
import pytest
from click.testing import CliRunner
from codex_autotest.cli import main
import openai

@pytest.fixture(autouse=True)
def clear_env(monkeypatch):
    # Ensure API key is not set by default
    monkeypatch.delenv('OPENAI_API_KEY', raising=False)
    yield

def test_init_creates_config_and_tests(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    result = runner.invoke(main, ['init'])
    assert result.exit_code == 0
    assert (tmp_path / '.codex-autotest.yaml').exists()
    assert (tmp_path / 'tests').is_dir()
    assert 'Initialized codex-autotest' in result.output

def test_init_fails_if_config_exists(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    config = tmp_path / '.codex-autotest.yaml'
    config.write_text('dummy: true')
    runner = CliRunner()
    result = runner.invoke(main, ['init'])
    assert result.exit_code == 0
    assert 'already exists' in result.output

def test_generate_requires_init(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    result = runner.invoke(main, ['generate', '--path', 'src'])
    assert result.exit_code == 0
    assert 'Configuration not found. Please run' in result.output

def test_generate_creates_test_file(tmp_path, monkeypatch):
    # Prepare source code
    src_dir = tmp_path / 'src'
    src_dir.mkdir()
    code = 'def add(a, b):\n    return a + b\n'
    src_file = src_dir / 'math_utils.py'
    src_file.write_text(code)
    # Write minimal config
    config = {
        'language': 'python',
        'framework': 'pytest',
        'prompts': {
            'unit_test': 'Test {framework} for {language} code:\n{code}'
        }
    }
    cfg_path = tmp_path / '.codex-autotest.yaml'
    cfg_path.write_text(yaml.dump(config))
    # Stub OpenAI response
    monkeypatch.setenv('OPENAI_API_KEY', 'testkey')
    def dummy_create(**kwargs):
        return {'choices': [{'message': {'content': 'def test_add(): pass'}}]}
    monkeypatch.setattr(openai.ChatCompletion, 'create', dummy_create)
    # Change to tmp working directory and run generate
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    result = runner.invoke(main, ['generate', '--path', 'src'])
    assert result.exit_code == 0
    # Check output file
    test_file = tmp_path / 'tests' / 'test_math_utils.py'
    assert test_file.exists()
    content = test_file.read_text()
    assert 'def test_add' in content

def test_review_regenerates_and_overwrites(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    # Setup source and test files
    src_dir = tmp_path / 'src'
    src_dir.mkdir()
    code = 'def add(a, b):\n    return a + b\n'
    (src_dir / 'math_utils.py').write_text(code)
    # Write config with src_path
    config = {
        'src_path': 'src',
        'language': 'python',
        'framework': 'pytest',
        'prompts': {
            'unit_test': 'Test {framework} for {language} code:\n{code}'
        }
    }
    (tmp_path / '.codex-autotest.yaml').write_text(yaml.dump(config))
    # Create existing test file
    tests_dir = tmp_path / 'tests'
    tests_dir.mkdir()
    test_file = tests_dir / 'test_math_utils.py'
    test_file.write_text('def test_old(): pass')
    # Stub OpenAI response
    monkeypatch.setenv('OPENAI_API_KEY', 'testkey')
    def dummy_create(**kwargs):
        return {'choices': [{'message': {'content': 'def test_add_new(): pass'}}]}
    monkeypatch.setattr(openai.ChatCompletion, 'create', dummy_create)
    # Run review: accept default prompt then confirm overwrite
    runner = CliRunner()
    # Use relative path under tests/ for review
    result = runner.invoke(main, ['review', 'tests/test_math_utils.py'], input='\ny\n')
    assert result.exit_code == 0
    # Check test file updated
    updated = test_file.read_text()
    assert 'def test_add_new' in updated
    assert 'Wrote updated tests to' in result.output
    
def test_mutate_generates_kill_tests(tmp_path, monkeypatch):
    import shutil, subprocess, json
    # Change into project dir
    monkeypatch.chdir(tmp_path)
    # Prepare source code
    src_dir = tmp_path / 'src'
    src_dir.mkdir()
    code = 'def foo():\n    return 42\n'
    (src_dir / 'mod.py').write_text(code)
    # Write config with kill_mutant prompt
    config = {
        'src_path': 'src',
        'language': 'python',
        'framework': 'pytest',
        'prompts': {
            'kill_mutant': 'Kill mutant diff:\n{diff}'
        }
    }
    (tmp_path / '.codex-autotest.yaml').write_text(yaml.dump(config))
    # Create tests dir
    (tmp_path / 'tests').mkdir()
    # Stub mutmut presence
    monkeypatch.setattr(shutil, 'which', lambda name: '/usr/bin/mutmut')
    # Stub subprocess.run for mutmut commands
    def fake_run(cmd, capture_output=False, text=False):
        class R:
            pass
        r = R()
        if cmd[:2] == ['mutmut', 'run']:
            r.returncode = 0; r.stdout = ''; r.stderr = ''
        elif cmd[:3] == ['mutmut', 'results', '--json']:
            r.returncode = 0
            r.stdout = json.dumps([{'id': 1, 'filename': 'src/mod.py', 'status': 'survived'}])
            r.stderr = ''
        elif cmd[:2] == ['mutmut', 'show']:
            r.returncode = 0; r.stdout = '--- mutant diff'; r.stderr = ''
        else:
            r.returncode = 1; r.stdout = ''; r.stderr = 'err'
        return r
    monkeypatch.setattr(subprocess, 'run', fake_run)
    # Stub OpenAI response
    monkeypatch.setenv('OPENAI_API_KEY', 'testkey')
    def dummy_create(**kwargs):
        return {'choices': [{'message': {'content': 'def test_kill(): pass'}}]}
    monkeypatch.setattr(openai.ChatCompletion, 'create', dummy_create)
    # Run mutate command
    runner = CliRunner()
    result = runner.invoke(main, ['mutate', '--path', 'src'])
    assert result.exit_code == 0
    # Check that kill test file was created
    test_file = tmp_path / 'tests' / 'test_mutant_mod_1.py'
    assert test_file.exists()
    content = test_file.read_text()
    assert 'def test_kill' in content