"""Формирование DOT-описания и вызов Graphviz."""
import subprocess
from pathlib import Path


def to_dot(graph: dict[str, list[str]], root: str) -> str:
    """Сгенерировать текст диаграммы в формате Graphviz DOT."""
    lines = ["digraph deps {", '  rankdir="LR";']
    for node in graph:
        style = ' shape="box" style="bold"' if node == root else ""
        lines.append(f'  "{node}" [{style.strip()}];')
    for node, deps in graph.items():
        for dep in deps:
            lines.append(f'  "{node}" -> "{dep}";')
    lines.append("}")
    return "\n".join(lines)


def render_png(dot_text: str, output: str) -> None:
    """Отрисовать DOT в PNG через утилиту dot."""
    dot_file = Path(output).with_suffix(".dot")
    dot_file.write_text(dot_text, encoding="utf-8")
    try:
        subprocess.run(
            ["dot", "-Tpng", str(dot_file), "-o", output],
            check=True,
            capture_output=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError) as exc:
        raise RuntimeError(
            "Graphviz не установлен или завершился с ошибкой"
        ) from exc