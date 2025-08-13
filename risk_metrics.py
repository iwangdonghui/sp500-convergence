"""
Risk Metrics Module for S&P 500 Analysis Tool

This module implements professional risk metrics calculations including:
- Sharpe Ratio (rolling and static)
- Sortino Ratio (downside risk-adjusted returns)
- Calmar Ratio (maximum drawdown-adjusted returns)
- Maximum Drawdown analysis
- Volatility analysis (annualized standard deviation)
- Risk-free rate integration

Author: Professional Investment Analysis Team
"""

import pandas as pd
import numpy as np
import requests
from typing import Dict, List, Tuple, Optional, Any, Union
from datetime import datetime, timedelta
import warnings

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

# Constants
TRADING_DAYS_PER_YEAR = 252
RISK_FREE_RATE_DEFAULT = 0.02  # 2% default risk-free rate
FRED_API_BASE = "https://api.stlouisfed.org/fred/series/observations"


class RiskFreeRateProvider:
    """Provider for risk-free rate data from FRED API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize risk-free rate provider.
        
        Args:
            api_key: FRED API key (optional, uses public access if None)
        """
        self.api_key = api_key
        self.cache = {}
    
    def get_risk_free_rate(self, start_year: int, end_year: int) -> pd.DataFrame:
        """
        Get risk-free rate data for the specified period.
        
        Args:
            start_year: Starting year
            end_year: Ending year
            
        Returns:
            DataFrame with year and risk_free_rate columns
        """
        cache_key = f"{start_year}_{end_year}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            # Try to fetch 10-year Treasury rate from FRED
            df = self._fetch_treasury_rate(start_year, end_year)
            self.cache[cache_key] = df
            return df
        except Exception as e:
            print(f"Warning: Could not fetch risk-free rate data: {e}")
            # Return default risk-free rate
            years = list(range(start_year, end_year + 1))
            df = pd.DataFrame({
                'year': years,
                'risk_free_rate': [RISK_FREE_RATE_DEFAULT] * len(years)
            })
            return df
    
    def _fetch_treasury_rate(self, start_year: int, end_year: int) -> pd.DataFrame:
        """Fetch 10-year Treasury rate from FRED API."""
        # For now, return default rates
        # TODO: Implement actual FRED API integration
        years = list(range(start_year, end_year + 1))
        
        # Use historical approximations for different periods
        rates = []
        for year in years:
            if year < 1980:
                rate = 0.04  # ~4% for pre-1980
            elif year < 2000:
                rate = 0.07  # ~7% for 1980-2000
            elif year < 2010:
                rate = 0.05  # ~5% for 2000-2010
            elif year < 2020:
                rate = 0.03  # ~3% for 2010-2020
            else:
                rate = 0.02  # ~2% for 2020+
            rates.append(rate)
        
        df = pd.DataFrame({
            'year': years,
            'risk_free_rate': rates
        })
        return df


