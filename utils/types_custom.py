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