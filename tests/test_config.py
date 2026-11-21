"""Тесты конфигурации."""
import pytest

from src.config import ConfigError, load_config


def _write(tmp_path, text: str) -> str:
    path = tmp_path / "c.toml"
    path.write_text(text, encoding="utf-8")
    return str(path)


BASE = """
package = "requests"
repo_url = "https://pypi.org"
test_mode = false
version = "2.31.0"
max_depth = 3
filter_substring = ""
output_file = "out.png"
"""


def test_valid_config(tmp_path):
    """Корректный конфиг читается без ошибок."""
    cfg = load_config(_write(tmp_path, BASE))
    assert cfg.max_depth == 3


def test_bad_depth(tmp_path):
    """max_depth вне диапазона отклоняется."""
    text = BASE.replace("max_depth = 3", "max_depth = 0")
    with pytest.raises(ConfigError):
        load_config(_write(tmp_path, text))