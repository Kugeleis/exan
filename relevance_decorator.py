"""
Adds practical relevance check to analysis results based on limits and threshold.
"""

from typing import Callable
import pandas as pd
from types_custom import AnalysisResult

def relevance_decorator(
    lower_limit: float, upper_limit: float, threshold: float = 0.2
) -> Callable[[Callable[..., AnalysisResult]], Callable[..., AnalysisResult]]:
    """
    Decorator to extend an analysis function with a relevance check.
    """
    def decorator(analyze_func: Callable[..., AnalysisResult]) -> Callable[..., AnalysisResult]:
        def wrapper(
            df: pd.DataFrame, group_col: str, value_col: str, *args, **kwargs
        ) -> AnalysisResult:
            result = analyze_func(df, group_col, value_col, *args, **kwargs)
            if "mean_values" in result and isinstance(result["mean_values"], list):
                range_val = upper_limit - lower_limit
                if range_val == 0:
                    result["relevance"] = False
                    result["message"] = "Zero range between limits – cannot assess relevance."
                else:
                    max_diff = max(result["mean_values"]) - min(result["mean_values"])
                    relevance = max_diff >= (threshold * range_val)
                    result["relevance"] = relevance
                    if not result.get("significant", False):
                        result["message"] = "No statistically significant difference."
                    elif relevance:
                        result["message"] = f"Significant AND relevant (Δ={max_diff:.2f}, threshold={threshold*100:.1f}%)."
                    else:
                        result["message"] = f"Significant but NOT relevant (Δ={max_diff:.2f} < {threshold*100:.1f}%)."
            return result
        return wrapper
    return decorator
