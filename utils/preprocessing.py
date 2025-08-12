"""
preprocessing.py
Data preparation utilities, e.g. outlier removal based on sigma threshold.
"""

import pandas as pd
from typing import Tuple, Dict

def load_data_with_limits(file_path: str) -> Tuple[pd.DataFrame, Dict[str, float]]:
    """
    Loads data from a CSV file, extracting limits from lines starting with "# limit:".

    :param file_path: Path to the CSV file.
    :return: A tuple containing the DataFrame and a dictionary of limits.
    """
    limits = {}
    header_lines = 0
    with open(file_path, "r") as f:
        for line in f:
            if line.startswith("# limit:"):
                parts = line.strip().split(":")[1].split(",")
                if len(parts) == 2:
                    limit_name, limit_value = parts
                    limits[limit_name.strip()] = float(limit_value.strip())
                header_lines += 1
            elif line.startswith("#"):
                header_lines += 1
            else:
                break

    df = pd.read_csv(file_path, skiprows=lambda x: x < header_lines)
    return df, limits


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
    filtered_subset = df.groupby(group_col, group_keys=False).apply(_filter_group, include_groups=False)
    filtered_df = df.loc[filtered_subset.index]
    return filtered_df.reset_index(drop=True)