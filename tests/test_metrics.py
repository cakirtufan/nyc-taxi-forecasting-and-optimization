import pandas as pd
from mean_forecaster import WeekdayMeanForecaster
import pytest
import numpy as np

forecaster = WeekdayMeanForecaster(
        observation_df=None, validation_df=None, window=None, horizon=None
        )

def test_mae_and_bias():

    prediction = pd.Series([90, 110, 130])
    actual = pd.Series([100, 120, 140])


    
    mae, bias = forecaster.calculate_mae_and_bias(prediction, actual)

    assert mae == 10
    assert bias == -10

def test_empty_input():

    prediction = pd.Series([], dtype=float)
    actual = pd.Series([], dtype=float)

    with pytest.raises(ValueError):
        forecaster.calculate_mae_and_bias(prediction, actual)

def test_different_lengths():

    prediction = pd.Series([90, 110,])
    actual = pd.Series([100, 120, 140])

    with pytest.raises(ValueError):
        forecaster.calculate_mae_and_bias(prediction, actual)

def test_infinite_values():

    prediction = pd.Series([90, np.inf, 130])
    actual = pd.Series([100, 120, 140])

    with pytest.raises(ValueError):
        forecaster.calculate_mae_and_bias(prediction, actual)

def test_single_observation():

    prediction = pd.Series([100])
    actual = pd.Series([120])

    mae, bias = forecaster.calculate_mae_and_bias(prediction, actual)

    assert mae == 20
    assert bias == -20
