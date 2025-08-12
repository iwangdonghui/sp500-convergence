#!/usr/bin/env python3
"""
S&P 500 Rolling Returns and Convergence Analysis Tool

This tool computes long-horizon rolling S&P 500 returns and "convergence" metrics
using nominal total returns (no inflation adjustment).

Author: Data Engineer
"""

import argparse
import csv
import os
import sys
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any
import warnings

import numpy as np
import pandas as pd
import requests

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

# Constants
FLOATING_TOLERANCE = 1e-12
DEFAULT_WINDOWS = [5, 10, 15, 20, 30]
DEFAULT_START_YEARS = [1926, 1957, 1972, 1985]
DEFAULT_THRESHOLDS = [0.0025, 0.005, 0.0075, 0.01]
SLICKCHARTS_URL = "https://www.slickcharts.com/sp500/returns/history.csv"


class SP500Analyzer:
    """Main class for S&P 500 rolling returns analysis."""
    
    def __init__(self, data: pd.DataFrame):
        """
        Initialize with S&P 500 data.
        
        Args:
            data: DataFrame with 'year' and 'return' columns
        """
        self.data = data.sort_values('year').reset_index(drop=True)
        self.years = self.data['year'].tolist()
        self.returns = self.data['return'].tolist()
        
    def compute_rolling_cagr(self, window_size: int, start_year: int) -> List[Tuple[int, float]]:
        """
        Compute rolling CAGR for a given window size and start year.
        
        Args:
            window_size: Number of years in the rolling window
            start_year: Starting year for the series
            
        Returns:
            List of (end_year, CAGR) tuples
        """
        results = []
        
        # Find the index where our start year begins
        try:
            start_idx = self.years.index(start_year)
        except ValueError:
            return results
            
        # Ensure we have enough data for at least one window
        if start_idx + window_size > len(self.years):
            return results
            
        for i in range(start_idx, len(self.years) - window_size + 1):
            end_idx = i + window_size
            window_returns = self.returns[i:end_idx]
            
            # Compute geometric mean using log-sum method
            log_returns = [np.log(1 + r) for r in window_returns]
            total_return = np.exp(sum(log_returns))
            cagr = total_return ** (1.0 / window_size) - 1
            
            # Apply floating point tolerance
            if abs(cagr) < FLOATING_TOLERANCE:
                cagr = 0.0
                
            results.append((self.years[end_idx - 1], cagr))
            
        return results
    
    def compute_all_rolling_cagrs(self, start_year: int) -> Dict[int, List[Tuple[int, float]]]:
        """
        Compute rolling CAGR for all window sizes for a given start year.
        
        Args:
            start_year: Starting year for the series
            
        Returns:
            Dictionary mapping window size to list of (end_year, CAGR) tuples
        """
        results = {}
        for window_size in DEFAULT_WINDOWS:
            results[window_size] = self.compute_rolling_cagr(window_size, start_year)
        return results
    
    def compute_window_statistics(self, start_year: int) -> pd.DataFrame:
        """
        Compute statistics for each window size.
        
        Args:
            start_year: Starting year for the series
            
        Returns:
            DataFrame with window statistics
        """
        rolling_cagrs = self.compute_all_rolling_cagrs(start_year)
        
        stats = []
        for window_size in DEFAULT_WINDOWS:
            cagrs = rolling_cagrs[window_size]
            
            if not cagrs:
                stats.append({
                    'window_size': window_size,
                    'best_window': 'N/A',
                    'best_cagr': np.nan,
                    'worst_window': 'N/A',
                    'worst_cagr': np.nan,
                    'avg_cagr': np.nan,
                    'count': 0
                })
                continue
                
            # Find best and worst windows
            best_idx = np.argmax([cagr for _, cagr in cagrs])
            worst_idx = np.argmin([cagr for _, cagr in cagrs])
            
            # Calculate start year for each window
            start_idx = self.years.index(start_year)
            best_start = self.years[start_idx + best_idx]
            best_end = cagrs[best_idx][0]
            worst_start = self.years[start_idx + worst_idx]
            worst_end = cagrs[worst_idx][0]
            
            stats.append({
                'window_size': window_size,
                'best_window': f"{best_start}-{best_end}",
                'best_cagr': cagrs[best_idx][1],
                'worst_window': f"{worst_start}-{worst_end}",
                'worst_cagr': cagrs[worst_idx][1],
                'avg_cagr': np.mean([cagr for _, cagr in cagrs]),
                'count': len(cagrs)
            })
            
        return pd.DataFrame(stats)
    
    def find_min_no_loss_horizon(self, start_year: int) -> Dict[str, Any]:
        """
        Find the minimum holding period where no N-year window has negative CAGR.
        
        Args:
            start_year: Starting year for the series
            
        Returns:
            Dictionary with no-loss horizon information
        """
        max_feasible = len(self.years) - self.years.index(start_year)
        
        for n in range(1, max_feasible + 1):
            cagrs = self.compute_rolling_cagr(n, start_year)
            if not cagrs:
                continue
                
            min_cagr = min(cagr for _, cagr in cagrs)
            if min_cagr >= 0:
                # Found the minimum no-loss horizon
                best_idx = np.argmax([cagr for _, cagr in cagrs])
                worst_idx = np.argmin([cagr for _, cagr in cagrs])
                
                start_idx = self.years.index(start_year)
                best_start = self.years[start_idx + best_idx]
                best_end = cagrs[best_idx][0]
                worst_start = self.years[start_idx + worst_idx]
                worst_end = cagrs[worst_idx][0]
                
                return {
                    'start_year_series': start_year,
                    'min_holding_years': n,
                    'worst_window': f"{worst_start}-{worst_end}",
                    'worst_cagr': cagrs[worst_idx][1],
                    'best_window': f"{best_start}-{best_end}",
                    'best_cagr': cagrs[best_idx][1],
                    'average_cagr': np.mean([cagr for _, cagr in cagrs]),
                    'num_windows_checked': len(cagrs)
                }
        
        # If no N satisfies the condition, return max feasible
        cagrs = self.compute_rolling_cagr(max_feasible, start_year)
        if cagrs:
            best_idx = np.argmax([cagr for _, cagr in cagrs])
            worst_idx = np.argmin([cagr for _, cagr in cagrs])
            
            start_idx = self.years.index(start_year)
            best_start = self.years[start_idx + best_idx]
            best_end = cagrs[best_idx][0]
            worst_start = self.years[start_idx + worst_idx]
            worst_end = cagrs[worst_idx][0]
            
            return {
                'start_year_series': start_year,
                'min_holding_years': max_feasible,
                'worst_window': f"{worst_start}-{worst_end}",
                'worst_cagr': cagrs[worst_idx][1],
                'best_window': f"{best_start}-{best_end}",
                'best_cagr': cagrs[best_idx][1],
                'average_cagr': np.mean([cagr for _, cagr in cagrs]),
                'num_windows_checked': len(cagrs),
                'note': 'Condition not met - max feasible horizon used'
            }
        
        return {
            'start_year_series': start_year,
            'min_holding_years': 'N/A',
            'worst_window': 'N/A',
            'worst_cagr': np.nan,
            'best_window': 'N/A',
            'best_cagr': np.nan,
            'average_cagr': np.nan,
            'num_windows_checked': 0,
            'note': 'No feasible windows'
        }
    
    def find_min_spread_horizon(self, start_year: int, threshold: float) -> Dict[str, Any]:
        """
        Find the minimum holding period where CAGR spread is within threshold.
        
        Args:
            start_year: Starting year for the series
            threshold: Maximum allowed CAGR spread
            
        Returns:
            Dictionary with spread horizon information
        """
        max_feasible = len(self.years) - self.years.index(start_year)
        
        for n in range(1, max_feasible + 1):
            cagrs = self.compute_rolling_cagr(n, start_year)
            if not cagrs:
                continue
                
            cagr_values = [cagr for _, cagr in cagrs]
            spread = max(cagr_values) - min(cagr_values)
            
            if spread <= threshold:
                # Found the minimum spread horizon
                best_idx = np.argmax(cagr_values)
                worst_idx = np.argmin(cagr_values)
                
                start_idx = self.years.index(start_year)
                best_start = self.years[start_idx + best_idx]
                best_end = cagrs[best_idx][0]
                worst_start = self.years[start_idx + worst_idx]
                worst_end = cagrs[worst_idx][0]
                
                return {
                    'start_year_series': start_year,
                    'threshold': threshold,
                    'min_holding_years': n,
                    'best_window': f"{best_start}-{best_end}",
                    'best_cagr': cagrs[best_idx][1],
                    'worst_window': f"{worst_start}-{worst_end}",
                    'worst_cagr': cagrs[worst_idx][1],
                    'spread': spread
                }
        
        # If no N satisfies the condition, return max feasible
        cagrs = self.compute_rolling_cagr(max_feasible, start_year)
        if cagrs:
            cagr_values = [cagr for _, cagr in cagrs]
            spread = max(cagr_values) - min(cagr_values)
            
            best_idx = np.argmax(cagr_values)
            worst_idx = np.argmin(cagr_values)
            
            start_idx = self.years.index(start_year)
            best_start = self.years[start_idx + best_idx]
            best_end = cagrs[best_idx][0]
            worst_start = self.years[start_idx + worst_idx]
            worst_end = cagrs[worst_idx][0]
            
            return {
                'start_year_series': start_year,
                'threshold': threshold,
                'min_holding_years': max_feasible,
                'best_window': f"{best_start}-{best_end}",
                'best_cagr': cagrs[best_idx][1],
                'worst_cagr': cagrs[worst_idx][1],
                'spread': spread,
                'note': 'Threshold not met - max feasible horizon used'
            }
        
        return {
            'start_year_series': start_year,
            'threshold': threshold,
            'min_holding_years': 'N/A',
            'best_window': 'N/A',
            'best_cagr': np.nan,
            'worst_window': 'N/A',
            'worst_cagr': np.nan,
            'spread': np.nan,
            'note': 'No feasible windows'
        }


