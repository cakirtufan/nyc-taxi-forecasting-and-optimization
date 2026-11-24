import duckdb
import matplotlib.pyplot as plt
from taxi_checks import general_check_trips, check_zero_duration_trips
from weather_checks import weatherdata_interpreter
import pandas as pd
import numpy as np


def display_in_sql(connection, daily_counts, daily_weather):
    
    connection.sql("""
        SELECT
            t.pickup_date,
            t.pickup_count,
            w.mean_temp,
            w.precipitation_mm,
            w.snowfall_cm
        FROM daily_counts AS t
        INNER JOIN daily_weather AS w
            ON t.pickup_date = w.weather_date
        ORDER BY t.pickup_date;
    """).show()

def get_data_frame(year, month):

    """
        Load, merge, and validate daily taxi pickup and weather data
        for a specified month and year.

        The function aggregates daily taxi pickups, joins them with
        weather records, and checks data completeness and consistency.
        If all validation checks pass, it calculates the weekday and
        pickup deviation from the corresponding weekday mean.

        Args:
            year (int): Year of the requested data.
            month (int): Month of the requested data (1–12).

        Returns:
            pandas.DataFrame: Validated daily dataset containing:
                - pickup_date: Date of the recorded pickups.
                - pickup_count: Total number of pickups per day.
                - mean_temp: Daily mean temperature.
                - precipitation_mm: Daily precipitation in millimeters.
                - snowfall_cm: Daily snowfall in centimeters.
                - weekday: Name of the weekday.
                - pickup_deviation: Difference between daily pickups
                and the mean pickup count for that weekday.

        Raises:
            ValueError: If dates do not match, weather values are missing,
                pickup totals are inconsistent, or the number of daily
                records does not match the number of days in the month.
    """

    file_path_weather = 'NYC_Weather_2024_2025/nyc_weather_2024_2025.csv'
    file_path = f'NYC_Yellow_Taxi/NYC_Yellow_Taxi_{year}/yellow_tripdata_{year}-{month:02d}.parquet'

    connection = duckdb.connect()
    connection_weather = duckdb.connect()
    general_check = general_check_trips(connection, file_path)
    weather_interpreter = weatherdata_interpreter(connection_weather, file_path_weather)


    inside_count = general_check.count_month_trips("count", year, month, "inside")

    daily_counts = general_check.count_trip_per_day(year, month)
    daily_weather = weather_interpreter.get_month_data(year, month)

    daily_data = daily_counts.merge(
        daily_weather,
        left_on = "pickup_date",
        right_on = "weather_date",
        how = "left",
        validate = "one_to_one"
    )

    matching_dates = False
    weather_complete = False
    count_match = False
    start_date, end_date = general_check.get_month_boundaries(year, month)
    days_complete = len(daily_data) == (end_date - start_date).days

    if (daily_data["pickup_date"] == daily_data["weather_date"]).all():

        matching_dates = True

    weather_complete = not daily_data[["mean_temp", "precipitation_mm", "snowfall_cm"]].isna().any().any()

    if daily_data["pickup_count"].sum() == inside_count:
        
        count_match = True

    if matching_dates and weather_complete and count_match and days_complete:

        daily_data = daily_data.drop(columns="weather_date")
        daily_data["weekday"] = daily_data["pickup_date"].dt.day_name()
        #daily_data.groupby("weekday")["pickup_count"].agg(["mean", "count"]).sort_values("mean")
        daily_data["pickup_deviation"]= daily_data["pickup_count"] - daily_data.groupby("weekday")["pickup_count"].transform("mean")

        return daily_data

    else:
        raise ValueError(f"Matching Date: {matching_dates}, Weather Complete: {weather_complete}, Count Match: {count_match}, Days Complete {days_complete}")

def calculate_mae_and_bias(prediction, count):

    """
        Evaluate forecast accuracy using MAE and mean forecast bias.

        Args:
            prediction : array-like
                Predicted demand values.

            count : array-like
                Actual observed demand values.

        Returns:
            mae : float
                Mean Absolute Error.

            bias : float
                Mean Forecast Error (prediction - actual).

    """

    if prediction.isna().any() or count.isna().any():

        raise ValueError("Data contains NaN values.")

    if len(prediction) != len(count):

        raise ValueError("Prediction and count not in same length")

    if prediction.empty or count.empty:

        raise ValueError("Prediction or count is empty")

    if not np.isfinite(prediction).all() or not np.isfinite(count).all():

        raise ValueError("Prediction or count has np.inf")

   
    mae = np.mean(np.abs(prediction - count))
    bias = np.mean(prediction - count)

    return mae, bias

