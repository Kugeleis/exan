"""
Plot classes for interactive visualizations using Plotly.
"""

from typing import Optional
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from .plot_registry import register_plot
from pathlib import Path

class Plot:
    """Base class for all plot types."""
    def plot(
        self,
        df: pd.DataFrame,
        group_col: str,
        value_col: str,
        lower_limit: Optional[float] = None,
        upper_limit: Optional[float] = None,
        output_config: Optional[dict] = None,
    ) -> go.Figure:
        raise NotImplementedError

    def _save_fig(self, fig: go.Figure, plot_name: str, output_config: Optional[dict] = None):
        if not output_config:
            return

        save_interactive = output_config.get("save_interactive_html", False)
        save_static = output_config.get("save_static_html", False)
        save_pdf = output_config.get("save_pdf", False)

        if not any([save_interactive, save_static, save_pdf]):
            return

        output_dir = Path(output_config.get("output_directory", "output"))
        output_dir.mkdir(parents=True, exist_ok=True)

        prefix = output_config.get("filename_prefix", "plot")
        filename = f"{prefix}_{plot_name}"

        if save_interactive:
            fig.write_html(output_dir / f"{filename}.html")
        if save_static:
            fig.write_image(output_dir / f"{filename}.png", format="png", engine="kaleido")
        if save_pdf:
            fig.write_image(output_dir / f"{filename}.pdf", format="pdf", engine="kaleido")

@register_plot
class BoxPlot(Plot):
    """Interactive box plot of all groups."""
    def plot(self, df: pd.DataFrame, group_col: str, value_col: str,
             lower_limit: Optional[float] = None,
             upper_limit: Optional[float] = None,
             output_config: Optional[dict] = None) -> go.Figure:
        fig = px.box(df, x=group_col, y=value_col, points="all", title="Boxplot")
        if lower_limit is not None:
            fig.add_hline(y=lower_limit, line_dash="dash", line_color="red")
        if upper_limit is not None:
            fig.add_hline(y=upper_limit, line_dash="dash", line_color="red")

        self._save_fig(fig, "boxplot", output_config)

        return fig

@register_plot
class CumulativeFrequencyPlot(Plot):
    """Cumulative frequency plot for each group."""
    def plot(self, df: pd.DataFrame, group_col: str, value_col: str,
             lower_limit: Optional[float] = None,
             upper_limit: Optional[float] = None,
             output_config: Optional[dict] = None) -> go.Figure:
        fig = go.Figure()
        for g in df[group_col].unique():
            vals = np.sort(df[df[group_col] == g][value_col])
            cum = np.arange(1, len(vals) + 1) / len(vals)
            fig.add_trace(go.Scatter(x=vals, y=cum, mode="lines", name=str(g)))
        if lower_limit is not None:
            fig.add_vline(x=lower_limit, line_dash="dash", line_color="red")
        if upper_limit is not None:
            fig.add_vline(x=upper_limit, line_dash="dash", line_color="red")

        self._save_fig(fig, "cumulative_frequency", output_config)

        return fig
