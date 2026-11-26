# Project Progress and Learning Roadmap

Last reviewed: November 27, 2026.

This roadmap tracks the NYC taxi project from data preparation to forecasting,
fleet decisions, and an operable software workflow. Status describes work
demonstrated in this repository, not mastery of an entire field or experience
from other projects.

- **Implemented:** the stated topic has been applied and its output inspected.
- **In progress:** some parts have been applied; remaining work is listed.
- **Planned:** not yet implemented in this project.

Automated test coverage is recorded separately from implementation. Results
and experiment history are documented in [README](README.md) and
[Project Diary](PROJECT_DIARY.md). Update this tracker after meaningful
milestones rather than marking a topic complete merely because it was discussed.

## 1. SQL & Data Engineering

| Topic | Status | Evidence / remaining work |
| --- | --- | --- |
| DuckDB and Parquet | Implemented | Read monthly taxi files, query trip records, and aggregate daily pickups before converting to pandas. |
| JOIN, GROUP BY, CTE | In progress | SQL grouping and joins, plus validated pandas joins, are used. CTE practice remains. |
| SQL window functions | Planned | Distinct from the rolling training windows used in forecasting. |
| Data quality and cleaning | In progress | Inspected timestamp anomalies, missing values, and zero durations; applied monthly date boundaries and join checks. Additional cleaning rules need measured comparisons. |
| Modular data processing | In progress | Reusable taxi/weather helpers and a monthly loader exist. Separate pipeline stages and configuration remain. |

**Target output:** a validated hourly demand table by taxi zone, with documented
cleaning rules. **Current output:** validated daily citywide counts joined to weather.

## 2. Exploratory Data Analysis

| Topic | Status | Evidence / remaining work |
| --- | --- | --- |
| Distributions and outlier analysis | In progress | Inspected ranges, low-count days, and large weekday deviations. Broader distribution analysis remains. |
| Time-series decomposition | Planned | Separate level/trend, seasonal structure, and remainder. |
| Seasonality and trend | In progress | Explored weekday patterns and changing demand levels. Formal decomposition and longer-period analysis remain. |
| Autocorrelation | Planned | Examine ACF/PACF and connect them to modelling choices. |
| Hypothesis formation and testing | In progress | Explored precipitation versus weekday deviations using Pearson/Spearman correlations. Formal hypothesis testing remains. |

**Target output:** an analytical account of demand behavior and testable
modelling hypotheses. **Current output:** plots and documented exploratory findings.

## 3. Statistics & Forecasting

| Topic | Status | Evidence / remaining work |
| --- | --- | --- |
| MAE, RMSE, WAPE, and forecast bias | In progress | MAE and signed bias implemented and unit-tested for selected cases. RMSE and WAPE remain. |
| Lag and rolling features | In progress | Rolling 7/14/28-day weekday means implemented; seven-day version reproduces the previous weekday count. General lag/rolling feature tables remain. |
| Time-based splitting | Implemented | January-February trained March forecasts; a March-selected baseline was tested on April. April subsequently became development data. |
| Walk-forward validation | Implemented | Horizon and update interval are separate. Overlapping forecast blocks are resolved to the latest origin per target day before MAE/bias; update intervals longer than the horizon are rejected. The comparison schedules have structural tests, but latest-origin selection and incomplete/irregular daily data still lack direct automated coverage. |
| Forecasting baselines | Implemented | Fixed all-history and 7/14/28-day means, expanding history, and rolling 7/14/28-day means compared on April. The 20 baseline plus 184 additional overlapping schedules total 204 configurations; synthetic tests check these counts and selected schedule constraints. Fixed 28-day history had lowest April MAE: 6,408.91. Details in diary. |
| ARIMA / SARIMA foundations | Planned | Study AR/MA terms, stationarity, differencing, and weekly seasonality; evaluate a first SARIMA model. |
| Exponential smoothing / ETS | Planned | Evaluate level, trend, and seasonal smoothing when useful. |

**Target output:** a reproducible forecasting benchmark without future-information
leakage. **Current output:** 204 weekday-mean schedule configurations on April,
with latest-forecast-per-day scoring. April is development data.
Use matching target dates, horizons, and refresh schedules for model comparisons;
reserve a later unseen period for final evaluation.

## 4. Machine Learning

| Topic | Status | Evidence / remaining work |
| --- | --- | --- |
| Linear Regression and Ridge | Planned | Fit models using forecast-time-available features. |
| Regularization and bias-variance trade-off | Planned | Evaluate generalization and sensitivity to model complexity. |
| Random Forest and XGBoost | Planned | Compare with simpler models under the same evaluation setup. |
| Hyperparameter tuning | Planned | Use temporal validation rather than random cross-validation. |
| Residual analysis and feature importance | In progress | Baseline signed/absolute errors examined by date and weekday. ML residual diagnostics and feature importance remain. |

**Target output:** compared and validated predictive models. Model breadth is
a learning goal, not a prerequisite for packaging the first working pipeline.

## 5. Mathematical Optimization

