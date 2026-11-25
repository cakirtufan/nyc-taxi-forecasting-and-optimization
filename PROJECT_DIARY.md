# Project Diary

## 2026-11-26 - Class extraction and fit/predict comparison

Extracted loading helpers into `data_loader.py` and introduced
`WeekdayMeanForecaster` in `mean_forecaster.py`. Added separate `fit` and
`predict` methods; prediction requires target dates, not target pickup counts.
The class still contains the older baseline and evaluation methods. Its
20-configuration comparison does not yet use fit/predict internally.

`inspect_data.py` now runs a focused experiment: seven-day training window,
28-day forecast horizon, and updates every 14 days. It loads January-April,
fits only on history before each origin, and evaluates available April dates.
The last blocks are truncated; overlapping forecasts retain origin and lead day.

Assistant ran the script successfully in the local Anaconda environment:

| Evaluation | Forecast rows | MAE | Bias |
| --- | ---: | ---: | ---: |
| All issued forecasts | 46 | 8644.326087 | -853.717391 |
| Latest forecast per target day | 30 | 9776.900000 | -1559.966667 |

Assertions confirmed that fit/predict matches the old windowed method at
every origin and target. Latest-per-day predictions also match the previous
seven-day-window, 14-day-horizon/update evaluator. The two metric summaries
answer different questions: all issued forecasts count overlapping targets
multiple times, while latest-per-day evaluates one forecast per April date.
This run is a regression comparison, not comprehensive automated test coverage.

Resume by reviewing this experiment and the distinction between horizon and
update interval. Then consolidate evaluation around fit/predict and simplify
the class responsibilities before SARIMA. Constructor data and horizon remain
from the transitional design; horizon is not used by fit/predict. The learner
requested stopping for the night and committing this checkpoint.

## 2026-11-25 - Automated fixed, rolling, and expanding baseline comparison

### Completed and understood

- Recorded daily rolling 14-day MAE 8,754.583333 and bias +469.85, about
  4.9% lower MAE than daily rolling seven-day forecasts.
- Traced weekday grouping and mapping: a 14-day window uses two previous
  observations of the target weekday, not the mean of all fourteen days.
- Distinguished training window, forecast horizon, and update frequency.
  Advancing forecast origins enables walk-forward evaluation; retaining all
  earlier history gives expanding windows, while trimming gives rolling windows.
- Implemented `walk_forward_evaluation` with selectable history/windowed
  models, half-open target intervals, and updates every `horizon` days.
  History contains actual observations strictly before the forecast origin;
  previous predictions are not fed back as observed history.
- Fixed if/elif/else branching and prediction-column selection. Practiced
  append versus extend and scalar versus iterable values.
- Pooled all predictions and actual values before calculating MAE/bias.
  Averaging unequal-sized block metrics without weighting would be incorrect.
- Implemented `compare_forecasting_baseline`: four fixed, four expanding,
  and twelve rolling configurations returned as a DataFrame, sorted by MAE
  by the caller. Discussed structured experiment metadata and nested loops.

### April 2024 results: all 20 configurations

User-executed results below are preserved to six decimal places as shared.
Bias is prediction minus actual; units are pickups/day. Fixed forecasts use
only pre-April observations. Expanding histories start January 1. A dash
means not applicable, rather than missing experimental data.

