import pytest
import io
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
            'group_col': 'group',
            'value_col': 'value',
            'lower_limit_col': 'lower',
            'upper_limit_col': 'upper',
            'analyses': [],
            'plots': []
        })
        yield mock

def test_main_2_groups(mock_config_loader):
    csv_content = """Value_Lower_Limit,1.0
Value_Upper_Limit,3.0
Group,Value
A,1
A,2
B,1
B,2
"""
    original_read_csv = pd.read_csv
    mock_open = MagicMock()
    mock_open.return_value.__enter__.return_value = io.StringIO(csv_content)

    with patch('builtins.open', mock_open):
        with patch('pandas.read_csv', lambda _, skiprows: original_read_csv(io.StringIO(csv_content), skiprows=skiprows)):
            with patch.object(TTestAnalysis, 'analyze', return_value={}) as mock_ttest, \
                 patch.object(MannWhitneyAnalysis, 'analyze', return_value={}) as mock_mannwhitney, \
                 patch.object(AnovaAnalysis, 'analyze', return_value={}) as mock_anova:

                with patch('main.ConfigLoader') as mock_config_loader_local:
                    instance = mock_config_loader_local.return_value
                    instance.settings = Box({
                        'group_col': 'Group',
                        'analyses': [],
                        'plots': [],
                        'output': {}
                    })
                    main.main()

                    assert mock_ttest.called
                    assert mock_mannwhitney.called
                    assert not mock_anova.called

def test_main_3_groups(mock_config_loader):
    csv_content = """Value_Lower_Limit,1.0
Value_Upper_Limit,3.0
Group,Value
A,1
A,2
B,1
B,2
C,1
C,2
"""
    original_read_csv = pd.read_csv
    mock_open = MagicMock()
    mock_open.return_value.__enter__.return_value = io.StringIO(csv_content)

    with patch('builtins.open', mock_open):
        with patch('pandas.read_csv', lambda _, skiprows: original_read_csv(io.StringIO(csv_content), skiprows=skiprows)):
            with patch.object(TTestAnalysis, 'analyze', return_value={}) as mock_ttest, \
                 patch.object(MannWhitneyAnalysis, 'analyze', return_value={}) as mock_mannwhitney, \
                 patch.object(AnovaAnalysis, 'analyze', return_value={}) as mock_anova:

                with patch('main.ConfigLoader') as mock_config_loader_local:
                    instance = mock_config_loader_local.return_value
                    instance.settings = Box({
                        'group_col': 'Group',
                        'analyses': [],
                        'plots': [],
                        'output': {}
                    })
                    main.main()

                    assert not mock_ttest.called
                    assert not mock_mannwhitney.called
                    assert mock_anova.called

def test_main_1_group(mock_config_loader):
    csv_content = """Value_Lower_Limit,1.0
Value_Upper_Limit,3.0
Group,Value
A,1
A,2
"""
    original_read_csv = pd.read_csv
    mock_open = MagicMock()
    mock_open.return_value.__enter__.return_value = io.StringIO(csv_content)

    with patch('builtins.open', mock_open):
        with patch('pandas.read_csv', lambda _, skiprows: original_read_csv(io.StringIO(csv_content), skiprows=skiprows)):
            with patch.object(TTestAnalysis, 'analyze', return_value={}) as mock_ttest, \
                 patch.object(MannWhitneyAnalysis, 'analyze', return_value={}) as mock_mannwhitney, \
                 patch.object(AnovaAnalysis, 'analyze', return_value={}) as mock_anova:

                with patch('main.ConfigLoader') as mock_config_loader_local:
                    instance = mock_config_loader_local.return_value
                    instance.settings = Box({
                        'group_col': 'Group',
                        'analyses': [],
                        'plots': [],
                        'output': {}
                    })
                    main.main()

                    assert not mock_ttest.called
                    assert not mock_mannwhitney.called
                    assert not mock_anova.called

def test_main_with_new_data_format(mock_config_loader):
    # Create a temporary CSV file with the new format
    csv_content = """Value_Lower_Limit,1.0
Value_Upper_Limit,3.0
Group,Value,Data2
A,2.13,1.23
A,1.97,4.56
B,1.77,3.12
B,1.57,1.45
"""
    original_read_csv = pd.read_csv
    mock_open = MagicMock()
    mock_open.return_value.__enter__.return_value = io.StringIO(csv_content)

    with patch('builtins.open', mock_open):
        with patch('pandas.read_csv', lambda _, skiprows: original_read_csv(io.StringIO(csv_content), skiprows=skiprows)):
            with patch('main.ConfigLoader') as mock_config_loader_local:
                instance = mock_config_loader_local.return_value
                instance.settings = Box({
                    'group_col': 'Group',
                    'analyses': [],
                    'plots': [],
                    'output': {}
                })
                with patch.object(TTestAnalysis, 'analyze', return_value={}) as mock_ttest, \
                    patch.object(MannWhitneyAnalysis, 'analyze', return_value={}) as mock_mannwhitney, \
                    patch('main.generate_report') as mock_generate_report:

                    main.main()

                    assert mock_ttest.call_count == 2
                    assert mock_mannwhitney.call_count == 2
