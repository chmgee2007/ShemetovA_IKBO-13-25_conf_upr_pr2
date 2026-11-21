"""Получение прямых зависимостей пакета PyPI по URL репозитория."""
import json
import urllib.request
from pathlib import Path

PYPI_JSON_URL = "https://pypi.org/pypi/{name}/{version}/json"


class FetchError(RuntimeError):
    """Ошибка получения данных о зависимостях."""


def parse_test_repo(path: str) -> dict[str, list[str]]:
    """Прочитать тестовый граф: строки вида 'A: B C'."""
    graph: dict[str, list[str]] = {}
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    for lineno, line in enumerate(lines, start=1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            raise FetchError(f"Строка {lineno}: ожидается 'ИМЯ: ЗАВИСИМОСТИ'")
        name, deps = line.split(":", 1)
        name = name.strip()
        if not name.isalpha() or not name.isupper():
            raise FetchError(
                f"Строка {lineno}: имя '{name}' должно быть заглавными буквами"
            )
        graph[name] = deps.split()
    return graph


def fetch_from_pypi(package: str, version: str) -> list[str]:
    """Получить прямые зависимости пакета с PyPI."""
    url = PYPI_JSON_URL.format(name=package, version=version)
    try:
        with urllib.request.urlopen(url, timeout=15) as resp:
            payload = json.load(resp)
    except Exception as exc:  # noqa: BLE001
        raise FetchError(f"Не удалось загрузить {url}: {exc}") from exc

    requires = payload.get("info", {}).get("requires_dist") or []
    deps: list[str] = []
    for item in requires:
        # отбрасываем extras и маркеры окружения
        if "extra ==" in item:
            continue
        name = item.split(";")[0].split(" ")[0].split("(")[0].strip()
        if name and name not in deps:
            deps.append(name)
    return deps


def fetch_direct_deps(cfg) -> list[str]:
    """Этап 2: вернуть прямые зависимости (test-режим или реальный)."""
    if cfg.test_mode:
        graph = parse_test_repo(cfg.repo_url)
        if cfg.package not in graph:
            raise FetchError(f"Пакет {cfg.package} не найден в тестовом графе")
        return list(graph[cfg.package])
    return fetch_from_pypi(cfg.package, cfg.version)