| Strategy | Window (days) | Horizon (days) | Update every (days) | MAE | Bias |
| --- | ---: | ---: | ---: | ---: | ---: |
| Fixed history | — | 30 | — | 12992.097436 | -12909.882051 |
| Fixed window | 7 | 30 | — | 7992.166667 | -4802.166667 |
| Fixed window | 14 | 30 | — | 7329.383333 | -4378.716667 |
| Fixed window | 28 | 30 | — | 6408.908333 | -2041.408333 |
| Expanding | — | 1 | 1 | 11723.572644 | -11101.351811 |
| Expanding | — | 7 | 7 | 11723.572644 | -11101.351811 |
| Expanding | — | 14 | 14 | 12092.299889 | -11598.659889 |
| Expanding | — | 28 | 28 | 12800.643137 | -12718.427753 |
| Rolling | 7 | 1 | 1 | 9208.866667 | 674.666667 |
| Rolling | 7 | 7 | 7 | 9208.866667 | 674.666667 |
| Rolling | 7 | 14 | 14 | 9776.900000 | -1559.966667 |
| Rolling | 7 | 28 | 28 | 8457.633333 | -5324.100000 |
| Rolling | 14 | 1 | 1 | 8754.583333 | 469.850000 |
| Rolling | 14 | 7 | 7 | 8754.583333 | 469.850000 |
| Rolling | 14 | 14 | 14 | 9863.916667 | -94.950000 |
| Rolling | 14 | 28 | 28 | 7476.950000 | -4550.116667 |
| Rolling | 28 | 1 | 1 | 7309.966667 | -148.716667 |
| Rolling | 28 | 7 | 7 | 7309.966667 | -148.716667 |
| Rolling | 28 | 14 | 14 | 7239.966667 | -832.366667 |
| Rolling | 28 | 28 | 28 | 6513.483333 | -1909.883333 |

### Interpretation and limits

- Fixed 28-day history had the lowest April MAE among the tested setups.
  More history or more frequent updates did not guarantee better accuracy.
- All-history forecasts substantially underpredicted April. The historical
  weekday averages were below April outcomes on average; the cause is not
  established by this comparison alone.
- Small signed bias does not imply small daily error. Rolling window 14,
  horizon 14 had bias -94.95 but MAE 9,863.916667.
- Daily and weekly schedules matched for every tested history choice. With
  this weekday-only model, no new same-weekday observation arrives between
  the weekly forecast origin and each target day. Whole-week rolling windows
  likewise retain the same relevant weekday observations. This equality
  does not generally hold for other forecasting models.
- Horizon and update interval are coupled. The benchmark compares operating
  schedules, not isolated effects of horizon or update frequency.
- Final blocks are truncated to available April dates. For example, a
  28-day schedule predicts April 1-28, then April 29-30 using refreshed history;
  it differs from the fixed full-month forecast on the final two dates.
- The evaluator assumes complete, unique daily validation rows; positional
  stepping is not a general solution for dates with gaps or duplicates.
  Counts are assumed available by the next forecast origin.
- April is development data after these comparisons. These are configurations
  of the same model family; reserve an unseen later period for final evaluation.
- Assistant reviewed the current implementation and learner-provided results.
  No new automated forecasting tests or assistant rerun were performed in
  this documentation update. Existing metric-test evidence remains dated
  November 24; it does not cover the new evaluator.

### Resume after the break

Baseline automation and the 20-run comparison are complete. Next introduce
SARIMA foundations, then compare an initial model with a baseline using
matching target dates, horizons, and update schedules. Package the first
forecasting workflow afterward, before expanding the model catalog or OR work.
Separating update frequency from horizon remains an optional later refinement.

The learner explicitly reaffirmed: guide in small steps and review their
code; do not supply full implementations unless requested. Continue in Turkish
when requested. Session paused after the comparison and documentation update.

## 2026-11-24 - Roadmap scope check

Reviewed the roadmap for missing engineering and evaluation skills. Added
continuous delivery/release validation separately from CI: versioned build,
deployment, smoke test, and rollback. Added experiment design/A/B testing to
the simulation stage, including metrics, randomization, uncertainty, and
interference between fleet decisions. Historical or simulated comparisons
will not be labelled live A/B experiments.

Kept the near-term milestones unchanged. Explicitly made Kubernetes,
distributed training, feature stores, and APIs optional rather than portfolio
requirements. The priority remains one reproducible, operated batch workflow.

## 2026-11-24 - Shared progress roadmap

Added `PROGRESS.md`, an English roadmap based on the eight agreed areas:
SQL/data engineering, EDA, statistics/forecasting, machine learning,
mathematical optimization, algorithms/solvers, simulation/decisions, and
software engineering/MLOps. Each topic records implementation status and
evidence or remaining work; section outputs distinguish current deliverables
from targets. Partial topics are not counted as complete.

