"""Поиск обратных зависимостей (кто зависит от пакета)."""
from collections import deque


def reverse_deps(graph: dict[str, list[str]], target: str) -> list[str]:
    """Вернуть пакеты, которые (транзитивно) зависят от target."""
    inverted: dict[str, list[str]] = {n: [] for n in graph}
    for node, deps in graph.items():
        for dep in deps:
            inverted.setdefault(dep, []).append(node)

    result: list[str] = []
    seen: set[str] = {target}
    queue: deque[str] = deque([target])

    while queue:
        current = queue.popleft()
        for parent in inverted.get(current, []):
            if parent in seen:
                continue
            seen.add(parent)
            result.append(parent)
            queue.append(parent)
    return result