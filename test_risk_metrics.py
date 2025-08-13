#!/usr/bin/env python3
"""
Test suite for risk metrics calculations.

This module tests the accuracy of risk metrics calculations against known values
and validates the implementation against industry standards.
"""

import unittest
import numpy as np
import pandas as pd
from risk_metrics import RiskMetricsCalculator, RiskFreeRateProvider, calculate_rolling_risk_metrics
from sp500_convergence import SP500Analyzer


class TestRiskMetricsCalculator(unittest.TestCase):
    """Test cases for RiskMetricsCalculator class."""
    
    def setUp(self):
        """Set up test data."""
        # Simple test data with known characteristics
        self.simple_returns = [0.10, 0.15, -0.05, 0.20, 0.08]
        self.risk_free_rates = [0.02, 0.02, 0.02, 0.02, 0.02]
        
        # More realistic S&P 500-like data
        np.random.seed(42)
        self.realistic_returns = [
            0.10, 0.15, -0.05, 0.20, 0.08, -0.10, 0.25, 0.12, -0.02, 0.18,
            0.06, -0.08, 0.22, 0.14, -0.15, 0.30, 0.05, 0.11, -0.03, 0.16
        ]
        self.realistic_rf_rates = [0.03] * len(self.realistic_returns)
    
    def test_sharpe_ratio_calculation(self):
        """Test Sharpe ratio calculation."""
        calculator = RiskMetricsCalculator(self.simple_returns, self.risk_free_rates)
        sharpe = calculator.sharpe_ratio()
        
        # Manual calculation for verification
        excess_returns = np.array(self.simple_returns) - np.array(self.risk_free_rates)
        expected_sharpe = np.mean(excess_returns) / np.std(excess_returns, ddof=1)
        
        self.assertAlmostEqual(sharpe, expected_sharpe, places=6)
        self.assertIsInstance(sharpe, float)
        self.assertFalse(np.isnan(sharpe))
    
    def test_sortino_ratio_calculation(self):
        """Test Sortino ratio calculation."""
        calculator = RiskMetricsCalculator(self.simple_returns, self.risk_free_rates)
        sortino = calculator.sortino_ratio()
        
        # Sortino should be higher than Sharpe for same data (less penalty for upside volatility)
        sharpe = calculator.sharpe_ratio()
        self.assertGreater(sortino, sharpe)
        self.assertIsInstance(sortino, float)
        self.assertFalse(np.isnan(sortino))
    
    def test_maximum_drawdown_calculation(self):
        """Test maximum drawdown calculation."""
        # Use data with known drawdown
        returns_with_drawdown = [0.10, 0.15, -0.20, -0.10, 0.05, 0.20]
        calculator = RiskMetricsCalculator(returns_with_drawdown)
        
        max_dd_info = calculator.maximum_drawdown()
        max_drawdown = max_dd_info['max_drawdown']
        
        # Verify drawdown is positive and reasonable
        self.assertGreater(max_drawdown, 0)
        self.assertLess(max_drawdown, 1)  # Should be less than 100%
        self.assertIsInstance(max_drawdown, float)
        
        # Check that peak comes before trough
        peak_idx = max_dd_info['peak_index']
        trough_idx = max_dd_info['trough_index']
        self.assertLess(peak_idx, trough_idx)
    
    def test_calmar_ratio_calculation(self):
        """Test Calmar ratio calculation."""
        calculator = RiskMetricsCalculator(self.realistic_returns)
        calmar = calculator.calmar_ratio()
        
        # Calmar should be positive for positive CAGR
        self.assertGreater(calmar, 0)
        self.assertIsInstance(calmar, float)
        self.assertFalse(np.isnan(calmar))
    
    def test_volatility_calculation(self):
        """Test volatility calculation."""
        calculator = RiskMetricsCalculator(self.simple_returns)
        volatility = calculator.volatility()
        
        # Manual calculation
        expected_volatility = np.std(self.simple_returns, ddof=1)
        
        self.assertAlmostEqual(volatility, expected_volatility, places=6)
        self.assertGreater(volatility, 0)
    
    def test_var_calculation(self):
        """Test Value at Risk calculation."""
        calculator = RiskMetricsCalculator(self.realistic_returns)
        var_95 = calculator.var_historical(0.05)
        var_99 = calculator.var_historical(0.01)
        
        # VaR should be positive (representing loss)
        self.assertGreater(var_95, 0)
        self.assertGreater(var_99, 0)
        
        # 99% VaR should be higher than 95% VaR
        self.assertGreater(var_99, var_95)
    
    def test_cvar_calculation(self):
        """Test Conditional Value at Risk calculation."""
        calculator = RiskMetricsCalculator(self.realistic_returns)
        cvar_95 = calculator.cvar_historical(0.05)
        var_95 = calculator.var_historical(0.05)
        
        # CVaR should be higher than VaR
        self.assertGreater(cvar_95, var_95)
        self.assertGreater(cvar_95, 0)
    
    def test_all_metrics(self):
        """Test that all_metrics returns complete dictionary."""
        calculator = RiskMetricsCalculator(self.realistic_returns, self.realistic_rf_rates)
        metrics = calculator.all_metrics()
        
        expected_keys = [
            'sharpe_ratio', 'sortino_ratio', 'calmar_ratio', 'volatility',
            'max_drawdown', 'var_95', 'cvar_95', 'var_99', 'cvar_99'
        ]
        
        for key in expected_keys:
            self.assertIn(key, metrics)
            self.assertIsInstance(metrics[key], (int, float))
    
    def test_edge_cases(self):
        """Test edge cases and error handling."""
        # Test with insufficient data
        short_returns = [0.10]
        calculator = RiskMetricsCalculator(short_returns)
        
        sharpe = calculator.sharpe_ratio()
        self.assertTrue(np.isnan(sharpe))
        
        # Test with zero volatility
        constant_returns = [0.05, 0.05, 0.05, 0.05]
        calculator = RiskMetricsCalculator(constant_returns)
        
        sharpe = calculator.sharpe_ratio()
        self.assertTrue(np.isnan(sharpe))  # Should be NaN due to zero volatility


