"""Точка входа: оркестрация этапов 1–5."""
import argparse
import sys

from src.config import ConfigError, load_config, print_config
from src.fetcher import FetchError, fetch_direct_deps, parse_test_repo
from src.graph import GraphError, build_graph, find_cycles
from src.reverse import reverse_deps
from src.visualizer import render_png, to_dot


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Визуализатор зависимостей")
    parser.add_argument("--config", required=True, help="путь к TOML-конфигу")
    parser.add_argument(
        "--reverse",
        metavar="PKG",
        help="вывести обратные зависимости для пакета",
    )
    return parser.parse_args()


def make_loader(cfg):
    if cfg.test_mode:
        cache = parse_test_repo(cfg.repo_url)

        def loader(name: str) -> list[str]:
            return cache.get(name, [])

        return loader
    from src.fetcher import fetch_from_pypi

    return lambda name: fetch_from_pypi(name, cfg.version)


def main() -> int:
    args = parse_args()
    try:
        cfg = load_config(args.config)
    except ConfigError as exc:
        print(f"[config] {exc}", file=sys.stderr)
        return 2

    print("=== Параметры ===")
    print_config(cfg)

    try:
        direct = fetch_direct_deps(cfg)
        print("\n=== Прямые зависимости ===")
        for dep in direct:
            print(dep)

        graph = build_graph(
            cfg.package, direct, make_loader(cfg),
            cfg.max_depth, cfg.filter_substring,
        )
        cycles = find_cycles(graph)
        if cycles:
            print("\n=== Обнаружены циклы ===")
            for cycle in cycles:
                print(" -> ".join(cycle))

        if args.reverse:
            print(f"\n=== Обратные зависимости {args.reverse} ===")
            for item in reverse_deps(graph, args.reverse):
                print(item)

        dot_text = to_dot(graph, cfg.package)
        print("\n=== DOT ===")
        print(dot_text)
        render_png(dot_text, cfg.output_file)
        print(f"\nPNG сохранён: {cfg.output_file}")
    except (FetchError, GraphError, RuntimeError) as exc:
        print(f"[error] {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())