| Topic | Status | Evidence / remaining work |
| --- | --- | --- |
| Linear Programming | Planned | Formulate a continuous allocation baseline. |
| Mixed-Integer Programming | Planned | Represent discrete fleet allocation decisions. |
| Decision variables and constraints | Planned | Define fleet size, capacity, and feasible movements. |
| Objective function | Planned | Specify operational costs and service priorities. |
| Assignment and min-cost flow | Planned | Identify when these formulations fit the decision problem. |
| Optimality gap and solver diagnostics | Planned | Interpret bounds, feasibility, termination, and solution quality. |

**Target output:** a mathematical fleet allocation model with explicit assumptions.

## 6. Algorithms & OR Solvers

| Topic | Status | Evidence / remaining work |
| --- | --- | --- |
| Greedy algorithms | Planned | Build a simple fleet-decision reference policy. |
| Branch-and-bound principles | Planned | Connect the search logic and bounds to integer optimization. |
| OR-Tools / HiGHS | Planned | Use OR-Tools as the primary toolkit; choose solver/formulation appropriately and consider HiGHS where useful. |
| Heuristics and local search | Planned | Explore alternatives when exact optimization is too costly. |
| Runtime and optimality comparison | Planned | Compare methods on identical instances and compute budgets. |

**Target output:** a benchmark of optimization methods for the taxi problem.

## 7. Simulation & Decision Making

| Topic | Status | Evidence / remaining work |
| --- | --- | --- |
| Discrete-time simulation | Planned | Define time steps and simulated fleet state transitions. |
| Forecast-to-optimization integration | Planned | Convert regional forecasts into allocation inputs. |
| Demand-supply imbalance | Planned | Evaluate shortages and surplus capacity by zone/time. |
| Relocation cost and unmet demand | Planned | Define and measure these quantities under explicit simulation assumptions. |
| Sensitivity and robustness analysis | Planned | Vary fleet capacity, costs, forecast errors, and operational assumptions. |
| Experiment design and A/B testing | Planned | Define a hypothesis, primary metric, guardrails, randomization unit, and uncertainty/sample-size considerations. Discuss interference between taxi zones and time-block (switchback) designs. Practice policy comparisons in simulation; do not describe historical backtests or simulated comparisons as live A/B tests. |

**Target output:** end-to-end operational performance analysis. Recorded trips
are observed pickups; unmet demand and vehicle availability are not directly
observed and must not be presented as measured ground truth.

## 8. Software Engineering & MLOps

Work on this section throughout the project, not only after modelling is finished.

| Topic | Status | Evidence / remaining work |
| --- | --- | --- |
| Git and project architecture | In progress | Version control and reusable helpers are in use. Separate preparation, training, prediction, and evaluation stages remain. |
| Unit and integration tests | In progress | Eleven pytest tests cover metric inputs, fit/predict weekday means and window choice, plus comparison counts, strategy mix, and update interval constraints. Direct walk-forward behavior, loader, and integration coverage remain. |
| Reproducible experiments | In progress | Two comparison functions return configuration metadata and MAE/bias in DataFrames; 204 learner-run April results were inspected. Environment specification and persistent run/data/model artifact tracking remain. |
| Configuration and logging | Planned | Replace hard-coded experiment choices with configuration and actionable run logs. |
| Batch inference pipeline | Planned | Provide a repeatable command that writes forecasts with dates and model/run metadata. |
| README and technical presentation | In progress | README, diary, and review approach documented. Final technical walkthrough remains. |
| Continuous integration | Implemented | GitHub Actions runs pytest with Python 3.13 on pushes and pull requests; the learner confirmed a passing run. This checks the current unit suite, not the data-dependent loader. |
| Continuous delivery (CD) and release validation | Planned | Build a versioned deployable artifact after checks pass, release it to a chosen execution environment, run a smoke test, and document rollback. Start with a deliberate release step; automatic deployment of every change is not required. |
| Docker and scheduled execution | Planned | Package and run the batch workflow on a documented schedule. |
| Monitoring and recovery | Planned | Check failures, input freshness/quality, and later forecast performance; document safe reruns and model rollback. |

**Target output:** a reproducible, tested, regularly operated forecasting workflow
with documented failure handling. No production deployment is claimed yet.

## Scope boundaries

Prioritize one working batch pipeline, one reproducible release path, and
useful operational checks. Kubernetes, distributed training, a feature store,
and an API are not requirements unless a concrete project need emerges.
Learn A/B experiment design during the decision/simulation stage; a live
experiment requires a real deployment and suitable traffic or operational
units, which this historical dataset alone cannot provide.

## Next milestones

1. Completed November 26-27: separate horizon from update interval; compare 20 baseline plus 184 additional schedules; add synthetic pytest coverage and a passing GitHub Actions check.
2. Learn SARIMA foundations and evaluate a first model against a baseline on matching dates and schedules. Add focused time-boundary tests as the evaluator evolves.
3. Package and operate the first forecasting pipeline, progressively adding
   the engineering practices above before expanding the model catalog.
4. Develop hourly/regional demand inputs and add MILP/OR-Tools and simulation.

The learner writes and runs the code. Each session should explain the purpose,
set a manageable task, review the result, and update this roadmap when warranted.
