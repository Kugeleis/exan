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
from box import Box # Import Box for style_settings

class Plot(ABC):
    """Base class for all plot types."""
    @abstractmethod
    def plot(
        self,
        df: pd.DataFrame,
        group_col: str,
        value_col: str,
        limits_dict: Dict[str, Optional[float]], # Consolidated limits
        fig: Optional[go.Figure] = None,
        row: Optional[int] = None,
        col: Optional[int] = None,
        results: Optional[List[Dict]] = None,
        style_settings: Box = None, # style_settings is now mandatory
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
        # Removed the ValueError check. Plotly's add_hline/add_vline handle None for row/col correctly for standalone figures.
        # For subplot figures, row/col are always provided from main.py.

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
        limits_dict: Dict[str, Optional[float]], # Consolidated limits
        is_horizontal: bool,
        row: Optional[int] = None,
        col: Optional[int] = None,
        style_settings: Box = None, # style_settings is now mandatory
    ):
        limit_styles = style_settings.limits_style

        limits_to_add = [
            (limits_dict.get("lower_limit"), "LSL"),
            (limits_dict.get("upper_limit"), "USL"),
            (limits_dict.get("target_value"), "T"),
        ]

        for limit_value, limit_key in limits_to_add:
            if limit_value is not None:
                style = limit_styles[limit_key]
                annotation_text = style["annotation_text"]
                line_color = style["line_color"]

                if is_horizontal:
                    annotation_position = style["annotation_position_horizontal"]
                    annotation_xshift = style["annotation_xshift_horizontal"]
                    annotation_yshift = style.get("annotation_yshift_horizontal", None)
                else:
                    annotation_position = style["annotation_position_vertical"]
                    annotation_xshift = style.get("annotation_xshift_vertical", None)
                    annotation_yshift = style["annotation_yshift_vertical"]

                self._add_limit_line(
                    fig,
                    limit_value,
                    annotation_text,
                    line_color,
                    is_horizontal,
                    row,
                    col,
                    annotation_position,
                    annotation_xshift,
                    annotation_yshift,
                )

    def _get_axis_updates(self, axis_style: Box) -> dict:
        updates = {}
        updates["tickfont_size"] = axis_style.font_size
        updates["tickfont_color"] = axis_style.font_color
        updates["title_font_size"] = axis_style.title_font_size
        updates["title_font_color"] = axis_style.title_font_color
        updates["showgrid"] = axis_style.show_grid
        updates["gridcolor"] = axis_style.grid_color
        updates["zeroline"] = axis_style.zero_line
        updates["zerolinecolor"] = axis_style.zero_line_color
        return updates

    def _apply_axis_style(
        self,
        fig: go.Figure,
        axis_style: Box,
        row: Optional[int] = None,
        col: Optional[int] = None,
        xaxis_name: str = "xaxis",
        yaxis_name: str = "yaxis",
    ):
        xaxis_updates = self._get_axis_updates(axis_style)
        yaxis_updates = self._get_axis_updates(axis_style)

        if row is not None and col is not None:
            fig.update_layout(**{f"{xaxis_name}{row if row > 1 else ''}": xaxis_updates})
            fig.update_layout(**{f"{yaxis_name}{col if col > 1 else ''}": yaxis_updates})
        else:
            fig.update_layout(xaxis=xaxis_updates, yaxis=yaxis_updates)


@register_plot
class BoxPlot(Plot):
    """Interactive box plot of all groups."""
    def plot(self, df: pd.DataFrame, group_col: str, value_col: str,
             limits_dict: Dict[str, Optional[float]], # Consolidated limits
             fig: Optional[go.Figure] = None,
             row: Optional[int] = None,
             col: Optional[int] = None,
             results: Optional[List[Dict]] = None,
             style_settings: Box = None) -> go.Figure:
        if fig is None:
            fig = go.Figure()

        for trace in px.box(df, x=group_col, y=value_col, points="all").data:
            fig.add_trace(trace, row=row, col=col)

        self._add_all_limit_lines(fig, limits_dict, True, style_settings=style_settings, row=row, col=col)
        self._apply_axis_style(fig, style_settings.axis, row=row, col=col, yaxis_name="yaxis")
        return fig

@register_plot
class CumulativeFrequencyPlot(Plot):
    """Cumulative frequency plot for each group."""
    def plot(self, df: pd.DataFrame, group_col: str, value_col: str,
             limits_dict: Dict[str, Optional[float]], # Consolidated limits
             fig: Optional[go.Figure] = None,
             row: Optional[int] = None,
             col: Optional[int] = None,
             results: Optional[List[Dict]] = None,
             style_settings: Box = None) -> go.Figure:
        if fig is None:
            fig = go.Figure()

        for g in df[group_col].unique():
            vals = np.sort(df[df[group_col] == g][value_col])
            cum = np.arange(1, len(vals) + 1) / len(vals)
            fig.add_trace(go.Scatter(x=vals, y=cum, mode="lines", name=str(g)), row=row, col=col)

        self._add_all_limit_lines(fig, limits_dict, False, style_settings=style_settings, row=row, col=col)
        self._apply_axis_style(fig, style_settings.axis, row=row, col=col, xaxis_name="xaxis")
        return fig

@register_plot
class SignificancePlot(Plot):
    """Bar chart of p-values for each column."""
    def plot(self,
             df: pd.DataFrame,
             group_col: str,
             value_col: str,
             limits_dict: Dict[str, Optional[float]], # Consolidated limits
             fig: Optional[go.Figure] = None,
             row: Optional[int] = None,
             col: Optional[int] = None,
             results: Optional[List[Dict]] = None,
             style_settings: Box = None) -> go.Figure:
        if results is None:
            return go.Figure()

        if fig is None:
            fig = go.Figure()

        columns = [result['column'] for result in results]
        p_values = [result['p_value'] for result in results]

        fig.add_trace(go.Bar(x=columns, y=p_values, name="P-Value"), row=row, col=col)
        fig.add_hline(y=0.05, line_dash="dash", line_color="red", annotation_text="Alpha=0.05", annotation_position="top right", row=row, col=col)
        self._apply_axis_style(fig, style_settings.axis, row, col, yaxis_name="yaxis", xaxis_name="xaxis")
        return fig