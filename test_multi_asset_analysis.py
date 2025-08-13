#!/usr/bin/env python3
"""
Test suite for multi-asset analysis functionality.

This module tests the multi-asset analysis engine including:
- Asset data loading and validation
- Correlation and covariance analysis
- Portfolio optimization
- Efficient frontier calculation
"""

import unittest
import pandas as pd
import numpy as np
from multi_asset_engine import (
    MultiAssetAnalyzer, AssetInfo, AssetClass, MockDataProvider, ASSET_UNIVERSE
)
from data_processor import DataProcessor


class TestMultiAssetEngine(unittest.TestCase):
    """Test cases for MultiAssetAnalyzer class."""
    
    def setUp(self):
        """Set up test environment."""
        self.analyzer = MultiAssetAnalyzer()

        # Add all test assets from universe
        for symbol, asset_info in ASSET_UNIVERSE.items():
            self.analyzer.add_asset(asset_info)

        self.test_symbols = ['SPY', 'TLT', 'GLD']
        self.start_year = 2000
        self.end_year = 2020
    
    def test_asset_info_creation(self):
        """Test AssetInfo dataclass creation and validation."""
        # Valid asset info
        asset = AssetInfo(
            symbol='TEST',
            name='Test Asset',
            asset_class=AssetClass.EQUITY,
            description='Test description',
            data_source='test',
            inception_year=2000
        )
        
        self.assertEqual(asset.symbol, 'TEST')
        self.assertEqual(asset.asset_class, AssetClass.EQUITY)
        
        # Invalid asset info (missing required fields)
        with self.assertRaises(ValueError):
            AssetInfo('', '', AssetClass.EQUITY, 'desc', 'source')
    
    def test_mock_data_provider(self):
        """Test mock data provider functionality."""
        provider = MockDataProvider()
        asset_info = ASSET_UNIVERSE['SPY']
        
        data = provider.get_data(asset_info, 2000, 2020)
        
        # Check data structure
        self.assertIsInstance(data, pd.DataFrame)
        self.assertIn('year', data.columns)
        self.assertIn('return', data.columns)
        self.assertEqual(len(data), 21)  # 2000-2020 inclusive
        
        # Check data validation
        self.assertTrue(provider.validate_data(data))
    
    def test_asset_data_loading(self):
        """Test asset data loading and caching."""
        # Load data for SPY
        data = self.analyzer.load_asset_data('SPY', self.start_year, self.end_year)
        
        self.assertIsInstance(data, pd.DataFrame)
        self.assertEqual(len(data), self.end_year - self.start_year + 1)
        
        # Test caching (should return same data)
        data2 = self.analyzer.load_asset_data('SPY', self.start_year, self.end_year)
        pd.testing.assert_frame_equal(data, data2)
        
        # Test invalid asset
        with self.assertRaises(ValueError):
            self.analyzer.load_asset_data('INVALID', self.start_year, self.end_year)
    
    def test_correlation_matrix(self):
        """Test correlation matrix calculation."""
        correlation_matrix = self.analyzer.get_correlation_matrix(
            self.test_symbols, self.start_year, self.end_year
        )
        
        # Check structure
        self.assertIsInstance(correlation_matrix, pd.DataFrame)
        self.assertEqual(correlation_matrix.shape, (3, 3))
        
        # Check diagonal is 1.0
        for i in range(len(self.test_symbols)):
            self.assertAlmostEqual(correlation_matrix.iloc[i, i], 1.0, places=6)
        
        # Check symmetry
        for i in range(len(self.test_symbols)):
            for j in range(len(self.test_symbols)):
                self.assertAlmostEqual(
                    correlation_matrix.iloc[i, j], 
                    correlation_matrix.iloc[j, i], 
                    places=6
                )
    
    def test_covariance_matrix(self):
        """Test covariance matrix calculation."""
        covariance_matrix = self.analyzer.get_covariance_matrix(
            self.test_symbols, self.start_year, self.end_year
        )
        
        # Check structure
        self.assertIsInstance(covariance_matrix, pd.DataFrame)
        self.assertEqual(covariance_matrix.shape, (3, 3))
        
        # Check symmetry
        for i in range(len(self.test_symbols)):
            for j in range(len(self.test_symbols)):
                self.assertAlmostEqual(
                    covariance_matrix.iloc[i, j], 
                    covariance_matrix.iloc[j, i], 
                    places=10
                )
    
    def test_portfolio_metrics(self):
        """Test portfolio metrics calculation."""
        weights = [0.6, 0.3, 0.1]  # SPY, TLT, GLD
        
        metrics = self.analyzer.calculate_portfolio_metrics(
            self.test_symbols, weights, self.start_year, self.end_year
        )
        
        # Check required metrics
        required_metrics = [
            'sharpe_ratio', 'volatility', 'max_drawdown', 
            'portfolio_return', 'portfolio_volatility'
        ]
        
        for metric in required_metrics:
            self.assertIn(metric, metrics)
            self.assertIsInstance(metrics[metric], (int, float))
        
        # Test invalid weights
        with self.assertRaises(ValueError):
            self.analyzer.calculate_portfolio_metrics(
                self.test_symbols, [0.5, 0.3], self.start_year, self.end_year  # Wrong length
            )
        
        with self.assertRaises(ValueError):
            self.analyzer.calculate_portfolio_metrics(
                self.test_symbols, [0.5, 0.3, 0.3], self.start_year, self.end_year  # Don't sum to 1
            )
    
    def test_efficient_frontier(self):
        """Test efficient frontier calculation."""
        frontier = self.analyzer.get_efficient_frontier(
            self.test_symbols, self.start_year, self.end_year, num_portfolios=100
        )
        
        # Check structure
        required_keys = ['returns', 'volatility', 'sharpe_ratio', 'weights']
        for key in required_keys:
            self.assertIn(key, frontier)
            self.assertEqual(len(frontier[key]), 100)
        
        # Check weights sum to 1
        for weights in frontier['weights']:
            self.assertAlmostEqual(sum(weights), 1.0, places=6)
    
    def test_asset_summary(self):
        """Test comprehensive asset summary."""
        summary = self.analyzer.get_asset_summary('SPY', self.start_year, self.end_year)
        
        # Check structure
        required_sections = ['asset_info', 'data_period', 'risk_metrics', 'basic_stats']
        for section in required_sections:
            self.assertIn(section, summary)
        
        # Check asset info
        asset_info = summary['asset_info']
        self.assertEqual(asset_info['symbol'], 'SPY')
        self.assertEqual(asset_info['asset_class'], 'equity')
        
        # Check data period
        data_period = summary['data_period']
        self.assertEqual(data_period['start_year'], self.start_year)
        self.assertEqual(data_period['end_year'], self.end_year)
        
        # Check risk metrics
        risk_metrics = summary['risk_metrics']
        self.assertIn('sharpe_ratio', risk_metrics)
        self.assertIn('max_drawdown', risk_metrics)


