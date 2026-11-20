import json
import sys
import os
import urllib.request


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

    for key in required_keys:
        if key not in config:
            print(f"Ошибка конфигурации: отсутствует параметр '{key}'.")
            sys.exit(1)

    if not isinstance(config["max_depth"], int) or config["max_depth"] < 0:
        print("Ошибка: 'max_depth' должно быть целым неотрицательным числом.")
        sys.exit(1)


def fetch_dependencies(package_name, version, repo_url):
    """
    Скачивает информацию о прямых зависимостях пакета из реестра.
    """
    # Формируем URL для API npm (например: https://registry.npmjs.org/express/4.18.2)
    url = f"{repo_url}/{package_name}/{version}"

    print(f"Запрос данных по адресу: {url}...")
    try:
        # Делаем HTTP-запрос без использования сторонних библиотек
        with urllib.request.urlopen(url) as response:
            if response.status == 200:
                data = json.loads(response.read().decode('utf-8'))
                # В ответе npm зависимости лежат в ключе "dependencies"
                dependencies = data.get("dependencies", {})
                return dependencies
            else:
                print(f"Ошибка сервера: статус {response.status}")
                return {}
    except urllib.error.HTTPError as e:
        print(f"Ошибка HTTP: Пакет '{package_name}' версии '{version}' не найден (код {e.code}).")
        return {}
    except urllib.error.URLError as e:
        print(f"Ошибка сети: не удалось подключиться к {repo_url}. Причина: {e.reason}")
        return {}
    except Exception as e:
        print(f"Неизвестная ошибка: {e}")
        return {}


def main():
    """Основная функция приложения."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, "..", "config.json")

    config = load_config(config_path)
    validate_config(config)

    print("\n--- Этап 2. Сбор данных ---")
    package_name = config["package_name"]
    version = config["version"]
    repo_url = config["repo_url"]

    deps = fetch_dependencies(package_name, version, repo_url)

    print(f"\nПрямые зависимости для пакета '{package_name}' (версия {version}):")
    if not deps:
        print("Зависимости не найдены (или пакет не имеет таковых).")
    else:
        for dep_name, dep_version in deps.items():
            print(f" - {dep_name}: {dep_version}")


if __name__ == "__main__":
    main()