def download_slickcharts_data() -> pd.DataFrame:
    """
    Download S&P 500 data from SlickCharts.
    
    Returns:
        DataFrame with year and return columns
    """
    print(f"Downloading data from {SLICKCHARTS_URL}...")
    
    try:
        response = requests.get(SLICKCHARTS_URL, timeout=30)
        response.raise_for_status()
        
        # Try to read as CSV
        content = response.text
        lines = content.strip().split('\n')
        
        # Auto-detect if header exists
        first_line = lines[0]
        second_line = lines[1]
        
        # Check if first line looks like a header (contains text)
        has_header = any(char.isalpha() for char in first_line)
        
        if has_header:
            # Skip header and parse
            data_lines = lines[1:]
        else:
            data_lines = lines
        
        # Parse data
        data = []
        for line in data_lines:
            if not line.strip():
                continue
            parts = line.split(',')
            if len(parts) >= 2:
                try:
                    year = int(parts[0].strip())
                    # Try to parse return value
                    ret_str = parts[1].strip().replace('%', '')
                    ret_val = float(ret_str)
                    
                    # Convert to decimal if it looks like percentage
                    if abs(ret_val) > 1.0:
                        ret_val = ret_val / 100.0
                    
                    data.append([year, ret_val])
                except (ValueError, IndexError):
                    continue
        
        if not data:
            raise ValueError("No valid data found in downloaded CSV")
        
        df = pd.DataFrame(data, columns=['year', 'return'])
        
        # Drop current year if present (incomplete)
        current_year = pd.Timestamp.now().year
        if current_year in df['year'].values:
            df = df[df['year'] != current_year]
            print(f"Dropped incomplete year {current_year}")
        
        # Sort and validate
        df = df.sort_values('year').reset_index(drop=True)
        
        print(f"Downloaded {len(df)} years of data: {df['year'].min()} to {df['year'].max()}")
        return df
        
    except Exception as e:
        print(f"Error downloading data: {e}")
        sys.exit(1)


