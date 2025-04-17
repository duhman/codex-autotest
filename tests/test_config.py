import pytest
from codex_autotest.config import DEFAULT_CONFIG, write_default_config, load_config

def test_write_and_load_default_config(tmp_path):
    config_path = tmp_path / '.codex-autotest.yaml'
    # Write default config
    write_default_config(str(config_path))
    assert config_path.exists()
    # Load and compare
    loaded = load_config(str(config_path))
    assert loaded == DEFAULT_CONFIG

def test_write_default_config_raises_if_exists(tmp_path):
    config_path = tmp_path / '.codex-autotest.yaml'
    config_path.write_text('dummy: true')
    with pytest.raises(FileExistsError):
        write_default_config(str(config_path))

def test_load_config_raises_if_missing(tmp_path):
    missing_path = tmp_path / '.codex-autotest.yaml'
    with pytest.raises(FileNotFoundError):
        load_config(str(missing_path))