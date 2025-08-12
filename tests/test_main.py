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
            'input': {
                'group_col': 'Group',
                'value_col': 'Value',
                'lower_limit_col': 'Lower_Limit',
                'upper_limit_col': 'Upper_Limit',
                'data_file': 'data/fake.csv'
            },
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
    # Mock config.input.data_file
    mock_config_loader.return_value.settings.input.data_file = csv_path

    with patch('main.load_data_with_limits', return_value=(pd.read_csv(csv_path, skiprows=2), mock_limits)) as mock_load_data:
        with patch.object(TTestAnalysis, 'analyze', return_value={'test': 'T-test', 'p_value': 0.01, 'statistic': 2.5}) as mock_ttest, \
             patch.object(MannWhitneyAnalysis, 'analyze', return_value={'test': 'Mann-Whitney', 'p_value': 0.02, 'statistic': 3.0}) as mock_mannwhitney, \
             patch.object(AnovaAnalysis, 'analyze', return_value={'test': 'ANOVA', 'p_value': 0.03, 'F_statistic': 4.0}) as mock_anova:
            main.run_analysis(mock_config_loader.return_value.settings, mock_config_loader.return_value.style_settings, mock_config_loader.return_value)
            assert mock_ttest.called
            assert mock_mannwhitney.called
            assert not mock_anova.called
            mock_load_data.assert_called_once_with(csv_path)

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
    # Mock config.input.data_file
    mock_config_loader.return_value.settings.input.data_file = csv_path

    with patch('main.load_data_with_limits', return_value=(pd.read_csv(csv_path, skiprows=2), mock_limits)) as mock_load_data:
        with patch.object(TTestAnalysis, 'analyze', return_value={'test': 'T-test', 'p_value': 0.01, 'statistic': 2.5}) as mock_ttest, \
             patch.object(MannWhitneyAnalysis, 'analyze', return_value={'test': 'Mann-Whitney', 'p_value': 0.02, 'statistic': 3.0}) as mock_mannwhitney, \
             patch.object(AnovaAnalysis, 'analyze', return_value={'test': 'ANOVA', 'p_value': 0.03, 'F_statistic': 4.0}) as mock_anova:
            main.run_analysis(mock_config_loader.return_value.settings, mock_config_loader.return_value.style_settings, mock_config_loader.return_value)
            assert not mock_ttest.called
            assert not mock_mannwhitney.called
            assert mock_anova.called
            mock_load_data.assert_called_once_with(csv_path)

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
    # Mock config.input.data_file
    mock_config_loader.return_value.settings.input.data_file = csv_path

    with patch('main.load_data_with_limits', return_value=(pd.read_csv(csv_path, skiprows=2), mock_limits)) as mock_load_data:
        with patch.object(TTestAnalysis, 'analyze', return_value={'test': 'T-test', 'p_value': 0.01, 'statistic': 2.5}) as mock_ttest, \
             patch.object(MannWhitneyAnalysis, 'analyze', return_value={'test': 'Mann-Whitney', 'p_value': 0.02, 'statistic': 3.0}) as mock_mannwhitney, \
             patch.object(AnovaAnalysis, 'analyze', return_value={'test': 'ANOVA', 'p_value': 0.03, 'F_statistic': 4.0}) as mock_anova:
            main.run_analysis(mock_config_loader.return_value.settings, mock_config_loader.return_value.style_settings, mock_config_loader.return_value)
            assert not mock_ttest.called
            assert not mock_mannwhitney.called
            assert not mock_anova.called
            mock_load_data.assert_called_once_with(csv_path)