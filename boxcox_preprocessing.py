"""
boxcox_preprocessing.py
Module providing iterative Box-Cox transformation utilities for data normalization.
"""

from typing import Tuple, Optional
import numpy as np
import pandas as pd
from scipy.stats import boxcox, boxcox_normmax

def boxcox_transform(
    data: pd.Series,
    lmbda: Optional[float] = None,
    offset: float = 1e-6
) -> Tuple[np.ndarray, float]:
    """
    Transforms data using Box-Cox transformation.
    If lambda is None, finds optimal lambda via maximum likelihood estimation.

    :param data: 1D numeric data (positive values required)
    :param lmbda: Box-Cox lambda parameter; if None, determine automatically
    :param offset: Small positive offset added if data contains zeros/negatives
    :returns: Tuple of (transformed data np.ndarray, used lambda value)
    """
    # Shift data if non-positive values exist
    if (data <= 0).any():
        shift = abs(data.min()) + offset
        data_shifted = data + shift
    else:
        data_shifted = data
        shift = 0.0

    if lmbda is None:
        # Find optimal lambda via MLE
        optimal_lambda = boxcox_normmax(data_shifted, method='mle')
    else:
        optimal_lambda = lmbda

    transformed = boxcox(data_shifted, lmbda=optimal_lambda)

    return transformed, optimal_lambda


def apply_boxcox_preprocessing(
    df: pd.DataFrame,
    value_col: str,
    group_col: Optional[str] = None,
    offset: float = 1e-6,
    global_transform: bool = False
) -> Tuple[pd.DataFrame, dict]:
    """
    Applies Box-Cox transformation on data, either globally or separately per group.

    :param df: DataFrame containing the data
    :param value_col: Name of the measurement column to transform
    :param group_col: Name of group column (required if global_transform=False)
    :param offset: Small positive offset to handle non-positive values
    :param global_transform: If True, transform the entire data together; else per group
    :return: Tuple of (transformed DataFrame with updated value_col, dict of lambdas per group or global)
    """

    transformed_df = df.copy()
    lambdas = {}

    if global_transform:
        data = df[value_col]
        transformed, lmbda = boxcox_transform(data, offset=offset)
        transformed_df[value_col] = transformed
        lambdas["global"] = lmbda
    else:
        if group_col is None:
            raise ValueError("group_col must be specified if global_transform is False")

        lambdas = {}
        transformed_values = []

        for grp, subdf in df.groupby(group_col):
            data = subdf[value_col]
            transformed, lmbda = boxcox_transform(data, offset=offset)
            transformed_values.append(pd.Series(transformed, index=subdf.index))
            lambdas[grp] = lmbda

        transformed_df[value_col] = pd.concat(transformed_values).sort_index()

    return transformed_df, lambdas
