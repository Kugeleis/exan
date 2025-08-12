"""
Plot classes for interactive visualizations using Plotly.
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from .plot_registry import register_plot
from plotly.subplots import make_subplots
from typing import List, Dict, Optional
from abc import ABC, abstractmethod

class Plot(ABC):
    """Base class for all plot types."""
    @abstractmethod
    def plot(
        self,
        df: pd.DataFrame,
        group_col: str,
        value_col: str,
        lower_limit: Optional[float] = None,
        upper_limit: Optional[float] = None,
        target_value: Optional[float] = None,
        fig: Optional[go.Figure] = None,
        row: Optional[int] = None,
        col: Optional[int] = None,
        results: Optional[List[Dict]] = None,
    ) -> go.Figure:
        raise NotImplementedError

    def _add_limit_line(
        self,
        fig: go.Figure,
        value: float,
        annotation_text: str,
        line_color: str,
        is_horizontal: bool,
        row: Optional[int] = None,
        col: Optional[int] = None,
        annotation_position: Optional[str] = None,
        annotation_xshift: Optional[int] = None,
        annotation_yshift: Optional[int] = None,
    ):
        if fig is not None and (row is None or col is None):
            raise ValueError("row and col must be provided when fig is not None for subplots.")

        if is_horizontal:
            fig.add_hline(
                y=value,
                line_dash="dash",
                line_color=line_color,
                annotation_text=annotation_text,
                annotation_position=annotation_position,
                row=row,
                col=col,
                annotation_xshift=annotation_xshift,
                annotation_yshift=annotation_yshift,
            )
        else:
            fig.add_vline(
                x=value,
                line_dash="dash",
                line_color=line_color,
                annotation_text=annotation_text,
                annotation_position=annotation_position,
                row=row,
                col=col,
                annotation_xshift=annotation_xshift,
                annotation_yshift=annotation_yshift,
            )

    def _add_all_limit_lines(
        self,
        fig: go.Figure,
        lower_limit: Optional[float],
        upper_limit: Optional[float],
        target_value: Optional[float],
        is_horizontal: bool,
        row: Optional[int] = None,
        col: Optional[int] = None,
        annotation_position: Optional[str] = None,
        annotation_xshift: Optional[int] = None,
        annotation_yshift: Optional[int] = None,
    ):
        if lower_limit is not None:
            self._add_limit_line(fig, lower_limit, "LSL", "red", is_horizontal, row, col, annotation_position, annotation_xshift, annotation_yshift)
        if upper_limit is not None:
            self._add_limit_line(fig, upper_limit, "USL", "red", is_horizontal, row, col, annotation_position, annotation_xshift, annotation_yshift)
        if target_value is not None:
            self._add_limit_line(fig, target_value, "T", "green", is_horizontal, row, col, annotation_position, annotation_xshift, annotation_yshift)

@register_plot
class BoxPlot(Plot):
    """Interactive box plot of all groups."""
    def plot(self, df: pd.DataFrame, group_col: str, value_col: str,
             lower_limit: Optional[float] = None,
             upper_limit: Optional[float] = None,
             target_value: Optional[float] = None,
             fig: Optional[go.Figure] = None,
             row: Optional[int] = None,
             col: Optional[int] = None,
             results: Optional[List[Dict]] = None) -> go.Figure:
        if fig is None:
            fig = go.Figure()

        for trace in px.box(df, x=group_col, y=value_col, points="all").data:
            fig.add_trace(trace, row=row, col=col)

        self._add_all_limit_lines(fig, lower_limit, upper_limit, target_value, True, row, col, "right", annotation_xshift=10)
        return fig

@register_plot
class CumulativeFrequencyPlot(Plot):
    """Cumulative frequency plot for each group."""
    def plot(self, df: pd.DataFrame, group_col: str, value_col: str,
             lower_limit: Optional[float] = None,
             upper_limit: Optional[float] = None,
             target_value: Optional[float] = None,
             fig: Optional[go.Figure] = None,
             row: Optional[int] = None,
             col: Optional[int] = None,
             results: Optional[List[Dict]] = None) -> go.Figure:
        if fig is None:
            fig = go.Figure()

        for g in df[group_col].unique():
            vals = np.sort(df[df[group_col] == g][value_col])
            cum = np.arange(1, len(vals) + 1) / len(vals)
            fig.add_trace(go.Scatter(x=vals, y=cum, mode="lines", name=str(g)), row=row, col=col)

        self._add_all_limit_lines(fig, lower_limit, upper_limit, target_value, False, row, col, "top", annotation_yshift=10)
        return fig

@register_plot
class SignificancePlot(Plot):
    """Bar chart of p-values for each column."""
    def plot(self,
             df: pd.DataFrame,
             group_col: str,
             value_col: str,
             lower_limit: Optional[float] = None,
             upper_limit: Optional[float] = None,
             target_value: Optional[float] = None,
             fig: Optional[go.Figure] = None,
             row: Optional[int] = None,
             col: Optional[int] = None,
             results: Optional[List[Dict]] = None) -> go.Figure:
        if results is None:
            return go.Figure()

        if fig is None:
            fig = go.Figure()

        columns = [result['column'] for result in results]
        p_values = [result['p_value'] for result in results]

        fig.add_trace(go.Bar(x=columns, y=p_values, name="P-Value"), row=row, col=col)
        fig.add_hline(y=0.05, line_dash="dash", line_color="red", annotation_text="Alpha=0.05", annotation_position="top right", row=row, col=col)
        return fig
