from typing import Dict
import plotly.graph_objects as go
from pathlib import Path
from fpdf import FPDF
import tempfile
import os
from abc import ABC, abstractmethod


class ReportGenerator(ABC):
    def __init__(self, plots: Dict[str, go.Figure], config: dict):
        self.plots = plots
        self.config = config
        self.output_config = self.config.get("output", {})
        self.report_config = self.config.get("report", {})
        self.output_dir = Path(self.output_config.get("output_directory", "output"))
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.prefix = self.report_config.get("name", "report")

    @abstractmethod
    def generate(self):
        pass


class InteractiveHTMLReportGenerator(ReportGenerator):
    def generate(self):
        filename = self.output_dir / f"{self.prefix}.html"
        with open(filename, 'w') as f:
            f.write("<html><head><title>Analysis Report</title></head><body>")
            f.write("<h1>Analysis Report</h1>")
            f.write("<h2>Report Information</h2>")
            f.write("<ul>")
            for key, value in self.report_config.items():
                f.write(f"<li><strong>{key}:</strong> {value}</li>")
            f.write("</ul>")
            for name, fig in self.plots.items():
                f.write(f"<h2>{name}</h2>")
                f.write(fig.to_html(full_html=False, include_plotlyjs='cdn'))
            f.write("</body></html>")


class StaticHTMLReportGenerator(ReportGenerator):
    def generate(self):
        filename = self.output_dir / f"{self.prefix}_static.html"
        with open(filename, 'w') as f:
            f.write("<html><head><title>Static Analysis Report</title></head><body>")
            f.write("<h1>Static Analysis Report</h1>")
            f.write("<h2>Report Information</h2>")
            f.write("<ul>")
            for key, value in self.report_config.items():
                f.write(f"<li><strong>{key}:</strong> {value}</li>")
            f.write("</ul>")
            for name, fig in self.plots.items():
                f.write(f"<h2>{name}</h2>")
                f.write(fig.to_html(full_html=False, include_plotlyjs=False))
            f.write("</body></html>")


class PDFReportGenerator(ReportGenerator):
    def generate(self):
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)

        # Title Page
        pdf.add_page()
        pdf.set_font("Arial", "B", 24)
        pdf.cell(0, 20, "Analysis Report", 0, 1, "C")
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 15, "Report Information", 0, 1, "L")
        pdf.set_font("Arial", "", 12)
        for key, value in self.report_config.items():
            pdf.cell(0, 10, f"  {key}: {value}", 0, 1, "L")

        for name, fig in self.plots.items():
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_image:
                fig.write_image(temp_image.name)

                pdf.add_page()
                pdf.set_font("Arial", "B", 16)
                pdf.cell(0, 10, name, 0, 1, "C")
                pdf.image(temp_image.name, x=10, y=30, w=190)

            os.remove(temp_image.name)

        pdf_filename = self.output_dir / f"{self.prefix}.pdf"
        pdf.output(str(pdf_filename))


def report_generator_factory(format: str, plots: Dict[str, go.Figure], config: dict) -> ReportGenerator:
    if format == "interactive_html":
        return InteractiveHTMLReportGenerator(plots, config)
    elif format == "static_html":
        return StaticHTMLReportGenerator(plots, config)
    elif format == "pdf":
        return PDFReportGenerator(plots, config)
    else:
        raise ValueError(f"Unknown report format: {format}")


def generate_report(plots: Dict[str, go.Figure], config: dict):
    """
    Generates a report containing multiple plots in various formats.
    """
    output_config = config.get("output", {})

    report_formats = []
    if output_config.get("save_interactive_html"):
        report_formats.append("interactive_html")
    if output_config.get("save_static_html"):
        report_formats.append("static_html")
    if output_config.get("save_pdf"):
        report_formats.append("pdf")

    for format in report_formats:
        generator = report_generator_factory(format, plots, config)
        generator.generate()