Added SARIMA/ETS explicitly and expanded engineering coverage to include CI,
Docker, scheduled execution, monitoring, and recovery. The README links to
the tracker, and the local learning agreement adopts it for future sessions.
The immediate next step remains the pending 14-day rolling result, followed
by SARIMA and packaging the first forecasting workflow. No code was changed.

## 2026-11-24 - Project direction: engineering beyond experiments

Clarified why this project matters: interviews are already happening, but
recurring feedback concerns production-code experience and the scale of prior
projects. The goal is therefore both forecasting/optimization practice and
evidence that the resulting software can be reproduced, tested, run regularly,
and diagnosed when something fails.

Agreed next steps:

1. Record the pending 14-day rolling-window results.
2. Introduce SARIMA and compare it with a baseline using matching dates,
   horizons, and update schedules.
3. Package the first forecasting pipeline before expanding the model catalog:
   separate preparation, training, prediction, and evaluation; add configuration
   and clear commands.
4. Build engineering practices into that workflow incrementally: dependency
   and artifact tracking, meaningful tests and CI, logging and error handling,
   Docker, scheduled batch execution, and checks for failed runs and forecast
   performance. Document reruns and recovery as these capabilities are added.
5. Add the MILP/OR-Tools decision layer and simulation on top of the forecasting
   workflow, with explicit fleet assumptions and operational comparisons.

These are planned capabilities, not completed work. No deployment, CI, or
monitoring was added in this session. An API is optional; a dependable batch
pipeline fits the initial use case. More models or a larger dataset alone do
not establish production readiness.

Updated the local learning agreement in `TRAINING_GOALS.md` so future sessions
retain this priority. Continue with small learner-written tasks, not a wholesale
rewrite or an infrastructure detour. The pending 14-day run remains the immediate
starting point, followed by SARIMA. Earlier plans to keep expanding baseline
experiments should not delay this sequence.

## 2026-11-24 - Evening: daily rolling forecasts and visual comparison

### Completed

Implemented daily walk-forward forecasting by reusing `windowed_weekday_mean`.
For each April date, the loop selects that single target row and history
strictly before it. The function then selects the most recent training
window. Earlier April observations can enter later forecasts once available;
the target day's count is used only to evaluate the prediction.

The experiment used April rather than the originally planned March period.
The current variable is named `validation_df` and contains April. Since we
are now exploring alternatives on April, it is no longer an untouched test
set for subsequent model selection. Reserve a later unseen period for final
evaluation.

Both baseline functions now return the prediction DataFrame, MAE, and bias.
The windowed function accepts `verbose=False` to suppress per-day output.
The loop collects daily metrics and one prediction per target date. Averaging
the daily metrics gives the overall metrics here because every call evaluates
exactly one observation; unequal-sized batches would require weighting.

### Recorded April results

| Forecast schedule | MAE | Bias |
| --- | ---: | ---: |
| Fixed seven-day window, forecast April once | 7,992.166666666667 | -4,802.166666666667 |
| Daily rolling seven-day window | 9,208.866666666667 | +674.6666666666666 |

The learner ran and shared these outputs. Daily updates reduced the magnitude
of bias but increased MAE by about 15.2%. For the objective of minimizing
absolute daily error, the fixed forecast performed better on this month.
This does not establish that monthly updates generally outperform daily
updates: the horizons and information available differ between schedules.

### Plot and interpretation

Created and shared a four-line April plot: actual pickups, the fixed
January-March weekday average, the fixed seven-day baseline, and the daily
rolling seven-day baseline. The two seven-day forecasts coincide for April
1-7 because both use the same previous-week weekday observations. After that,
the rolling forecast starts using April counts while the fixed one keeps
repeating March 25-31.

The April 11 actual peak appears in the rolling forecast on April 18. This
illustrates the seasonal-naive limitation: it repeats last week's unusual
days without knowing whether they will recur. Discussed averaging two prior
observations per weekday with a 14-day window, or four with 28 days, assuming
complete daily coverage.

### Exact stopping point