class TestRiskFreeRateProvider(unittest.TestCase):
    """Test cases for RiskFreeRateProvider class."""
    
    def setUp(self):
        """Set up test provider."""
        self.provider = RiskFreeRateProvider()
    
    def test_get_risk_free_rate(self):
        """Test risk-free rate retrieval."""
        rf_data = self.provider.get_risk_free_rate(2000, 2005)
        
        self.assertIsInstance(rf_data, pd.DataFrame)
        self.assertIn('year', rf_data.columns)
        self.assertIn('risk_free_rate', rf_data.columns)
        self.assertEqual(len(rf_data), 6)  # 2000-2005 inclusive
        
        # Check that rates are reasonable
        rates = rf_data['risk_free_rate'].tolist()
        for rate in rates:
            self.assertGreater(rate, 0)
            self.assertLess(rate, 0.20)  # Less than 20%


class TestSP500AnalyzerRiskMetrics(unittest.TestCase):
    """Test cases for SP500Analyzer risk metrics integration."""
    
    def setUp(self):
        """Set up test analyzer with sample data."""
        # Create sample S&P 500 data
        years = list(range(1990, 2021))
        np.random.seed(42)
        returns = np.random.normal(0.10, 0.20, len(years))  # 10% mean, 20% volatility
        
        self.data = pd.DataFrame({
            'year': years,
            'return': returns
        })
        
        self.analyzer = SP500Analyzer(self.data)
    
    def test_compute_risk_metrics(self):
        """Test risk metrics computation for entire period."""
        metrics = self.analyzer.compute_risk_metrics(1990)
        
        # Check that all expected metrics are present
        expected_keys = [
            'sharpe_ratio', 'sortino_ratio', 'calmar_ratio', 'volatility',
            'max_drawdown', 'cagr', 'start_year', 'end_year', 'period_length'
        ]
        
        for key in expected_keys:
            self.assertIn(key, metrics)
        
        # Check period information
        self.assertEqual(metrics['start_year'], 1990)
        self.assertEqual(metrics['end_year'], 2020)
        self.assertEqual(metrics['period_length'], 31)
    
    def test_compute_risk_metrics_with_window(self):
        """Test risk metrics computation for specific window."""
        metrics = self.analyzer.compute_risk_metrics(1990, window_size=10)
        
        self.assertEqual(metrics['start_year'], 1990)
        self.assertEqual(metrics['end_year'], 1999)
        self.assertEqual(metrics['period_length'], 10)
    
    def test_compute_rolling_risk_metrics(self):
        """Test rolling risk metrics computation."""
        rolling_metrics = self.analyzer.compute_rolling_risk_metrics(1990, window_size=10)
        
        # Should have 22 windows (31 years - 10 + 1)
        expected_windows = len(self.data) - 10 + 1
        self.assertEqual(len(rolling_metrics), expected_windows)
        
        # Check first and last windows
        first_window = rolling_metrics[0]
        last_window = rolling_metrics[-1]
        
        self.assertEqual(first_window['start_year'], 1990)
        self.assertEqual(first_window['end_year'], 1999)
        self.assertEqual(last_window['start_year'], 2011)
        self.assertEqual(last_window['end_year'], 2020)
    
    def test_invalid_start_year(self):
        """Test handling of invalid start year."""
        metrics = self.analyzer.compute_risk_metrics(1980)  # Before data starts
        self.assertEqual(metrics, {})
        
        rolling_metrics = self.analyzer.compute_rolling_risk_metrics(1980, 10)
        self.assertEqual(rolling_metrics, [])


class TestRollingRiskMetrics(unittest.TestCase):
    """Test cases for rolling risk metrics calculation."""
    
    def test_calculate_rolling_risk_metrics(self):
        """Test rolling risk metrics calculation function."""
        returns = [0.10, 0.15, -0.05, 0.20, 0.08, -0.10, 0.25]
        window_size = 3
        
        rolling_metrics = calculate_rolling_risk_metrics(returns, window_size)
        
        # Should have 5 windows (7 returns - 3 + 1)
        self.assertEqual(len(rolling_metrics), 5)
        
        # Check that each window has the expected metrics
        for metrics in rolling_metrics:
            self.assertIn('sharpe_ratio', metrics)
            self.assertIn('volatility', metrics)
            self.assertIn('window_start_index', metrics)
            self.assertIn('window_end_index', metrics)


if __name__ == '__main__':
    # Run all tests
    unittest.main(verbosity=2)
