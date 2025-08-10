import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
import main
from utils.analyses import AnovaAnalysis, TTestAnalysis, MannWhitneyAnalysis

@pytest.fixture
def mock_config_loader():
    with patch('main.ConfigLoader') as mock:
        instance = mock.return_value
        instance.settings.group_col = 'group'
        instance.settings.value_col = 'value'
        instance.settings.lower_limit_col = 'lower'
        instance.settings.upper_limit_col = 'upper'
        instance.settings.analyses = []
        instance.settings.plots = []
        yield mock

def create_mock_df(num_groups):
    num_rows = num_groups * 2
    groups = [chr(65 + i) for i in range(num_groups)]
    data = {'group': [], 'value': [], 'lower': [10] * num_rows, 'upper': [20] * num_rows}
    for g in groups:
        data['group'].extend([g] * 2)
        data['value'].extend([1, 2])
    return pd.DataFrame(data)

@patch('pandas.read_csv')
def test_main_2_groups(mock_read_csv, mock_config_loader):
    mock_read_csv.return_value = create_mock_df(2)

    with patch.object(TTestAnalysis, 'analyze', return_value={}) as mock_ttest, \
         patch.object(MannWhitneyAnalysis, 'analyze', return_value={}) as mock_mannwhitney, \
         patch.object(AnovaAnalysis, 'analyze', return_value={}) as mock_anova:

        main.main()

        assert mock_ttest.called
        assert mock_mannwhitney.called
        assert not mock_anova.called

@patch('pandas.read_csv')
def test_main_3_groups(mock_read_csv, mock_config_loader):
    mock_read_csv.return_value = create_mock_df(3)

    with patch.object(TTestAnalysis, 'analyze', return_value={}) as mock_ttest, \
         patch.object(MannWhitneyAnalysis, 'analyze', return_value={}) as mock_mannwhitney, \
         patch.object(AnovaAnalysis, 'analyze', return_value={}) as mock_anova:

        main.main()

        assert not mock_ttest.called
        assert not mock_mannwhitney.called
        assert mock_anova.called

@patch('pandas.read_csv')
def test_main_1_group(mock_read_csv, mock_config_loader):
    mock_read_csv.return_value = create_mock_df(1)

    with patch.object(TTestAnalysis, 'analyze', return_value={}) as mock_ttest, \
         patch.object(MannWhitneyAnalysis, 'analyze', return_value={}) as mock_mannwhitney, \
         patch.object(AnovaAnalysis, 'analyze', return_value={}) as mock_anova:

        main.main()

        assert not mock_ttest.called
        assert not mock_mannwhitney.called
        assert not mock_anova.called
