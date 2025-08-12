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
        lower_limit: Optional[float] = None,
        upper_limit: Optional[float] = None,
        target_value: Optional[float] = None,
        fig: Optional[go.Figure] = None,
        row: Optional[int] = None,
        col: Optional[int] = None,
        results: Optional[List[Dict]] = None,
        style_settings: Optional[Box] = None, # Added style_settings
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
        style_settings: Optional[Box] = None, # Added style_settings
    ):
        if style_settings is None or "limits_style" not in style_settings:
            # Fallback to hardcoded values if style_settings is not provided or incomplete
            limit_styles = {
                "LSL": {"annotation_text": "LSL", "line_color": "red", "annotation_position_horizontal": "right", "annotation_xshift_horizontal": 10, "annotation_position_vertical": "top", "annotation_yshift_vertical": 10},
                "USL": {"annotation_text": "USL", "line_color": "red", "annotation_position_horizontal": "right", "annotation_xshift_horizontal": 10, "annotation_position_vertical": "top", "annotation_yshift_vertical": 10},
                "T": {"annotation_text": "T", "line_color": "green", "annotation_position_horizontal": "right", "annotation_xshift_horizontal": 10, "annotation_position_vertical": "top", "annotation_yshift_vertical": 10},
            }
        else:
            limit_styles = style_settings.limits_style

        limits_to_add = [
            (lower_limit, "LSL"),
            (upper_limit, "USL"),
            (target_value, "T"),
        ]

        for limit_value, limit_key in limits_to_add:
            if limit_value is not None:
                style = limit_styles.get(limit_key, {})
                annotation_text = style.get("annotation_text", limit_key)
                line_color = style.get("line_color", "red" if limit_key != "T" else "green")

                if is_horizontal:
                    annotation_position = style.get("annotation_position_horizontal", "right")
                    annotation_xshift = style.get("annotation_xshift_horizontal", 10)
                    annotation_yshift = style.get("annotation_yshift_horizontal", None)
                else:
                    annotation_position = style.get("annotation_position_vertical", "top")
                    annotation_xshift = style.get("annotation_xshift_vertical", None)
                    annotation_yshift = style.get("annotation_yshift_vertical", 10)

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
        if "font_size" in axis_style: updates["tickfont_size"] = axis_style.font_size
        if "font_color" in axis_style: updates["tickfont_color"] = axis_style.font_color
        if "title_font_size" in axis_style: updates["title_font_size"] = axis_style.title_font_size
        if "title_font_color" in axis_style: updates["title_font_color"] = axis_style.title_font_color
        if "show_grid" in axis_style: updates["showgrid"] = axis_style.show_grid
        if "grid_color" in axis_style: updates["gridcolor"] = axis_style.grid_color
        if "zero_line" in axis_style: updates["zeroline"] = axis_style.zero_line
        if "zero_line_color" in axis_style: updates["zerolinecolor"] = axis_style.zero_line_color
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
        if axis_style is None:
            return

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
             lower_limit: Optional[float] = None,
             upper_limit: Optional[float] = None,
             target_value: Optional[float] = None,
             fig: Optional[go.Figure] = None,
             row: Optional[int] = None,
             col: Optional[int] = None,
             results: Optional[List[Dict]] = None,
             style_settings: Optional[Box] = None) -> go.Figure:
        if fig is None:
            fig = go.Figure()

        for trace in px.box(df, x=group_col, y=value_col, points="all").data:
            fig.add_trace(trace, row=row, col=col)

        self._add_all_limit_lines(fig, lower_limit, upper_limit, target_value, True, row, col, style_settings=style_settings)
        if style_settings and "axis" in style_settings:
            self._apply_axis_style(fig, style_settings.axis, row, col, yaxis_name="yaxis")
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
             results: Optional[List[Dict]] = None,
             style_settings: Optional[Box] = None) -> go.Figure:
        if fig is None:
            fig = go.Figure()

        for g in df[group_col].unique():
            vals = np.sort(df[df[group_col] == g][value_col])
            cum = np.arange(1, len(vals) + 1) / len(vals)
            fig.add_trace(go.Scatter(x=vals, y=cum, mode="lines", name=str(g)), row=row, col=col)

        self._add_all_limit_lines(fig, lower_limit, upper_limit, target_value, False, row, col, style_settings=style_settings)
        if style_settings and "axis" in style_settings:
            self._apply_axis_style(fig, style_settings.axis, row, col, xaxis_name="xaxis")
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
             results: Optional[List[Dict]] = None,
             style_settings: Optional[Box] = None) -> go.Figure:
        if results is None:
            return go.Figure()

        if fig is None:
            fig = go.Figure()

        columns = [result['column'] for result in results]
        p_values = [result['p_value'] for result in results]

        fig.add_trace(go.Bar(x=columns, y=p_values, name="P-Value"), row=row, col=col)
        fig.add_hline(y=0.05, line_dash="dash", line_color="red", annotation_text="Alpha=0.05", annotation_position="top right", row=row, col=col)
        if style_settings and "axis" in style_settings:
            self._apply_axis_style(fig, style_settings.axis, row, col, yaxis_name="yaxis", xaxis_name="xaxis")
        return fig