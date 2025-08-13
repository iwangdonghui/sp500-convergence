"""
Multi-Asset Analysis Engine for S&P 500 Analysis Tool

This module extends the analysis capabilities to support multiple asset classes including:
- Stock indices (S&P 500, NASDAQ, Dow Jones, Russell 2000)
- Bond indices (10-Year Treasury, Corporate Bonds, High Yield)
- Commodity indices (Gold, Oil, Agricultural)
- Real Estate (REITs)
- International markets (Europe, Asia, Emerging Markets)

Author: Professional Investment Analysis Team
"""

import pandas as pd
import numpy as np
import requests
import io
from typing import Dict, List, Tuple, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import warnings

# Import existing modules
from risk_metrics import RiskMetricsCalculator, RiskFreeRateProvider
from sp500_convergence import SP500Analyzer

warnings.filterwarnings('ignore')


class AssetClass(Enum):
    """Asset class enumeration."""
    EQUITY = "equity"
    BOND = "bond"
    COMMODITY = "commodity"
    REIT = "reit"
    INTERNATIONAL = "international"
    ALTERNATIVE = "alternative"


@dataclass
class AssetInfo:
    """Asset information container."""
    symbol: str
    name: str
    asset_class: AssetClass
    description: str
    data_source: str
    currency: str = "USD"
    inception_year: int = 1926
    
    def __post_init__(self):
        """Validate asset information."""
        if not self.symbol or not self.name:
            raise ValueError("Symbol and name are required")
        if self.inception_year < 1850 or self.inception_year > datetime.now().year:
            raise ValueError("Invalid inception year")


class AssetDataProvider:
    """Base class for asset data providers."""
    
    def __init__(self):
        self.cache = {}
    
    def get_data(self, asset_info: AssetInfo, start_year: int, end_year: int) -> pd.DataFrame:
        """
        Get historical data for an asset.
        
        Args:
            asset_info: Asset information
            start_year: Starting year
            end_year: Ending year
            
        Returns:
            DataFrame with columns: year, return, [additional metrics]
        """
        raise NotImplementedError("Subclasses must implement get_data method")
    
    def validate_data(self, data: pd.DataFrame) -> bool:
        """Validate data format."""
        required_columns = ['year', 'return']
        return all(col in data.columns for col in required_columns)


class MockDataProvider(AssetDataProvider):
    """Mock data provider for testing and demonstration."""
    
    def get_data(self, asset_info: AssetInfo, start_year: int, end_year: int) -> pd.DataFrame:
        """Generate realistic mock data for different asset classes."""
        years = list(range(max(start_year, asset_info.inception_year), end_year + 1))
        
        # Set random seed based on asset symbol for consistency
        np.random.seed(hash(asset_info.symbol) % 2**32)
        
        # Asset class specific parameters
        params = self._get_asset_parameters(asset_info.asset_class)
        
        returns = []
        for i, year in enumerate(years):
            # Add some market cycles and correlations
            market_factor = self._get_market_factor(year)
            
            # Generate return with asset-specific characteristics
            base_return = params['mean_return'] + market_factor * params['market_beta']
            volatility = params['volatility']
            
            # Add some autocorrelation for bonds and commodities
            if i > 0 and asset_info.asset_class in [AssetClass.BOND, AssetClass.COMMODITY]:
                autocorr = 0.3 * returns[-1]
                base_return += autocorr
            
            annual_return = np.random.normal(base_return, volatility)
            returns.append(annual_return)
        
        data = pd.DataFrame({
            'year': years,
            'return': returns,
            'asset_class': asset_info.asset_class.value,
            'symbol': asset_info.symbol
        })
        
        return data
    
    def _get_asset_parameters(self, asset_class: AssetClass) -> Dict[str, float]:
        """Get asset class specific parameters."""
        params = {
            AssetClass.EQUITY: {
                'mean_return': 0.10,
                'volatility': 0.20,
                'market_beta': 1.0
            },
            AssetClass.BOND: {
                'mean_return': 0.05,
                'volatility': 0.08,
                'market_beta': -0.3
            },
            AssetClass.COMMODITY: {
                'mean_return': 0.06,
                'volatility': 0.25,
                'market_beta': 0.2
            },
            AssetClass.REIT: {
                'mean_return': 0.09,
                'volatility': 0.18,
                'market_beta': 0.8
            },
            AssetClass.INTERNATIONAL: {
                'mean_return': 0.08,
                'volatility': 0.22,
                'market_beta': 0.9
            },
            AssetClass.ALTERNATIVE: {
                'mean_return': 0.12,
                'volatility': 0.15,
                'market_beta': 0.5
            }
        }
        return params.get(asset_class, params[AssetClass.EQUITY])
    
    def _get_market_factor(self, year: int) -> float:
        """Get market factor for specific years (crises, booms)."""
        # Major market events
        if year in [1929, 1930, 1931]:  # Great Depression
            return -0.15
        elif year in [2000, 2001, 2002]:  # Dot-com crash
            return -0.08
        elif year in [2008, 2009]:  # Financial crisis
            return -0.12
        elif year == 2020:  # COVID-19
            return -0.05
        elif year in [1995, 1996, 1997, 1998, 1999]:  # Tech boom
            return 0.05
        elif year in [2013, 2014, 2015, 2016, 2017]:  # Post-crisis recovery
            return 0.03
        else:
            return 0.0


