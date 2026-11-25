import duckdb
from taxi_checks import general_check_trips, check_zero_duration_trips
from weather_checks import weatherdata_interpreter

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