The learner stopped for the day after discussing the 14-day comparison.
The saved loop already uses `window=14`, and its plot label says
"Daily rolling 14-day baseline." The fixed comparison remains at seven days.
No 14-day rolling metrics or plot have been shared or verified yet.

Next session: run the current script, record the 14-day rolling MAE and bias,
and compare them with the seven-day rolling results above. Continue in small
steps; do not restart the completed loop or jump into new models. Earlier
entries describe the previous stopping points and are superseded by this one.

Documentation was updated after reviewing the saved code. Forecasting code
was not changed or rerun during this update. Existing docstrings still need
to describe the tuple returns and the verbose argument.

## 2026-11-24 - Follow-up: metric validation and first unit tests

Added `tests/test_metrics.py` and strengthened the metric helper before
continuing with forecasting models. Renamed `caluclate_mae_and_bias` to
`calculate_mae_and_bias` and updated both baseline callers. The helper now
raises `ValueError` for NaN values, unequal lengths, empty inputs, and
non-finite values. The April evaluation variable in `main()` is now `test_df`.

### Tests reviewed and run

| Test | Expected behavior |
| --- | --- |
| Known underprediction example | MAE 10 and bias -10 |
| Empty inputs | Raise ValueError |
| Different lengths | Raise ValueError |
| Infinite prediction | Raise ValueError |
| Single observation: prediction 100, actual 120 | MAE 20 and bias -20 |

The assistant inspected the scripts and ran the five tests successfully with
the local Anaconda Python: **5 passed**. The default shell Python did not have
pytest installed; using the existing Anaconda environment resolved this without
installing anything. The normal repository-root command is
`python -m pytest tests/test_metrics.py -q` in that environment.

These tests verify metric behavior using small synthetic Series, independently
of the raw data files. They do not yet exercise the forecasting functions or
the monthly loader. NaN rejection is implemented but lacks a dedicated test.
The metric helper also assumes matching Series indexes: pandas subtraction
aligns by labels, so equal lengths alone do not guarantee matching observations.
This remains a review finding, not a fix made during the documentation update.
The docstring's broad "array-like" description is wider than the current
Series-based implementation supports.

### Direction and stopping point

Continue building small models before expanding raw-data cleaning. Later,
compare errors before and after specific cleaning rules to measure their
effect. This keeps the learning process connected to forecasting outcomes.
The existing monthly date filter remains in place; other trip-quality flags
have not become automatic exclusions.

Daily walk-forward seasonal naive on March remains the next modeling step
and has not been implemented. The five passing tests establish a starting
point for code verification, not complete coverage. Review existing behavior
in small steps rather than introducing a broad new testing or refactoring task.

## 2026-11-24 - First forecasting baselines and April test

### What we built

Moved from exploratory plots to forecasts evaluated on later dates. The
learner combined January-March into 91 chronological, unique daily rows
with seven columns and 9,554,722 total pickups. March contributed 31 days
and 3,582,605 pickups. The initial split was 60 training days in January-February
and 31 validation days in March.

Implemented three helpers in `inspect_data.py`:

- `calculate_mae_and_bias`: returns mean absolute error and mean signed error
  (the original spelling typo was corrected in the follow-up session).
- `windowed_weekday_mean`: selects the 7, 14, or 28 calendar days immediately
  before the first prediction date, calculates weekday averages, and maps
  them to the evaluation dates.
- `all_history_weekday_mean`: calculates weekday averages from all supplied
  training history before the first prediction date.

Both forecasting functions copy the input DataFrames, return predictions,
and print metrics. They fit once per call and keep the seven weekday values
fixed throughout the evaluation period. The windowed function was renamed
from `rolling_window_weekday_mean` to avoid implying daily updates that are
not implemented. Its printed label still uses the older wording.

### March validation results

All forecasts were made using history before March 1, with no actual March
counts used to update predictions during the month.

| Training history | MAE | Bias |
| --- | ---: | ---: |
| Last 7 days | 9,335.29 | -6,869.61 |
| Last 14 days | 11,316.69 | -11,276.05 |
| Last 28 days | 12,063.92 | -12,063.92 |
| February only (29 days) | 12,338.38 | -12,338.38 |
| January-February | 15,889.18 | -15,889.18 |

