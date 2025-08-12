#!/usr/bin/env python3
"""
Demonstration script for the S&P 500 Rolling Returns and Convergence Analysis Tool.

This script shows how to use the tool programmatically and demonstrates its capabilities.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from sp500_convergence import SP500Analyzer, generate_rolling_cagr_csvs, generate_summary_csvs, generate_no_loss_summary, generate_spread_grid


def create_realistic_sp500_data():
    """
    Create realistic S&P 500 data for demonstration purposes.
    
    This simulates the kind of data you would get from SlickCharts or other sources.
    """
    print("Creating realistic S&P 500 data...")
    
    # Historical periods with realistic patterns
    periods = [
        (1926, 1929, 0.15, 0.08),    # Roaring 20s
        (1930, 1932, -0.25, 0.15),   # Great Depression
        (1933, 1945, 0.12, 0.20),    # Recovery and WWII
        (1946, 1965, 0.10, 0.15),    # Post-war boom
        (1966, 1982, 0.06, 0.20),    # Stagflation period
        (1983, 1999, 0.15, 0.15),    # Bull market
        (2000, 2009, 0.02, 0.25),    # Dot-com bust and financial crisis
        (2010, 2023, 0.12, 0.15),    # Recovery and growth
    ]
    
    data = []
    np.random.seed(42)  # For reproducible results
    
    for start_year, end_year, mean_return, volatility in periods:
        for year in range(start_year, end_year + 1):
            # Add some realistic year-to-year correlation
            if year == start_year:
                base_return = np.random.normal(mean_return, volatility)
            else:
                # Add some persistence
                base_return = 0.7 * base_return + 0.3 * np.random.normal(mean_return, volatility)
            
            # Ensure returns are reasonable
            return_val = max(-0.50, min(0.80, base_return))
            data.append([year, return_val])
    
    df = pd.DataFrame(data, columns=['year', 'return'])
    print(f"Created {len(df)} years of data: {df['year'].min()} to {df['year'].max()}")
    print(f"Sample statistics:")
    print(f"  Mean return: {df['return'].mean():.3f}")
    print(f"  Std return: {df['return'].std():.3f}")
    print(f"  Min return: {df['return'].min():.3f}")
    print(f"  Max return: {df['return'].max():.3f}")
    
    return df


def demonstrate_analysis():
    """Demonstrate the full analysis capabilities."""
    print("\n" + "="*70)
    print("S&P 500 ANALYSIS DEMONSTRATION")
    print("="*70)
    
    # Create data
    df = create_realistic_sp500_data()
    
    # Create analyzer
    analyzer = SP500Analyzer(df)
    
    # Define analysis parameters
    start_years = [1926, 1957, 1972, 1985]
    thresholds = [0.0025, 0.005, 0.0075, 0.01]
    
    print(f"\nAnalysis Parameters:")
    print(f"  Start years: {start_years}")
    print(f"  Thresholds: {[f'{t:.1%}' for t in thresholds]}")
    print(f"  Window sizes: 5, 10, 15, 20, 30 years")
    
    # Demonstrate rolling CAGR computation
    print(f"\n" + "-"*50)
    print("ROLLING CAGR COMPUTATION")
    print("-"*50)
    
    for start_year in start_years[:2]:  # Show first two for brevity
        print(f"\nRolling CAGR from {start_year}:")
        for window_size in [5, 10, 15]:
            cagrs = analyzer.compute_rolling_cagr(window_size, start_year)
            if cagrs:
                print(f"  {window_size}-year windows: {len(cagrs)} periods")
                print(f"    Best: {cagrs[np.argmax([cagr for _, cagr in cagrs])]}")
                print(f"    Worst: {cagrs[np.argmin([cagr for _, cagr in cagrs])]}")
            else:
                print(f"  {window_size}-year windows: Not enough data")
    
    # Demonstrate no-loss horizon analysis
    print(f"\n" + "-"*50)
    print("NO-LOSS HORIZON ANALYSIS")
    print("-"*50)
    
    for start_year in start_years:
        result = analyzer.find_min_no_loss_horizon(start_year)
        print(f"\nFrom {start_year}:")
        print(f"  Minimum holding period for no losses: {result['min_holding_years']} years")
        print(f"  Worst window: {result['worst_window']} ({result['worst_cagr']:.3f})")
        print(f"  Best window: {result['best_window']} ({result['best_cagr']:.3f})")
        print(f"  Average CAGR: {result['average_cagr']:.3f}")
    
    # Demonstrate convergence analysis
    print(f"\n" + "-"*50)
    print("CONVERGENCE ANALYSIS")
    print("-"*50)
    
    for start_year in start_years[:2]:  # Show first two for brevity
        print(f"\nFrom {start_year}:")
        for threshold in thresholds:
            result = analyzer.find_min_spread_horizon(start_year, threshold)
            print(f"  Threshold {threshold:.1%}: {result['min_holding_years']} years")
            print(f"    Spread: {result['spread']:.4f}")
            print(f"    Best: {result['best_window']} ({result['best_cagr']:.3f})")
            print(f"    Worst: {result['worst_window']} ({result['worst_cagr']:.3f})")
    
    return analyzer, start_years, thresholds


def generate_output_files(analyzer, start_years, thresholds):
    """Generate all output files."""
    print(f"\n" + "="*70)
    print("GENERATING OUTPUT FILES")
    print("="*70)
    
    # Create output directory
    outdir = Path("./demo_output")
    outdir.mkdir(exist_ok=True)
    
    print(f"Output directory: {outdir.absolute()}")
    
    try:
        # Generate rolling CAGR CSVs
        print("\nGenerating rolling CAGR CSV files...")
        generate_rolling_cagr_csvs(analyzer, start_years, str(outdir))
        
        # Generate summary CSVs
        print("Generating summary statistics CSV files...")
        generate_summary_csvs(analyzer, start_years, str(outdir))
        
        # Generate no-loss summary
        print("Generating no-loss horizon summary...")
        generate_no_loss_summary(analyzer, start_years, str(outdir))
        
        # Generate spread grid
        print("Generating spread threshold grid...")
        generate_spread_grid(analyzer, start_years, thresholds, str(outdir))
        
        # List generated files
        print(f"\nGenerated files:")
        for file in sorted(outdir.glob("*.csv")):
            file_size = file.stat().st_size
            print(f"  {file.name} ({file_size} bytes)")
        
        print(f"\n✓ All output files generated successfully!")
        
    except Exception as e:
        print(f"\n✗ Error generating output files: {e}")
        raise


def show_usage_examples():
    """Show command-line usage examples."""
    print(f"\n" + "="*70)
    print("COMMAND-LINE USAGE EXAMPLES")
    print("="*70)
    
    examples = [
        {
            "description": "Full analysis with downloaded data",
            "command": """python3 sp500_convergence.py \\
  --download_slickcharts \\
  --start_years 1926,1957,1972,1985 \\
  --thresholds 0.0025,0.005,0.0075,0.01 \\
  --outdir ./output""",
            "note": "Downloads data from SlickCharts and generates all analyses"
        },
        {
            "description": "Custom start years and threshold range",
            "command": """python3 sp500_convergence.py \\
  --download_slickcharts \\
  --start_years 1957,1972 \\
  --thr_min 0.0025 \\
  --thr_max 0.01 \\
  --thr_steps 16 \\
  --outdir ./custom_output""",
            "note": "Uses custom start years and generates 16 evenly spaced thresholds"
        },
        {
            "description": "Use local CSV file",
            "command": """python3 sp500_convergence.py \\
  --csv ./sp500_data.csv \\
  --start_years 1957,1972,1985 \\
  --thresholds 0.005,0.01 \\
  --outdir ./local_analysis""",
            "note": "Analyzes data from a local CSV file"
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\n{i}. {example['description']}")
        print(f"   {example['note']}")
        print(f"   Command:")
        print(f"   {example['command']}")


def main():
    """Run the complete demonstration."""
    print("S&P 500 Rolling Returns and Convergence Analysis Tool")
    print("Demonstration Script")
    print("="*70)
    
    try:
        # Run the analysis demonstration
        analyzer, start_years, thresholds = demonstrate_analysis()
        
        # Generate output files
        generate_output_files(analyzer, start_years, thresholds)
        
        # Show usage examples
        show_usage_examples()
        
        print(f"\n" + "="*70)
        print("DEMONSTRATION COMPLETE!")
        print("="*70)
        print(f"\nThe tool has been successfully demonstrated with:")
        print(f"  • Realistic S&P 500 data simulation")
        print(f"  • Rolling CAGR computation")
        print(f"  • No-loss horizon analysis")
        print(f"  • Convergence metrics")
        print(f"  • Complete output file generation")
        print(f"\nCheck the 'demo_output' directory for generated CSV files.")
        print(f"\nTo analyze real data, use the command-line examples shown above.")
        
    except Exception as e:
        print(f"\n" + "="*70)
        print(f"DEMONSTRATION FAILED: {e}")
        print("="*70)
        raise


if __name__ == "__main__":
    main()
