# Project Diary

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
