#!/usr/bin/env python3
"""
Test script for professional report generation functionality.

This script tests the PDF and Excel report generation capabilities
to ensure they work correctly with sample data.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import tempfile
import os

from sp500_convergence import SP500Analyzer
from data_processor import DataProcessor
from report_generator import generate_comprehensive_report, ChartExporter


def create_test_data():
    """Create realistic test data for report generation."""
    print("Creating test data...")
    
    # Create sample S&P 500 data (1990-2023)
    years = list(range(1990, 2024))
    np.random.seed(42)
    
    # Generate realistic returns with some volatility
    base_return = 0.10  # 10% average return
    volatility = 0.20   # 20% volatility
    
    returns = []
    for i, year in enumerate(years):
        # Add some market cycles
        if year in [2000, 2001, 2002]:  # Dot-com crash
            ret = np.random.normal(-0.10, 0.25)
        elif year in [2008, 2009]:  # Financial crisis
            ret = np.random.normal(-0.20, 0.30)
        elif year == 2020:  # COVID impact
            ret = np.random.normal(0.15, 0.35)
        else:
            ret = np.random.normal(base_return, volatility)
        
        returns.append(ret)
    
    data = pd.DataFrame({
        'year': years,
        'return': returns
    })
    
    print(f"Created {len(data)} years of test data ({data['year'].min()}-{data['year'].max()})")
    return data


def test_pdf_report_generation():
    """Test PDF report generation."""
    print("\n" + "="*60)
    print("TESTING PDF REPORT GENERATION")
    print("="*60)
    
    # Create test data and analyzer
    data = create_test_data()
    analyzer = SP500Analyzer(data)
    
    # Create data processor
    processor = DataProcessor()
    processor.set_data(data)
    
    try:
        print("Generating PDF report...")
        pdf_data = processor.generate_professional_report('pdf')
        
        # Save to temporary file for verification
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            tmp_file.write(pdf_data)
            pdf_path = tmp_file.name
        
        # Check file size and existence
        file_size = os.path.getsize(pdf_path)
        print(f"✅ PDF report generated successfully!")
        print(f"   File size: {file_size:,} bytes")
        print(f"   Temporary file: {pdf_path}")
        
        # Clean up
        os.unlink(pdf_path)
        
        return True
        
    except Exception as e:
        print(f"❌ PDF report generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_excel_report_generation():
    """Test Excel report generation."""
    print("\n" + "="*60)
    print("TESTING EXCEL REPORT GENERATION")
    print("="*60)
    
    # Create test data and analyzer
    data = create_test_data()
    analyzer = SP500Analyzer(data)
    
    # Create data processor
    processor = DataProcessor()
    processor.set_data(data)
    
    try:
        print("Generating Excel report...")
        excel_data = processor.generate_professional_report('excel')
        
        # Save to temporary file for verification
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_file:
            tmp_file.write(excel_data)
            excel_path = tmp_file.name
        
        # Check file size and existence
        file_size = os.path.getsize(excel_path)
        print(f"✅ Excel report generated successfully!")
        print(f"   File size: {file_size:,} bytes")
        print(f"   Temporary file: {excel_path}")
        
        # Verify Excel file can be opened
        import openpyxl
        workbook = openpyxl.load_workbook(excel_path)
        sheet_names = workbook.sheetnames
        print(f"   Sheets: {sheet_names}")
        
        # Clean up
        os.unlink(excel_path)
        
        return True
        
    except Exception as e:
        print(f"❌ Excel report generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_chart_export():
    """Test chart export functionality."""
    print("\n" + "="*60)
    print("TESTING CHART EXPORT")
    print("="*60)
    
    # Create test data and analyzer
    data = create_test_data()
    analyzer = SP500Analyzer(data)
    
    # Create data processor
    processor = DataProcessor()
    processor.set_data(data)
    
    try:
        print("Exporting risk metrics chart...")
        chart_data = processor.export_chart('risk_metrics', 'png')
        
        # Save to temporary file for verification
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            tmp_file.write(chart_data)
            chart_path = tmp_file.name
        
        # Check file size and existence
        file_size = os.path.getsize(chart_path)
        print(f"✅ Chart export successful!")
        print(f"   File size: {file_size:,} bytes")
        print(f"   Temporary file: {chart_path}")
        
        # Clean up
        os.unlink(chart_path)
        
        return True
        
    except Exception as e:
        print(f"❌ Chart export failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_comprehensive_report_function():
    """Test the comprehensive report generation function directly."""
    print("\n" + "="*60)
    print("TESTING COMPREHENSIVE REPORT FUNCTION")
    print("="*60)
    
    # Create mock analysis results
    analysis_results = {
        'risk_metrics': {
            1990: {
                'overall': {
                    'cagr': 0.10,
                    'sharpe_ratio': 0.5,
                    'sortino_ratio': 0.7,
                    'calmar_ratio': 0.3,
                    'volatility': 0.20,
                    'max_drawdown': 0.15,
                    'var_95': 0.08,
                    'cvar_95': 0.12
                }
            },
            2000: {
                'overall': {
                    'cagr': 0.08,
                    'sharpe_ratio': 0.4,
                    'sortino_ratio': 0.6,
                    'calmar_ratio': 0.25,
                    'volatility': 0.22,
                    'max_drawdown': 0.18,
                    'var_95': 0.10,
                    'cvar_95': 0.15
                }
            }
        }
    }
    
    config = {
        'start_years': [1990, 2000],
        'windows': [5, 10, 15, 20],
        'thresholds': [0.005, 0.01]
    }
    
    try:
        # Test PDF generation
        print("Testing direct PDF generation...")
        pdf_data = generate_comprehensive_report(analysis_results, config, 'pdf')
        print(f"✅ Direct PDF generation successful! Size: {len(pdf_data):,} bytes")
        
        # Test Excel generation
        print("Testing direct Excel generation...")
        excel_data = generate_comprehensive_report(analysis_results, config, 'excel')
        print(f"✅ Direct Excel generation successful! Size: {len(excel_data):,} bytes")
        
        return True
        
    except Exception as e:
        print(f"❌ Direct report generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all report generation tests."""
    print("🚀 Starting Professional Report Generation Tests")
    print("=" * 80)
    
    tests = [
        ("Comprehensive Report Function", test_comprehensive_report_function),
        ("PDF Report Generation", test_pdf_report_generation),
        ("Excel Report Generation", test_excel_report_generation),
        ("Chart Export", test_chart_export),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All report generation tests passed!")
        print("✅ Professional report system is ready for use!")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
    
    return passed == total


if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
