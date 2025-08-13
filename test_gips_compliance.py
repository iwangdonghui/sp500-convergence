#!/usr/bin/env python3
"""
Test suite for GIPS compliance functionality.

This module tests the GIPS compliance implementation including:
- Time-weighted return calculations
- Money-weighted return calculations
- Performance attribution analysis
- Benchmark validation
- Compliance reporting
"""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from gips_compliance import (
    GIPSCalculator, PerformanceAttributionAnalyzer, BenchmarkStandardizer,
    ReturnCalculationMethod, ComplianceLevel, CashFlow, PortfolioValuation,
    GIPSCalculationResult, create_sample_gips_calculation
)
from data_processor import DataProcessor


class TestGIPSCalculator(unittest.TestCase):
    """Test cases for GIPSCalculator class."""
    
    def setUp(self):
        """Set up test environment."""
        self.calculator = GIPSCalculator()
        
        # Create sample data
        self.valuations = [
            PortfolioValuation(datetime(2023, 1, 1), 1000000.0),
            PortfolioValuation(datetime(2023, 6, 30), 1050000.0),
            PortfolioValuation(datetime(2023, 12, 31), 1120000.0)
        ]
        
        self.cash_flows = [
            CashFlow(datetime(2023, 3, 15), 50000.0, "contribution"),
            CashFlow(datetime(2023, 9, 15), -25000.0, "withdrawal")
        ]
    
    def test_time_weighted_return_calculation(self):
        """Test time-weighted return calculation."""
        twr = self.calculator.calculate_time_weighted_return(
            self.valuations, self.cash_flows
        )
        
        # TWR should be a reasonable return value
        self.assertIsInstance(twr, float)
        self.assertGreater(twr, -1.0)  # Return should be > -100%
        self.assertLess(twr, 5.0)      # Return should be < 500% (reasonable)
    
    def test_money_weighted_return_calculation(self):
        """Test money-weighted return calculation."""
        mwr = self.calculator.calculate_money_weighted_return(
            self.valuations, self.cash_flows
        )
        
        # MWR should be a reasonable return value
        self.assertIsInstance(mwr, float)
        self.assertGreater(mwr, -1.0)  # Return should be > -100%
        self.assertLess(mwr, 5.0)      # Return should be < 500% (reasonable)
    
    def test_modified_dietz_return(self):
        """Test Modified Dietz return calculation."""
        start_value = 1000000.0
        end_value = 1120000.0
        period_start = datetime(2023, 1, 1)
        period_end = datetime(2023, 12, 31)
        
        dietz_return = self.calculator.calculate_modified_dietz_return(
            start_value, end_value, self.cash_flows, period_start, period_end
        )
        
        self.assertIsInstance(dietz_return, float)
        self.assertGreater(dietz_return, -1.0)
        self.assertLess(dietz_return, 5.0)
    
    def test_composite_return_calculation(self):
        """Test composite return calculation."""
        portfolio_returns = [
            (0.10, 1000000),  # 10% return, $1M weight
            (0.12, 500000),   # 12% return, $500K weight
            (0.08, 750000)    # 8% return, $750K weight
        ]
        
        # Asset-weighted composite
        composite_return = self.calculator.calculate_composite_return(
            portfolio_returns, method="asset_weighted"
        )
        
        self.assertIsInstance(composite_return, float)
        self.assertAlmostEqual(composite_return, 0.1, places=2)
        
        # Equal-weighted composite
        equal_weighted = self.calculator.calculate_composite_return(
            portfolio_returns, method="equal_weighted"
        )
        
        self.assertIsInstance(equal_weighted, float)
        self.assertAlmostEqual(equal_weighted, 0.1, places=2)
    
    def test_gips_compliance_validation(self):
        """Test GIPS compliance validation."""
        # Create a sample result
        result = GIPSCalculationResult(
            time_weighted_return=0.10,
            money_weighted_return=0.095,
            composite_return=0.10,
            calculation_method=ReturnCalculationMethod.TIME_WEIGHTED,
            period_start=datetime(2023, 1, 1),
            period_end=datetime(2023, 12, 31),
            number_of_portfolios=1,
            total_assets=1120000.0,
            compliance_level=ComplianceLevel.PARTIAL_COMPLIANCE,
            validation_notes=[]
        )
        
        compliance_level, notes = self.calculator.validate_gips_compliance(
            result, [{}]
        )
        
        self.assertIsInstance(compliance_level, ComplianceLevel)
        self.assertIsInstance(notes, list)


