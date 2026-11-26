# NYC Taxi Demand Forecasting and Assignment Lab

A hands-on learning project exploring how taxi trip forecasts can support
fleet assignment and relocation decisions.

The project uses NYC Yellow Taxi trip records from 2024 and 2025 to develop
skills in SQL, Python, time-series forecasting, and operations research.

## Project status

See [Project Progress and Learning Roadmap](PROGRESS.md) for the eight work
areas, implemented topics, remaining tasks, and next milestones.

Daily pickup aggregation, weather integration, and weekday-mean forecasting
baselines are implemented. Chronological experiments used March for initial
window selection and April for development. The baseline grid compares 20
fixed, rolling, and expanding schedules; a second grid adds 184 schedules
whose update interval is shorter than their forecast horizon. The walk-forward
evaluator selects the latest issued forecast for each target day before
computing MAE and bias. Fleet optimization is not yet implemented.

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

Introduce SARIMA foundations, then compare a first model with a weekday-mean
baseline on matching target dates and forecast/update schedules. Reserve a
later unseen period for final evaluation; April has become development data.

### Forecasting snapshot

The weekday-mean model learns one average per weekday from either all
available history or the latest 7, 14, or 28 days. The seven-day version
equals a weekly seasonal-naive forecast when daily observations are complete.
MAE measures average absolute error in recorded pickups; signed bias is
prediction minus actual. Neither metric directly measures missed customers.

| April 2024 setup | MAE (pickups/day) | Bias (pickups/day) |
| --- | ---: | ---: |
| Fixed 28-day window, one full-month forecast | 6,408.91 | -2,041.41 |
| Rolling 28-day window, daily updates | 7,309.97 | -148.72 |
| Expanding history, daily updates | 11,723.57 | -11,101.35 |

The fixed 28-day setup had the lowest April MAE among the 204 tested
configurations. These are schedules of the same weekday-mean model family,
not 204 different models. A lower bias does not necessarily mean a lower MAE.
For overlapping forecast horizons, the benchmark scores each target day once
using its latest issued forecast. The evaluator currently returns that selected
daily table; it does not return the superseded long-horizon predictions.
The [Project Diary](PROJECT_DIARY.md) records the full 20-run baseline table,
a summary of the 184 additional schedules, and interpretation.

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

### Engineering roadmap

The next milestone is an operable forecasting pipeline, not just a larger
collection of models. Following the completed baseline comparison and an
initial SARIMA experiment, development will focus on:

- Separate, configurable commands for data preparation, training, prediction,
  and evaluation.
- Reproducible environments and recorded data provenance, model artifacts,
  experiment settings, and metrics.
- Meaningful unit and integration tests, CI, input validation, logging,
  and explicit failure handling.
- Docker packaging and scheduled batch forecasts, with documented reruns
  and recovery procedures.
- Checks for run failures, stale or invalid inputs, and forecast performance
  after actual counts become available.

These capabilities are planned; the current implementation remains an
experimental script with metric unit tests. An API will be added only if
needed. Fleet optimization and simulation will build on this pipeline.

## Forecasting approaches: a learning reference

There is no fixed number of approaches: choices about how we use the data
can be combined with different forecasting models. The prediction horizon
should reflect the operational decision; the training window is a modeling
choice evaluated with chronological validation.

### Questions to answer before choosing a model

Start with the operational need, then choose and validate the modeling setup:

1. **Forecast horizon:** How far ahead do we need predictions? For daily
   data, one step means one day; multiple steps might mean the next seven days.
2. **Forecast refresh frequency:** How often do we need fresh predictions:
   daily, weekly, or monthly?
3. **Training window and observation weights:** How much history should
   influence the forecast? Should observations have equal weights, or should
   recent observations receive more weight?
4. **Model:** How do we turn that information into predictions?

For example: "We allocate taxis each morning, so we need a forecast for the
coming day, refreshed every morning. We will compare 28-day and 56-day
training windows using chronological validation."

