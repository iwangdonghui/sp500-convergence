# Quick Start Guide

## Get Started in 3 Steps

### 1. Install Dependencies
```bash
pip3 install -r requirements.txt
```

### 2. Run Analysis with Downloaded Data
```bash
python3 sp500_convergence.py \
  --download_slickcharts \
  --start_years 1926,1957,1972,1985 \
  --thresholds 0.0025,0.005,0.0075,0.01 \
  --outdir ./output
```

### 3. Check Results
The tool will generate 9 CSV files in the `./output` directory:
- **Rolling CAGR tables**: 4 files (one per baseline)
- **Window statistics**: 4 files (one per baseline)  
- **No-loss horizon summary**: 1 file
- **Spread threshold grid**: 1 file

## Alternative: Use Local Data
```bash
python3 sp500_convergence.py \
  --csv ./your_data.csv \
  --start_years 1957,1972 \
  --thresholds 0.005,0.01 \
  --outdir ./analysis
```

## Test the Tool
```bash
python3 test_sp500_tool.py
```

## See a Demo
```bash
python3 demo.py
```

## What You Get

- **Rolling CAGR**: Annualized returns for 5, 10, 15, 20, 30-year windows
- **Best/Worst Windows**: Identifies optimal and challenging investment periods
- **No-Loss Horizon**: Minimum holding period to avoid losses
- **Convergence Metrics**: How returns stabilize over longer horizons

## Data Format
Your CSV should have:
- Column 1: Year (e.g., 1926, 1927, 1928...)
- Column 2: Total Return (e.g., 0.075, 0.089, 0.043...)

The tool automatically:
- Detects headers vs. no headers
- Converts percentages to decimals
- Drops incomplete years
- Sorts chronologically

## Need Help?
- Check `README.md` for detailed documentation
- Run `python3 sp500_convergence.py --help` for CLI options
- Use `demo.py` to see examples
