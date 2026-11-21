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