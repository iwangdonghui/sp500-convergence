---
title: SP500 Convergence
emoji: 📈
colorFrom: blue
colorTo: green
sdk: streamlit
app_file: app.py
pinned: false
---


# S&P 500 Rolling Returns and Convergence Analysis Tool

A comprehensive Python CLI tool for analyzing long-horizon rolling S&P 500 returns and "convergence" metrics using nominal total returns (no inflation adjustment).

## Features

- **Automatic Data Download**: Downloads S&P 500 annual total returns from SlickCharts
- **Flexible Input**: Accepts both downloaded data and local CSV files
- **Smart Parsing**: Auto-detects CSV headers and normalizes return formats
- **Multiple Baselines**: Supports custom start years (default: 1926, 1957, 1972, 1985)
- **Comprehensive Analysis**: Computes rolling CAGR, window statistics, no-loss horizons, and convergence metrics
- **Robust Output**: Generates multiple CSV files with detailed analysis results

## Installation

1. Clone or download this repository
2. Install required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Basic Command Structure

```bash
python sp500_convergence.py [OPTIONS]
```

### Data Source Options

**Download from SlickCharts (recommended):**
```bash
python sp500_convergence.py --download_slickcharts [OTHER_OPTIONS]
```

**Use local CSV file:**
```bash
python sp500_convergence.py --csv path/to/your/file.csv [OTHER_OPTIONS]
```

### Required Parameters

- **Data source**: Either `--download_slickcharts` or `--csv <filepath>`
- **Thresholds**: Either `--thresholds <comma_list>` or threshold range (`--thr_min`, `--thr_max`, `--thr_steps`)

### Example Commands

#### Full Analysis with Default Parameters
```bash
python sp500_convergence.py \
  --download_slickcharts \
  --start_years 1926,1957,1972,1985 \
  --thresholds 0.0025,0.005,0.0075,0.01 \
  --outdir ./output
```

#### Custom Start Years and Threshold Range
```bash
python sp500_convergence.py \
  --download_slickcharts \
  --start_years 1926,1957 \
  --thr_min 0.0025 \
  --thr_max 0.01 \
  --thr_steps 16 \
  --outdir ./custom_output
```

#### Using Local Data
```bash
python sp500_convergence.py \
  --csv ./sp500_data.csv \
  --start_years 1957,1972,1985 \
  --thresholds 0.005,0.01 \
  --outdir ./local_analysis
```

## Output Files

The tool generates several CSV files in the specified output directory:

### A) Rolling CAGR Tables
- **Format**: One CSV per baseline start year
- **Columns**: EndYear, 5y, 10y, 15y, 20y, 30y (values as decimals)
- **Files**:
  - `sp500_rolling_CAGR_1926_full_years.csv`
  - `sp500_rolling_CAGR_1957_full_years.csv`
  - `sp500_rolling_CAGR_1972_full_years.csv`
  - `sp500_rolling_CAGR_1985_full_years.csv`

### B) Window Statistics
- **Format**: One CSV per baseline start year
- **Columns**: window_size, best_window, best_cagr, worst_window, worst_cagr, avg_cagr, count
- **Files**:
  - `sp500_rolling_summary_1926.csv`
  - `sp500_rolling_summary_1957.csv`
  - `sp500_rolling_summary_1972.csv`
  - `sp500_rolling_summary_1985.csv`

### C) No-Loss Minimum Horizon
- **File**: `min_no_loss_summary.csv`
- **Columns**: start_year_series, min_holding_years, worst_window, worst_cagr, best_window, best_cagr, average_cagr, num_windows_checked

### D) Spread Threshold Grid
- **File**: `min_spread_grid_nominal.csv`
- **Columns**: start_year_series, threshold, min_holding_years, best_window, best_cagr, worst_window, worst_cagr, spread

## Data Processing

### Input Requirements
- **Format**: CSV with year and total return columns
- **Headers**: Auto-detected (supports both headerless and headed formats)
- **Returns**: Automatically normalized to decimal format (e.g., 7.5% → 0.075)
- **Validation**: Malformed rows are dropped, data is sorted by year

### Data Cleaning
- Current (incomplete) year is automatically dropped to avoid YTD bias
- Returns are normalized to decimal format regardless of input format
- Data is sorted chronologically and validated

### Computational Methods
- **Geometric Compounding**: Uses log-sum vectorization for numerical stability
- **Floating Point Tolerance**: 1e-12 for consistent comparisons
- **Rolling Windows**: Computes returns for overlapping N-year periods

## Algorithm Details

### Rolling CAGR Calculation
For a window of length N with yearly returns r_t:
- **Total Return**: ∏(1 + r_t)
- **CAGR**: (Total)^(1/N) - 1
- **Implementation**: Uses log-sum method: exp(∑ln(1 + r_t))^(1/N) - 1

### No-Loss Horizon
Finds the smallest N such that every rolling N-year window has CAGR ≥ 0.

### Convergence Metrics
For each threshold, finds the smallest N where:
max(CAGR) - min(CAGR) ≤ threshold

## Error Handling

- **Network Issues**: Graceful handling of download failures
- **Data Quality**: Robust parsing with clear error messages
- **Insufficient Data**: Clear warnings when requested windows cannot be computed
- **Edge Cases**: Handles cases where conditions cannot be met within available data

## Performance Considerations

- **Vectorized Operations**: Uses NumPy for efficient array operations
- **Memory Efficient**: Processes data in chunks where appropriate
- **Scalable**: Handles large datasets efficiently

## Troubleshooting

### Common Issues

1. **Download Failures**: Check internet connection and try again
2. **CSV Parsing Errors**: Ensure your CSV has at least 2 columns (year, return)
3. **Memory Issues**: For very large datasets, consider processing in smaller chunks
4. **Permission Errors**: Ensure write access to the output directory

### Data Format Examples

**Headerless CSV:**
```
1926,0.075
1927,0.089
1928,0.043
```

**Headed CSV:**
```
Year,Total_Return
1926,7.5
1927,8.9
1928,4.3
```

## Contributing

This tool is designed to be extensible. Key areas for enhancement:
- Additional statistical measures
- Support for other market indices
- Inflation-adjusted analysis options
- Interactive visualization capabilities

## License

This tool is provided as-is for educational and research purposes.

## Citation

If you use this tool in research, please cite:
```
S&P 500 Rolling Returns and Convergence Analysis Tool
Data Engineer, 2024
```

## Support

For issues or questions:
1. Check the error messages for specific guidance
2. Verify your input data format
3. Ensure all required dependencies are installed
4. Check that you have write permissions for the output directory