class RiskMetricsCalculator:
    """Calculator for professional risk metrics."""
    
    def __init__(self, returns: List[float], risk_free_rates: Optional[List[float]] = None):
        """
        Initialize risk metrics calculator.
        
        Args:
            returns: List of annual returns (as decimals)
            risk_free_rates: List of annual risk-free rates (optional)
        """
        self.returns = np.array(returns)
        self.risk_free_rates = np.array(risk_free_rates) if risk_free_rates else None
        
        # Calculate excess returns if risk-free rates provided
        if self.risk_free_rates is not None:
            self.excess_returns = self.returns - self.risk_free_rates
        else:
            self.excess_returns = self.returns - RISK_FREE_RATE_DEFAULT
    
    def sharpe_ratio(self) -> float:
        """
        Calculate Sharpe ratio.
        
        Returns:
            Sharpe ratio (excess return / volatility)
        """
        if len(self.excess_returns) < 2:
            return np.nan
        
        mean_excess = np.mean(self.excess_returns)
        std_excess = np.std(self.excess_returns, ddof=1)
        
        if std_excess == 0:
            return np.nan
        
        return mean_excess / std_excess
    
    def sortino_ratio(self) -> float:
        """
        Calculate Sortino ratio (downside risk-adjusted return).
        
        Returns:
            Sortino ratio (excess return / downside deviation)
        """
        if len(self.excess_returns) < 2:
            return np.nan
        
        mean_excess = np.mean(self.excess_returns)
        
        # Calculate downside deviation (only negative excess returns)
        downside_returns = self.excess_returns[self.excess_returns < 0]
        if len(downside_returns) == 0:
            return np.inf  # No downside risk
        
        downside_deviation = np.sqrt(np.mean(downside_returns ** 2))
        
        if downside_deviation == 0:
            return np.nan
        
        return mean_excess / downside_deviation
    
    def maximum_drawdown(self) -> Dict[str, float]:
        """
        Calculate maximum drawdown and related statistics.
        
        Returns:
            Dictionary with max_drawdown, peak_date, trough_date, recovery_date
        """
        if len(self.returns) < 2:
            return {
                'max_drawdown': np.nan,
                'peak_index': np.nan,
                'trough_index': np.nan,
                'recovery_index': np.nan
            }
        
        # Calculate cumulative returns
        cumulative = np.cumprod(1 + self.returns)
        
        # Calculate running maximum (peak)
        running_max = np.maximum.accumulate(cumulative)
        
        # Calculate drawdown
        drawdown = (cumulative - running_max) / running_max
        
        # Find maximum drawdown
        max_dd_index = np.argmin(drawdown)
        max_drawdown = drawdown[max_dd_index]
        
        # Find peak before maximum drawdown
        peak_index = np.argmax(running_max[:max_dd_index + 1])
        
        # Find recovery point (if any)
        recovery_index = np.nan
        for i in range(max_dd_index + 1, len(cumulative)):
            if cumulative[i] >= running_max[max_dd_index]:
                recovery_index = i
                break
        
        return {
            'max_drawdown': abs(max_drawdown),
            'peak_index': peak_index,
            'trough_index': max_dd_index,
            'recovery_index': recovery_index
        }
    
    def calmar_ratio(self) -> float:
        """
        Calculate Calmar ratio (CAGR / Maximum Drawdown).
        
        Returns:
            Calmar ratio
        """
        if len(self.returns) < 2:
            return np.nan
        
        # Calculate CAGR
        total_return = np.prod(1 + self.returns)
        years = len(self.returns)
        cagr = (total_return ** (1/years)) - 1
        
        # Calculate maximum drawdown
        max_dd_info = self.maximum_drawdown()
        max_drawdown = max_dd_info['max_drawdown']
        
        if np.isnan(max_drawdown) or max_drawdown == 0:
            return np.nan
        
        return cagr / max_drawdown
    
    def volatility(self) -> float:
        """
        Calculate annualized volatility (standard deviation).
        
        Returns:
            Annualized volatility
        """
        if len(self.returns) < 2:
            return np.nan
        
        return np.std(self.returns, ddof=1)
    
    def var_historical(self, confidence_level: float = 0.05) -> float:
        """
        Calculate Value at Risk using historical method.
        
        Args:
            confidence_level: Confidence level (e.g., 0.05 for 95% VaR)
            
        Returns:
            VaR value (positive number representing loss)
        """
        if len(self.returns) < 10:  # Need sufficient data
            return np.nan
        
        return -np.percentile(self.returns, confidence_level * 100)
    
    def cvar_historical(self, confidence_level: float = 0.05) -> float:
        """
        Calculate Conditional Value at Risk (Expected Shortfall).
        
        Args:
            confidence_level: Confidence level (e.g., 0.05 for 95% CVaR)
            
        Returns:
            CVaR value (positive number representing expected loss)
        """
        if len(self.returns) < 10:  # Need sufficient data
            return np.nan
        
        var_threshold = -self.var_historical(confidence_level)
        tail_losses = self.returns[self.returns <= var_threshold]
        
        if len(tail_losses) == 0:
            return np.nan
        
        return -np.mean(tail_losses)
    
    def all_metrics(self) -> Dict[str, float]:
        """
        Calculate all risk metrics.
        
        Returns:
            Dictionary with all calculated metrics
        """
        max_dd_info = self.maximum_drawdown()
        
        return {
            'sharpe_ratio': self.sharpe_ratio(),
            'sortino_ratio': self.sortino_ratio(),
            'calmar_ratio': self.calmar_ratio(),
            'volatility': self.volatility(),
            'max_drawdown': max_dd_info['max_drawdown'],
            'var_95': self.var_historical(0.05),
            'cvar_95': self.cvar_historical(0.05),
            'var_99': self.var_historical(0.01),
            'cvar_99': self.cvar_historical(0.01)
        }


def calculate_rolling_risk_metrics(
    returns: List[float], 
    window_size: int,
    risk_free_rates: Optional[List[float]] = None
) -> List[Dict[str, float]]:
    """
    Calculate rolling risk metrics for a given window size.
    
    Args:
        returns: List of annual returns
        window_size: Rolling window size in years
        risk_free_rates: List of risk-free rates (optional)
        
    Returns:
        List of dictionaries with risk metrics for each window
    """
    if len(returns) < window_size:
        return []
    
    results = []
    
    for i in range(len(returns) - window_size + 1):
        window_returns = returns[i:i + window_size]
        window_rf_rates = None
        
        if risk_free_rates:
            window_rf_rates = risk_free_rates[i:i + window_size]
        
        calculator = RiskMetricsCalculator(window_returns, window_rf_rates)
        metrics = calculator.all_metrics()
        
        # Add window information
        metrics['window_start_index'] = i
        metrics['window_end_index'] = i + window_size - 1
        
        results.append(metrics)
    
    return results