The last seven days were February 23-29. Because each weekday appeared once,
their weekday means reproduced the seasonal-naive forecast exactly: repeat
the last observed week throughout March. Older observations increased
underprediction in this experiment; this does not establish a universal
advantage for short training windows.

Inspected daily errors and grouped both signed and absolute errors by weekday:

| Weekday | Seasonal-naive MAE | Bias |
| --- | ---: | ---: |
| Monday | 8,915.75 | -8,915.75 |
| Tuesday | 6,317.00 | 6,317.00 |
| Wednesday | 10,734.75 | -10,734.75 |
| Thursday | 4,669.75 | -784.25 |
| Friday | 18,094.40 | -18,094.40 |
| Saturday | 10,041.80 | -7,970.20 |
| Sunday | 5,232.80 | -5,232.80 |

Every March Tuesday was overpredicted; Fridays were consistently
underpredicted. Thursday's small bias concealed errors in both directions.
These are diagnostics from one month, not established long-term patterns.

### April test

Selected the seven-day window using March, then loaded April and supplied
January-March as training history. The function selected March 25-31 and
forecast all of April without updates. The learner reported:

- MAE: 7,992.166666666667 pickups/day.
- Bias: -4,802.166666666667 pickups/day.

Both overprediction and underprediction occurred, with net underprediction.
The lower error than March is encouraging, but different months have different
forecasting difficulty. April was held out for this selection and has now
been inspected. Further development needs a later unseen final test period.
The assistant reviewed the code and recorded learner-run outputs; it did not
rerun the forecasting experiments.

### Concepts clarified

Training-window length, observation weights, forecast horizon, forecast
refresh frequency, and retraining frequency are separate decisions. A model
with lag inputs can accept new observations without changing its fitted
parameters. Our weekday-mean baseline only changes its predictions when its
weekday means are recalculated.

MAE measures absolute error; bias measures signed error. Absolute bias cannot
exceed MAE. Equality with negative bias means no overpredictions; a smaller
absolute bias means errors occur in both directions. Correcting March's
predictions using March's measured bias would not be a valid forecast made
before March began.

Data leakage became clear through a historical-testing example: the full
DataFrame contains March 8's count, but a simulated forecast made on March 1
must not see it. A later forecast can use it once available. Known calendar
features and weather forecasts issued in advance are allowed; future actual
counts and future observed weather are not. Comparing predictions with actual
outcomes afterward is valid evaluation. The learner answered all five
availability/leakage quiz questions correctly after clarifying answer order.

### Python practice

- Used `groupby` to estimate weekday means and `map` to assign predictions.
- Used the minimum target date and `pd.Timedelta` to define training windows;
  retained pandas timestamps for comparisons.
- Learned why scalar `and` cannot combine pandas Boolean Series, and why
  `&` needs separately parenthesized comparisons.
- Chose two consecutive row filters as a readable alternative. Combining
  two already filtered DataFrames with `&` is not Boolean row filtering.
- Preserved original DataFrames with copies and added function docstrings.

### Next session - exact stopping point

Begin implementing **daily walk-forward seasonal naive on March**, predicting
one day at a time using the actual count from seven days earlier. This has
been discussed but not coded. For March 8, March 1's count becomes usable
because the forecast is now made during March, not before the entire month.
Assume historical counts are available by each forecast time and state that
assumption explicitly.

Start by returning the evaluation period to March and preparing chronologically
ordered, unique, complete daily history. A seven-row lag corresponds to seven
calendar days only when dates are complete. Compare results with the monthly
fixed-origin baseline while acknowledging the different horizon and update
schedule. Keep April's already observed results separate from development;
choose a later untouched period for eventual final testing.

The current `main()` still runs the April seven-day test. Some comments
describe the earlier March split and need updating; the evaluation variable
was renamed to `test_df` in the follow-up. Weather-source documentation remains open.

Continue with small steps: the learner writes and runs code, the assistant
reviews and explains. Use readable English documentation, useful language
corrections, and Turkish explanations when requested.

## 2026-11-21 — Project reset

