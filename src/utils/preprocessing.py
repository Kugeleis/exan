"""
preprocessing.py
Data preparation utilities, e.g. outlier removal based on sigma threshold.
"""

import pandas as pd
from typing import Tuple, Dict, List

def load_data_with_limits(file_path: str) -> Tuple[pd.DataFrame, Dict[str, Dict[str, float]]]:
    """
    Loads data from a CSV file, extracting limits from lines starting with "# limit:".
    Limits can be defined per column, e.g., "# limit: Lower_Limit, 1.0, 0.5"

    :param file_path: Path to the CSV file.
    :return: A tuple containing the DataFrame and a dictionary of limits.
             The limits dictionary will have the structure: 
             {"Limit_Name": {"Column_Name": Value}}
    """
    limits: Dict[str, Dict[str, float]] = {}
    header_lines = 0
    column_names: List[str] = []

    with open(file_path, "r") as f:
        lines = f.readlines()
        for i, line in enumerate(lines):
            if line.startswith("# limit:"):
                parts = [p.strip() for p in line.strip().split(":")[1].split(",")]
                limit_name = parts[0]
                limit_values = [float(v) for v in parts[1:]]

                # Assuming the first non-comment line is the header
                if not column_names:
                    # Find the actual header line after comments
                    for j in range(i + 1, len(lines)):
                        if not lines[j].strip().startswith("#"):
                            column_names = [col.strip() for col in lines[j].strip().split(",")]
                            break

                # Exclude the group_col from column_names for limits if it's not a value column
                # This assumes limits are only for value columns
                # For now, let's assume all columns after the first are value columns for limits
                # A more robust solution would involve reading config.group_col here, but that's not possible
                # within this function without passing config.
                value_column_names = column_names[1:] # Assuming first column is group_col

                if len(limit_values) == len(value_column_names):
                    limits[limit_name] = {col_name: val for col_name, val in zip(value_column_names, limit_values)}
                else:
                    # Handle cases where limits might be missing for some columns or are generic
                    # For now, if count doesn't match, store as a single value if only one is provided
                    if len(limit_values) == 1:
                        # This case might mean a generic limit for all value columns
                        # Or it's an error in the CSV format
                        # For now, we'll store it as a generic limit if it's not column-specific
                        limits[limit_name] = {"__generic__": limit_values[0]}
                    else:
                        # If the number of limits doesn't match the number of value columns, it's ambiguous.
                        # We'll skip this limit line or log a warning.
                        pass # Or raise an error/log a warning

                header_lines += 1
            elif line.strip().startswith("#"):
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
