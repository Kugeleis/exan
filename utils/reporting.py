from typing import List
import plotly.graph_objects as go
from pathlib import Path
from fpdf import FPDF
import tempfile
import os

def generate_report(figures: List[go.Figure], plot_names: List[str], config: dict):
    """
    Generates a report containing multiple plots in various formats.
    """
    output_config = config.get("output", {})
    report_config = config.get("report", {})
    output_dir = Path(output_config.get("output_directory", "output"))
    output_dir.mkdir(parents=True, exist_ok=True)
    prefix = report_config.get("name", "report")

    if output_config.get("save_interactive_html"):
        filename = output_dir / f"{prefix}.html"
        with open(filename, 'w') as f:
            f.write("<html><head><title>Analysis Report</title></head><body>")
            f.write("<h1>Analysis Report</h1>")
            for fig, name in zip(figures, plot_names):
                f.write(f"<h2>{name}</h2>")
                f.write(fig.to_html(full_html=False, include_plotlyjs='cdn'))
            f.write("</body></html>")

    if output_config.get("save_static_html"):
        filename = output_dir / f"{prefix}_static.html"
        with open(filename, 'w') as f:
            f.write("<html><head><title>Static Analysis Report</title></head><body>")
            f.write("<h1>Static Analysis Report</h1>")
            for fig, name in zip(figures, plot_names):
                f.write(f"<h2>{name}</h2>")
                f.write(fig.to_html(full_html=False, include_plotlyjs=False))
            f.write("</body></html>")

    if output_config.get("save_pdf"):
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)

        for fig, name in zip(figures, plot_names):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_image:
                fig.write_image(temp_image.name)

                pdf.add_page()
                pdf.set_font("Arial", "B", 16)
                pdf.cell(0, 10, name, 0, 1, "C")
                pdf.image(temp_image.name, x=10, y=30, w=190)

            os.remove(temp_image.name)

        pdf_filename = output_dir / f"{prefix}.pdf"
        pdf.output(str(pdf_filename))