def all_history_weekday_mean(train_df, validation_df):

    """
        Predict daily taxi demand using an all-history
        weekday mean baseline.

        Args:
            train_df : pd.DataFrame

            validation_df : pd.DataFrame
            
        Returns:
            pd.DataFrame
                Validation dataset with an additional column:
                'all_history_mean_prediction'.
    """

    earliest_prediction_date = validation_df["pickup_date"].min()

    train_copy = train_df.copy()
    valid_copy = validation_df.copy()

    train_copy = train_copy[train_copy["pickup_date"] < earliest_prediction_date]

    history_weekday_mean = train_copy.groupby("weekday")["pickup_count"].mean()
    valid_copy["all_history_mean_prediction"] = valid_copy["weekday"].map(history_weekday_mean)

    mae, bias = calculate_mae_and_bias(valid_copy["all_history_mean_prediction"], valid_copy["pickup_count"])

    print(f"All History Model MAE: {mae} and BIAS:{bias} in all history training")

    return valid_copy, mae, bias


def windowed_weekday_mean(train_df, validation_df, window, verbose = True):

    """
        Predict demand by windowed weekday mean baseline.

        Args
        
            train_df : pd.DataFrame
                Historical daily pickup counts and weekday information.

            validation_df : pd.DataFrame
                Validation data containing pickup dates, weekdays,
                and actual pickup counts.

            window : int
                Number of historical days used for prediction.
                Supported values: 7, 14, 28.

        Returns:

            pd.DataFrame
                Validation dataset with an additional column:
                'weekday_mean_prediction'.
    """

    if window in [7,14,28]:

        earliest_prediction_date = validation_df["pickup_date"].min()

        window_start = earliest_prediction_date - pd.Timedelta(days = window)
        window_start = window_start

        valid_copy = validation_df.copy()
        train_copy = train_df.copy()

        windowed_train = train_copy[train_copy["pickup_date"] >= window_start]
        windowed_train = windowed_train[windowed_train["pickup_date"] < earliest_prediction_date]


        weekday_mean = windowed_train.groupby("weekday")["pickup_count"].mean()
        valid_copy["weekday_mean_prediction"] = valid_copy["weekday"].map(weekday_mean) 

        mae, bias = calculate_mae_and_bias(valid_copy["weekday_mean_prediction"], valid_copy["pickup_count"])

        if verbose:

            print(f"Rolling window weekday {earliest_prediction_date} Mean Model MAE: {mae} and BIAS:{bias} with a {window} days training window")
        
        else:

            pass

        return valid_copy, mae, bias

    else:

        raise ValueError("Please select training window in [7,14,28]")



def main():

    january_df = get_data_frame(2024,1)
    febuary_df = get_data_frame(2024,2)
    march_df = get_data_frame(2024,3)
    april_df = get_data_frame(2024,4)

    combined_df = pd.concat([january_df, febuary_df, march_df, april_df], ignore_index=True).sort_values(by=["pickup_date"])

    print(combined_df.shape)
    print(combined_df["pickup_date"].nunique())
    print(combined_df["pickup_date"].is_monotonic_increasing)
    print(combined_df["pickup_count"].sum())

    train_df = combined_df[combined_df["pickup_date"] < april_df["pickup_date"].min()]

    validation_df = combined_df[combined_df["pickup_date"] >= april_df["pickup_date"].min()]


    df_all, mae_all, bias_all = all_history_weekday_mean(train_df, validation_df)

    plt.plot(df_all["pickup_date"], df_all["all_history_mean_prediction"], label = "All History")
    plt.plot(df_all["pickup_date"], df_all["pickup_count"], label = "Count")

    df_window, mae_window, bias_window = windowed_weekday_mean(train_df, validation_df, window = 7)

    plt.plot(df_window["pickup_date"], df_window["weekday_mean_prediction"], label = "Fixed 7-day baseline")

    mae_list = []
    bias_list = []
    rolling_prediction = []

    for date in validation_df["pickup_date"]:

        target_date = validation_df[validation_df["pickup_date"] == date]  
        history = combined_df[combined_df["pickup_date"] < date]

        df, mae, bias = windowed_weekday_mean(history, target_date, window=14, verbose=False)
        mae_list.append(mae)
        bias_list.append(bias)
        rolling_prediction.append(df["weekday_mean_prediction"].values[0])

    print(f"Mean mae: {np.mean(mae_list)}")
    print(f"Mean bias: {np.mean(bias_list)}")

    plt.plot(validation_df["pickup_date"], rolling_prediction, label = "Daily rolling 14-day baseline.")
    plt.legend()
    plt.show()
    


if __name__ == "__main__":

    main()