import plotly.graph_objects as go
from pathlib import Path
from fpdf import FPDF
import tempfile
import os
from abc import ABC, abstractmethod
from typing import List, cast
from .types_custom import Config, AnalysisResult

class ReportGenerator(ABC):
    """
    Abstract base class for all report generators.

    Attributes:
        plots (dict[str, go.Figure]): A dictionary of plot figures, where keys are plot names.
        results (List[Dict]): A list of analysis results, each a dictionary.
        config (Config): The configuration object for the report.
        output_config (dict): Configuration specific to output settings.
        report_config (dict): Configuration specific to report details.
        output_dir (Path): The directory where reports will be saved.
        prefix (str): The prefix for report filenames.
    """
    def __init__(self, plots: dict[str, go.Figure], results: List[AnalysisResult], config: Config):
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
        """
        Sorts the plots dictionary based on the p-value of the corresponding analysis results.
        Plots with lower p-values (higher significance) come first.
        """
        if not self.results:
            return

        # Create a dictionary to map column names to p-values
        p_values = {result['column']: result['p_value'] for result in self.results if 'column' in result and 'p_value' in result}

        # Sort the plots based on the p-value of the corresponding column
        # The plot name is expected to be in the format "{plot_type}_{column_name}"
        self.plots = dict(sorted(self.plots.items(), key=lambda item: p_values.get(cast(str, item[0].split('_')[-1]), float('inf')))) # pyright: ignore[reportCallIssue, reportArgumentType]

    def _generate_overview_table_html(self) -> str:
        """
        Generates an HTML table for the overview of analysis results.

        Returns:
            str: An HTML string representing the overview table.
        """
        if not self.results:
            return ""

        html_lines = []
        html_lines.append("<h2>Analysis Overview</h2>")
        html_lines.append("<table border='1'>")
        html_lines.append("<tr><th>Column</th><th>Test</th><th>P-Value</th><th>Significant</th><th>Relevance</th><th>Message</th></tr>")

        for result in self.results:
            column_name = result.get('column', 'N/A')
            plot_link_html = column_name # Default to just the column name

            # Find the plot name that contains the column_name
            # This assumes that the plot name contains the column_name
            # and that the plot_id generation logic is consistent
            for plot_name in self.plots.keys():
                if column_name in plot_name:
                    # Generate the plot_id as done in generate() method
                    plot_id = plot_name.replace(' ', '_').replace('(', '').replace(')', '').replace('=', '').replace('.', '').replace(',', '')
                    plot_link_html = f"<a href=\"#{plot_id}\">{column_name}</a>"
                    break # Found a link, break from inner loop

            html_lines.append(
                f"<tr>"
                f"<td>{plot_link_html}</td>"
                f"<td>{result.get('test', 'N/A')}</td>"
                f"<td>{result.get('p_value', 'N/A'):.4f}</td>"
                f"<td>{result.get('significant', 'N/A')}</td>"
                f"<td>{result.get('relevance', 'N/A')}</td>"
                f"<td>{result.get('message', 'N/A')}</td>"
                f"</tr>"
            )
        html_lines.append("</table>")
        return "".join(html_lines)

    def _generate_overview_table_pdf(self, pdf: FPDF):
        """
        Generates a PDF table for the overview of analysis results.

        Args:
            pdf (FPDF): The FPDF object to which the table will be added.
        """
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
        """
        Abstract method to generate the report. Must be implemented by subclasses.
        """
        pass


class InteractiveHTMLReportGenerator(ReportGenerator):
    """
    Generates an interactive HTML report.
    """
    def generate(self):
        """
        Generates the interactive HTML report and saves it to the output directory.
        """
        filename = self.output_dir / f"{self.prefix}.html"
        with open(filename, 'w') as f:
            f.write("<html><head><title>Analysis Report</title></head><body><a name=\"top\"></a>")
            f.write("<h1>Analysis Report</h1>")
            f.write("<h2>Report Information</h2>")
            f.write("<ul>")
            for key, value in self.report_config.items():
                f.write(f"<li><strong>{key}:</strong> {value}</li>")
            f.write("</ul>")
            f.write(self._generate_overview_table_html())
            for name, fig in self.plots.items():
                plot_id = name.replace(' ', '_').replace('(', '').replace(')', '').replace('=', '').replace('.', '').replace(',', '') # Create a valid ID
                f.write(f"<h2 id=\"{plot_id}\">{name}</h2>")
                f.write(fig.to_html(full_html=False, include_plotlyjs='cdn'))
                f.write("<p><a href=\"#top\">Back to Top</a></p>")
            f.write("</body></html>")


class StaticHTMLReportGenerator(ReportGenerator):
    """
    Generates a static HTML report.
    """
    def generate(self):
        """
        Generates the static HTML report and saves it to the output directory.
        """
        filename = self.output_dir / f"{self.prefix}_static.html"
        with open(filename, 'w') as f:
            f.write("<html><head><title>Static Analysis Report</title></head><body><a name=\"top\"></a>")
            f.write("<h1>Static Analysis Report</h1>")
            f.write("<h2>Report Information</h2>")
            f.write("<ul>")
            for key, value in self.report_config.items():
                f.write(f"<li><strong>{key}:</strong> {value}</li>")
            f.write("</ul>")
            f.write(self._generate_overview_table_html())
            for name, fig in self.plots.items():
                plot_id = name.replace(' ', '_').replace('(', '').replace(')', '').replace('=', '').replace('.', '').replace(',', '') # Create a valid ID
                f.write(f"<h2 id=\"{plot_id}\">{name}</h2>")
                f.write(fig.to_html(full_html=False, include_plotlyjs=False))
                f.write("<p><a href=\"#top\">Back to Top</a></p>")
            f.write("</body></html>")


class PDFReportGenerator(ReportGenerator):
    """
    Generates a PDF report.
    """
    def generate(self):
        """
        Generates the PDF report and saves it to the output directory.
        """
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


def report_generator_factory(format: str, plots: dict[str, go.Figure], results: List[AnalysisResult], config: Config) -> ReportGenerator:
    """
    Factory function to create a ReportGenerator instance based on the specified format.

    Args:
        format (str): The desired report format (e.g., "interactive_html", "static_html", "pdf").
        plots (dict[str, go.Figure]): A dictionary of plot figures.
        results (List[AnalysisResult]): A list of analysis results.
        config (Config): The configuration object.

    Returns:
        ReportGenerator: An instance of a concrete ReportGenerator subclass.

    Raises:
        ValueError: If an unknown report format is provided.
    """
    if format == "interactive_html":
        return InteractiveHTMLReportGenerator(plots, results, config)
    elif format == "static_html":
        return StaticHTMLReportGenerator(plots, results, config)
    elif format == "pdf":
        return PDFReportGenerator(plots, results, config)
    else:
        raise ValueError(f"Unknown report format: {format}")

def generate_report(plots: dict[str, go.Figure], results: list[AnalysisResult], config: Config):
    """
    Generates a report containing multiple plots in various formats.

    Args:
        plots (dict[str, go.Figure]): A dictionary of plot figures.
        results (list[AnalysisResult]): A list of analysis results.
        config (Config): The configuration object.
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
