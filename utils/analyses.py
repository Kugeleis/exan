"""
analyses.py
Defines statistical analysis modules. All classes implement a common `analyze` interface.
"""

from abc import ABC
from typing import Union
import pandas as pd
import numpy as np
from scipy import stats
from scipy.stats._result_classes import TtestResult
from .types_custom import AnalysisResult
from analysis_registry import register_analysis


class Analysis(ABC):
    """
    Abstract base class for all statistical analysis types.
    """

    def analyze(
        self, df: pd.DataFrame, group_col: str, value_col: str
    ) -> AnalysisResult:
        """
        Execute analysis on a given dataset.
        """
        raise NotImplementedError


@register_analysis
class AnovaAnalysis(Analysis):
    """Performs one-way ANOVA across 2 or more groups."""

    def analyze(
        self, df: pd.DataFrame, group_col: str, value_col: str
    ) -> AnalysisResult:
        groups = df[group_col].unique()
        samples = [df[df[group_col] == g][value_col] for g in groups]
        result = stats.f_oneway(*samples)
        mean_values = [float(np.mean(s)) for s in samples]
        return {
            "test": "ANOVA",
            "F_statistic": float(result.statistic),
            "p_value": float(result.pvalue),
            "significant": bool(result.pvalue < 0.05),
            "mean_values": mean_values,
        }


@register_analysis
class TTestAnalysis(Analysis):
    """Performs independent t-test for exactly two groups."""

    def analyze(
        self, df: pd.DataFrame, group_col: str, value_col: str
    ) -> AnalysisResult:
        groups = df[group_col].unique()
        if len(groups) != 2:
            return {"error": "T-Test requires exactly two groups."}
        g1 = df[df[group_col] == groups[0]][value_col]
        g2 = df[df[group_col] == groups[1]][value_col]
        result: TtestResult = stats.ttest_ind(g1, g2, equal_var=False)
        mean_values = [float(np.mean(g1)), float(np.mean(g2))]
        return {
            "test": "T-Test",
            "t_statistic": float(result.statistic),
            "p_value": float(result.pvalue),
            "significant": bool(result.pvalue < 0.05),
            "mean_values": mean_values,
        }


@register_analysis
class MannWhitneyAnalysis(Analysis):
    """Performs Mann-Whitney U test (non-parametric) for two groups."""

    def analyze(
        self, df: pd.DataFrame, group_col: str, value_col: str
    ) -> AnalysisResult:
        groups = df[group_col].unique()
        if len(groups) != 2:
            return {"error": "Mann-Whitney U-Test requires exactly two groups."}
        g1 = df[df[group_col] == groups[0]][value_col]
        g2 = df[df[group_col] == groups[1]][value_col]
        result = stats.mannwhitneyu(g1, g2, alternative="two-sided")
        mean_values = [float(np.mean(g1)), float(np.mean(g2))]
        return {
            "test": "Mann-Whitney U-Test",
            "U_statistic": float(result.statistic),
            "p_value": float(result.pvalue),
            "significant": bool(result.pvalue < 0.05),
            "mean_values": mean_values,
        }
