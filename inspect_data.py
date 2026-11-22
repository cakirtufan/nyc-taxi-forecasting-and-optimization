import duckdb
import matplotlib.pyplot as plt

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
   
def count_zero_duration_trips(connection, file_path):

    """Return number of the zero duration trips.

    Args:
        connection: An open DuckDB connection.
        file_path: Path to a Parquet file.

    Returns:
        Int-> Number of zero duration trips 
    """
    return connection.sql(f"""
        SELECT COUNT(*)
        FROM read_parquet('{file_path}') 
        WHERE tpep_pickup_datetime = tpep_dropoff_datetime;
        """).fetchall()[0][0]

def check_min_max_datetime(connection, file_path):

    """Return table of min max timestamp in given dataset.

    Args:
        connection: An open DuckDB connection.
        file_path: Path to a Parquet file.

    Returns:
        None, table of min and max timestamp in given dataset 
    """

    return connection.sql(f"""
        SELECT  MIN(tpep_pickup_datetime) AS earliest_pickup,
                MAX(tpep_pickup_datetime) AS latest_pickup
        FROM read_parquet('{file_path}')   
    """).show()

def count_outside_month_trips(connection, file_path, mode):

    """ Find the data in dataset where timestamp outside the month
    Args:
        connection: An open DuckDB connection.
        file_path: Path to a Parquet file.
        mode: 'table' or 'count'

    Returns:
        None, display the data if mode is table
        int, the number of the trip outside boundary
    
    """

    if mode == "count":
        count = connection.sql(f"""
                SELECT COUNT(*) AS count_outside_month_trips
                FROM read_parquet('{file_path}')
                WHERE tpep_pickup_datetime < '2024-01-01 00:00:00' OR
                tpep_pickup_datetime >= '2024-02-01 00:00:00';
                """).fetchall()[0][0]

        print(f"Number of outside month trips: {count}")
        return count

    elif mode == "table":

        connection.sql(f"""
            SELECT  tpep_pickup_datetime,
                    tpep_dropoff_datetime,
                    PULocationID,
                    DOLocationID,
                    trip_distance

            FROM read_parquet('{file_path}')
            WHERE tpep_pickup_datetime < '2024-01-01 00:00:00' OR
            tpep_pickup_datetime >= '2024-02-01 00:00:00'
            ORDER BY tpep_pickup_datetime DESC;
            """).show()

    else:

        raise ValueError("mode must be 'count' or 'table'") 


def count_trip_per_day(connection, file_path):

    """ Counts the number of the trip per day in given month data
    Args:
        connection: An open DuckDB connection.
        file_path: Path to a Parquet file.


    Returns:
        DataFrame 
    """

    return connection.sql(f"""
        SELECT  CAST(tpep_pickup_datetime AS DATE) AS pickup_date,
                COUNT(*) as pickup_count
        FROM read_parquet('{file_path}')
        WHERE tpep_pickup_datetime >= '2024-01-01 00:00:00' AND
        tpep_pickup_datetime < '2024-02-01 00:00:00'
        GROUP BY pickup_date
        ORDER BY pickup_date;
        """).df()


def count_inside_month_trips(connection, file_path, mode):

    """ Find the data in dataset where timestamp inside the month
    Args:
        connection: An open DuckDB connection.
        file_path: Path to a Parquet file.
        mode: 'table' or 'count'

    Returns:
        None, display the data if mode is table
        int, the number of the trip inside boundary
    
    """


    if mode == "count":
        count = connection.sql(f"""
                SELECT COUNT(*) AS count_inside_month_trips
                FROM read_parquet('{file_path}')
                WHERE tpep_pickup_datetime >= '2024-01-01 00:00:00' AND
                tpep_pickup_datetime < '2024-02-01 00:00:00';
                """).fetchall()[0][0]

        print(f"Number of inside month trips: {count}")
        return count

    elif mode == "table":

        connection.sql(f"""
            SELECT  tpep_pickup_datetime,
                    tpep_dropoff_datetime,
                    PULocationID,
                    DOLocationID,
                    trip_distance

            FROM read_parquet('{file_path}')
            WHERE tpep_pickup_datetime >= '2024-01-01 00:00:00' AND
            tpep_pickup_datetime < '2024-02-01 00:00:00'
            ORDER BY tpep_pickup_datetime DESC;
            """).show()

    else:

        raise ValueError("mode must be 'count' or 'table'")                                