### Goal
Learn demand forecasting and operations research using NYC Yellow Taxi data.

### Progress
- Renamed the project folder.
- Started removing the previous courier assignment project.
- Updated .gitignore to exclude local data and training goals.

### Working agreement
- Use English and correct useful grammar mistakes.
- I write and run the code; the assistant guides me step by step.
- Ask me to explain and defend my technical choices.

### Next step
- Verify the cleanup with git status --short.
- Inspect the taxi dataset before choosing our first analysis.

## 2026-11-21 — SQL exploration and initial data-quality checks

### Completed
- Renamed the local folder and GitHub repository for the NYC taxi project.
- Removed the previous courier assignment scripts and dependencies.
- Updated README.md and .gitignore; kept raw taxi data out of Git.
- Installed DuckDB and created inspect_data.py.
- Installed the VS Code Python and Pylance extensions.
- Inspected the January 2024 Parquet schema using SQL.
- Previewed pickup/drop-off timestamps and location IDs.
- Calculated trip durations by subtracting timestamps.
- Filtered and counted negative-duration trips.
- Wrote a check for missing pickup or drop-off timestamps.

### Findings
- Total records: 2,964,624.
- Negative-duration records: 56.
- Negative-duration percentage: approximately 0.00189%.
- Missing-timestamp query written; result not yet recorded.
- No data-cleaning rules applied yet.

### Lessons learned
- Allocation depends on demand, existing taxis, and service capacity.
- Passenger trip duration excludes travel to reach the customer.
- DESCRIBE reports schema; SELECT retrieves records.
- WHERE filters records; COUNT(*) counts matching records.
- IS NULL checks missing values; OR includes either condition.
- LIMIT restricts output but does not establish chronological order.
- SQL file-path strings need quotes.
- .show() displays results; .fetchall()[0][0] extracts a scalar count.
- This installed DuckDB version does not support fetchone() on relations.
- A small number of detected errors does not prove the dataset is clean.

### Next session
- Run and record the missing-timestamp count.
- Continue checking zero durations and timestamp ranges.
- Review findings before deciding on cleaning rules.

### Working agreement
- Continue in English, with useful grammar corrections.
- User writes and runs the code; assistant guides step by step.


## 2026-11-21 — Evening: deeper data-quality checks

### Findings — January 2024 file
- Total records: 2,964,624.
- Negative durations: 56 (~0.00189%).
- Missing pickup or drop-off timestamps: 0.
- Zero durations: 814 (~0.02746%).

Among the 814 zero-duration records:
- Positive recorded distance: 56.
- Different pickup and drop-off zone IDs: 630.
- Positive total_amount: 760.
- Zero total_amount: 50.
- Negative total_amount: 4.
- Missing total_amount: 0, inferred from the counts above.

These checks overlap; their counts must not be added together.

Pickup timestamp range:
- Earliest: 2002-12-31 22:59:39.
- Latest: 2024-02-01 00:01:15.

The file contains pickup timestamps outside January 2024.
Their count has not yet been calculated.

### Interpretation
- Positive amounts do not prove payment collection or a valid trip.
- Different zone IDs do not prove actual movement.
- Negative amounts might represent corrections or reversals;
  this explanation remains unconfirmed.
- Zero-duration records are unsuitable as reliable travel-duration
  labels, but their usefulness for pickup forecasting needs
  separate assessment.
- Preserve raw records and compare demand counts with and without
  flagged records before finalizing cleaning rules.
- No cleaning filters have been applied to the source data.

### Python and SQL practice
- Combined conditions using AND and OR.
- Used IS NULL, equality, inequality, MIN, and MAX.
- Extracted scalar counts using .fetchall()[0][0].
- Practiced organizing related checks into a class.
- Reviewed __init__, self, indentation, and method arguments.
- Use == for string value comparisons, not is.
- Distinguished printing results from returning values.

### Future extension discussed
Compare forecast-driven optimization with learned heuristics
after establishing reliable data, simulation, and baselines.

### Next step
Count pickups outside January 2024:
- Earlier than 2024-01-01 00:00:00, OR
- At or after 2024-02-01 00:00:00.

