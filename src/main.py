import json
import sys
import os
import urllib.request
import urllib.error


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
    """Скачивает прямые зависимости пакета из реестра npm."""
    url = f"{repo_url}/{package_name}/{version}"
    try:
        with urllib.request.urlopen(url) as response:
            if response.status == 200:
                data = json.loads(response.read().decode('utf-8'))
                return data.get("dependencies", {})
            return {}
    except urllib.error.HTTPError:
        return {}
    except Exception as e:
        print(f"Ошибка сети при запросе {package_name}: {e}")
        return {}


def build_graph(start_package, start_version, config):
    """Строит граф зависимостей с помощью нерекурсивного DFS."""
    graph = {}
    stack = [(start_package, start_version, 0)]
    visited = set()

    max_depth = config["max_depth"]
    filter_sub = config["filter_substring"]
    repo_url = config["repo_url"]
    test_mode = config["test_mode"]

    test_data = {}
    if test_mode:
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            test_file_path = os.path.join(current_dir, "..", repo_url)
            with open(test_file_path, 'r', encoding='utf-8') as f:
                test_data = json.load(f)
        except Exception as e:
            print(f"Ошибка чтения тестового файла {repo_url}: {e}")
            sys.exit(1)

    while stack:
        current_pkg, current_ver, depth = stack.pop()

        if current_pkg in visited or depth > max_depth:
            continue

        if filter_sub and filter_sub in current_pkg:
            continue

        visited.add(current_pkg)

        if test_mode:
            deps = test_data.get(current_pkg, {})
        else:
            deps = fetch_dependencies(current_pkg, current_ver, repo_url)

        graph[current_pkg] = list(deps.keys())

        for dep_name, dep_version in deps.items():
            clean_ver = dep_version.replace('^', '').replace('~', '').strip()
            stack.append((dep_name, clean_ver, depth + 1))

    return graph


def find_reverse_dependencies(target_pkg, graph):
    """Находит все пакеты, которые зависят от target_pkg."""
    reverse_deps = []
    for pkg, deps in graph.items():
        if target_pkg in deps:
            reverse_deps.append(pkg)
    return reverse_deps


def generate_plantuml(graph):
    """Генерирует текстовое описание графа для PlantUML."""
    lines = ["@startuml", "skinparam packageStyle rectangle"]

    for pkg, deps in graph.items():
        if not deps:
            lines.append(f'package "{pkg}" {{}}')
        for dep in deps:
            lines.append(f'"{pkg}" --> "{dep}"')

    lines.append("@enduml")
    return "\n".join(lines)


def main():
    """Основная функция приложения."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, "..", "config.json")

    config = load_config(config_path)
    validate_config(config)

    print("\n--- Этап 3. Построение графа зависимостей ---")
    graph = build_graph(config["package_name"], config["version"], config)

    for pkg, deps in graph.items():
        print(f"[{pkg}] зависит от: {', '.join(deps) if deps else 'нет'}")

    print(f"\n--- Этап 4. Обратные зависимости для '{config['package_name']}' ---")
    rev_deps = find_reverse_dependencies(config["package_name"], graph)
    if rev_deps:
        print(f"Пакеты, зависящие от '{config['package_name']}': {', '.join(rev_deps)}")
    else:
        print(f"Пакетов, зависящих от '{config['package_name']}', не найдено (он корневой).")

    print("\n--- Этап 5. Визуализация PlantUML ---")
    plantuml_code = generate_plantuml(graph)
    print(plantuml_code)

    puml_path = os.path.join(current_dir, "..", "graph.puml")
    with open(puml_path, "w", encoding="utf-8") as f:
        f.write(plantuml_code)
    print(f"\nКод PlantUML сохранен в файл 'graph.puml' в корне проекта.")


if __name__ == "__main__":
    main()