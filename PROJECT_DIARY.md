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
