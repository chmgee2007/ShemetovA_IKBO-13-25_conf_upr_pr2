"""Загрузка и валидация конфигурации из TOML-файла."""
from dataclasses import dataclass
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # Python < 3.11
    import tomli as tomllib  # type: ignore

MAX_DEPTH_LIMIT = 50


class ConfigError(ValueError):
    """Ошибка конфигурации."""


@dataclass
class Config:
    """Пользовательские настройки приложения."""

    package: str
    repo_url: str
    test_mode: bool
    version: str
    max_depth: int
    filter_substring: str
    output_file: str


def _require(data: dict, key: str) -> object:
    if key not in data:
        raise ConfigError(f"Отсутствует параметр: {key}")
    return data[key]


def load_config(path: str) -> Config:
    """Прочитать и провалидировать TOML-конфиг."""
    file = Path(path)
    if not file.is_file():
        raise ConfigError(f"Файл конфигурации не найден: {path}")

    with file.open("rb") as fh:
        raw = tomllib.load(fh)

    package = str(_require(raw, "package"))
    if not package.strip():
        raise ConfigError("package не может быть пустым")

    repo_url = str(_require(raw, "repo_url"))
    if not repo_url.strip():
        raise ConfigError("repo_url не может быть пустым")

    test_mode = _require(raw, "test_mode")
    if not isinstance(test_mode, bool):
        raise ConfigError("test_mode должен быть true/false")

    version = str(_require(raw, "version"))
    if not version.strip():
        raise ConfigError("version не может быть пустой")

    max_depth = _require(raw, "max_depth")
    if not isinstance(max_depth, int) or not 0 < max_depth <= MAX_DEPTH_LIMIT:
        raise ConfigError(
            f"max_depth должен быть целым в диапазоне 1..{MAX_DEPTH_LIMIT}"
        )

    filter_substring = str(_require(raw, "filter_substring"))

    output_file = str(_require(raw, "output_file"))
    if not output_file.strip():
        raise ConfigError("output_file не может быть пустым")

    return Config(
        package=package,
        repo_url=repo_url,
        test_mode=test_mode,
        version=version,
        max_depth=max_depth,
        filter_substring=filter_substring,
        output_file=output_file,
    )


def print_config(cfg: Config) -> None:
    """Вывести параметры в формате ключ-значение (Этап 1)."""
    items = [
        ("package", cfg.package),
        ("repo_url", cfg.repo_url),
        ("test_mode", cfg.test_mode),
        ("version", cfg.version),
        ("max_depth", cfg.max_depth),
        ("filter_substring", cfg.filter_substring),
        ("output_file", cfg.output_file),
    ]
    for key, value in items:
        print(f"{key} = {value}")