class TestDataProcessorMultiAsset(unittest.TestCase):
    """Test cases for DataProcessor multi-asset functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.processor = DataProcessor()
        
        # Create mock S&P 500 data
        years = list(range(2000, 2021))
        returns = np.random.normal(0.10, 0.20, len(years))
        self.sp500_data = pd.DataFrame({'year': years, 'return': returns})
        
        # Set data
        self.processor.set_data(self.sp500_data)
    
    def test_get_available_assets(self):
        """Test getting available assets grouped by class."""
        available_assets = self.processor.get_available_assets()
        
        # Check structure
        self.assertIsInstance(available_assets, dict)
        
        # Check that we have different asset classes
        expected_classes = ['equity', 'bond', 'commodity', 'reit', 'international']
        for asset_class in expected_classes:
            self.assertIn(asset_class, available_assets)
            self.assertIsInstance(available_assets[asset_class], list)
    
    def test_set_selected_assets(self):
        """Test setting selected assets."""
        # Valid assets
        valid_assets = ['SPY', 'TLT', 'GLD']
        self.processor.set_selected_assets(valid_assets)
        self.assertEqual(self.processor.selected_assets, valid_assets)
        
        # Invalid assets
        with self.assertRaises(ValueError):
            self.processor.set_selected_assets(['SPY', 'INVALID'])
    
    def test_multi_asset_analysis(self):
        """Test comprehensive multi-asset analysis."""
        # Set selected assets
        selected_assets = ['SPY', 'TLT', 'GLD']
        self.processor.set_selected_assets(selected_assets)
        
        # Run analysis
        results = self.processor.compute_multi_asset_analysis(2000, 2020)
        
        # Check structure
        expected_sections = ['individual_assets', 'correlation_matrix', 'covariance_matrix', 'asset_class_summary']
        for section in expected_sections:
            self.assertIn(section, results)
        
        # Check individual assets
        individual_assets = results['individual_assets']
        for symbol in selected_assets:
            self.assertIn(symbol, individual_assets)
        
        # Check correlation matrix
        correlation_matrix = results['correlation_matrix']
        self.assertEqual(correlation_matrix.shape, (3, 3))
        
        # Check asset class summary
        asset_class_summary = results['asset_class_summary']
        self.assertIsInstance(asset_class_summary, dict)


def run_integration_test():
    """Run integration test with realistic scenario."""
    print("\n" + "="*60)
    print("MULTI-ASSET ANALYSIS INTEGRATION TEST")
    print("="*60)
    
    # Create processor
    processor = DataProcessor()
    
    # Create mock S&P 500 data
    years = list(range(1990, 2024))
    np.random.seed(42)
    returns = np.random.normal(0.10, 0.20, len(years))
    sp500_data = pd.DataFrame({'year': years, 'return': returns})
    
    # Set data
    processor.set_data(sp500_data)
    
    print("✅ S&P 500 data loaded")
    
    # Get available assets
    available_assets = processor.get_available_assets()
    print(f"✅ Available asset classes: {list(available_assets.keys())}")
    
    # Select diverse portfolio
    selected_assets = ['SPY', 'TLT', 'GLD', 'VNQ', 'EFA']
    processor.set_selected_assets(selected_assets)
    print(f"✅ Selected assets: {selected_assets}")
    
    # Run multi-asset analysis
    try:
        results = processor.compute_multi_asset_analysis(2000, 2023)
        print("✅ Multi-asset analysis completed")
        
        # Display key results
        print(f"\n📊 Analysis Results:")
        print(f"   • Individual assets analyzed: {len(results['individual_assets'])}")
        print(f"   • Correlation matrix shape: {results['correlation_matrix'].shape}")
        print(f"   • Asset classes covered: {len(results['asset_class_summary'])}")
        
        if 'efficient_frontier' in results:
            frontier = results['efficient_frontier']
            max_sharpe_idx = np.argmax(frontier['sharpe_ratio'])
            print(f"   • Efficient frontier portfolios: {len(frontier['returns'])}")
            print(f"   • Best Sharpe ratio: {frontier['sharpe_ratio'][max_sharpe_idx]:.3f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("🚀 Starting Multi-Asset Analysis Tests")
    print("=" * 80)
    
    # Run unit tests
    print("\n📋 Running Unit Tests...")
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # Run integration test
    print("\n🔧 Running Integration Test...")
    success = run_integration_test()
    
    if success:
        print("\n🎉 All tests passed!")
        print("✅ Multi-asset analysis system is ready for use!")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")


if __name__ == '__main__':
    main()
