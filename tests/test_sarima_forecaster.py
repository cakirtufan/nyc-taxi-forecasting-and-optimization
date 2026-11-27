import pandas as pd
from sarima_forecaster import SARIMAForecaster
import pytest
import numpy as np

def make_synthetic_data_without_pickup_count():

    history = pd.DataFrame({
            "pickup_date": pd.date_range("2024-01-01", periods=14, freq="D")

        })

    return history

def make_synthetic_data_without_pickup_date():

    history = pd.DataFrame({
        "pickup_count": [10, 20, 30, 40, 50, 60, 70,
                        30, 60, 30, 40, 50, 60, 70]
    })

    return history

def make_synthetic_data_empty_pickup_date():

    history = pd.DataFrame({
        "pickup_date": [],
        "pickup_count": 10,
    })

    return history


def make_synthetic_data_empty_pickup_count():

    history = pd.DataFrame({
        "pickup_date": "2024-01-01",
        "pickup_count": [],
    })

    return history

def make_synthetic_data_with_NaN():

    history = pd.DataFrame({
        "pickup_date": pd.date_range("2024-01-01", periods=14, freq="D"),
        "pickup_count": [10, 20, 30, None, 50, 60, 70,
                        30, 60, 30, 40, 50, 60, 70],
    })

    return history

def make_synthetic_data_with_inf():

    history = pd.DataFrame({
        "pickup_date": pd.date_range("2024-01-01", periods=14, freq="D"),
        "pickup_count": [10, 20, 30, np.inf, 50, 60, 70,
                        30, 60, 30, 40, 50, 60, 70],
    })

    return history

def make_synthetic_data_repeating_pickup_date():

    history = pd.DataFrame({
        "pickup_date": pd.to_datetime(["2024-01-01", "2024-01-01"]),
        "pickup_count": [1,1],
    })

    return history

def make_synthetic_data_non_date_format():

    history = pd.DataFrame({
        "pickup_date": [1, "2024-01-01"],
        "pickup_count": [1,1],
    })

    return history

def make_synthetic_data_non_number_format():

    history = pd.DataFrame({
        "pickup_date": pd.date_range("2024-01-01", periods=2, freq="D"),
        "pickup_count": ["1",1],
    })

    return history



@pytest.mark.parametrize(
    ("make_data_function", "expected_message"),
    [
        (make_synthetic_data_empty_pickup_count, "Pickup date or count empty"),
        (make_synthetic_data_empty_pickup_date, "Pickup date or count empty"),
        (make_synthetic_data_with_inf, "Pick up count has non-finite values"),
        (make_synthetic_data_with_NaN, "Data contains NaN values."),
        (make_synthetic_data_without_pickup_count, "Pickup count not in DataFrame"),
        (make_synthetic_data_without_pickup_date, "Pickup date not in DataFrame"),
        (make_synthetic_data_repeating_pickup_date, "Repeating pickup date")
    ],
    )

def test_fit_history(make_data_function, expected_message):
    forecaster = SARIMAForecaster(None, None)
    history_df = make_data_function()

    with pytest.raises(ValueError, match=expected_message):
        forecaster.fit(history_df)

@pytest.mark.parametrize(
    ("make_data_function", "expected_message"),
    [
        (make_synthetic_data_non_date_format, "Pickup date column must be of datetime type."),
        (make_synthetic_data_non_number_format, "Pickup count column must be of numeric type.")
    ],
    )

def test_fit_history_type(make_data_function, expected_message):

    forecaster = SARIMAForecaster(None, None)
    history_df = make_data_function()

    with pytest.raises(TypeError, match=expected_message):
        forecaster.fit(history_df)