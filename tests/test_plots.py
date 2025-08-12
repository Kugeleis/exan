# tests/test_plots.py
import pytest
import pandas as pd
import plotly.graph_objects as go
from utils.plots import BoxPlot, CumulativeFrequencyPlot, SignificancePlot
from box import Box

@pytest.fixture
def mock_df():
    data = {'group': ['A', 'A', 'B', 'B'], 'value': [1, 2, 3, 4]}
    return pd.DataFrame(data)

@pytest.fixture
def mock_results():
    return [
        {
            "column": "value",
            "test": "T-Test",
            "p_value": 0.04,
            "significant": True,
            "relevance": True,
            "message": "Significant and relevant",
        },
    ]

@pytest.fixture
def mock_style_settings():
    return Box({
        "limits_style": {
            "LSL": {"annotation_text": "LSL", "line_color": "red", "annotation_position_horizontal": "right", "annotation_xshift_horizontal": 10, "annotation_position_vertical": "top", "annotation_yshift_vertical": 10},
            "USL": {"annotation_text": "USL", "line_color": "red", "annotation_position_horizontal": "right", "annotation_xshift_horizontal": 10, "annotation_position_vertical": "top", "annotation_yshift_vertical": 10},
            "T": {"annotation_text": "T", "line_color": "green", "annotation_position_horizontal": "right", "annotation_xshift_horizontal": 10, "annotation_position_vertical": "top", "annotation_yshift_vertical": 10},
        },
        "axis": {
            "font_size": 12,
            "font_color": "black",
            "title_font_size": 14,
            "title_font_color": "gray",
            "show_grid": True,
            "grid_color": "lightgray",
            "zero_line": True,
            "zero_line_color": "black",
        }
    })

def test_boxplot_returns_figure(mock_df, mock_style_settings):
    plotter = BoxPlot()
    fig = plotter.plot(mock_df, 'group', 'value', style_settings=mock_style_settings)
    assert isinstance(fig, go.Figure)

def test_cumulative_frequency_plot_returns_figure(mock_df, mock_style_settings):
    plotter = CumulativeFrequencyPlot()
    fig = plotter.plot(mock_df, 'group', 'value', style_settings=mock_style_settings)
    assert isinstance(fig, go.Figure)

def test_significance_plot_returns_figure(mock_df, mock_style_settings, mock_results):
    plotter = SignificancePlot()
    fig = plotter.plot(mock_df, 'group', 'value', results=mock_results, style_settings=mock_style_settings)
    assert isinstance(fig, go.Figure)