def load_local_csv(filepath: str) -> pd.DataFrame:
    """
    Load S&P 500 data from a local CSV file.
    
    Args:
        filepath: Path to the CSV file
        
    Returns:
        DataFrame with year and return columns
    """
    print(f"Loading data from {filepath}...")
    
    try:
        # Try to read with pandas first
        df = pd.read_csv(filepath)
        
        # Auto-detect columns
        if len(df.columns) >= 2:
            # Try to identify year and return columns
            year_col = None
            return_col = None
            
            for col in df.columns:
                col_lower = str(col).lower()
                if any(keyword in col_lower for keyword in ['year', 'date', 'yr']):
                    year_col = col
                elif any(keyword in col_lower for keyword in ['return', 'ret', 'cagr', 'total']):
                    return_col = col
            
            if year_col is None or return_col is None:
                # Assume first two columns
                year_col = df.columns[0]
                return_col = df.columns[1]
            
            # Extract and clean data
            data = []
            for _, row in df.iterrows():
                try:
                    year = int(row[year_col])
                    ret_val = float(row[return_col])
                    
                    # Convert to decimal if it looks like percentage
                    if abs(ret_val) > 1.0:
                        ret_val = ret_val / 100.0
                    
                    data.append([year, ret_val])
                except (ValueError, TypeError):
                    continue
            
            if not data:
                raise ValueError("No valid data found in CSV")
            
            df_clean = pd.DataFrame(data, columns=['year', 'return'])
            
        else:
            # Try manual parsing for headerless CSV
            with open(filepath, 'r') as f:
                reader = csv.reader(f)
                data = []
                for row in reader:
                    if len(row) >= 2:
                        try:
                            year = int(row[0].strip())
                            ret_str = row[1].strip().replace('%', '')
                            ret_val = float(ret_str)
                            
                            # Convert to decimal if it looks like percentage
                            if abs(ret_val) > 1.0:
                                ret_val = ret_val / 100.0
                            
                            data.append([year, ret_val])
                        except (ValueError, IndexError):
                            continue
            
            if not data:
                raise ValueError("No valid data found in CSV")
            
            df_clean = pd.DataFrame(data, columns=['year', 'return'])
        
        # Drop current year if present (incomplete)
        current_year = pd.Timestamp.now().year
        if current_year in df_clean['year'].values:
            df_clean = df_clean[df_clean['year'] != current_year]
            print(f"Dropped incomplete year {current_year}")
        
        # Sort and validate
        df_clean = df_clean.sort_values('year').reset_index(drop=True)
        
        print(f"Loaded {len(df_clean)} years of data: {df_clean['year'].min()} to {df_clean['year'].max()}")
        return df_clean
        
    except Exception as e:
        print(f"Error loading CSV file: {e}")
        sys.exit(1)


