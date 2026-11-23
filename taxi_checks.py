from datetime import date

class general_check_trips:

    """General inspection of trips such as:

            describe_database,
            preview_trips,
            preview_invalid_trips (zero duration trips),
            count_negative_duration_trips,
            total_trips,
            missing_timestamp_count,
            count_zero_duration_trips,
            check_min_max_datetime,
            count_outside_month_trips,
            count_trip_per_day,
            count_inside_month_trips,


        Args:
            connection: An open DuckDB connection.
            file_path: Path to a Parquet file.
    """

    def __init__(self, connection, file_path):

        self.connection = connection
        self.file_path = file_path


    def get_month_boundaries(self, year, month):

        start_date = date(year, month, 1)

        if month == 12:
            end_date = date(year + 1, 1, 1)
        else:
            end_date = date(year, month + 1, 1)

        return start_date, end_date

    def describe_database(self):

        """Display column names, data types, and schema metadata.
        
            Args:
                connection: An open DuckDB connection.
                file_path: Path to a Parquet file.
            
            Returns:
                None, Prints the schema to the console.
        """

        self.connection.sql(f"""
            DESCRIBE SELECT *
            FROM read_parquet('{self.file_path}');
            """).show()

    def preview_trips(self):

        """Display pickup and drop-off timestamps, trip duruation and location IDs.

        Args:
            connection: An open DuckDB connection.
            file_path: Path to a Parquet file.

        Returns:
            None. Prints five trip records to the console.
        """

        self.connection.sql(f"""
        SELECT      tpep_pickup_datetime,
                    tpep_dropoff_datetime,
                    tpep_dropoff_datetime - tpep_pickup_datetime AS trip_duration,
                    PULocationID,
                    DOLocationID

            FROM read_parquet('{self.file_path}')
            LIMIT 5;
            """).show()

    def preview_invalid_trips(self):

        """Display invalid trips.

        Args:
            connection: An open DuckDB connection.
            file_path: Path to a Parquet file.

        Returns:
            None. Prints five invalid trip records to the console.
        """

        self.connection.sql(f"""
        SELECT      tpep_pickup_datetime,
                    tpep_dropoff_datetime,
                    tpep_dropoff_datetime - tpep_pickup_datetime AS trip_duration,
                    PULocationID,
                    DOLocationID,


            FROM read_parquet('{self.file_path}')
            WHERE tpep_dropoff_datetime < tpep_pickup_datetime
            LIMIT 5;
            """).show()


    def count_negative_duration_trips(self):

        """Return number of the invalid trips.

        Args:
            connection: An open DuckDB connection.
            file_path: Path to a Parquet file.

        Returns:
            Int-> Number of invalid trip 
        """

        return self.connection.sql(f"""
        SELECT COUNT(*) AS negative_duration_count
            FROM read_parquet('{self.file_path}')
            WHERE tpep_dropoff_datetime < tpep_pickup_datetime;
            """).fetchall()[0][0]

    def total_trips(self):

        """Return number of the total trips.

        Args:
            connection: An open DuckDB connection.
            file_path: Path to a Parquet file.

        Returns:
            Int-> Number of total trips
        """

        return self.connection.sql(f"""
        SELECT COUNT(*) AS total_count
            FROM read_parquet('{self.file_path}');
            """).fetchall()[0][0]


    def missing_timestamp_count(self):

        """Return number of the missing timestamp.

        Args:
            connection: An open DuckDB connection.
            file_path: Path to a Parquet file.

        Returns:
            Int, Number of missing timestamp
        """

        return self.connection.sql(f"""
        SELECT COUNT(*) AS total_count
            FROM read_parquet('{self.file_path}')
            WHERE tpep_pickup_datetime IS NULL OR tpep_dropoff_datetime IS NULL;
            """).fetchall()[0][0]
    
    def count_zero_duration_trips(self):

        """Return number of the zero duration trips.

        Args:
            connection: An open DuckDB connection.
            file_path: Path to a Parquet file.

        Returns:
            Int-> Number of zero duration trips 
        """

        count = self.connection.sql(f"""
            SELECT COUNT(*)
            FROM read_parquet('{self.file_path}') 
            WHERE tpep_pickup_datetime = tpep_dropoff_datetime;
            """).fetchall()[0][0]

        print(f"Number of the zero duration trips {count}")

        return count
    def check_min_max_datetime(self):

        """Return table of min max timestamp in given dataset.

        Args:
            connection: An open DuckDB connection.
            file_path: Path to a Parquet file.

        Returns:
            None, table of min and max timestamp in given dataset 
        """

        return self.connection.sql(f"""
            SELECT  MIN(tpep_pickup_datetime) AS earliest_pickup,
                    MAX(tpep_pickup_datetime) AS latest_pickup
            FROM read_parquet('{self.file_path}')   
        """).show()

    def count_month_trips(self, mode, year, month, boundary):

        """ Find the data in dataset where timestamp given boundary
        Args:
            connection: An open DuckDB connection.
            file_path: Path to a Parquet file.
            mode: 'table' or 'count'
            boundary: "inside", "outside"

        Returns:
            None, display the data if mode is table
            int, the number of the trip outside boundary
        
        """

        start_date, end_date = self.get_month_boundaries(year, month)

        def count_data(condition):
            count_data = self.connection.sql(f"""
                SELECT COUNT(*) AS count_outside_month_trips
                FROM read_parquet('{self.file_path}')
                {condition}
                ;
                """).fetchall()[0][0]
            
            return count_data

        def table_data(condition):
            table_data = self.connection.sql(f"""
            SELECT  tpep_pickup_datetime,
                    tpep_dropoff_datetime,
                    PULocationID,
                    DOLocationID,
                    trip_distance

            FROM read_parquet('{self.file_path}')
            {condition}
            ORDER BY tpep_pickup_datetime DESC;
            """).show()

        outside_condition = f"WHERE tpep_pickup_datetime < '{start_date} 00:00:00' OR tpep_pickup_datetime >= '{end_date} 00:00:00'"
        inside_condition = f"WHERE tpep_pickup_datetime >= '{start_date} 00:00:00' AND tpep_pickup_datetime < '{end_date} 00:00:00'"    

        if boundary == "inside":
            condition = inside_condition
        elif boundary == "outside":
            condition = outside_condition
        else:
            raise ValueError("Boundary must be 'inside' or 'outside'")
            

        if mode == "count":

            count = count_data(condition)

            print(f"Number of {boundary} month trips: {count}")
            return count

        elif mode == "table":

            table_data(condition)

        else:

            raise ValueError("mode must be 'count' or 'table'") 

 
    def count_trip_per_day(self, year, month):

        """ Counts the number of the trip per day in given month data
        Args:
            connection: An open DuckDB connection.
            file_path: Path to a Parquet file.


        Returns:
            DataFrame 
        """
        start_date, end_date = self.get_month_boundaries(year, month)

        return self.connection.sql(f"""
            SELECT  CAST(tpep_pickup_datetime AS DATE) AS pickup_date,
                    COUNT(*) as pickup_count
            FROM read_parquet('{self.file_path}')
            WHERE tpep_pickup_datetime >= '{start_date} 00:00:00' AND
            tpep_pickup_datetime < '{end_date} 00:00:00'
            GROUP BY pickup_date
            ORDER BY pickup_date;
            """).df()


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

            if type == 'non_zero_distance':

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

            return count

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


