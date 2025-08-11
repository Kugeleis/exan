"""
Plot classes for interactive visualizations using Plotly.
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from .plot_registry import register_plot

class Plot:
    """Base class for all plot types."""
    def plot(
        self,
        df: pd.DataFrame,
        group_col: str,
        value_col: str,
        lower_limit: float | None = None,
        upper_limit: float | None = None,
    ) -> go.Figure:
        raise NotImplementedError

@register_plot
class BoxPlot(Plot):
    """Interactive box plot of all groups."""
    def plot(self, df: pd.DataFrame, group_col: str, value_col: str,
             lower_limit: float | None = None,
             upper_limit: float | None = None) -> go.Figure:
        fig = px.box(df, x=group_col, y=value_col, points="all", title="Boxplot")
        if lower_limit is not None:
            fig.add_hline(y=lower_limit, line_dash="dash", line_color="red")
        if upper_limit is not None:
            fig.add_hline(y=upper_limit, line_dash="dash", line_color="red")
        return fig

@register_plot
class CumulativeFrequencyPlot(Plot):
    """Cumulative frequency plot for each group."""
    def plot(self, df: pd.DataFrame, group_col: str, value_col: str,
             lower_limit: float | None = None,
             upper_limit: float | None = None) -> go.Figure:
        fig = go.Figure()
        for g in df[group_col].unique():
            vals = np.sort(df[df[group_col] == g][value_col])
            cum = np.arange(1, len(vals) + 1) / len(vals)
            fig.add_trace(go.Scatter(x=vals, y=cum, mode="lines", name=str(g)))
        if lower_limit is not None:
            fig.add_vline(x=lower_limit, line_dash="dash", line_color="red")
        if upper_limit is not None:
            fig.add_vline(x=upper_limit, line_dash="dash", line_color="red")
        return fig