Then inspect those records before choosing a date-filtering policy.
## 2026-11-22 - Date filtering and first daily pickup time series

### Completed and verified
- Counted 18 pickups outside January 2024: 10 on December 31, 2023;
  3 on February 1, 2024; and 5 with dates in 2002 or 2009.
- Two displayed old-date rows matched in the selected columns; exact
  duplication across all columns has not been checked.
- Counted 2,964,606 pickups inside January. Inside plus outside counts
  reconcile to the original 2,964,624 records.
- Used the half-open pickup interval: >= January 1 AND < February 1.
- Agreed that a January pickup belongs to January even if drop-off is
  in February. Boundary-adjacent trips are not automatically invalid.
- Aggregated pickups by CAST(tpep_pickup_datetime AS DATE), using
  COUNT(*), GROUP BY, and chronological ORDER BY.
- Converted the aggregated DuckDB result to pandas using .df().
- User verified 31 daily rows and a pickup_count sum of 2,964,606.
- User reported producing the first daily pickup plot with matplotlib;
  the plot itself was not shared for inspection.

### Lessons and interpretation
- Outside an interval uses OR; inside the interval uses AND.
- .show() displays results and returns None; .fetchall()[0][0] extracts
  a scalar, while .df() returns a pandas DataFrame.
- DuckDB can aggregate millions of raw rows before transferring just
  the 31 daily summary rows into pandas.
- DuckDB's abbreviated display does not indicate missing dates;
  .show(max_rows=31) displays all January daily rows.
- Daily counts suggest a possible weekly pattern; more data is needed
  to assess its consistency.
- This is an exploratory date-filtered series, not a fully cleaned
  dataset. Other quality flags and duplicate policy remain unresolved.

### Next session
- User proposed adding simple daily NYC weather data for January 2024.
- Consider mean temperature, precipitation, and snowfall; select a
  source and location representation, then join daily weather by date.
- No weather data has been retrieved yet.
- Observed historical weather is useful for exploration. Forecasting
  must use weather information available at the prediction time to
  avoid leakage.
- Local AI autocomplete setup (Continue/Ollama) was deferred.

### Working agreement
- User writes and runs learning code; assistant guides step by step.
- Continue primarily in English, with useful language corrections.

## 2026-11-23 - Weather integration, exploratory analysis, and monthly loader

### Completed

- Read the local 2024-2025 weather CSV with DuckDB, skipping three metadata
  lines. Inspected daily mean temperature, precipitation, and snowfall.
- Added weather inspection, coverage, NULL, range, hottest-date, and monthly
  extraction methods. Monthly range checks now use the requested date interval;
  the standalone NULL check still reads the full CSV. The loader checks missing
  weather again on the actual joined monthly DataFrame.
- Generalized month boundaries, including December rollover and leap years.
  Corrected an accidental recursive call by separating the boundary helper
  from the weather retrieval method.
- Generalized taxi file paths with year and zero-padded month. Learned that
  changing a date filter does not change the source file automatically.
- Joined daily taxi counts to weather using pandas LEFT JOIN with
  validate="one_to_one". Also practiced SQL INNER JOIN over pandas DataFrames.
  DuckDB reads accessible DataFrame variable names; interpolating their printed
  contents into an f-string is not a valid table reference.
- January inputs had shapes (31, 2) and (31, 4); the pandas join had (31, 6)
  with zero missing values. The SQL join displayed 31 rows and five columns.
- February joined output had shape (29, 6), pickup sum 3,007,511, and matching
  pickup/weather dates on every row, as reported by the learner.
- Built get_data_frame(year, month) in inspect_data.py. It returns date,
  pickup count, three weather variables, weekday, and pickup_deviation after
  validation, or raises an error. The final version was reviewed, not executed
  by the assistant; no final three-month run output was shared.

### Recorded quality-check results

| Check | January 2024 | February 2024 |
| --- | ---: | ---: |
| Pickups inside month | 2,964,606 | 3,007,511 |
| Pickups outside month | 18 | 15 |
| Zero-duration records in source file | 814 | 796 |
| Zero-duration records with different zone IDs | 630 | 647 |
| Daily rows | 31 | 29 |

