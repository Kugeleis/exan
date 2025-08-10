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
    Removes rows where the value is an outlier, based on the Median Absolute Deviation (MAD) method.
    A value is considered an outlier if it is outside median ± sigma_cutoff * MAD.
    
    :param df: Input DataFrame
    :param value_col: Measurement column
    :param group_col: Grouping column
    :param sigma_cutoff: Multiplier for MAD for rejection
    :return: Filtered DataFrame
    """
    def _filter_group(group: pd.DataFrame) -> pd.DataFrame:
        median = group[value_col].median()
        mad = (group[value_col] - median).abs().median()
        mad_std = mad * 1.4826 # scale MAD to be comparable to std deviation

        if mad_std == 0:
            return group

        lower = median - sigma_cutoff * mad_std
        upper = median + sigma_cutoff * mad_std
        return group[(group[value_col] >= lower) & (group[value_col] <= upper)]

    # Apply filtering per group
    filtered_df = df.groupby(group_col, group_keys=False).apply(_filter_group)
    return filtered_df.reset_index(drop=True)
