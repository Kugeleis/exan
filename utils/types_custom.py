from typing import TypedDict

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
