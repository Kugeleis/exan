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
    mean_values: List[float]
    error: str