Refreshing predictions and retraining the model are separate decisions.
A fitted model can receive new inputs daily while being retrained weekly.
Specify both schedules, and use only inputs available when each forecast
is issued.

### Forecasting setup

| Setup choice | Approach | What it means |
| --- | --- | --- |
| Training window | Fixed historical window | Keep using January-February without adding new observations. |
| Training window | Expanding window | Add newly observed days while keeping all earlier data. |
| Training window | Rolling window | Always use the most recent fixed period, such as 28 days. |
| Observation weighting | More weight on recent data | Retain older observations but reduce their influence. |
| Forecast horizon | One step ahead | Predict tomorrow's daily pickups. |
| Forecast horizon | Multiple steps ahead | Predict each of the next seven or 31 days. |
| Forecast refresh frequency | Daily, weekly, monthly | Decide how often to issue fresh predictions using available inputs. |
| Retraining frequency | Daily, weekly, monthly | Decide how often to refit the model using newly available observations. |

For example, we can combine a rolling 28-day training window with daily
updates and forecasts for the next seven days. Training-window length,
forecast horizon, and update frequency are separate choices.

### Forecasting models

| Forecasting approach | Basic idea | Main limitation |
| --- | --- | --- |
| Weekday average | Use the training-period average for the target weekday. | Fixed weekday values do not follow changing levels automatically. |
| Naive | Predict the latest observed value. | Ignores the weekly pattern. |
| Seasonal naive | Use the most recent observed value for the same weekday; repeat the last observed week for longer horizons. | An unusual day can distort the forecast. |
| Moving average | Predict using the average of recent days. | Smooths over weekday differences and lags behind changes. |
| Exponential smoothing / ETS | Update level, and optionally trend and seasonality, giving more influence to recent observations. | Sudden changes and external effects can remain difficult. |
| SARIMA / SARIMAX | Model time dependence and seasonal patterns, optionally with external variables. | Requires careful model specification. |
| Regression: linear, Ridge, etc. | Learn relationships with weekday, trend, past pickups, and other features. | Performance depends on features and model assumptions. |
| Tree models: boosting, random forest | Learn nonlinear relationships between forecasting features and pickups. | Standard trees struggle to extrapolate trends beyond training values. |
| Neural forecasting models | Learn temporal relationships using neural networks. | Usually require more data and tuning than our small starting dataset. |

A longer training window does not automatically teach a model trends or
seasonality. A weekday-average model still learns just seven fixed values.
Shorter windows can respond to changing levels, but fewer observations make
the estimates more sensitive to unusual days.

### Validation and comparison

Our first experiment uses January-February to predict all March days from
the end of February, without updating during March. A second version uses
February alone. Both use the same March validation dates.

Walk-forward validation repeats forecasting at several dates, always using
only information available at each forecast date. Training windows and models
should be compared on the same target dates, horizons, and update schedule.
For example, a forecast issued at the end of February cannot use actual
March pickups as lag inputs; daily forecasts issued during March can use
earlier March observations once those observations become available.

The fixed-origin seasonal-naive and weekday-average comparisons are complete,
including an April test of the window selected on March. The implemented
`windowed_weekday_mean` selects one window before the first target date;
it does not advance the window during the call. `all_history_weekday_mean`
uses all supplied history before that date. Rolling and expanding evaluation
require advancing the forecast date and updating the available history.
`walk_forward_evaluation` advances through target blocks and passes earlier
observations to either baseline function. The windowed model trims that
history; the all-history model retains it, giving expanding evaluation.
April was initially held out for the March-selected baseline but is now
part of development as additional update schedules and windows are explored.

Leakage is about information availability at forecast time. A historical
DataFrame already contains future outcomes relative to a simulated forecast
date. A forecast issued on March 1 must not use March 8's actual count; a
forecast issued on March 14 may use it once available. Target-day weekdays
are known in advance, whereas target-day observed weather is not. An archived
weather forecast issued before the prediction is a valid potential input.
Using actual outcomes afterward to calculate MAE and bias is evaluation,
not leakage.

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
- `data_loader.py` - validated monthly taxi/weather loading.
- `mean_forecaster.py` - weekday-mean baselines, fit/predict, walk-forward
  evaluation, MAE/bias, and comparison grids.