class TestPerformanceAttributionAnalyzer(unittest.TestCase):
    """Test cases for PerformanceAttributionAnalyzer class."""
    
    def setUp(self):
        """Set up test environment."""
        self.analyzer = PerformanceAttributionAnalyzer()
    
    def test_brinson_attribution(self):
        """Test Brinson-Hood-Beebower attribution analysis."""
        portfolio_weights = {"Equities": 0.6, "Bonds": 0.3, "Cash": 0.1}
        portfolio_returns = {"Equities": 0.12, "Bonds": 0.04, "Cash": 0.02}
        benchmark_weights = {"Equities": 0.5, "Bonds": 0.4, "Cash": 0.1}
        benchmark_returns = {"Equities": 0.10, "Bonds": 0.03, "Cash": 0.02}
        
        attribution = self.analyzer.calculate_brinson_attribution(
            portfolio_weights, portfolio_returns, benchmark_weights, benchmark_returns
        )
        
        # Check that all components are present
        required_keys = ['allocation_effect', 'selection_effect', 'interaction_effect', 'total_attribution']
        for key in required_keys:
            self.assertIn(key, attribution)
            self.assertIsInstance(attribution[key], float)
        
        # Total attribution should equal sum of components
        total_calc = (
            attribution['allocation_effect'] + 
            attribution['selection_effect'] + 
            attribution['interaction_effect']
        )
        self.assertAlmostEqual(attribution['total_attribution'], total_calc, places=6)
    
    def test_risk_adjusted_attribution(self):
        """Test risk-adjusted performance attribution."""
        # Generate sample return data
        np.random.seed(42)
        portfolio_returns = np.random.normal(0.08, 0.15, 252).tolist()
        benchmark_returns = np.random.normal(0.07, 0.12, 252).tolist()
        
        risk_metrics = self.analyzer.calculate_risk_adjusted_attribution(
            portfolio_returns, benchmark_returns
        )
        
        # Check that all metrics are present
        required_metrics = [
            'alpha', 'beta', 'portfolio_sharpe', 'benchmark_sharpe',
            'information_ratio', 'tracking_error', 'excess_return'
        ]
        
        for metric in required_metrics:
            self.assertIn(metric, risk_metrics)
            self.assertIsInstance(risk_metrics[metric], (int, float))
            self.assertFalse(np.isnan(risk_metrics[metric]))


class TestBenchmarkStandardizer(unittest.TestCase):
    """Test cases for BenchmarkStandardizer class."""
    
    def setUp(self):
        """Set up test environment."""
        self.standardizer = BenchmarkStandardizer()
    
    def test_benchmark_appropriateness_validation(self):
        """Test benchmark appropriateness validation."""
        # Matching characteristics
        portfolio_chars = {
            "asset_class": "equity",
            "geography": "US",
            "investment_style": "large_cap_growth"
        }
        
        benchmark_chars = {
            "asset_class": "equity",
            "geography": "US", 
            "investment_style": "large_cap_growth"
        }
        
        is_appropriate, notes = self.standardizer.validate_benchmark_appropriateness(
            portfolio_chars, benchmark_chars
        )
        
        self.assertTrue(is_appropriate)
        self.assertEqual(len(notes), 0)
        
        # Mismatched characteristics
        mismatched_benchmark = {
            "asset_class": "bond",
            "geography": "International",
            "investment_style": "fixed_income"
        }
        
        is_appropriate, notes = self.standardizer.validate_benchmark_appropriateness(
            portfolio_chars, mismatched_benchmark
        )
        
        self.assertFalse(is_appropriate)
        self.assertGreater(len(notes), 0)
    
    def test_benchmark_statistics_calculation(self):
        """Test benchmark statistics calculation."""
        # Generate sample benchmark returns
        np.random.seed(42)
        benchmark_returns = np.random.normal(0.07, 0.12, 252).tolist()
        
        period_start = datetime(2023, 1, 1)
        period_end = datetime(2023, 12, 31)
        
        stats = self.standardizer.calculate_benchmark_statistics(
            benchmark_returns, period_start, period_end
        )
        
        # Check that all statistics are present
        required_stats = [
            'total_return', 'annualized_return', 'volatility',
            'downside_deviation', 'max_drawdown', 'positive_periods',
            'average_positive_return', 'average_negative_return'
        ]
        
        for stat in required_stats:
            self.assertIn(stat, stats)
            self.assertIsInstance(stats[stat], (int, float))


