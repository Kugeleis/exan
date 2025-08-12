import pytest
import pandas as pd
from utils.preprocessing import load_data_with_limits
import os

@pytest.fixture
def create_dummy_csv(tmp_path):
    csv_content = """# limit: Lower_Limit, 1.0, 0.5
# limit: Target, 2.0, 1.0
# limit: Upper_Limit, 3.0, 2.0
Group,Value,Data2
A,2.13,1.23
A,1.97,4.56
B,1.77,3.12
"""
    csv_path = tmp_path / "dummy.csv"
    csv_path.write_text(csv_content)
    return csv_path

def test_load_data_with_limits(create_dummy_csv):
    df, limits = load_data_with_limits(create_dummy_csv)

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 3
    assert "Group" in df.columns
    assert "Value" in df.columns
    assert "Data2" in df.columns

    assert isinstance(limits, dict)
    assert "Lower_Limit" in limits
    assert "Target" in limits
    assert "Upper_Limit" in limits

    assert limits["Lower_Limit"]["Value"] == 1.0
    assert limits["Lower_Limit"]["Data2"] == 0.5
    assert limits["Target"]["Value"] == 2.0
    assert limits["Target"]["Data2"] == 1.0
    assert limits["Upper_Limit"]["Value"] == 3.0
    assert limits["Upper_Limit"]["Data2"] == 2.0
