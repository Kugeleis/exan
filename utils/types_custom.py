"""
types_custom.py

This module defines custom type hints using `TypedDict` for various
configuration structures and data analysis results. These types enhance
code readability and enable static type checking for complex dictionary
structures.
"""

from typing import TypedDict, List

class AnalysisResult(TypedDict, total=False):
    test: str
    F_statistic: float
    t_statistic: float
    U_statistic: float
    p_value: float
    significant: bool
    relevance: bool
    message: str
    mean_values: list[float]
    error: str

class ReportConfig(TypedDict):
    name: str
    author: str
    description: str

class OutlierRemovalConfig(TypedDict):
    enabled: bool
    sigma_cutoff: float

class PreprocessingConfig(TypedDict):
    outlier_removal: OutlierRemovalConfig

class AnalysisConfig(TypedDict):
    name: str
    relevance: bool
    relevance_threshold: float

class PlotConfig(TypedDict):
    name: str

class OutputConfig(TypedDict):
    save_interactive_html: bool
    save_static_html: bool
    save_pdf: bool
    output_directory: str

class AxisStyle(TypedDict, total=False):
    font_size: int
    font_color: str
    title_font_size: int
    title_font_color: str
    show_grid: bool
    grid_color: str
    zero_line: bool
    zero_line_color: str

class LimitsStyle(TypedDict, total=False):
    annotation_text: str
    line_color: str
    annotation_position_horizontal: str
    annotation_xshift_horizontal: int
    annotation_position_vertical: str
    annotation_yshift_vertical: int

class LimitsStyles(TypedDict):
    LSL: LimitsStyle
    USL: LimitsStyle
    T: LimitsStyle

class StyleConfig(TypedDict, total=False):
    limits_style: LimitsStyles
    axis: AxisStyle

class Config(TypedDict):
    report: ReportConfig
    group_col: str
    value_col: str
    lower_limit_col: str
    upper_limit_col: str
    preprocessing: PreprocessingConfig
    analyses: List[AnalysisConfig]
    plots: List[PlotConfig]
    output: OutputConfig