class MultiAssetAnalyzer:
    """Multi-asset analysis engine."""
    
    def __init__(self, data_provider: AssetDataProvider = None):
        """
        Initialize multi-asset analyzer.
        
        Args:
            data_provider: Data provider instance
        """
        self.data_provider = data_provider or MockDataProvider()
        self.assets = {}
        self.data_cache = {}
        self.rf_provider = RiskFreeRateProvider()
    
    def add_asset(self, asset_info: AssetInfo) -> None:
        """Add an asset to the analysis."""
        self.assets[asset_info.symbol] = asset_info
    
    def load_asset_data(self, symbol: str, start_year: int, end_year: int) -> pd.DataFrame:
        """Load data for a specific asset."""
        if symbol not in self.assets:
            raise ValueError(f"Asset {symbol} not found. Add it first using add_asset().")
        
        cache_key = f"{symbol}_{start_year}_{end_year}"
        if cache_key in self.data_cache:
            return self.data_cache[cache_key]
        
        asset_info = self.assets[symbol]
        data = self.data_provider.get_data(asset_info, start_year, end_year)
        
        if not self.data_provider.validate_data(data):
            raise ValueError(f"Invalid data format for asset {symbol}")
        
        self.data_cache[cache_key] = data
        return data
    
    def get_correlation_matrix(self, symbols: List[str], start_year: int, end_year: int) -> pd.DataFrame:
        """Calculate correlation matrix between assets."""
        returns_data = {}
        
        # Load data for all assets
        for symbol in symbols:
            data = self.load_asset_data(symbol, start_year, end_year)
            returns_data[symbol] = data.set_index('year')['return']
        
        # Create aligned DataFrame
        returns_df = pd.DataFrame(returns_data)
        
        # Calculate correlation matrix
        correlation_matrix = returns_df.corr()
        return correlation_matrix
    
    def get_covariance_matrix(self, symbols: List[str], start_year: int, end_year: int) -> pd.DataFrame:
        """Calculate covariance matrix between assets."""
        returns_data = {}
        
        # Load data for all assets
        for symbol in symbols:
            data = self.load_asset_data(symbol, start_year, end_year)
            returns_data[symbol] = data.set_index('year')['return']
        
        # Create aligned DataFrame
        returns_df = pd.DataFrame(returns_data)
        
        # Calculate covariance matrix
        covariance_matrix = returns_df.cov()
        return covariance_matrix
    
    def calculate_portfolio_metrics(self, symbols: List[str], weights: List[float], 
                                  start_year: int, end_year: int) -> Dict[str, float]:
        """Calculate portfolio metrics for given weights."""
        if len(symbols) != len(weights):
            raise ValueError("Number of symbols must match number of weights")
        
        if abs(sum(weights) - 1.0) > 1e-6:
            raise ValueError("Weights must sum to 1.0")
        
        # Load data for all assets
        returns_data = {}
        for symbol in symbols:
            data = self.load_asset_data(symbol, start_year, end_year)
            returns_data[symbol] = data.set_index('year')['return']
        
        # Create aligned DataFrame
        returns_df = pd.DataFrame(returns_data)
        
        # Calculate portfolio returns
        portfolio_returns = (returns_df * weights).sum(axis=1)
        
        # Calculate portfolio metrics
        rf_rates = self.rf_provider.get_risk_free_rate(start_year, end_year)['risk_free_rate'].tolist()
        
        calculator = RiskMetricsCalculator(portfolio_returns.tolist(), rf_rates)
        metrics = calculator.all_metrics()
        
        # Add portfolio specific metrics
        metrics['portfolio_return'] = portfolio_returns.mean()
        metrics['portfolio_volatility'] = portfolio_returns.std()
        
        return metrics
    
    def get_efficient_frontier(self, symbols: List[str], start_year: int, end_year: int, 
                             num_portfolios: int = 100) -> Dict[str, List[float]]:
        """Calculate efficient frontier for given assets."""
        # Load data for all assets
        returns_data = {}
        for symbol in symbols:
            data = self.load_asset_data(symbol, start_year, end_year)
            returns_data[symbol] = data.set_index('year')['return']
        
        returns_df = pd.DataFrame(returns_data)
        
        # Calculate expected returns and covariance matrix
        expected_returns = returns_df.mean()
        cov_matrix = returns_df.cov()
        
        # Generate random portfolios
        num_assets = len(symbols)
        results = {
            'returns': [],
            'volatility': [],
            'sharpe_ratio': [],
            'weights': []
        }
        
        # Get risk-free rate
        rf_data = self.rf_provider.get_risk_free_rate(start_year, end_year)
        risk_free_rate = rf_data['risk_free_rate'].mean()
        
        for _ in range(num_portfolios):
            # Generate random weights
            weights = np.random.random(num_assets)
            weights /= np.sum(weights)
            
            # Calculate portfolio metrics
            portfolio_return = np.sum(expected_returns * weights)
            portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            sharpe_ratio = (portfolio_return - risk_free_rate) / portfolio_volatility
            
            results['returns'].append(portfolio_return)
            results['volatility'].append(portfolio_volatility)
            results['sharpe_ratio'].append(sharpe_ratio)
            results['weights'].append(weights.tolist())
        
        return results
    
    def get_asset_summary(self, symbol: str, start_year: int, end_year: int) -> Dict[str, Any]:
        """Get comprehensive summary for an asset."""
        if symbol not in self.assets:
            raise ValueError(f"Asset {symbol} not found")
        
        asset_info = self.assets[symbol]
        data = self.load_asset_data(symbol, start_year, end_year)
        
        # Calculate basic statistics
        returns = data['return'].tolist()
        rf_rates = self.rf_provider.get_risk_free_rate(start_year, end_year)['risk_free_rate'].tolist()
        
        calculator = RiskMetricsCalculator(returns, rf_rates)
        risk_metrics = calculator.all_metrics()
        
        # Add asset information
        summary = {
            'asset_info': {
                'symbol': asset_info.symbol,
                'name': asset_info.name,
                'asset_class': asset_info.asset_class.value,
                'description': asset_info.description
            },
            'data_period': {
                'start_year': start_year,
                'end_year': end_year,
                'total_years': len(data)
            },
            'risk_metrics': risk_metrics,
            'basic_stats': {
                'mean_return': np.mean(returns),
                'median_return': np.median(returns),
                'std_return': np.std(returns),
                'min_return': np.min(returns),
                'max_return': np.max(returns),
                'positive_years': sum(1 for r in returns if r > 0),
                'negative_years': sum(1 for r in returns if r < 0)
            }
        }
        
        return summary


