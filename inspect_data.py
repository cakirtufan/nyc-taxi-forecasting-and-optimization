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

window = 14
horizon = 14
update_every = 14

forecaster = WeekdayMeanForecaster(
    df=combined_df,
    validation_df=validation_df,
    window=window,
    horizon=horizon
)

baseline = forecaster.compare_forecasting_baseline()
additional_update_schedules = forecaster.compare_additional_update_schedules()     