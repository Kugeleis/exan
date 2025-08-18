import pytest
import pandas as pd
from src.utils.relevance_decorator import relevance_decorator

def mock_analysis_significant(df, group_col, value_col):
    return {
        "significant": True,
        "mean_values": [10, 20]
    }

def mock_analysis_not_significant(df, group_col, value_col):
    return {
        "significant": False,
        "mean_values": [10, 11]
    }

def test_relevance_decorator_relevant():
    limits = {"lower_limit": 0, "upper_limit": 50}
    decorated_analysis = relevance_decorator(limits, threshold=0.1)(mock_analysis_significant)
    result = decorated_analysis(pd.DataFrame(), "", "")
    assert result["relevance"] is True
    assert "Significant AND relevant" in result["message"]

def test_relevance_decorator_not_relevant():
    limits = {"lower_limit": 0, "upper_limit": 50}
    decorated_analysis = relevance_decorator(limits, threshold=0.5)(mock_analysis_significant)
    result = decorated_analysis(pd.DataFrame(), "", "")
    assert result["relevance"] is False
    assert "Significant but NOT relevant" in result["message"]

def test_relevance_decorator_not_significant():
    limits = {"lower_limit": 0, "upper_limit": 50}
    decorated_analysis = relevance_decorator(limits, threshold=0.1)(mock_analysis_not_significant)
    result = decorated_analysis(pd.DataFrame(), "", "")
    assert "No statistically significant difference" in result["message"]

def test_relevance_decorator_zero_range():
    limits = {"lower_limit": 50, "upper_limit": 50}
    decorated_analysis = relevance_decorator(limits, threshold=0.1)(mock_analysis_significant)
    result = decorated_analysis(pd.DataFrame(), "", "")
    assert result["relevance"] is False
    assert "Zero range" in result["message"]

def test_relevance_decorator_missing_limits():
    limits = {"lower_limit": 0}
    decorated_analysis = relevance_decorator(limits, threshold=0.1)(mock_analysis_significant)
    result = decorated_analysis(pd.DataFrame(), "", "")
    assert result["relevance"] is False
    assert "Missing lower or upper limit" in result["message"]
