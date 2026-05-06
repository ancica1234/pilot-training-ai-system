"""
Run this script to print a Mermaid diagram of the agent graph to the terminal,
and optionally save a PNG to graph/graph.png.

Usage:
    OPENAI_API_KEY=dummy python3.11 -m graph.visualise
"""

import os
os.environ.setdefault("GROQ_API_KEY", "dummy")  # satisfy validation without a real key

from graph.graph import graph


def print_mermaid() -> None:
    print("── Mermaid diagram ───────────────────────────────────────────")
    print(graph.get_graph().draw_mermaid())
    print("──────────────────────────────────────────────────────────────")


def save_png(path: str = "graph/graph.png") -> None:
    try:
        png = graph.get_graph().draw_mermaid_png()
        with open(path, "wb") as f:
            f.write(png)
        print(f"PNG saved to {path}")
    except Exception as e:
        print(f"Could not save PNG (is graphviz installed?): {e}")


if __name__ == "__main__":
    print_mermaid()
    save_png()