class check_zero_duration_trips:

    """Inspect trips with identical pickup and drop-off timestamps.
        Args:
            connection: An open DuckDB connection.
            file_path: Path to a Parquet file.
    """

    def __init__(self, connection, file_path):

        self.connection = connection
        self.file_path = file_path
        

    def check_distance_and_total_amount(self, mode, type):

        """
            Args:
                mode: select the mode in ['count', 'table', ]
                type: select the type in ['non_zero_distance', 'non_zero_total_amount']
            Returns: 
                Int, if mode is count then number of zero duration in type.
                None, Table of table of pickup_time, dropoff_time, trip_distance, fare_amount, PULocationID, DOLocationID, tip_amount, total_amount
        
        
        """

        if mode == "count":

            if type is 'non_zero_distance':

                count = self.connection.sql(f"""
                    SELECT COUNT(*) AS non_zero_distance 

                    FROM read_parquet('{self.file_path}')
                    WHERE tpep_pickup_datetime = tpep_dropoff_datetime AND
                        trip_distance > 0
                    ;

                    """).fetchall()[0][0]
                
                print(f"Number of zero duration trips with non zero distance is: {count}")
                

                return count
            
            elif type == 'non_zero_total_amount':
                        
                count = self.connection.sql(f"""
                    SELECT  COUNT(*) AS non_zero_total_amount_count

                    FROM read_parquet('{self.file_path}')
                    WHERE tpep_pickup_datetime = tpep_dropoff_datetime AND
                        total_amount > 0
                    ;

                    """).fetchall()[0][0]

                print(f"Number of zero duration trips with non zero amount is: {count}")

                return count

            else:
                raise ValueError("type must be 'non_zero_distance' or 'non_zero_total_amount'")
            

        elif mode == "table":

            if type == 'non_zero_distance':

                return self.connection.sql(f"""
                    SELECT  tpep_pickup_datetime,
                            tpep_dropoff_datetime,
                            trip_distance, 
                            fare_amount, 
                            PULocationID, 
                            DOLocationID

                    FROM read_parquet('{self.file_path}')
                    WHERE tpep_pickup_datetime = tpep_dropoff_datetime AND
                        trip_distance > 0
                    ;

                    """).show()

            elif type == 'non_zero_total_amount':
            
                            return self.connection.sql(f"""
                                SELECT  trip_distance, 
                                        fare_amount, 
                                        tip_amount, 
                                        total_amount
            
                                FROM read_parquet('{self.file_path}')
                                WHERE tpep_pickup_datetime = tpep_dropoff_datetime AND
                                    total_amount > 0
                                ;
            
                                """).show()

            else:
                raise ValueError("type must be 'non_zero_distance' or 'non_zero_total_amount'")

        else:
            raise ValueError("mode must be 'count' or 'table'")

    def pick_up_and_drop_off(self,mode):

        if mode == "count":

            count = self.connection.sql(f"""
                SELECT COUNT(*) AS count 

                FROM read_parquet('{self.file_path}')
                WHERE PULocationID != DOLocationID AND 
                tpep_pickup_datetime = tpep_dropoff_datetime

                ;

                """).fetchall()[0][0]
            
            print(f"Zero-duration trips with different zone IDs: {count}")

        elif mode == 'table':

                return self.connection.sql(f"""
                    SELECT  trip_distance, 
                            PULocationID,
                            DOLocationID

                    FROM read_parquet('{self.file_path}')
                    WHERE PULocationID != DOLocationID AND 
                    tpep_pickup_datetime = tpep_dropoff_datetime
                    ;

                    """).show()

        else:
            raise ValueError("mode must be 'count' or 'table'")


file_path = 'NYC_Yellow_Taxi/NYC_Yellow_Taxi_2024/yellow_tripdata_2024-01.parquet'
connection = duckdb.connect()
describe_database(connection, file_path)
preview_trips(connection, file_path)
invalid_trips = count_negative_duration_trips(connection, file_path)
number_of_total_trips = total_trips(connection, file_path)

calculate_invalid_trip_percentage(invalid_trips, number_of_total_trips)
missing_timestamp = missing_timestamp_count(connection, file_path)
zero_duration_trips = count_zero_duration_trips(connection, file_path)
print(number_of_total_trips)

print(f"Trips with missing timestamps: {missing_timestamp}")
print(f"Zero trips: {zero_duration_trips}, Zero duration trips percentage: {(zero_duration_trips/number_of_total_trips)*100}")
function = check_zero_duration_trips(connection, file_path)
function.check_distance_and_total_amount("count", "non_zero_distance")
function.pick_up_and_drop_off("count")
check_min_max_datetime(connection, file_path)
count_outside_month_trips(connection, file_path, "count")
count_inside_month_trips(connection, file_path, "count")
daily_counts = count_trip_per_day(connection, file_path)

print(len(daily_counts))
print(daily_counts["pickup_count"].sum())

plt.plot(daily_counts["pickup_date"], daily_counts["pickup_count"])
plt.xlabel("Pickup date")
plt.ylabel("Recorded pickups")
plt.title("Daily NYC Yellow Taxi pickups — January 2024")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()