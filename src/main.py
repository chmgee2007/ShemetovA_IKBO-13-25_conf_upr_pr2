import json
import sys
import os


def load_config(filepath):
    """Загружает конфигурацию из JSON-файла."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Ошибка: Файл конфигурации '{filepath}' не найден.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Ошибка: Файл '{filepath}' имеет неверный формат JSON.")
        sys.exit(1)


def validate_config(config):
    """Проверяет наличие и корректность всех параметров."""
    required_keys = [
        "package_name", "repo_url", "test_mode",
        "version", "max_depth", "filter_substring"
    ]

    # 1. Проверка на наличие всех ключей
    for key in required_keys:
        if key not in config:
            print(f"Ошибка конфигурации: отсутствует параметр '{key}'.")
            sys.exit(1)

    # 2. Проверка типов и значений
    if not isinstance(config["package_name"], str) or not config["package_name"]:
        print("Ошибка: 'package_name' должно быть непустой строкой.")
        sys.exit(1)

    if not isinstance(config["repo_url"], str) or not config["repo_url"]:
        print("Ошибка: 'repo_url' должно быть непустой строкой.")
        sys.exit(1)

    if not isinstance(config["test_mode"], bool):
        print("Ошибка: 'test_mode' должно быть булевым значением (true/false).")
        sys.exit(1)

    if not isinstance(config["max_depth"], int) or config["max_depth"] < 0:
        print("Ошибка: 'max_depth' должно быть целым неотрицательным числом.")
        sys.exit(1)

    if not isinstance(config["filter_substring"], str):
        print("Ошибка: 'filter_substring' должно быть строкой.")
        sys.exit(1)


def main():
    """Основная функция приложения."""
    # Находим путь к папке, где лежит main.py (папка src)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Поднимаемся на уровень выше и ищем config.json в корне проекта
    config_path = os.path.join(current_dir, "..", "config.json")

    print("Загрузка конфигурации...")
    config = load_config(config_path)

    print("Проверка параметров...")
    validate_config(config)

    print("\n--- Параметры конфигурации ---")
    for key, value in config.items():
        print(f"{key}: {value}")
    print("------------------------------")
    print("Конфигурация успешно загружена и проверена.")


if __name__ == "__main__":
    main()