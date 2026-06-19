"""Shared graph visualization tool for compiled LangGraph State Machines."""

from typing import Callable

def draw_graphs(builds: list[tuple[str, Callable]]) -> None:
    """Print ASCII + Mermaid renderings for each (label, build_fn) pair."""

    for label, build in builds:
        compiled = build().get_graph()
        print(f"--- {label} (ASCII) ---")
        try:
            print(compiled.draw_ascii())
        except ImportError as err:
            print(f"(skipping ASCII: {err})")
        print()
        print(f"--- {label} (Mermaid - past into https://mermaid.live) ---")
        print(compiled.draw_mermaid())
        print()