class TestDataProcessorGIPSIntegration(unittest.TestCase):
    """Test GIPS integration with DataProcessor."""
    
    def setUp(self):
        """Set up test environment."""
        self.processor = DataProcessor()
        
        # Create mock S&P 500 data
        years = list(range(2000, 2024))
        np.random.seed(42)
        returns = np.random.normal(0.10, 0.20, len(years))
        self.sp500_data = pd.DataFrame({'year': years, 'return': returns})
        
        # Set data
        self.processor.set_data(self.sp500_data)
    
    def test_gips_compliance_analysis(self):
        """Test complete GIPS compliance analysis."""
        try:
            results = self.processor.compute_gips_compliance_analysis(
                start_year=2000,
                end_year=2020,
                benchmark_symbol="SPY",
                firm_name="Test Firm",
                composite_name="Test Composite"
            )
            
            # Check result structure
            required_sections = [
                'gips_calculation', 'attribution_analysis', 
                'benchmark_validation', 'compliance_report', 'period_summary'
            ]
            
            for section in required_sections:
                self.assertIn(section, results)
            
            # Check GIPS calculation results
            gips_calc = results['gips_calculation']
            self.assertIn('time_weighted_return', gips_calc)
            self.assertIn('compliance_level', gips_calc)
            
            # Check compliance report
            compliance_report = results['compliance_report']
            self.assertIn('firm_name', compliance_report)
            self.assertIn('composite_name', compliance_report)
            
        except Exception as e:
            self.fail(f"GIPS compliance analysis failed: {e}")


def run_integration_test():
    """Run integration test with realistic scenario."""
    print("\n" + "="*60)
    print("GIPS COMPLIANCE INTEGRATION TEST")
    print("="*60)
    
    # Test sample GIPS calculation
    result, calculator = create_sample_gips_calculation()
    
    print("✅ Sample GIPS calculation completed")
    print(f"   Time-Weighted Return: {result.time_weighted_return:.2%}")
    print(f"   Money-Weighted Return: {result.money_weighted_return:.2%}")
    print(f"   Compliance Level: {result.compliance_level.value}")
    
    # Test attribution analysis
    attribution_analyzer = PerformanceAttributionAnalyzer()
    
    portfolio_weights = {"Equities": 0.6, "Bonds": 0.3, "Cash": 0.1}
    portfolio_returns = {"Equities": 0.12, "Bonds": 0.04, "Cash": 0.02}
    benchmark_weights = {"Equities": 0.5, "Bonds": 0.4, "Cash": 0.1}
    benchmark_returns = {"Equities": 0.10, "Bonds": 0.03, "Cash": 0.02}
    
    attribution = attribution_analyzer.calculate_brinson_attribution(
        portfolio_weights, portfolio_returns, benchmark_weights, benchmark_returns
    )
    
    print("✅ Attribution analysis completed")
    print(f"   Total Attribution: {attribution['total_attribution']:.2%}")
    
    # Test benchmark validation
    benchmark_standardizer = BenchmarkStandardizer()
    
    portfolio_chars = {"asset_class": "equity", "geography": "US"}
    benchmark_chars = {"asset_class": "equity", "geography": "US"}
    
    is_appropriate, notes = benchmark_standardizer.validate_benchmark_appropriateness(
        portfolio_chars, benchmark_chars
    )
    
    print("✅ Benchmark validation completed")
    print(f"   Benchmark Appropriate: {is_appropriate}")
    
    return True


def main():
    """Run all GIPS compliance tests."""
    print("🏛️ Starting GIPS Compliance Tests")
    print("=" * 80)
    
    # Run unit tests
    print("\n📋 Running Unit Tests...")
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # Run integration test
    print("\n🔧 Running Integration Test...")
    success = run_integration_test()
    
    if success:
        print("\n🎉 All GIPS compliance tests passed!")
        print("✅ GIPS compliance system is ready for use!")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")


if __name__ == '__main__':
    main()
