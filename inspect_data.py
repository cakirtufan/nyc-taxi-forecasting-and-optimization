import duckdb

def describe_database(connection, file_path):

    """Display column names, data types, and schema metadata.
    
        Args:
            connection: An open DuckDB connection.
            file_path: Path to a Parquet file.
        
        Returns:
            None, Prints the schema to the console.
    """

    connection.sql(f"""
        DESCRIBE SELECT *
        FROM read_parquet('{file_path}');
        """).show()

def preview_trips(connection, file_path):

    """Display pickup and drop-off timestamps, trip duruation and location IDs.

    Args:
        connection: An open DuckDB connection.
        file_path: Path to a Parquet file.

    Returns:
        None. Prints five trip records to the console.
    """

    connection.sql(f"""
    SELECT      tpep_pickup_datetime,
                tpep_dropoff_datetime,
                tpep_dropoff_datetime - tpep_pickup_datetime AS trip_duration,
                PULocationID,
                DOLocationID

        FROM read_parquet('{file_path}')
        LIMIT 5;
        """).show()

def preview_invalid_trips(connection, file_path):

    """Display invalid trips.

    Args:
        connection: An open DuckDB connection.
        file_path: Path to a Parquet file.

    Returns:
        None. Prints five invalid trip records to the console.
    """

    connection.sql(f"""
    SELECT      tpep_pickup_datetime,
                tpep_dropoff_datetime,
                tpep_dropoff_datetime - tpep_pickup_datetime AS trip_duration,
                PULocationID,
                DOLocationID,


        FROM read_parquet('{file_path}')
        WHERE tpep_dropoff_datetime < tpep_pickup_datetime
        LIMIT 5;
        """).show()


def count_negative_duration_trips(connection, file_path):

    """Return number of the invalid trips.

    Args:
        connection: An open DuckDB connection.
        file_path: Path to a Parquet file.

    Returns:
        Int-> Number of invalid trip 
    """

    return connection.sql(f"""
    SELECT COUNT(*) AS negative_duration_count
        FROM read_parquet('{file_path}')
        WHERE tpep_dropoff_datetime < tpep_pickup_datetime;
        """).fetchall()[0][0]

def total_trips(connection, file_path):

    """Return number of the total trips.

    Args:
        connection: An open DuckDB connection.
        file_path: Path to a Parquet file.

    Returns:
        Int-> Number of total trips
    """

    return connection.sql(f"""
    SELECT COUNT(*) AS total_count
        FROM read_parquet('{file_path}');
        """).fetchall()[0][0]

def calculate_invalid_trip_percentage(invalid_trips, total_trips):

    """ 
        Args:
            invalid_trips (int): Number of the invalid trip
            total_trips (int): Number of the total trips
        
        Returns:
            Float-> Invalid trip percentage 

    """
    percentage = (invalid_trips/total_trips) * 100
    print(f"Negative durations percentage: {percentage:.5f}%")
    return percentage

def missing_timestamp_count(connection, file_path):

    """Return number of the missing timestamp.

    Args:
        connection: An open DuckDB connection.
        file_path: Path to a Parquet file.

    Returns:
        Int, Number of missing timestamp
    """

    return connection.sql(f"""
    SELECT COUNT(*) AS total_count
        FROM read_parquet('{file_path}')
        WHERE tpep_pickup_datetime IS NULL OR tpep_dropoff_datetime IS NULL;
        """).fetchall()[0][0]
    

file_path = 'NYC_Yellow_Taxi/NYC_Yellow_Taxi_2024/yellow_tripdata_2024-01.parquet'
connection = duckdb.connect()
describe_database(connection, file_path)
preview_trips(connection, file_path)
invalid_trips = count_negative_duration_trips(connection, file_path)
number_of_total_trips = total_trips(connection, file_path)

calculate_invalid_trip_percentage(invalid_trips, number_of_total_trips)
missing_timestamp = missing_timestamp_count(connection, file_path)

print(missing_timestamp)