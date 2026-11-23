import duckdb
import matplotlib.pyplot as plt
from taxi_checks import general_check_trips
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

def main():

    file_path = 'NYC_Yellow_Taxi/NYC_Yellow_Taxi_2024/yellow_tripdata_2024-01.parquet'
    connection = duckdb.connect()
    general_check = general_check_trips(connection, file_path)

    general_check.count_outside_month_trips("count", 2024, 1)
    general_check.count_inside_month_trips("count", 2024, 1)
    daily_counts = general_check.count_trip_per_day(2024, 1)

    connection_weather = duckdb.connect()
    file_path_weather = 'NYC_Weather_2024_2025/nyc_weather_2024_2025.csv'

    weather_interpreter = weatherdata_interpreter(connection_weather, file_path_weather)
    daily_weather = weather_interpreter.get_month_data(2024,1)

    daily_data = daily_counts.merge(
        daily_weather,
        left_on = "pickup_date",
        right_on = "weather_date",
        how = "left",
        validate = "one_to_one"
    )
    daily_data = daily_data.drop(columns="weather_date")
    daily_data["weekday"] = daily_data["pickup_date"].dt.day_name()

    daily_data.groupby("weekday")["pickup_count"].agg(["mean", "count"]).sort_values("mean")

    daily_data["pickup_deviation"]= daily_data["pickup_count"] - daily_data.groupby("weekday")["pickup_count"].transform("mean")

    plt.scatter(daily_data["precipitation_mm"], daily_data["pickup_deviation"], c=daily_data["pickup_date"].dt.day)
    plt.xlabel("precipitation in mm")
    plt.ylabel("pickup deviation")
    plt.hlines(0, daily_data["precipitation_mm"].min(), daily_data["precipitation_mm"].max())
    plt.colorbar(label="Day of January")
    plt.show()
    

if __name__ == "__main__":

    main()