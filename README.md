# NYC Taxi Demand Forecasting and Assignment Lab

A hands-on learning project exploring how taxi trip forecasts can support
fleet assignment and relocation decisions.

The project uses NYC Yellow Taxi trip records from 2024 and 2025 to develop
skills in SQL, Python, time-series forecasting, and operations research.

## Project status

Initial setup and data exploration. Forecasting models and optimization
workflows have not yet been implemented.

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

Recorded trips measure observed pickups, not all passenger demand.
Fleet availability and individual vehicle states will require explicit
simulation assumptions.

## Project files

- `README.md` — project overview.
- `PROJECT_DIARY.md` — progress, lessons learned, and next steps.
- `NYC_Yellow_Taxi/` — local trip records and data dictionary.

## Learning approach

Build the workflow step by step, explain assumptions, prevent data leakage,
and defend technical choices with evidence.