def generate_rolling_cagr_csvs(analyzer: SP500Analyzer, start_years: List[int], outdir: str):
    """
    Generate rolling CAGR CSV files for each baseline.
    
    Args:
        analyzer: SP500Analyzer instance
        start_years: List of start years
        outdir: Output directory
    """
    print("\nGenerating rolling CAGR CSV files...")
    
    for start_year in start_years:
        rolling_cagrs = analyzer.compute_all_rolling_cagrs(start_year)
        
        # Create DataFrame for output
        all_years = set()
        for cagrs in rolling_cagrs.values():
            all_years.update(year for year, _ in cagrs)
        
        all_years = sorted(list(all_years))
        
        # Build output data
        output_data = []
        for end_year in all_years:
            row = {'EndYear': end_year}
            for window_size in DEFAULT_WINDOWS:
                cagrs = rolling_cagrs[window_size]
                cagr_value = None
                for year, cagr in cagrs:
                    if year == end_year:
                        cagr_value = cagr
                        break
                row[f'{window_size}y'] = cagr_value if cagr_value is not None else np.nan
            output_data.append(row)
        
        # Create DataFrame and save
        df_output = pd.DataFrame(output_data)
        filename = f"sp500_rolling_CAGR_{start_year}_full_years.csv"
        filepath = os.path.join(outdir, filename)
        df_output.to_csv(filepath, index=False)
        print(f"  Saved: {filename}")


def generate_summary_csvs(analyzer: SP500Analyzer, start_years: List[int], outdir: str):
    """
    Generate summary statistics CSV files for each baseline.
    
    Args:
        analyzer: SP500Analyzer instance
        start_years: List of start years
        outdir: Output directory
    """
    print("\nGenerating summary statistics CSV files...")
    
    for start_year in start_years:
        stats_df = analyzer.compute_window_statistics(start_year)
        
        filename = f"sp500_rolling_summary_{start_year}.csv"
        filepath = os.path.join(outdir, filename)
        stats_df.to_csv(filepath, index=False)
        print(f"  Saved: {filename}")


def generate_no_loss_summary(analyzer: SP500Analyzer, start_years: List[int], outdir: str):
    """
    Generate no-loss horizon summary CSV.
    
    Args:
        analyzer: SP500Analyzer instance
        start_years: List of start years
        outdir: Output directory
    """
    print("\nGenerating no-loss horizon summary...")
    
    no_loss_data = []
    for start_year in start_years:
        result = analyzer.find_min_no_loss_horizon(start_year)
        no_loss_data.append(result)
    
    df_no_loss = pd.DataFrame(no_loss_data)
    filepath = os.path.join(outdir, "min_no_loss_summary.csv")
    df_no_loss.to_csv(filepath, index=False)
    print(f"  Saved: min_no_loss_summary.csv")


