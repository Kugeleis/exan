"""
Adds practical relevance check to analysis results based on limits and threshold.
"""

import collections.abc
import pandas as pd
from typing import Dict, Optional
from .types_custom import AnalysisResult

def relevance_decorator(
    limits_dict: Dict[str, Optional[float]], threshold: float = 0.2
) -> collections.abc.Callable[[collections.abc.Callable[..., AnalysisResult]], collections.abc.Callable[..., AnalysisResult]]:
    """
    Decorator to extend an analysis function with a relevance check.
    """
    def decorator(analyze_func: collections.abc.Callable[..., AnalysisResult]) -> collections.abc.Callable[..., AnalysisResult]:
        def wrapper(
            df: pd.DataFrame, group_col: str, value_col: str, *args, **kwargs
        ) -> AnalysisResult:
            result = analyze_func(df, group_col, value_col, *args, **kwargs)
            if "mean_values" in result and isinstance(result["mean_values"], list):
                lower_limit = limits_dict.get("lower_limit")
                upper_limit = limits_dict.get("upper_limit")

                if lower_limit is None or upper_limit is None:
                    result["relevance"] = False
                    result["message"] = "Missing lower or upper limit – cannot assess relevance."
                else:
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
                            result["message"] = f"Significant AND relevant (Diff={max_diff:.2f}, threshold={threshold*100:.1f}%)."
                        else:
                            result["message"] = f"Significant but NOT relevant (Diff={max_diff:.2f} < {threshold*100:.1f}%)."
            return result
        return wrapper
    return decorator
