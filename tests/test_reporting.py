# tests/test_reporting.py
import pytest
from unittest.mock import MagicMock, patch, mock_open
import plotly.graph_objects as go
from utils.reporting import generate_html_report

@patch('pathlib.Path.mkdir')
@patch('builtins.open', new_callable=mock_open)
def test_generate_html_report(mock_file_open, mock_mkdir):
    figures = [go.Figure(), go.Figure()]
    plot_names = ["Plot 1", "Plot 2"]
    output_config = {
        "output_directory": "test_report_output",
        "filename_prefix": "test_report"
    }

    generate_html_report(figures, plot_names, output_config)

    mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)

    from pathlib import Path
    filename = Path("test_report_output/test_report.html")
    mock_file_open.assert_called_once_with(filename, 'w')

    handle = mock_file_open()

    # Check that the HTML content is written correctly
    # I will check for some key parts of the HTML structure
    handle.write.assert_any_call("<html><head><title>Analysis Report</title></head><body>")
    handle.write.assert_any_call("<h1>Analysis Report</h1>")
    handle.write.assert_any_call("<h2>Plot 1</h2>")
    handle.write.assert_any_call("<h2>Plot 2</h2>")
    handle.write.assert_any_call("</body></html>")