# Predefined asset universe
ASSET_UNIVERSE = {
    # US Equity Indices
    'SPY': AssetInfo('SPY', 'S&P 500', AssetClass.EQUITY, 'Large-cap US stocks', 'mock', inception_year=1926),
    'QQQ': AssetInfo('QQQ', 'NASDAQ 100', AssetClass.EQUITY, 'Technology-heavy US stocks', 'mock', inception_year=1971),
    'DIA': AssetInfo('DIA', 'Dow Jones', AssetClass.EQUITY, 'Blue-chip US stocks', 'mock', inception_year=1896),
    'IWM': AssetInfo('IWM', 'Russell 2000', AssetClass.EQUITY, 'Small-cap US stocks', 'mock', inception_year=1979),
    
    # Bond Indices
    'TLT': AssetInfo('TLT', '20+ Year Treasury', AssetClass.BOND, 'Long-term US government bonds', 'mock', inception_year=1926),
    'IEF': AssetInfo('IEF', '7-10 Year Treasury', AssetClass.BOND, 'Intermediate US government bonds', 'mock', inception_year=1926),
    'LQD': AssetInfo('LQD', 'Investment Grade Corporate', AssetClass.BOND, 'Corporate bonds', 'mock', inception_year=1973),
    'HYG': AssetInfo('HYG', 'High Yield Corporate', AssetClass.BOND, 'High-yield corporate bonds', 'mock', inception_year=1983),
    
    # Commodities
    'GLD': AssetInfo('GLD', 'Gold', AssetClass.COMMODITY, 'Gold commodity', 'mock', inception_year=1968),
    'USO': AssetInfo('USO', 'Oil', AssetClass.COMMODITY, 'Crude oil commodity', 'mock', inception_year=1983),
    'DBA': AssetInfo('DBA', 'Agriculture', AssetClass.COMMODITY, 'Agricultural commodities', 'mock', inception_year=1991),
    
    # REITs
    'VNQ': AssetInfo('VNQ', 'US REITs', AssetClass.REIT, 'US Real Estate Investment Trusts', 'mock', inception_year=1972),
    
    # International
    'EFA': AssetInfo('EFA', 'Developed Markets', AssetClass.INTERNATIONAL, 'EAFE developed markets', 'mock', inception_year=1970),
    'EEM': AssetInfo('EEM', 'Emerging Markets', AssetClass.INTERNATIONAL, 'Emerging market stocks', 'mock', inception_year=1988),
    'FEZ': AssetInfo('FEZ', 'Europe', AssetClass.INTERNATIONAL, 'European stocks', 'mock', inception_year=1970),
}
