import pytest
from unittest.mock import MagicMock, patch, mock_open, call
import plotly.graph_objects as go
from utils.reporting import (
    generate_report,
    report_generator_factory,
    InteractiveHTMLReportGenerator,
    StaticHTMLReportGenerator,
    PDFReportGenerator,
)
from pathlib import Path

from box import Box

@pytest.fixture
def mock_config():
    return Box({
        "output": {
            "output_directory": "test_report_output",
            "save_interactive_html": True,
            "save_static_html": True,
            "save_pdf": True,
        },
        "report": {"name": "my_test_report"},
    })

@pytest.fixture
def mock_plots():
    return {
        "Plot 1": go.Figure(),
        "Plot 2": go.Figure(),
    }

@pytest.fixture
def mock_results():
    return [
        {
            "column": "Test Column 1",
            "test": "T-Test",
            "p_value": 0.04,
            "significant": True,
            "relevance": True,
            "message": "Significant and relevant",
        },
        {
            "column": "Test Column 2",
            "test": "ANOVA",
            "p_value": 0.1,
            "significant": False,
            "relevance": False,
            "message": "Not significant",
        },
    ]

@patch("utils.reporting.get_project_version", return_value="0.0.0")
@patch("pathlib.Path.mkdir")
@patch("builtins.open", new_callable=mock_open)
def test_interactive_html_report_generator(mock_file_open, mock_mkdir, mock_get_version, mock_plots, mock_results, mock_config):
    generator = InteractiveHTMLReportGenerator(mock_plots, mock_results, mock_config)
    generator.generate()

    mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
    filename = Path("test_report_output/my_test_report.html")
    mock_file_open.assert_called_once_with(filename, "w")
    handle = mock_file_open()
    handle.write.assert_any_call("<html><head><title>Analysis Report</title></head><body><a name=\"top\"></a>")
    handle.write.assert_any_call("<h1>Analysis Report</h1>")

@patch("utils.reporting.get_project_version", return_value="0.0.0")
@patch("pathlib.Path.mkdir")
@patch("builtins.open", new_callable=mock_open)
def test_static_html_report_generator(mock_file_open, mock_mkdir, mock_get_version, mock_plots, mock_results, mock_config):
    generator = StaticHTMLReportGenerator(mock_plots, mock_results, mock_config)
    generator.generate()

    mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
    filename = Path("test_report_output/my_test_report_static.html")
    mock_file_open.assert_called_once_with(filename, "w")
    handle = mock_file_open()
    handle.write.assert_any_call("<html><head><title>Static Analysis Report</title></head><body><a name=\"top\"></a>")
    handle.write.assert_any_call("<h1>Static Analysis Report</h1>")


@patch("utils.reporting.get_project_version", return_value="0.0.0")
@patch("pathlib.Path.mkdir")
@patch("utils.reporting.FPDF")
@patch("plotly.graph_objects.Figure.write_image")
@patch("utils.reporting.tempfile.NamedTemporaryFile")
@patch("utils.reporting.os.remove")
def test_pdf_report_generator(mock_os_remove, mock_tempfile, mock_write_image, mock_fpdf, mock_mkdir, mock_get_version, mock_plots, mock_results, mock_config):
    # Mock the temporary file context manager
    mock_temp_file_instance = MagicMock()
    mock_temp_file_instance.__enter__.return_value.name = "temp_image.png"
    mock_tempfile.return_value = mock_temp_file_instance

    generator = PDFReportGenerator(mock_plots, mock_results, mock_config)
    generator.generate()

    mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
    assert mock_write_image.call_count == 2

    pdf_instance = mock_fpdf.return_value
    assert pdf_instance.add_page.call_count == 4  # Title page, overview table + 2 plots
    pdf_instance.output.assert_called_once_with(str(Path("test_report_output/my_test_report.pdf")))


def test_report_generator_factory(mock_plots, mock_results, mock_config):
    interactive_gen = report_generator_factory("interactive_html", mock_plots, mock_results, mock_config)
    assert isinstance(interactive_gen, InteractiveHTMLReportGenerator)

    static_gen = report_generator_factory("static_html", mock_plots, mock_results, mock_config)
    assert isinstance(static_gen, StaticHTMLReportGenerator)

    pdf_gen = report_generator_factory("pdf", mock_plots, mock_results, mock_config)
    assert isinstance(pdf_gen, PDFReportGenerator)

    with pytest.raises(ValueError):
        report_generator_factory("unknown_format", mock_plots, mock_results, mock_config)


@patch("utils.reporting.report_generator_factory")
def test_generate_report(mock_factory, mock_plots, mock_results, mock_config):
    mock_interactive_gen = MagicMock()
    mock_static_gen = MagicMock()
    mock_pdf_gen = MagicMock()

    def side_effect(format, plots, results, config):
        if format == "interactive_html":
            return mock_interactive_gen
        elif format == "static_html":
            return mock_static_gen
        elif format == "pdf":
            return mock_pdf_gen

    mock_factory.side_effect = side_effect

    generate_report(mock_plots, mock_results, mock_config)

    mock_factory.assert_has_calls([
        call("interactive_html", mock_plots, mock_results, mock_config),
        call("static_html", mock_plots, mock_results, mock_config),
        call("pdf", mock_plots, mock_results, mock_config)
    ])

    mock_interactive_gen.generate.assert_called_once()
    mock_static_gen.generate.assert_called_once()
    mock_pdf_gen.generate.assert_called_once()