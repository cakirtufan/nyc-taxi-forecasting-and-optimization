from datetime import date

class weatherdata_interpreter:

    """Inspect the weather of NYC in given dataset.
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


    def inspect_data(self):

        """ Display the first five weather records, skipping the CSV's three metadata lines.

            Returns:
                None, display table

        """

        self.connection.sql(f"""
            SELECT *
            FROM read_csv('{self.file_path}', skip=3, header=True)
            LIMIT 5;
            """).show()

    def check_data_coverage(self):

        """ Display the data coverage with respect to total_count, distinct_date_count, earliest_date and latest_date

            Returns:
                None, display table

        """

        self.connection.sql(f"""
            SELECT  COUNT(*) AS total_count,
                    COUNT(DISTINCT(time)) AS distinct_date_count,
                    MIN(time) AS earliest_date,
                    MAX(time) AS latest_date
                    
            FROM read_csv('{self.file_path}', skip=3, header=True)
            ;
            """).show()

    def check_null(self):

        
        """ Display the number of NULL in temp, precipitation and snowfall

            Returns:
                None, display table

        """

        self.connection.sql(f"""
            SELECT              SUM(CASE
            WHEN "temperature_2m_mean (°C)" IS NULL THEN 1
            ELSE 0
            END) AS null_temp_count,
            SUM(CASE
            WHEN "precipitation_sum (mm)" IS NULL THEN 1
            ELSE 0
            END) AS null_precipitation_count,
            SUM(CASE
            WHEN "snowfall_sum (cm)" IS NULL THEN 1
            ELSE 0
            END) AS null_snowfall_coun

            FROM read_csv('{self.file_path}', skip=3, header=True)
            ;
            """).show()       

    def check_value_ranges(self, year, month):

        """ Display the number of min and max of the temp, precipitation and snowfall

            Returns:
                None, display table

        """

        start_date, end_date = self.get_month_boundaries(year, month)

        self.connection.sql(f"""
            SELECT  MIN("temperature_2m_mean (°C)") as min_temp,
                    MAX("temperature_2m_mean (°C)") as max_temp,
                    MIN("precipitation_sum (mm)") as min_precipitation,
                    MAX("precipitation_sum (mm)") as max_precipitation,
                    MIN("snowfall_sum (cm)") as min_snowfall,
                    MAX("snowfall_sum (cm)") as max_snowfall

            FROM read_csv('{self.file_path}', skip=3, header=True)
            WHERE time >= '{start_date}' AND time < '{end_date}' 
            ;
            """).show()

    def check_hottest_dates(self):

        """ Disply the five dates with the highest daily mean temperatures.

            Returns:
                None, display table

        """

        self.connection.sql(f"""
        SELECT  time,
                "temperature_2m_mean (°C)" as mean_temp
                FROM read_csv('{self.file_path}', skip=3, header=True)   
                ORDER BY "temperature_2m_mean (°C)" DESC
                LIMIT 5;
        """).show()

    def get_month_data(self, year, month):

        """ Return January 2024 weather records as a pandas DataFrame, ordered by date. 

            Returns:
                DataFrame

        """

        start_date, end_date = self.get_month_boundaries(year, month)


        return self.connection.sql(f"""
        SELECT  time AS weather_date,
                "temperature_2m_mean (°C)" AS mean_temp,
                "precipitation_sum (mm)" AS precipitation_mm,
                "snowfall_sum (cm)" AS snowfall_cm
        FROM read_csv('{self.file_path}', skip=3, header=True)
        WHERE time >= '{start_date}' AND time < '{end_date}'
        ORDER BY time; 
        """).df()