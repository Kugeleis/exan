import pytest
import pandas as pd
import numpy as np
from src.utils.boxcox_preprocessing import boxcox_transform, apply_boxcox_preprocessing

def test_boxcox_transform():
    data = pd.Series([1, 2, 3, 4, 5])
    transformed_data, lmbda = boxcox_transform(data)
    assert transformed_data is not None
    assert isinstance(lmbda, float)
    assert len(transformed_data) == len(data)

def test_boxcox_transform_with_zero():
    data = pd.Series([0, 1, 2, 3, 4, 5])
    transformed_data, lmbda = boxcox_transform(data)
    assert transformed_data is not None
    assert isinstance(lmbda, float)
    assert len(transformed_data) == len(data)

def test_apply_boxcox_preprocessing_global():
    df = pd.DataFrame({
        'group': ['A', 'A', 'B', 'B'],
        'value': [1, 2, 3, 4]
    })
    transformed_df, lambdas = apply_boxcox_preprocessing(df, 'value', global_transform=True)
    assert 'global' in lambdas
    assert not transformed_df['value'].equals(df['value'])

def test_apply_boxcox_preprocessing_per_group():
    df = pd.DataFrame({
        'group': ['A', 'A', 'B', 'B'],
        'value': [1, 2, 10, 11]
    })
    transformed_df, lambdas = apply_boxcox_preprocessing(df, 'value', group_col='group')
    assert 'A' in lambdas
    assert 'B' in lambdas
    assert not transformed_df['value'].equals(df['value'])

def test_apply_boxcox_preprocessing_raises_error_without_group_col():
    df = pd.DataFrame({
        'group': ['A', 'A', 'B', 'B'],
        'value': [1, 2, 3, 4]
    })
    with pytest.raises(ValueError):
        apply_boxcox_preprocessing(df, 'value')
