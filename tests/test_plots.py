# tests/test_plots.py
import pytest
from unittest.mock import MagicMock, patch
import pandas as pd
from utils.plots import BoxPlot
from pathlib import Path

@pytest.fixture
def mock_df():
    data = {'group': ['A', 'A', 'B', 'B'], 'value': [1, 2, 3, 4]}
    return pd.DataFrame(data)

@patch('pathlib.Path.mkdir')
@patch('plotly.graph_objects.Figure.write_html')
@patch('plotly.graph_objects.Figure.write_image')
def test_boxplot_save(mock_write_image, mock_write_html, mock_mkdir, mock_df):
    plotter = BoxPlot()
    output_config = {
        "save_interactive_html": True,
        "save_static_html": True,
        "save_pdf": True,
        "output_directory": "test_output",
        "filename_prefix": "test_plot"
    }

    plotter.plot(mock_df, 'group', 'value', output_config=output_config)

    output_dir = Path("test_output")
    mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)

    filename_html = output_dir / "test_plot_boxplot.html"
    mock_write_html.assert_called_once_with(filename_html)

    filename_pdf = output_dir / "test_plot_boxplot.pdf"
    mock_write_image.assert_any_call(filename_pdf, format="pdf", engine="kaleido")

    # for static html
    mock_write_image.assert_any_call(output_dir / "test_plot_boxplot.html", format="html", engine="kaleido")

    assert mock_write_image.call_count == 2

@pytest.mark.parametrize("output_config", [None, {}])
@patch('pathlib.Path.mkdir')
@patch('plotly.graph_objects.Figure.write_html')
@patch('plotly.graph_objects.Figure.write_image')
def test_boxplot_no_save(mock_write_image, mock_write_html, mock_mkdir, output_config, mock_df):
    plotter = BoxPlot()

    plotter.plot(mock_df, 'group', 'value', output_config=output_config)

    mock_mkdir.assert_not_called()
    mock_write_html.assert_not_called()
    mock_write_image.assert_not_called()
