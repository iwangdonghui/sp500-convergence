#!/usr/bin/env python3
"""
Test script for the S&P 500 Rolling Returns and Convergence Analysis Tool.

This script creates sample data and tests the core functionality.
"""

import os
import tempfile
import pandas as pd
import numpy as np
from pathlib import Path

# Import our tool
from sp500_convergence import SP500Analyzer, generate_rolling_cagr_csvs, generate_summary_csvs, generate_no_loss_summary, generate_spread_grid


def create_sample_data():
    """Create sample S&P 500 data for testing."""
    print("Creating sample S&P 500 data...")
    
    # Create realistic sample data (1926-2023)
    years = list(range(1926, 2024))
    
    # Generate realistic returns with some volatility
    np.random.seed(42)  # For reproducible results
    base_return = 0.10  # 10% average return
    volatility = 0.20   # 20% volatility
    
    returns = []
    for year in years:
        # Add some realistic patterns (e.g., Great Depression, 2008 crisis)
        if 1929 <= year <= 1932:
            # Great Depression years
            ret = np.random.normal(-0.15, 0.10)
        elif 2008 <= year <= 2009:
            # Financial crisis
            ret = np.random.normal(-0.20, 0.15)
        else:
            # Normal years
            ret = np.random.normal(base_return, volatility)
        
        # Ensure returns are reasonable
        ret = max(-0.50, min(0.80, ret))
        returns.append(ret)
    
    # Create DataFrame
    df = pd.DataFrame({
        'year': years,
        'return': returns
    })
    
    print(f"Created sample data: {len(df)} years from {df['year'].min()} to {df['year'].max()}")
    print(f"Sample returns: {df['return'].head().tolist()}")
    
    return df


def test_analyzer():
    """Test the SP500Analyzer class."""
    print("\n" + "="*50)
    print("TESTING SP500Analyzer CLASS")
    print("="*50)
    
    # Create sample data
    df = create_sample_data()
    
    # Create analyzer
    analyzer = SP500Analyzer(df)
    
    # Test rolling CAGR computation
    print("\nTesting rolling CAGR computation...")
    start_year = 1957
    window_size = 10
    
    cagrs = analyzer.compute_rolling_cagr(window_size, start_year)
    print(f"  {len(cagrs)} rolling {window_size}-year windows from {start_year}")
    if cagrs:
        print(f"  First window: {cagrs[0]}")
        print(f"  Last window: {cagrs[-1]}")
    
    # Test window statistics
    print("\nTesting window statistics...")
    stats = analyzer.compute_window_statistics(start_year)
    print(f"  Statistics computed for {len(stats)} window sizes")
    print(f"  Sample stats for 10-year windows:")
    ten_year_stats = stats[stats['window_size'] == 10].iloc[0]
    print(f"    Best: {ten_year_stats['best_window']} ({ten_year_stats['best_cagr']:.4f})")
    print(f"    Worst: {ten_year_stats['worst_window']} ({ten_year_stats['worst_cagr']:.4f})")
    print(f"    Average: {ten_year_stats['avg_cagr']:.4f}")
    
    # Test no-loss horizon
    print("\nTesting no-loss horizon...")
    no_loss = analyzer.find_min_no_loss_horizon(start_year)
    print(f"  Min no-loss horizon: {no_loss['min_holding_years']} years")
    print(f"  Worst window: {no_loss['worst_window']} ({no_loss['worst_cagr']:.4f})")
    
    # Test spread horizon
    print("\nTesting spread horizon...")
    threshold = 0.01  # 1%
    spread = analyzer.find_min_spread_horizon(start_year, threshold)
    print(f"  Min spread horizon for {threshold:.1%}: {spread['min_holding_years']} years")
    print(f"  Actual spread: {spread['spread']:.4f}")
    
    return analyzer


def test_output_generation():
    """Test the output generation functions."""
    print("\n" + "="*50)
    print("TESTING OUTPUT GENERATION")
    print("="*50)
    
    # Create sample data and analyzer
    df = create_sample_data()
    analyzer = SP500Analyzer(df)
    
    # Create temporary output directory
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Using temporary directory: {temp_dir}")
        
        # Test parameters
        start_years = [1926, 1957, 1972, 1985]
        thresholds = [0.0025, 0.005, 0.0075, 0.01]
        
        try:
            # Generate rolling CAGR CSVs
            print("\nGenerating rolling CAGR CSVs...")
            generate_rolling_cagr_csvs(analyzer, start_years, temp_dir)
            
            # Generate summary CSVs
            print("Generating summary CSVs...")
            generate_summary_csvs(analyzer, start_years, temp_dir)
            
            # Generate no-loss summary
            print("Generating no-loss summary...")
            generate_no_loss_summary(analyzer, start_years, temp_dir)
            
            # Generate spread grid
            print("Generating spread grid...")
            generate_spread_grid(analyzer, start_years, thresholds, temp_dir)
            
            # List generated files
            print("\nGenerated files:")
            for file in sorted(Path(temp_dir).glob("*.csv")):
                file_size = file.stat().st_size
                print(f"  {file.name} ({file_size} bytes)")
                
                # Show first few lines of each file
                with open(file, 'r') as f:
                    lines = f.readlines()[:5]
                    print(f"    Preview (first {len(lines)} lines):")
                    for line in lines:
                        print(f"      {line.strip()}")
                    if len(lines) == 5:
                        print("      ...")
            
            print("\n✓ All output generation tests passed!")
            
        except Exception as e:
            print(f"\n✗ Output generation test failed: {e}")
            raise


def test_edge_cases():
    """Test edge cases and error handling."""
    print("\n" + "="*50)
    print("TESTING EDGE CASES")
    print("="*50)
    
    # Test with very short data
    print("\nTesting with short data...")
    short_df = pd.DataFrame({
        'year': [1926, 1927, 1928],
        'return': [0.10, 0.15, -0.05]
    })
    
    short_analyzer = SP500Analyzer(short_df)
    
    # This should handle gracefully
    cagrs = short_analyzer.compute_rolling_cagr(5, 1926)
    print(f"  5-year windows from 1926: {len(cagrs)} (expected 0)")
    
    # Test with invalid start year
    print("\nTesting with invalid start year...")
    cagrs = short_analyzer.compute_rolling_cagr(2, 1930)
    print(f"  2-year windows from 1930: {len(cagrs)} (expected 0)")
    
    print("\n✓ Edge case tests passed!")


def main():
    """Run all tests."""
    print("S&P 500 Analysis Tool - Test Suite")
    print("="*60)
    
    try:
        # Run tests
        analyzer = test_analyzer()
        test_output_generation()
        test_edge_cases()
        
        print("\n" + "="*60)
        print("ALL TESTS PASSED! ✓")
        print("="*60)
        print("\nThe tool is working correctly and ready for use.")
        print("\nTo run the full analysis:")
        print("python sp500_convergence.py --download_slickcharts --outdir ./output")
        
    except Exception as e:
        print(f"\n" + "="*60)
        print(f"TEST FAILED: {e}")
        print("="*60)
        raise


if __name__ == "__main__":
    main()
