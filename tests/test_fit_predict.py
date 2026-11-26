import pandas as pd
from mean_forecaster import WeekdayMeanForecaster
import pytest

def make_synthetic_data():
    """Seven training days and two future dates for fit/predict tests."""
    history = pd.DataFrame({
        "pickup_date": pd.date_range("2024-01-01", periods=14, freq="D"),
        "pickup_count": [10, 20, 30, 40, 50, 60, 70,
                        30, 60, 30, 40, 50, 60, 70],
    })
    history["weekday"] = history["pickup_date"].dt.day_name()

    target = pd.DataFrame({
        "pickup_date": pd.to_datetime(["2024-01-15", "2024-01-16"]),
    })
    return history, target

def make_comparison_data():

    dates = pd.date_range("2024-01-01", periods=58, freq="D")
    counts = [10,20,30,40,50,60,70] * 8 + [10,20]

    combined = pd.DataFrame({"pickup_date": dates, "pickup_count": counts})

    combined["weekday"] = combined["pickup_date"].dt.day_name()

    history = combined.iloc[:28].copy()
    target = combined.iloc[28:].copy()

    return history, target, combined

def test_fit_empty():

    forecaster = WeekdayMeanForecaster(
        df=None, validation_df=None, window=None, horizon=None
        )

    history = pd.Series([], dtype=float)

    with pytest.raises(ValueError):
        forecaster.fit(history=history)

def test_fit_invalid_window():

    forecaster = WeekdayMeanForecaster(
        df=None, validation_df=None, window=3, horizon=None
        )

    history, _ = make_synthetic_data()
    with pytest.raises(ValueError):
        forecaster.fit(history=history)

def test_seven_day_window():

    train, target = make_synthetic_data()

    forecaster = WeekdayMeanForecaster(
        df=None, validation_df=None, window=7, horizon=None
        )

    fit = forecaster.fit(train)
    prediction = fit.predict(target)

    assert prediction.tolist() == [30,60]


def test_train_mean():

    train, target = make_synthetic_data()

    forecaster = WeekdayMeanForecaster(
        df=None, validation_df=None, window=None, horizon=None
        )

    fit = forecaster.fit(train)
    prediction = fit.predict(target)

    assert prediction.tolist() == [20,40]

def test_compare_forecasting_baseline_has_20_configurations():

    _, target, combined = make_comparison_data()

    forecaster = WeekdayMeanForecaster(
            df=combined, validation_df=target, window=None, horizon=None
            )

    df = forecaster.compare_forecasting_baseline()
    
    assert len(df) == 20
    assert df["strategy"].value_counts().to_dict() == {"rolling": 12, "fixed": 4, "expanding": 4}

def test_additional_update_schedules_has_184_configurations():


    _, target, combined = make_comparison_data()

    forecaster = WeekdayMeanForecaster(
            df=combined, validation_df=target, window=None, horizon=None
            )

    df = forecaster.compare_additional_update_schedules()

    assert len(df) == 184
    assert (df["update_every"] < df["horizon"]).all()
