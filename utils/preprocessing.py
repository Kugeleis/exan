"""
preprocessing.py
Data preparation utilities, e.g. outlier removal based on sigma threshold.
"""

import pandas as pd

def filter_outliers(
    df: pd.DataFrame,
    value_col: str,
    group_col: str,
    sigma_cutoff: float = 3.0
) -> pd.DataFrame:
    """
    Removes rows where the value is outside mean ± sigma_cutoff * std deviation, per group.
    
    :param df: Input DataFrame
    :param value_col: Measurement column
    :param group_col: Grouping column
    :param sigma_cutoff: Standard deviation multiplier for rejection
    :return: Filtered DataFrame
    """
    def _filter_group(group: pd.DataFrame) -> pd.DataFrame:
        mean = group[value_col].mean()
        std = group[value_col].std()
        lower = mean - sigma_cutoff * std
        upper = mean + sigma_cutoff * std
        return group[(group[value_col] >= lower) & (group[value_col] <= upper)]

    # Apply filtering per group
    filtered_df = df.groupby(group_col, group_keys=False).apply(_filter_group)
    return filtered_df.reset_index(drop=True)
