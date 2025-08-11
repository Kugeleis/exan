# tests/test_reporting.py
import pytest
from unittest.mock import MagicMock, patch, mock_open
import plotly.graph_objects as go
from utils.reporting import generate_report

@patch('pathlib.Path.mkdir')
@patch('builtins.open', new_callable=mock_open)
@patch('plotly.graph_objects.Figure.write_image')
def test_generate_report(mock_write_image, mock_file_open, mock_mkdir):
    figures = [go.Figure(), go.Figure()]
    plot_names = ["Plot 1", "Plot 2"]
    config = {
        "output": {
            "output_directory": "test_report_output",
            "save_interactive_html": True,
            "save_static_html": True,
            "save_pdf": True,
        },
        "report": {
            "name": "my_test_report"
        }
    }

    generate_report(figures, plot_names, config)

    mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)

    from pathlib import Path
    # Check for interactive html
    interactive_filename = Path("test_report_output/my_test_report.html")
    # Check for static html
    static_filename = Path("test_report_output/my_test_report_static.html")

    # Check that open was called for html files
    mock_file_open.assert_any_call(interactive_filename, 'w')
    mock_file_open.assert_any_call(static_filename, 'w')

    handle = mock_file_open()

    # Check that the HTML content is written correctly
    handle.write.assert_any_call("<html><head><title>Analysis Report</title></head><body>")
    handle.write.assert_any_call("<h1>Analysis Report</h1>")
    handle.write.assert_any_call("<h2>Plot 1</h2>")
    handle.write.assert_any_call("<h2>Plot 2</h2>")
    handle.write.assert_any_call("</body></html>")

    # Check for pdf calls
    pdf_filename_1 = "test_report_output/my_test_report_Plot 1.pdf"
    pdf_filename_2 = "test_report_output/my_test_report_Plot 2.pdf"
    mock_write_image.assert_any_call(str(Path(pdf_filename_1)))
    mock_write_image.assert_any_call(str(Path(pdf_filename_2)))
