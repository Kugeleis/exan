import pytest
import pandas as pd
from utils.preprocessing import filter_outliers

@pytest.fixture
def outlier_data():
    df = pd.DataFrame({
        'group': ['A'] * 10 + ['B'] * 10,
        'value': list(range(10)) + list(range(10, 20))
    })
    df.loc[19, 'value'] = 1000 # extreme outlier
    return df

def test_filter_outliers_removes_outlier(outlier_data):
    filtered_df = filter_outliers(outlier_data, 'value', 'group', sigma_cutoff=3.0)

    # The outlier in group B should be removed
    assert len(filtered_df) == 19
    assert 1000 not in filtered_df['value'].values

    # Group A should be unaffected
    assert len(filtered_df[filtered_df['group'] == 'A']) == 10
