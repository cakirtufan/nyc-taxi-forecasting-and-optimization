# NYC Taxi Demand Forecasting and Assignment Lab

A hands-on learning project exploring how taxi trip forecasts can support
fleet assignment and relocation decisions.

The project uses NYC Yellow Taxi trip records from 2024 and 2025 to develop
skills in SQL, Python, time-series forecasting, and operations research.

## Project status

Daily pickup aggregation and weather integration are implemented. January
and February 2024 results have been inspected; a reusable monthly loader
now checks the join before returning a pandas DataFrame. January weather
and weekday patterns have been explored. Forecasting models and optimization
workflows have not yet been implemented.

### Current findings

| Month | Pickups inside month | Records outside month | Daily rows |
| --- | ---: | ---: | ---: |
| January 2024 | 2,964,606 | 18 | 31 |
| February 2024 | 3,007,511 | 15 | 29 |

January Mondays and Sundays had lower average pickups than other weekdays.
Precipitation had little association with deviations from the January
weekday averages: Pearson r = -0.023742 and Spearman rho = -0.100938.
These are exploratory results from 31 days, not evidence that precipitation
has no predictive value or a causal effect.

### Next step

Run the final monthly loader for January, February, and March 2024 and
confirm 31, 29, and 31 rows. Combine them into a chronological 91-day
dataset before proceeding to forecasting baselines and temporal validation.

## Objectives

- Explore and validate real taxi trip data using SQL and Python.
- Forecast recorded pickups by location and time.
- Compare forecasting models using chronological validation.
- Formulate assignment and relocation problems with Google OR-Tools.
- Evaluate operational decisions in a simulated fleet environment.

## Planned workflow

1. **Data inspection:** understand the schema, missing values, and anomalies.
2. **Demand aggregation:** count pickups by taxi zone and time interval.
3. **Forecasting:** establish simple baselines before testing more complex models.
4. **Optimization:** define decision variables, objectives, and constraints.
5. **Simulation:** compare forecast-driven decisions with simple heuristics.

## Data

Source: [NYC TLC Trip Record Data](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page)

Monthly Parquet files are stored locally under `NYC_Yellow_Taxi/`
and excluded from version control.

Daily weather is stored locally in
`NYC_Weather_2024_2025/nyc_weather_2024_2025.csv`. It contains mean
temperature (degrees Celsius), precipitation (mm), and snowfall (cm).
The reader skips three metadata lines. The CSV metadata identifies
America/New_York and coordinates approximately 40.808434, -74.0199;
the download source and extraction settings still need documenting.

Trips are selected by pickup time using a half-open monthly interval:
first day inclusive, first day of the next month exclusive. Other trip
quality flags are inspected but not automatically removed from pickup counts.

Historical weather is used for exploration. Operational forecasts must use
weather information available at prediction time. `pickup_deviation` uses
the same month's observed weekday means: it is an exploratory statistic,
not a forecast error or a valid contemporaneous forecasting input.

Recorded trips measure observed pickups, not all passenger demand.
Fleet availability and individual vehicle states will require explicit
simulation assumptions.

## Project files

- `README.md` — project overview.
- `PROJECT_DIARY.md` — progress, lessons learned, and next steps.
- `inspect_data.py` - monthly loading, validated pandas LEFT JOIN, and SQL join example.
- `taxi_checks.py` - trip-quality checks, month boundaries, and daily aggregation.
- `weather_checks.py` - CSV inspection, weather checks, and monthly extraction.
- `NYC_Yellow_Taxi/` — local trip records and data dictionary.
- `NYC_Weather_2024_2025/` - local daily weather CSV.

The monthly loader checks one-to-one date keys, matching dates, complete
weather values, preservation of the inside-month pickup total, and the
expected day count. It raises an error if validation fails. These checks
do not establish that every raw trip or weather measurement is valid.

## Learning approach

Build the workflow step by step, explain assumptions, prevent data leakage,
and defend technical choices with evidence.
The learner writes and runs the code; the assistant explains the purpose,
offers hints, and reviews attempts. Work one step at a time without providing
unsolicited implementations. Sessions are primarily in English, with Turkish
clarifications when useful.
