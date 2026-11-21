import json
import sys
import os
import urllib.request
import urllib.error


def load_config(filepath):
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

        if current_pkg in visited:
            continue

        if depth > max_depth:
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
            # Очищаем версию от ^ и ~
            clean_ver = dep_version.replace('^', '').replace('~', '').strip()
            stack.append((dep_name, clean_ver, depth + 1))

    return graph


def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, "..", "config.json")

    config = load_config(config_path)
    validate_config(config)

    print("\n--- Этап 3. Построение графа зависимостей ---")
    graph = build_graph(config["package_name"], config["version"], config)

    for pkg, deps in graph.items():
        if deps:
            print(f"[{pkg}] зависит от: {', '.join(deps)}")
        else:
            print(f"[{pkg}] не имеет зависимостей (или они отфильтрованы).")


if __name__ == "__main__":
    main()