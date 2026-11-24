""""
Logic review	
Data validation	
Edge case testing	
Unit testing	
Data leakage check	
Code readability	
Version control	
"""


import pandas as pd
from inspect_data import calculate_mae_and_bias
import pytest
import numpy as np

def test_mae_and_bias():

    prediction = pd.Series([90, 110, 130])
    actual = pd.Series([100, 120, 140])

    mae, bias = calculate_mae_and_bias(
        prediction, actual
    )

    assert mae == 10
    assert bias == -10

def test_empty_input():

    prediction = pd.Series([], dtype=float)
    actual = pd.Series([], dtype=float)

    with pytest.raises(ValueError):
        calculate_mae_and_bias(prediction, actual)

def test_different_lengths():

    prediction = pd.Series([90, 110,])
    actual = pd.Series([100, 120, 140])

    with pytest.raises(ValueError):
        calculate_mae_and_bias(prediction, actual)

def test_infinite_values():

    prediction = pd.Series([90, np.inf, 130])
    actual = pd.Series([100, 120, 140])

    with pytest.raises(ValueError):
        calculate_mae_and_bias(prediction, actual)

def test_single_observation():

    prediction = pd.Series([100])
    actual = pd.Series([120])

    mae, bias = calculate_mae_and_bias(
        prediction, actual
    )

    assert mae == 20
    assert bias == -20