def generate_spread_grid(analyzer: SP500Analyzer, start_years: List[int], thresholds: List[float], outdir: str):
    """
    Generate spread threshold grid CSV.
    
    Args:
        analyzer: SP500Analyzer instance
        start_years: List of start years
        thresholds: List of threshold values
        outdir: Output directory
    """
    print("\nGenerating spread threshold grid...")
    
    spread_data = []
    for start_year in start_years:
        for threshold in thresholds:
            result = analyzer.find_min_spread_horizon(start_year, threshold)
            spread_data.append(result)
    
    df_spread = pd.DataFrame(spread_data)
    filepath = os.path.join(outdir, "min_spread_grid_nominal.csv")
    df_spread.to_csv(filepath, index=False)
    print(f"  Saved: min_spread_grid_nominal.csv")


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="S&P 500 Rolling Returns and Convergence Analysis Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download data and generate all outputs
  python sp500_convergence.py \\
    --download_slickcharts \\
    --start_years 1926,1957,1972,1985 \\
    --thresholds 0.0025,0.005,0.0075,0.01 \\
    --outdir ./out

  # Use local CSV with threshold range
  python sp500_convergence.py \\
    --csv data.csv \\
    --start_years 1926,1957 \\
    --thr_min 0.0025 --thr_max 0.01 --thr_steps 16 \\
    --outdir ./out
        """
    )
    
    # Data source options (mutually exclusive)
    data_group = parser.add_mutually_exclusive_group(required=True)
    data_group.add_argument('--download_slickcharts', action='store_true',
                           help='Download data from SlickCharts')
    data_group.add_argument('--csv', type=str,
                           help='Path to local CSV file')
    
    # Analysis parameters
    parser.add_argument('--start_years', type=str, default='1926,1957,1972,1985',
                       help='Comma-separated list of start years (default: 1926,1957,1972,1985)')
    
    # Threshold options (mutually exclusive)
    threshold_group = parser.add_mutually_exclusive_group(required=True)
    threshold_group.add_argument('--thresholds', type=str,
                                help='Comma-separated list of threshold values')
    threshold_group.add_argument('--thr_min', type=float,
                                help='Minimum threshold value')
    threshold_group.add_argument('--thr_max', type=float,
                                help='Maximum threshold value')
    threshold_group.add_argument('--thr_steps', type=int,
                                help='Number of threshold steps')
    
    parser.add_argument('--outdir', type=str, default='./out',
                       help='Output directory for CSV files (default: ./out)')
    
    args = parser.parse_args()
    
    # Parse start years
    try:
        start_years = [int(y.strip()) for y in args.start_years.split(',')]
    except ValueError:
        print("Error: Invalid start_years format. Use comma-separated integers.")
        sys.exit(1)
    
    # Parse or generate thresholds
    if args.thresholds:
        try:
            thresholds = [float(t.strip()) for t in args.thresholds.split(',')]
        except ValueError:
            print("Error: Invalid thresholds format. Use comma-separated floats.")
            sys.exit(1)
    else:
        if not all([args.thr_min, args.thr_max, args.thr_steps]):
            print("Error: Must specify all of --thr_min, --thr_max, and --thr_steps")
            sys.exit(1)
        
        thresholds = np.linspace(args.thr_min, args.thr_max, args.thr_steps)
        thresholds = [round(t, 6) for t in thresholds]  # Round to avoid floating point issues
    
    # Create output directory
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    
    # Load data
    if args.download_slickcharts:
        df = download_slickcharts_data()
    else:
        df = load_local_csv(args.csv)
    
    # Validate data
    if len(df) < 30:
        print("Warning: Limited data available. Some analyses may not be possible.")
    
    # Create analyzer
    analyzer = SP500Analyzer(df)
    
    # Print run summary
    print(f"\n{'='*60}")
    print("RUN SUMMARY")
    print(f"{'='*60}")
    print(f"Data span: {df['year'].min()} to {df['year'].max()} ({len(df)} years)")
    print(f"Start years: {', '.join(map(str, start_years))}")
    print(f"Thresholds: {', '.join(map(str, thresholds))}")
    print(f"Output directory: {outdir.absolute()}")
    print(f"{'='*60}")
    
    # Generate all outputs
    try:
        generate_rolling_cagr_csvs(analyzer, start_years, str(outdir))
        generate_summary_csvs(analyzer, start_years, str(outdir))
        generate_no_loss_summary(analyzer, start_years, str(outdir))
        generate_spread_grid(analyzer, start_years, thresholds, str(outdir))
        
        print(f"\n{'='*60}")
        print("ANALYSIS COMPLETE")
        print(f"{'='*60}")
        print(f"All CSV files have been generated in: {outdir.absolute()}")
        
        # Print file list
        print("\nGenerated files:")
        for file in sorted(outdir.glob("*.csv")):
            print(f"  {file.name}")
            
    except Exception as e:
        print(f"\nError during analysis: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
