import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
from box import Box
import main
from utils.analyses import AnovaAnalysis, TTestAnalysis, MannWhitneyAnalysis

@pytest.fixture
def mock_config_loader():
    with patch('main.ConfigLoader') as mock:
        instance = mock.return_value
        instance.settings = Box({
            'group_col': 'Group',
            'analyses': [],
            'plots': [],
            'output': {}
        })
        # Mock style_settings as well, as it's now mandatory
        instance.style_settings = Box({
            "limits_style": {
                "LSL": {"annotation_text": "LSL", "line_color": "red", "annotation_position_horizontal": "right", "annotation_xshift_horizontal": 10, "annotation_position_vertical": "top", "annotation_yshift_vertical": 10},
                "USL": {"annotation_text": "USL", "line_color": "red", "annotation_position_horizontal": "right", "annotation_xshift_horizontal": 10, "annotation_position_vertical": "top", "annotation_yshift_vertical": 10},
                "T": {"annotation_text": "T", "line_color": "green", "annotation_position_horizontal": "right", "annotation_xshift_horizontal": 10, "annotation_position_vertical": "top", "annotation_yshift_vertical": 10},
            },
            "axis": {
                "font_size": 12,
                "font_color": "black",
                "title_font_size": 14,
                "title_font_color": "gray",
                "show_grid": True,
                "grid_color": "lightgray",
                "zero_line": True,
                "zero_line_color": "black",
            }
        })
        yield mock

@pytest.fixture
def create_dummy_csv(tmp_path):
    def _create_csv(content):
        csv_path = tmp_path / "dummy.csv"
        csv_path.write_text(content)
        return csv_path
    return _create_csv

def test_main_2_groups(mock_config_loader, create_dummy_csv):
    csv_content = """# limit: Lower_Limit, 1.0
# limit: Upper_Limit, 3.0
Group,Value
A,1
A,2
B,1
B,2
"""
    csv_path = create_dummy_csv(csv_content)
    # Update return_value to match new limits structure
    mock_limits = {
        "Lower_Limit": {"Value": 1.0},
        "Upper_Limit": {"Value": 3.0},
    }
    with patch('main.load_data_with_limits', return_value=(pd.read_csv(csv_path, skiprows=2), mock_limits)):
        with patch.object(TTestAnalysis, 'analyze', return_value={}) as mock_ttest, \
             patch.object(MannWhitneyAnalysis, 'analyze', return_value={}) as mock_mannwhitney, \
             patch.object(AnovaAnalysis, 'analyze', return_value={}) as mock_anova:
            main.main()
            assert mock_ttest.called
            assert mock_mannwhitney.called
            assert not mock_anova.called

def test_main_3_groups(mock_config_loader, create_dummy_csv):
    csv_content = """# limit: Lower_Limit, 1.0
# limit: Upper_Limit, 3.0
Group,Value
A,1
A,2
B,1
B,2
C,1
C,2
"""
    csv_path = create_dummy_csv(csv_content)
    # Update return_value to match new limits structure
    mock_limits = {
        "Lower_Limit": {"Value": 1.0},
        "Upper_Limit": {"Value": 3.0},
    }
    with patch('main.load_data_with_limits', return_value=(pd.read_csv(csv_path, skiprows=2), mock_limits)):
        with patch.object(TTestAnalysis, 'analyze', return_value={}) as mock_ttest, \
             patch.object(MannWhitneyAnalysis, 'analyze', return_value={}) as mock_mannwhitney, \
             patch.object(AnovaAnalysis, 'analyze', return_value={}) as mock_anova:
            main.main()
            assert not mock_ttest.called
            assert not mock_mannwhitney.called
            assert mock_anova.called

def test_main_1_group(mock_config_loader, create_dummy_csv):
    csv_content = """# limit: Lower_Limit, 1.0
# limit: Upper_Limit, 3.0
Group,Value
A,1
A,2
"""
    csv_path = create_dummy_csv(csv_content)
    # Update return_value to match new limits structure
    mock_limits = {
        "Lower_Limit": {"Value": 1.0},
        "Upper_Limit": {"Value": 3.0},
    }
    with patch('main.load_data_with_limits', return_value=(pd.read_csv(csv_path, skiprows=2), mock_limits)):
        with patch.object(TTestAnalysis, 'analyze', return_value={}) as mock_ttest, \
             patch.object(MannWhitneyAnalysis, 'analyze', return_value={}) as mock_mannwhitney, \
             patch.object(AnovaAnalysis, 'analyze', return_value={}) as mock_anova:
            main.main()
            assert not mock_ttest.called
            assert not mock_mannwhitney.called
            assert not mock_anova.called
