from typing import List
import plotly.graph_objects as go
from pathlib import Path

def generate_html_report(figures: List[go.Figure], plot_names: List[str], output_config: dict):
    """
    Generates a single HTML report containing multiple plots.
    """
    output_dir = Path(output_config.get("output_directory", "output"))
    output_dir.mkdir(parents=True, exist_ok=True)

    prefix = output_config.get("filename_prefix", "report")
    filename = output_dir / f"{prefix}.html"

    with open(filename, 'w') as f:
        f.write("<html><head><title>Analysis Report</title></head><body>")
        f.write("<h1>Analysis Report</h1>")

        for fig, name in zip(figures, plot_names):
            f.write(f"<h2>{name}</h2>")
            f.write(fig.to_html(full_html=False, include_plotlyjs='cdn'))

        f.write("</body></html>")
