import pandas as pd

def filter_outliers(df: pd.DataFrame, value_col: str, group_col: str, sigma_cutoff: float = 3.0) -> pd.DataFrame:
    """
    Removes data points lying outside mean ± sigma_cutoff * std deviation per group.
    
    :param df: Input DataFrame
    :param value_col: Column name with measurements
    :param group_col: Column name for grouping
    :param sigma_cutoff: Number of standard deviations for cutoff
    :return: Filtered DataFrame
    """
    def filter_group(group):
        mean = group[value_col].mean()
        std = group[value_col].std()
        lower_bound = mean - sigma_cutoff * std
        upper_bound = mean + sigma_cutoff * std
        filtered = group[(group[value_col] >= lower_bound) & (group[value_col] <= upper_bound)]
        return filtered

    filtered_df = df.groupby(group_col).apply(filter_group).reset_index(drop=True)
    return filtered_df