Zero-duration categories overlap. They remain quality flags, not automatic
exclusions from the pickup series. February inside plus outside counts total
3,007,526; this sum is not an independent raw-row-count validation.

Full-CSV weather checks found zero NULL values in all three variables.
Ranges were -11.7 to 34.1 degrees Celsius, 0 to 65.6 mm precipitation,
and 0 to 18.13 cm snowfall. The hottest dates clustered in June/July 2025;
their seasonal placement is not independent measurement verification.

After correcting the range-check scope, February ranges were -2.6 to 13.3
degrees Celsius, 0 to 26.1 mm precipitation, and 0 to 18.13 cm snowfall.
The unchanged snowfall maximum can legitimately occur in February.

### January weekday and weather exploration

| Weekday | Mean daily pickups | Number of days |
| --- | ---: | ---: |
| Monday | 81,655.40 | 5 |
| Sunday | 84,825.50 | 4 |
| Tuesday | 92,732.40 | 5 |
| Wednesday | 99,006.40 | 5 |
| Friday | 102,147.00 | 4 |
| Saturday | 105,289.50 | 4 |
| Thursday | 107,146.75 | 4 |

- Compared means rather than weekday totals because groups contain unequal
  numbers of days. Eight of the ten lowest-count days were Sundays or Mondays.
- Used groupby, agg(["mean", "count"]), and sorting after aggregation.
- Used transform("mean") to align each weekday mean with the original rows.
  pickup_deviation = pickup_count minus that month's weekday mean.
  January 7's deviation was -17,282.5 pickups.
- Inspected normalized time-series overlays, deviation over time, and
  precipitation-versus-deviation scatter plots coloured by day of month.
  Added labels, a zero reference line, and a colour bar.
- Early January was mostly below its weekday baseline; January 22-31 was
  above it. This remaining time pattern is not explained by weekday alone.
- Precipitation versus pickup_deviation: Pearson -0.023742; Spearman -0.100938.
  Conclusion: little linear or monotonic association in this January sample.
  No significance test or causal analysis was performed.
- Do not discard precipitation on this basis alone. Its predictive value
  needs comparison on later unseen dates, with weather inputs available at
  forecast time. Historical observed weather alone does not meet that condition.

### Validation and Python lessons

- LEFT JOIN preserves taxi days with missing weather; INNER JOIN drops them.
- One-to-one validation prevents duplicate date keys from multiplying rows.
- Use independent checks, not if/elif, when every condition must be evaluated.
- Series comparisons require .all() or .any() to produce a single Boolean.
  A DataFrame NULL check needs .any().any() to cover rows and columns.
- Compare the joined pickup sum with inside_count, not inside plus outside.
- Compare row count with (end_date - start_date).days. Together with the
  existing month filters and unique date keys, this checks monthly coverage.
- Printing results is not validation; failed checks must block the return.
- Dividing by monthly maxima is only a plotting aid: Celsius ratios are not
  physically meaningful, and an all-zero snowfall month creates a zero divisor.
- Monthly weekday deviations use the same month's outcomes. They are not
  out-of-sample errors and must not be used as contemporaneous forecast inputs.

### Next session - exact stopping point

1. Run the final get_data_frame function for January, February, and March 2024.
   Calls are already present in main(); final execution results remain unconfirmed.
2. Confirm successful returns with 31, 29, and 31 rows; record March totals.
3. Concatenate into a chronological 91-day dataset and verify date coverage
   and preservation of monthly totals. No combined dataset has been confirmed yet.
4. Keep monthly deviations explicitly exploratory; plan chronological training
   and evaluation before computing forecasting features or fitted baselines.
5. Document the weather source/extraction settings and check daily time alignment.

### Working agreement

- The learner writes and runs learning code. Give goals and small hints first;
  do not jump ahead with unsolicited code or full implementations.
- Read current project files when context is uncertain instead of guessing or
  asking the learner to repeat completed work.
- Session ended at the learner's request; resume at the stopping point above.
