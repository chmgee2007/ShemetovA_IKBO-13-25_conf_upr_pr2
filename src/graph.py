"""Построение графа зависимостей итеративным DFS."""
from collections import deque


class GraphError(RuntimeError):
    """Ошибка построения графа."""


def build_graph(
    root: str,
    direct_deps: list[str],
    loader,
    max_depth: int,
    filter_substring: str,
) -> dict[str, list[str]]:
    """Построить граф зависимостей итеративным DFS.

    loader(name) -> list[str] возвращает прямые зависимости пакета.
    Пакеты с filter_substring в имени не включаются.
    """
    graph: dict[str, list[str]] = {}
    visited: set[str] = set()
    # стек: (пакет, текущая глубина)
    stack: deque[tuple[str, int]] = deque()
    stack.append((root, 0))

    while stack:
        node, depth = stack.pop()
        if node in visited:
            continue
        visited.add(node)

        if filter_substring and filter_substring in node:
            graph.setdefault(node, [])
            continue

        if depth >= max_depth:
            graph.setdefault(node, [])
            continue

        try:
            deps = loader(node) if node != root else direct_deps
        except Exception as exc:  # noqa: BLE001
            raise GraphError(f"Ошибка загрузки {node}: {exc}") from exc

        graph[node] = [d for d in deps if not (
            filter_substring and filter_substring in d
        )]
        for dep in reversed(graph[node]):
            if dep not in visited:
                stack.append((dep, depth + 1))

    return graph


def find_cycles(graph: dict[str, list[str]]) -> list[list[str]]:
    """Найти циклы (для отчёта, не ломая обход)."""
    cycles: list[list[str]] = []
    color: dict[str, int] = {}
    path: list[str] = []

    def dfs(node: str) -> None:
        color[node] = 1
        path.append(node)
        for nxt in graph.get(node, []):
            if color.get(nxt, 0) == 1:
                idx = path.index(nxt)
                cycles.append(path[idx:] + [nxt])
            elif color.get(nxt, 0) == 0:
                dfs(nxt)
        path.pop()
        color[node] = 2

    for node in graph:
        if color.get(node, 0) == 0:
            dfs(node)
    return cycles