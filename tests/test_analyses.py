import pytest
import pandas as pd
import numpy as np
from utils.analyses import AnovaAnalysis, TTestAnalysis, MannWhitneyAnalysis

@pytest.fixture
def sample_data():
    return pd.DataFrame({
        'group': ['A', 'A', 'B', 'B', 'C', 'C'],
        'value': [1, 2, 3, 4, 5, 6]
    })

def test_anova_analysis(sample_data):
    analyzer = AnovaAnalysis()
    result = analyzer.analyze(sample_data, 'group', 'value')
    assert result['test'] == 'ANOVA'
    assert 'F_statistic' in result
    assert 'p_value' in result
    assert 'significant' in result
    assert len(result['mean_values']) == 3

def test_ttest_analysis(sample_data):
    analyzer = TTestAnalysis()
    # T-test requires exactly two groups
    two_group_data = sample_data[sample_data['group'].isin(['A', 'B'])]
    result = analyzer.analyze(two_group_data, 'group', 'value')
    assert result['test'] == 'T-Test'
    assert 't_statistic' in result
    assert 'p_value' in result
    assert 'significant' in result
    assert len(result['mean_values']) == 2

def test_ttest_analysis_error_with_multiple_groups(sample_data):
    analyzer = TTestAnalysis()
    result = analyzer.analyze(sample_data, 'group', 'value')
    assert 'error' in result

def test_mannwhitney_analysis(sample_data):
    analyzer = MannWhitneyAnalysis()
    # Mann-Whitney U-Test requires exactly two groups
    two_group_data = sample_data[sample_data['group'].isin(['A', 'B'])]
    result = analyzer.analyze(two_group_data, 'group', 'value')
    assert result['test'] == 'Mann-Whitney U-Test'
    assert 'U_statistic' in result
    assert 'p_value' in result
    assert 'significant' in result
    assert len(result['mean_values']) == 2

def test_mannwhitney_analysis_error_with_multiple_groups(sample_data):
    analyzer = MannWhitneyAnalysis()
    result = analyzer.analyze(sample_data, 'group', 'value')
    assert 'error' in result
