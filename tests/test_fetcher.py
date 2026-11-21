"""Тесты парсера тестового репозитория."""
import pytest

from src.fetcher import FetchError, parse_test_repo


def test_parse_ok(tmp_path):
    """Корректный файл парсится."""
    f = tmp_path / "r.txt"
    f.write_text("A: B C\nB: C\n", encoding="utf-8")
    assert parse_test_repo(str(f))["A"] == ["B", "C"]


def test_parse_bad_name(tmp_path):
    """Строчные имена запрещены."""
    f = tmp_path / "r.txt"
    f.write_text("a: B\n", encoding="utf-8")
    with pytest.raises(FetchError):
        parse_test_repo(str(f))