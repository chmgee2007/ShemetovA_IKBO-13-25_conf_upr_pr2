"""Тесты DFS-обхода."""
from src.graph import build_graph, find_cycles


def test_depth_limit():
    """Глубина ограничивает обход."""
    data = {"A": ["B"], "B": ["C"], "C": ["D"]}
    loader = lambda n: data.get(n, [])
    graph = build_graph("A", ["B"], loader, max_depth=1, filter_substring="")
    assert "C" not in graph


def test_filter():
    """Пакеты с подстрокой исключаются."""
    data = {"A": ["B", "SKIP_X"], "B": []}
    loader = lambda n: data.get(n, [])
    graph = build_graph("A", data["A"], loader, 5, "SKIP")
    assert "SKIP_X" not in graph


def test_cycle_detected():
    """Цикл находится без зависания."""
    data = {"A": ["B"], "B": ["A"]}
    assert find_cycles(data)