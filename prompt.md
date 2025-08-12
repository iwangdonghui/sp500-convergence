# The Prompt for Cursor:

>[!NOTE]
> The whole project was created by cursor (except this markdown file).

## Role & Goal

Act as a data engineer and analyst. Deliver a re-runnable Python CLI tool and CSV artifacts that compute long-horizon rolling S&P 500 returns and “convergence” metrics using nominal total returns (no inflation adjustment).

Data (must auto-download or accept a local file)

* S&P 500 annual total returns (with dividends)

Default source CSV: https://www.slickcharts.com/sp500/returns/history.csv
The CSV contains year and annual total return (may be in percent or decimal).

Ingestion Rules

* Accept headerless or headered CSV; auto-detect which column is year and which is total return.
* Normalize total returns to decimal (e.g., 0.075 = 7.5%) even if the CSV is in percent.
* Drop the current (incomplete) year if present to avoid YTD bias.
* Sort strictly by year; drop malformed rows.

## Core Definitions

* For a window of length N with yearly returns r_t, use geometric compounding:
> $Total =\prod (1+r_t); CAGR = \text{Total}^{1/N} - 1$.
* Use log-sum vectorization to compute rolling products: \sum \ln(1+r_t) \rightarrow \exp(\cdot).
* Floating comparison tolerance: 1e-12.

Required Computations & Deliverables

### A) Rolling CAGR tables (four baselines)

Compute rolling annualized returns using window sizes 5, 10, 15, 20, 30 years for baselines: 1926, 1957, 1972, 1985.

Output (one row per end year): EndYear, 5y, 10y, 15y, 20y, 30y (values as decimals)

Files (one CSV per baseline):

* sp500_rolling_CAGR_1926_full_years.csv
* sp500_rolling_CAGR_1957_full_years.csv
* sp500_rolling_CAGR_1972_full_years.csv
* sp500_rolling_CAGR_1985_full_years.csv

### B) Window statistics (four baselines)

For each window size in {5, 10, 15, 20, 30}, compute for baselines 1926, 1957, 1972, 1985:

* Best window: start–end, with its CAGR
* Worst window: start–end, with its CAGR
* Average CAGR across all windows
* Sample count (number of windows)

Files (one CSV per baseline):

* sp500_rolling_summary_1926.csv
* sp500_rolling_summary_1957.csv
* sp500_rolling_summary_1972.csv
* sp500_rolling_summary_1985.csv

Note: Median window is intentionally omitted.

### C) “No-loss” minimum horizon

Find the smallest N such that every rolling N-year window (from each baseline) has CAGR ≥ 0.
Also report the counterexample at N−1 (worst window & CAGR).

File: min_no_loss_summary.csv
Columns: start_year_series, min_holding_years, worst_window, worst_cagr, best_window, best_cagr, average_cagr, num_windows_checked
Baselines: 1926, 1957, 1972, 1985.

### D) “Spread ≤ threshold” minimum horizon (convergence)

For start years {1926, 1957, 1972, 1985} (support any list via CLI) and thresholds {0.0025, 0.005, 0.0075, 0.01} (i.e., 0.25%, 0.5%, 0.75%, 1.0%), find the smallest N such that across all N-year windows:

$\max(\text{CAGR}) - \min(\text{CAGR}) \le \text{threshold}$

Also capture the best and worst windows at that N.

File: min_spread_grid_nominal.csv

Columns: start_year_series, threshold, min_holding_years, best_window, best_cagr, worst_window, worst_cagr, spread

### CLI Requirements

Provide a single CLI script that supports:

* --download_slickcharts (download the source CSV) or --csv <path> (use local file)
* --start_years <comma_list> (e.g., 1926,1957,1972,1985)
* Either --thresholds <comma_list> or a range: --thr_min --thr_max --thr_steps
* --outdir <dir> (all outputs written here)

### Robustness & Quality:

* Gracefully handle short series (if a requested window can’t be computed, skip with a clear note).
* If no N satisfies a condition before the series ends, return N = max feasible and flag that the condition wasn’t met.
* Deterministic output ordering and consistent file naming for reproducibility.
* Print a brief run summary (years span used, whether the current year was dropped, thresholds, start years, counts).

Example Commands

Nominal, download data, generate CSVs:

``` bash
python sp500_convergence.py \
  --download_slickcharts \
  --start_years 1926,1957,1972,1985 \
  --thresholds 0.0025,0.005,0.0075,0.01 \
  --outdir ./out
```

Nominal with threshold range:

``` bash
python sp500_convergence.py \
  --download_slickcharts \
  --start_years 1926,1957 \
  --thr_min 0.0025 --thr_max 0.01 --thr_steps 16 \
  --outdir ./out
```