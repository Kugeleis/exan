"""
Plot classes for interactive visualizations using Plotly.
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from .plot_registry import register_plot
from plotly.subplots import make_subplots
from typing import List, Dict

class Plot:
    """Base class for all plot types."""
    def plot(
        self,
        df: pd.DataFrame,
        group_col: str,
        value_col: str,
        lower_limit: float | None = None,
        upper_limit: float | None = None,
        fig: go.Figure | None = None,
        row: int | None = None,
        col: int | None = None,
        results: List[Dict] | None = None,
    ) -> go.Figure:
        raise NotImplementedError

@register_plot
class BoxPlot(Plot):
    """Interactive box plot of all groups."""
    def plot(self, df: pd.DataFrame, group_col: str, value_col: str,
             lower_limit: float | None = None,
             upper_limit: float | None = None,
             fig: go.Figure | None = None,
             row: int | None = None,
             col: int | None = None,
             results: List[Dict] | None = None) -> go.Figure:
        if fig is None:
            fig = go.Figure()

        for trace in px.box(df, x=group_col, y=value_col, points="all").data:
            fig.add_trace(trace, row=row, col=col)

        if lower_limit is not None:
            fig.add_hline(y=lower_limit, line_dash="dash", line_color="red", row=row, col=col)
        if upper_limit is not None:
            fig.add_hline(y=upper_limit, line_dash="dash", line_color="red", row=row, col=col)
        return fig

@register_plot
class CumulativeFrequencyPlot(Plot):
    """Cumulative frequency plot for each group."""
    def plot(self, df: pd.DataFrame, group_col: str, value_col: str,
             lower_limit: float | None = None,
             upper_limit: float | None = None,
             fig: go.Figure | None = None,
             row: int | None = None,
             col: int | None = None,
             results: List[Dict] | None = None) -> go.Figure:
        if fig is None:
            fig = go.Figure()

        for g in df[group_col].unique():
            vals = np.sort(df[df[group_col] == g][value_col])
            cum = np.arange(1, len(vals) + 1) / len(vals)
            fig.add_trace(go.Scatter(x=vals, y=cum, mode="lines", name=str(g)), row=row, col=col)

        if lower_limit is not None:
            fig.add_vline(x=lower_limit, line_dash="dash", line_color="red", row=row, col=col)
        if upper_limit is not None:
            fig.add_vline(x=upper_limit, line_dash="dash", line_color="red", row=row, col=col)
        return fig

@register_plot
class SignificancePlot(Plot):
    """Bar chart of p-values for each column."""
    def plot(self, df: pd.DataFrame, group_col: str, value_col: str,
             lower_limit: float | None = None,
             upper_limit: float | None = None,
             fig: go.Figure | None = None,
             row: int | None = None,
             col: int | None = None,
             results: List[Dict] | None = None) -> go.Figure:
        if results is None:
            return go.Figure()

        if fig is None:
            fig = go.Figure()

        columns = [result['column'] for result in results]
        p_values = [result['p_value'] for result in results]

        fig.add_trace(go.Bar(x=columns, y=p_values, name="P-Value"), row=row, col=col)
        fig.add_hline(y=0.05, line_dash="dash", line_color="red", row=row, col=col)
        return fig