- `inspect_data.py` - April experiment runner and learning exercises.
- `taxi_checks.py` - trip-quality checks, month boundaries, and daily aggregation.
- `weather_checks.py` - CSV inspection, weather checks, and monthly extraction.
- `tests/test_metrics.py` - synthetic unit tests for MAE and forecast bias.
- `NYC_Yellow_Taxi/` — local trip records and data dictionary.
- `NYC_Weather_2024_2025/` - local daily weather CSV.

The monthly loader checks one-to-one date keys, matching dates, complete
weather values, preservation of the inside-month pickup total, and the
expected day count. It raises an error if validation fails. These checks
do not establish that every raw trip or weather measurement is valid.

## Tests

Run from the repository root in the Python environment containing the project
dependencies and `pytest`:

```sh
python -m pytest tests/test_metrics.py -q
```

The five tests check a known MAE/bias result, empty inputs, unequal lengths,
an infinite prediction, and a single observation. All five passed on
November 24, 2026 in the local Anaconda environment. They use synthetic
pandas Series and do not load the taxi or weather files. Importing the
project module still requires its dependencies: pandas, NumPy, DuckDB,
and matplotlib.

`calculate_mae_and_bias` rejects missing values, empty inputs, unequal lengths,
and non-finite values. Its current implementation expects pandas Series with
matching indexes. Missing-value rejection does not yet have a dedicated test,
and index alignment is not explicitly validated. The suite currently tests
metrics, not the forecasting functions, date boundaries, or the monthly loader.

## Code review approach

The current baseline and metric code was reviewed against the following
seven areas. The review combined manual inspection, checks against known
results, and automated tests.

| Review area | What was done |
| --- | --- |
| Logic review | Traced date filtering, weekday grouping, and prediction mapping. Confirmed the MAE and signed-bias formulas and checked that a complete seven-day weekday mean reproduces seasonal naive. |
| Data validation | Checked date uniqueness, chronological order, monthly coverage, join consistency, and pickup totals. Added metric checks that reject missing, empty, unequal-length, or non-finite inputs. |
| Edge case testing | Used small synthetic Series to check empty inputs, different lengths, an infinite prediction, and a single observation. Invalid cases must raise an error; a single valid observation must return the expected metrics. |
| Unit testing | Added five pytest tests with explicit expected results or expected exceptions. All five passed in the local Anaconda environment. |
| Data leakage check | Reviewed the training cutoff so only dates before the first prediction date contribute to weekday means. Kept March for window selection and used April for the subsequent test. Identified monthly pickup deviations and future observed weather as unsuitable forecast-time inputs. |
| Code readability | Extracted reusable metric and baseline functions, added docstrings, used two readable date filters, and renamed the windowed function to reflect its actual behavior. Renamed the April evaluation dataset to `test_df`. |
| Version control | Used Git status and diffs to inspect changes and recorded the baselines, metric tests, and documentation in a descriptive commit. Local taxi records remain excluded from version control. |

The review also recorded remaining gaps: Series index alignment is not
validated, NaN rejection has no dedicated test, and automated coverage does
not yet include the forecasting functions or loader. Some comments, printed
labels, and the metric input docstring still need to be aligned with the code.

## Learning approach

Build the workflow step by step, explain assumptions, prevent data leakage,
and defend technical choices with evidence.
The learner writes and runs the code; the assistant explains the purpose,
offers hints, and reviews attempts. Work one step at a time without providing
unsolicited implementations. Sessions are primarily in English, with Turkish
clarifications when useful.

Establish small forecasting baselines first, then measure how specific data
cleaning choices change their errors. Raw-trip quality flags remain visible;
additional exclusions will be evaluated rather than applied without comparison.

---

*Code written by a human. Docs polished by AI. Bugs are a team effort.*
