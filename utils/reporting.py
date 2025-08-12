import plotly.graph_objects as go
from pathlib import Path
from fpdf import FPDF
import tempfile
import os
from abc import ABC, abstractmethod
from typing import List, Dict
from .types_custom import Config

class ReportGenerator(ABC):
    def __init__(self, plots: dict[str, go.Figure], results: List[Dict], config: Config):
        self.plots = plots
        self.results = results
        self.config = config
        self.output_config = self.config["output"]
        self.report_config = self.config["report"]
        self.output_dir = Path(self.output_config["output_directory"])
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.prefix = self.report_config["name"]
        self._sort_plots_by_significance()

    def _sort_plots_by_significance(self):
        if not self.results:
            return

        # Create a dictionary to map column names to p-values
        p_values = {result['column']: result['p_value'] for result in self.results}

        # Sort the plots based on the p-value of the corresponding column
        self.plots = dict(sorted(self.plots.items(), key=lambda item: p_values.get(item[0].split('_')[-1], float('inf'))))

    def _generate_overview_table_html(self) -> str:
        """Generates an HTML table for the overview of results."""
        if not self.results:
            return ""

        html = "<h2>Analysis Overview</h2>"
        html += "<table border='1'><tr><th>Column</th><th>Test</th><th>P-Value</th><th>Significant</th><th>Relevance</th><th>Message</th></tr>"
        for result in self.results:
            html += f"<tr><td>{result.get('column', 'N/A')}</td><td>{result.get('test', 'N/A')}</td><td>{result.get('p_value', 'N/A'):.4f}</td><td>{result.get('significant', 'N/A')}</td><td>{result.get('relevance', 'N/A')}</td><td>{result.get('message', 'N/A')}</td></tr>"
        html += "</table>"
        return html

    def _generate_overview_table_pdf(self, pdf):
        """Generates a PDF table for the overview of results."""
        if not self.results:
            return

        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "Analysis Overview", 0, 1, "C")
        pdf.set_font("Arial", "B", 10)
        pdf.cell(40, 10, "Column", 1, 0, "C")
        pdf.cell(40, 10, "Test", 1, 0, "C")
        pdf.cell(30, 10, "P-Value", 1, 0, "C")
        pdf.cell(30, 10, "Significant", 1, 0, "C")
        pdf.cell(30, 10, "Relevance", 1, 0, "C")
        pdf.cell(100, 10, "Message", 1, 1, "C")

        pdf.set_font("Arial", "", 10)
        for result in self.results:
            pdf.cell(40, 10, str(result.get('column', 'N/A')), 1, 0)
            pdf.cell(40, 10, str(result.get('test', 'N/A')), 1, 0)
            pdf.cell(30, 10, f"{result.get('p_value', 'N/A'):.4f}", 1, 0)
            pdf.cell(30, 10, str(result.get('significant', 'N/A')), 1, 0)
            pdf.cell(30, 10, str(result.get('relevance', 'N/A')), 1, 0)
            pdf.cell(100, 10, str(result.get('message', 'N/A')), 1, 1)

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
            f.write(self._generate_overview_table_html())
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
            f.write(self._generate_overview_table_html())
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

        self._generate_overview_table_pdf(pdf)

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


def report_generator_factory(format: str, plots: dict[str, go.Figure], results: List[Dict], config: Config) -> ReportGenerator:
    if format == "interactive_html":
        return InteractiveHTMLReportGenerator(plots, results, config)
    elif format == "static_html":
        return StaticHTMLReportGenerator(plots, results, config)
    elif format == "pdf":
        return PDFReportGenerator(plots, results, config)
    else:
        raise ValueError(f"Unknown report format: {format}")

def generate_report(plots: dict[str, go.Figure], results: List[Dict], config: Config):
    """
    Generates a report containing multiple plots in various formats.
    """
    output_config = config["output"]

    report_formats = []
    if output_config["save_interactive_html"]:
        report_formats.append("interactive_html")
    if output_config["save_static_html"]:
        report_formats.append("static_html")
    if output_config["save_pdf"]:
        report_formats.append("pdf")

    for format in report_formats:
        generator = report_generator_factory(format, plots, results, config)
        generator.generate()
