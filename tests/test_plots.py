# tests/test_plots.py
import pytest
import pandas as pd
import plotly.graph_objects as go
from utils.plots import BoxPlot

@pytest.fixture
def mock_df():
    data = {'group': ['A', 'A', 'B', 'B'], 'value': [1, 2, 3, 4]}
    return pd.DataFrame(data)

def test_boxplot_returns_figure(mock_df):
    plotter = BoxPlot()
    fig = plotter.plot(mock_df, 'group', 'value')
    assert isinstance(fig, go.Figure)
