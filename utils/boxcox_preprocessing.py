"""
boxcox_preprocessing.py

This module provides utilities for applying Box-Cox transformation to data.
It supports both global and group-wise transformations, handling non-positive values
by applying an offset.
"""

import numpy as np
import pandas as pd
from scipy.stats import boxcox, boxcox_normmax

def boxcox_transform(
    data: pd.Series,
    lmbda: float | None = None,
    offset: float = 1e-6
) -> tuple[np.ndarray, float]:
    """
    Transforms data using Box-Cox transformation.
    If lambda is None, finds optimal lambda via maximum likelihood estimation.

    Args:
        data (pd.Series): 1D numeric data (positive values required for direct transformation).
        lmbda (float | None): Box-Cox lambda parameter. If None, it is determined automatically
                              using maximum likelihood estimation (`boxcox_normmax`).
        offset (float): A small positive offset added to data if it contains zeros or negative values
                        to ensure all values are positive before transformation.

    Returns:
        tuple[np.ndarray, float]: A tuple containing:
            - transformed_data (np.ndarray): The Box-Cox transformed data.
            - used_lambda (float): The lambda value used for the transformation.
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
    group_col: str | None = None,
    offset: float = 1e-6,
    global_transform: bool = False
) -> tuple[pd.DataFrame, dict]:
    """
    Applies Box-Cox transformation on data, either globally or separately per group.

    Args:
        df (pd.DataFrame): DataFrame containing the data to be transformed.
        value_col (str): Name of the measurement column in `df` to transform.
        group_col (str | None): Name of the grouping column in `df`. Required if `global_transform` is False.
        offset (float): Small positive offset to handle non-positive values in the data.
        global_transform (bool): If True, the entire `value_col` is transformed together.
                                 If False, transformation is applied independently to each group defined by `group_col`.

    Returns:
        tuple[pd.DataFrame, dict]: A tuple containing:
            - transformed_df (pd.DataFrame): The DataFrame with the `value_col` updated with transformed values.
            - lambdas (dict): A dictionary of lambda values used for transformation. If `global_transform` is True,
                              it contains a single 'global' key. Otherwise, it contains lambda values per group.

    Raises:
        ValueError: If `group_col` is None when `global_transform` is False.
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