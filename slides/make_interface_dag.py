"""Render the interface DAG as an interactive figure for the slides.

The deck embeds the result in an iframe, so hovering over a node during the talk
shows its name and description. Regenerate with `pixi run slides-dag` whenever the
pinned GETTSIM changes.
"""

from pathlib import Path

from gettsim import plot

OUT = Path(__file__).parent / "public" / "interface_dag.html"

# Plotly writes `height: 100%`, which only resolves if its ancestors have a height.
FILL_IFRAME = """<style>
  html, body { height: 100%; margin: 0; }
  body > div { height: 100%; }
</style>
"""


def main() -> None:
    fig = plot.dag.interface(show_node_description=True)
    fig.update_layout(autosize=True, margin={"l": 8, "r": 8, "t": 8, "b": 8}, title=None)
    fig.write_html(
        OUT,
        include_plotlyjs="cdn",
        full_html=True,
        default_width="100%",
        default_height="100%",
        config={"responsive": True, "displayModeBar": False},
    )
    OUT.write_text(OUT.read_text().replace("<head>", "<head>\n" + FILL_IFRAME, 1))
    print(f"wrote {OUT}")  # noqa: T201


if __name__ == "__main__":
    main()
