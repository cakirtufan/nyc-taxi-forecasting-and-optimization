import data_loader
from mean_forecaster import WeekdayMeanForecaster
import pandas as pd

january_df = data_loader.get_data_frame(2024,1)
febuary_df = data_loader.get_data_frame(2024,2)
march_df = data_loader.get_data_frame(2024,3)
april_df = data_loader.get_data_frame(2024,4)

combined_df = pd.concat([january_df, febuary_df, march_df, april_df], ignore_index=True).sort_values(by=["pickup_date"])

train_df = combined_df[combined_df["pickup_date"] < april_df["pickup_date"].min()]

validation_df = combined_df[combined_df["pickup_date"] >= april_df["pickup_date"].min()]

window = 7
horizon = 28
update_every = 14

forecaster = WeekdayMeanForecaster(
    df=combined_df,
    validation_df=validation_df,
    window=window,
    horizon=horizon
)

forecast_blocks = []

for origin in validation_df["pickup_date"].iloc[::update_every]:

    history = combined_df[combined_df["pickup_date"] < origin]
    targets = validation_df[
        (validation_df["pickup_date"] >= origin)
        & (validation_df["pickup_date"] < origin + pd.Timedelta(days=horizon))
    ]

    forecaster.fit(history)
    predictions = forecaster.predict(targets[["pickup_date"]])

    # Compare both implementations using exactly the same origin and targets.
    reference, _, _ = forecaster.windowed_weekday_mean(
        history, targets, window=window
    )
    pd.testing.assert_series_equal(
        predictions,
        reference["weekday_mean_prediction"],
        check_names=False
    )

    block = targets[["pickup_date", "pickup_count"]].copy()
    block["forecast_origin"] = origin
    block["lead_day"] = (block["pickup_date"] - origin).dt.days + 1
    block["prediction"] = predictions
    block["reference_prediction"] = reference["weekday_mean_prediction"]
    forecast_blocks.append(block)

forecasts = pd.concat(forecast_blocks, ignore_index=True)

mae, bias = forecaster.calculate_mae_and_bias(
    forecasts["prediction"], forecasts["pickup_count"]
)
reference_mae, reference_bias = forecaster.calculate_mae_and_bias(
    forecasts["reference_prediction"], forecasts["pickup_count"]
)

print(f"Window={window}, horizon={horizon}, update_every={update_every}")
print(f"Forecast rows: {len(forecasts)}; unique target days: {forecasts['pickup_date'].nunique()}")
print(f"All issued forecasts: MAE={mae}, bias={bias}")
print(f"Same-schedule reference: MAE={reference_mae}, bias={reference_bias}")

# Latest available forecast per day: each April day receives equal weight.
latest = (
    forecasts.sort_values(["pickup_date", "forecast_origin"])
    .drop_duplicates("pickup_date", keep="last")
    .reset_index(drop=True)
)
latest_mae, latest_bias = forecaster.calculate_mae_and_bias(
    latest["prediction"], latest["pickup_count"]
)

# The original horizon=14 evaluator also refreshes every fourteen days.
previous_predictions, previous_mae, previous_bias = forecaster.walk_forward_evaluation(
    history=combined_df,
    target=validation_df,
    window=window,
    horizon=update_every,
    model="windowed"
)
pd.testing.assert_series_equal(
    latest["prediction"],
    pd.Series(previous_predictions, dtype=float),
    check_names=False
)
print(f"Latest forecast per day: MAE={latest_mae}, bias={latest_bias}")
print(f"Previous 14-day horizon/update: MAE={previous_mae}, bias={previous_bias}")
print("Prediction comparisons passed.")
