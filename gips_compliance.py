#!/usr/bin/env python3
"""
GIPS Compliance Module

This module implements Global Investment Performance Standards (GIPS) 2020 
compliance functionality including:
- Time-weighted return calculations
- Money-weighted return calculations  
- Composite return calculations
- Performance attribution analysis
- Compliance validation and reporting

GIPS Standards ensure fair representation and full disclosure of investment 
performance results to prospective clients and consultants.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Union
from dataclasses import dataclass
from enum import Enum
import warnings


class ReturnCalculationMethod(Enum):
    """GIPS-compliant return calculation methods."""
    TIME_WEIGHTED = "time_weighted"
    MONEY_WEIGHTED = "money_weighted"
    MODIFIED_DIETZ = "modified_dietz"
    TRUE_TIME_WEIGHTED = "true_time_weighted"


class ComplianceLevel(Enum):
    """GIPS compliance levels."""
    FULL_COMPLIANCE = "full_compliance"
    PARTIAL_COMPLIANCE = "partial_compliance"
    NON_COMPLIANT = "non_compliant"


@dataclass
class CashFlow:
    """Represents a cash flow event for GIPS calculations."""
    date: datetime
    amount: float
    flow_type: str  # 'contribution', 'withdrawal', 'dividend', 'fee'
    description: Optional[str] = None


@dataclass
class PortfolioValuation:
    """Represents portfolio valuation at a specific date."""
    date: datetime
    market_value: float
    accrued_income: float = 0.0
    cash_balance: float = 0.0


@dataclass
class GIPSCalculationResult:
    """Results of GIPS-compliant performance calculations."""
    time_weighted_return: float
    money_weighted_return: Optional[float]
    composite_return: Optional[float]
    calculation_method: ReturnCalculationMethod
    period_start: datetime
    period_end: datetime
    number_of_portfolios: int
    total_assets: float
    compliance_level: ComplianceLevel
    validation_notes: List[str]


class GIPSCalculator:
    """
    GIPS-compliant performance calculator.
    
    Implements calculation methodologies according to GIPS 2020 standards
    for accurate and standardized investment performance measurement.
    """
    
    def __init__(self):
        self.validation_errors = []
        self.calculation_warnings = []
    
    def calculate_time_weighted_return(
        self,
        valuations: List[PortfolioValuation],
        cash_flows: List[CashFlow],
        use_daily_valuation: bool = True
    ) -> float:
        """
        Calculate time-weighted return according to GIPS standards.
        
        Time-weighted returns measure the compound rate of growth of one unit 
        of currency invested in a portfolio over a stated measurement period.
        
        Args:
            valuations: List of portfolio valuations
            cash_flows: List of cash flows during the period
            use_daily_valuation: Whether to use daily valuation (recommended)
            
        Returns:
            Time-weighted return as decimal (e.g., 0.10 for 10%)
        """
        if len(valuations) < 2:
            raise ValueError("At least two valuations required for TWR calculation")
        
        # Sort valuations and cash flows by date
        valuations = sorted(valuations, key=lambda x: x.date)
        cash_flows = sorted(cash_flows, key=lambda x: x.date)
        
        # Calculate sub-period returns
        sub_period_returns = []
        
        for i in range(len(valuations) - 1):
            start_val = valuations[i]
            end_val = valuations[i + 1]
            
            # Get cash flows in this sub-period
            period_cash_flows = [
                cf for cf in cash_flows 
                if start_val.date < cf.date <= end_val.date
            ]
            
            # Calculate sub-period return
            net_cash_flow = sum(cf.amount for cf in period_cash_flows)
            
            if start_val.market_value <= 0:
                sub_return = 0.0
                self.calculation_warnings.append(
                    f"Zero or negative starting value on {start_val.date}"
                )
            else:
                # Basic time-weighted return formula
                sub_return = (
                    (end_val.market_value - start_val.market_value - net_cash_flow) 
                    / start_val.market_value
                )
            
            sub_period_returns.append(sub_return)
        
        # Compound sub-period returns
        total_return = 1.0
        for sub_return in sub_period_returns:
            total_return *= (1.0 + sub_return)
        
        return total_return - 1.0
    
    def calculate_money_weighted_return(
        self,
        valuations: List[PortfolioValuation],
        cash_flows: List[CashFlow],
        max_iterations: int = 100,
        tolerance: float = 1e-6
    ) -> float:
        """
        Calculate money-weighted return (Internal Rate of Return) using Newton-Raphson method.
        
        Money-weighted returns measure the compound rate of growth of all funds 
        invested in the account over the evaluation period.
        
        Args:
            valuations: List of portfolio valuations
            cash_flows: List of cash flows
            max_iterations: Maximum iterations for IRR calculation
            tolerance: Convergence tolerance
            
        Returns:
            Money-weighted return as decimal
        """
        if len(valuations) < 2:
            raise ValueError("At least two valuations required for MWR calculation")
        
        start_val = min(valuations, key=lambda x: x.date)
        end_val = max(valuations, key=lambda x: x.date)
        
        # Create cash flow timeline
        all_flows = []
        
        # Initial investment (negative cash flow)
        all_flows.append((-start_val.market_value, 0))
        
        # Intermediate cash flows
        for cf in cash_flows:
            days_from_start = (cf.date - start_val.date).days
            all_flows.append((cf.amount, days_from_start))
        
        # Final value (positive cash flow)
        total_days = (end_val.date - start_val.date).days
        all_flows.append((end_val.market_value, total_days))
        
        # Newton-Raphson method to find IRR
        rate = 0.1  # Initial guess
        
        for iteration in range(max_iterations):
            npv = 0.0
            npv_derivative = 0.0
            
            for amount, days in all_flows:
                factor = (1 + rate) ** (days / 365.25)
                npv += amount / factor
                npv_derivative -= amount * (days / 365.25) / (factor * (1 + rate))
            
            if abs(npv) < tolerance:
                return rate
            
            if abs(npv_derivative) < tolerance:
                self.calculation_warnings.append("IRR calculation may be unstable")
                break
            
            rate = rate - npv / npv_derivative
        
        self.calculation_warnings.append(
            f"IRR calculation did not converge after {max_iterations} iterations"
        )
        return rate
    
    def calculate_modified_dietz_return(
        self,
        start_value: float,
        end_value: float,
        cash_flows: List[CashFlow],
        period_start: datetime,
        period_end: datetime
    ) -> float:
        """
        Calculate Modified Dietz return.
        
        The Modified Dietz method is an approximation of the time-weighted return
        that weights cash flows by the amount of time they are held in the portfolio.
        
        Args:
            start_value: Portfolio value at period start
            end_value: Portfolio value at period end  
            cash_flows: Cash flows during the period
            period_start: Start date of measurement period
            period_end: End date of measurement period
            
        Returns:
            Modified Dietz return as decimal
        """
        total_days = (period_end - period_start).days
        
        if total_days <= 0:
            raise ValueError("Period end must be after period start")
        
        weighted_cash_flows = 0.0
        total_cash_flows = 0.0
        
        for cf in cash_flows:
            if period_start <= cf.date <= period_end:
                days_remaining = (period_end - cf.date).days
                weight = days_remaining / total_days
                weighted_cash_flows += cf.amount * weight
                total_cash_flows += cf.amount
        
        if start_value + weighted_cash_flows <= 0:
            self.calculation_warnings.append(
                "Denominator close to zero in Modified Dietz calculation"
            )
            return 0.0
        
        return (
            (end_value - start_value - total_cash_flows) / 
            (start_value + weighted_cash_flows)
        )
    
    def calculate_composite_return(
        self,
        portfolio_returns: List[Tuple[float, float]],  # (return, weight)
        method: str = "asset_weighted"
    ) -> float:
        """
        Calculate composite return from individual portfolio returns.
        
        Args:
            portfolio_returns: List of (return, weight) tuples
            method: Weighting method ('asset_weighted', 'equal_weighted')
            
        Returns:
            Composite return as decimal
        """
        if not portfolio_returns:
            return 0.0
        
        if method == "asset_weighted":
            total_weight = sum(weight for _, weight in portfolio_returns)
            if total_weight <= 0:
                return 0.0
            
            weighted_return = sum(
                ret * weight for ret, weight in portfolio_returns
            )
            return weighted_return / total_weight
        
        elif method == "equal_weighted":
            returns = [ret for ret, _ in portfolio_returns]
            return sum(returns) / len(returns)
        
        else:
            raise ValueError(f"Unknown composite method: {method}")
    
    def validate_gips_compliance(
        self,
        calculation_result: GIPSCalculationResult,
        portfolios_data: List[Dict],
        benchmark_data: Optional[Dict] = None
    ) -> Tuple[ComplianceLevel, List[str]]:
        """
        Validate GIPS compliance of calculation results.
        
        Args:
            calculation_result: Results to validate
            portfolios_data: Portfolio data used in calculations
            benchmark_data: Benchmark comparison data
            
        Returns:
            Tuple of (compliance_level, validation_notes)
        """
        validation_notes = []
        compliance_issues = 0
        
        # Check calculation methodology
        if calculation_result.calculation_method not in [
            ReturnCalculationMethod.TIME_WEIGHTED,
            ReturnCalculationMethod.TRUE_TIME_WEIGHTED
        ]:
            validation_notes.append(
                "GIPS requires time-weighted returns for most composites"
            )
            compliance_issues += 1
        
        # Check minimum portfolio requirements
        if calculation_result.number_of_portfolios < 5:
            validation_notes.append(
                "Composite should include at least 5 portfolios for statistical significance"
            )
        
        # Check data quality
        if len(self.calculation_warnings) > 0:
            validation_notes.extend([
                f"Calculation warning: {warning}" 
                for warning in self.calculation_warnings
            ])
        
        # Check period coverage
        period_days = (calculation_result.period_end - calculation_result.period_start).days
        if period_days < 365:
            validation_notes.append(
                "GIPS recommends at least one year of performance history"
            )
        
        # Determine compliance level
        if compliance_issues == 0 and len(self.calculation_warnings) == 0:
            compliance_level = ComplianceLevel.FULL_COMPLIANCE
        elif compliance_issues <= 2:
            compliance_level = ComplianceLevel.PARTIAL_COMPLIANCE
        else:
            compliance_level = ComplianceLevel.NON_COMPLIANT
        
        return compliance_level, validation_notes
    
    def generate_gips_report(
        self,
        calculation_result: GIPSCalculationResult,
        firm_name: str,
        composite_name: str,
        benchmark_name: Optional[str] = None,
        benchmark_return: Optional[float] = None
    ) -> Dict:
        """
        Generate GIPS-compliant performance report.
        
        Args:
            calculation_result: Calculation results
            firm_name: Investment firm name
            composite_name: Name of the composite
            benchmark_name: Name of benchmark (if applicable)
            benchmark_return: Benchmark return for comparison
            
        Returns:
            Dictionary containing formatted GIPS report
        """
        report = {
            "firm_name": firm_name,
            "composite_name": composite_name,
            "period_start": calculation_result.period_start.strftime("%Y-%m-%d"),
            "period_end": calculation_result.period_end.strftime("%Y-%m-%d"),
            "time_weighted_return": f"{calculation_result.time_weighted_return:.2%}",
            "number_of_portfolios": calculation_result.number_of_portfolios,
            "total_assets": f"${calculation_result.total_assets:,.0f}",
            "calculation_method": calculation_result.calculation_method.value,
            "compliance_level": calculation_result.compliance_level.value,
            "validation_notes": calculation_result.validation_notes
        }
        
        if calculation_result.money_weighted_return is not None:
            report["money_weighted_return"] = f"{calculation_result.money_weighted_return:.2%}"
        
        if benchmark_name and benchmark_return is not None:
            report["benchmark_name"] = benchmark_name
            report["benchmark_return"] = f"{benchmark_return:.2%}"
            report["excess_return"] = f"{calculation_result.time_weighted_return - benchmark_return:.2%}"
        
        # Add GIPS compliance statement
        if calculation_result.compliance_level == ComplianceLevel.FULL_COMPLIANCE:
            report["compliance_statement"] = (
                f"{firm_name} claims compliance with the Global Investment "
                "Performance Standards (GIPS®) and has prepared and presented "
                "this report in compliance with the GIPS standards."
            )
        else:
            report["compliance_statement"] = (
                f"This report does not fully comply with GIPS standards. "
                f"See validation notes for details."
            )
        
        return report
    
    def clear_warnings(self):
        """Clear calculation warnings and validation errors."""
        self.calculation_warnings.clear()
        self.validation_errors.clear()


def create_sample_gips_calculation():
    """Create a sample GIPS calculation for demonstration."""
    calculator = GIPSCalculator()
    
    # Sample portfolio valuations
    valuations = [
        PortfolioValuation(datetime(2023, 1, 1), 1000000.0),
        PortfolioValuation(datetime(2023, 6, 30), 1050000.0),
        PortfolioValuation(datetime(2023, 12, 31), 1120000.0)
    ]
    
    # Sample cash flows
    cash_flows = [
        CashFlow(datetime(2023, 3, 15), 50000.0, "contribution"),
        CashFlow(datetime(2023, 9, 15), -25000.0, "withdrawal")
    ]
    
    # Calculate returns
    twr = calculator.calculate_time_weighted_return(valuations, cash_flows)
    mwr = calculator.calculate_money_weighted_return(valuations, cash_flows)
    
    # Create result
    result = GIPSCalculationResult(
        time_weighted_return=twr,
        money_weighted_return=mwr,
        composite_return=twr,  # Single portfolio
        calculation_method=ReturnCalculationMethod.TIME_WEIGHTED,
        period_start=datetime(2023, 1, 1),
        period_end=datetime(2023, 12, 31),
        number_of_portfolios=1,
        total_assets=1120000.0,
        compliance_level=ComplianceLevel.PARTIAL_COMPLIANCE,
        validation_notes=[]
    )
    
    # Validate compliance
    compliance_level, notes = calculator.validate_gips_compliance(result, [])
    result.compliance_level = compliance_level
    result.validation_notes = notes
    
    return result, calculator


class PerformanceAttributionAnalyzer:
    """
    Performance attribution analysis for GIPS compliance.

    Analyzes the sources of portfolio performance relative to benchmarks
    and provides detailed attribution analysis.
    """

    def __init__(self):
        self.attribution_methods = [
            "brinson_hood_beebower",
            "brinson_fachler",
            "arithmetic_attribution",
            "geometric_attribution"
        ]

    def calculate_brinson_attribution(
        self,
        portfolio_weights: Dict[str, float],
        portfolio_returns: Dict[str, float],
        benchmark_weights: Dict[str, float],
        benchmark_returns: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Calculate Brinson-Hood-Beebower attribution analysis.

        Args:
            portfolio_weights: Portfolio sector/asset weights
            portfolio_returns: Portfolio sector/asset returns
            benchmark_weights: Benchmark sector/asset weights
            benchmark_returns: Benchmark sector/asset returns

        Returns:
            Dictionary with attribution components
        """
        allocation_effect = 0.0
        selection_effect = 0.0
        interaction_effect = 0.0

        # Ensure all sectors are covered
        all_sectors = set(portfolio_weights.keys()) | set(benchmark_weights.keys())

        for sector in all_sectors:
            pw = portfolio_weights.get(sector, 0.0)
            pr = portfolio_returns.get(sector, 0.0)
            bw = benchmark_weights.get(sector, 0.0)
            br = benchmark_returns.get(sector, 0.0)

            # Allocation effect: (wp - wb) * rb
            allocation_effect += (pw - bw) * br

            # Selection effect: wb * (rp - rb)
            selection_effect += bw * (pr - br)

            # Interaction effect: (wp - wb) * (rp - rb)
            interaction_effect += (pw - bw) * (pr - br)

        return {
            "allocation_effect": allocation_effect,
            "selection_effect": selection_effect,
            "interaction_effect": interaction_effect,
            "total_attribution": allocation_effect + selection_effect + interaction_effect
        }

    def calculate_risk_adjusted_attribution(
        self,
        portfolio_returns: List[float],
        benchmark_returns: List[float],
        risk_free_rate: float = 0.02
    ) -> Dict[str, float]:
        """
        Calculate risk-adjusted performance attribution.

        Args:
            portfolio_returns: Time series of portfolio returns
            benchmark_returns: Time series of benchmark returns
            risk_free_rate: Risk-free rate for Sharpe ratio calculation

        Returns:
            Dictionary with risk-adjusted metrics
        """
        portfolio_returns = np.array(portfolio_returns)
        benchmark_returns = np.array(benchmark_returns)

        # Calculate basic statistics
        portfolio_mean = np.mean(portfolio_returns)
        benchmark_mean = np.mean(benchmark_returns)
        portfolio_std = np.std(portfolio_returns, ddof=1)
        benchmark_std = np.std(benchmark_returns, ddof=1)

        # Calculate excess returns
        portfolio_excess = portfolio_returns - risk_free_rate
        benchmark_excess = benchmark_returns - risk_free_rate

        # Sharpe ratios
        portfolio_sharpe = np.mean(portfolio_excess) / np.std(portfolio_excess, ddof=1)
        benchmark_sharpe = np.mean(benchmark_excess) / np.std(benchmark_excess, ddof=1)

        # Information ratio
        active_returns = portfolio_returns - benchmark_returns
        information_ratio = np.mean(active_returns) / np.std(active_returns, ddof=1)

        # Beta calculation
        covariance = np.cov(portfolio_returns, benchmark_returns)[0, 1]
        beta = covariance / np.var(benchmark_returns, ddof=1)

        # Alpha calculation (Jensen's alpha)
        alpha = portfolio_mean - (risk_free_rate + beta * (benchmark_mean - risk_free_rate))

        return {
            "alpha": alpha,
            "beta": beta,
            "portfolio_sharpe": portfolio_sharpe,
            "benchmark_sharpe": benchmark_sharpe,
            "information_ratio": information_ratio,
            "tracking_error": np.std(active_returns, ddof=1),
            "excess_return": portfolio_mean - benchmark_mean
        }


class BenchmarkStandardizer:
    """
    Standardizes benchmark comparisons for GIPS compliance.

    Ensures consistent and appropriate benchmark selection and comparison
    methodologies according to GIPS standards.
    """

    def __init__(self):
        self.benchmark_criteria = [
            "representative",
            "investable",
            "measurable",
            "unambiguous",
            "reflective_of_investment_style"
        ]

    def validate_benchmark_appropriateness(
        self,
        portfolio_characteristics: Dict,
        benchmark_characteristics: Dict
    ) -> Tuple[bool, List[str]]:
        """
        Validate if benchmark is appropriate for the portfolio.

        Args:
            portfolio_characteristics: Portfolio style/characteristics
            benchmark_characteristics: Benchmark characteristics

        Returns:
            Tuple of (is_appropriate, validation_notes)
        """
        validation_notes = []
        is_appropriate = True

        # Check asset class alignment
        portfolio_asset_class = portfolio_characteristics.get("asset_class", "")
        benchmark_asset_class = benchmark_characteristics.get("asset_class", "")

        if portfolio_asset_class != benchmark_asset_class:
            validation_notes.append(
                f"Asset class mismatch: Portfolio ({portfolio_asset_class}) "
                f"vs Benchmark ({benchmark_asset_class})"
            )
            is_appropriate = False

        # Check geographic focus
        portfolio_geography = portfolio_characteristics.get("geography", "")
        benchmark_geography = benchmark_characteristics.get("geography", "")

        if portfolio_geography and benchmark_geography:
            if portfolio_geography != benchmark_geography:
                validation_notes.append(
                    f"Geographic focus mismatch: Portfolio ({portfolio_geography}) "
                    f"vs Benchmark ({benchmark_geography})"
                )

        # Check investment style
        portfolio_style = portfolio_characteristics.get("investment_style", "")
        benchmark_style = benchmark_characteristics.get("investment_style", "")

        if portfolio_style and benchmark_style:
            if portfolio_style != benchmark_style:
                validation_notes.append(
                    f"Investment style mismatch: Portfolio ({portfolio_style}) "
                    f"vs Benchmark ({benchmark_style})"
                )

        return is_appropriate, validation_notes

    def calculate_benchmark_statistics(
        self,
        benchmark_returns: List[float],
        period_start: datetime,
        period_end: datetime
    ) -> Dict[str, float]:
        """
        Calculate comprehensive benchmark statistics.

        Args:
            benchmark_returns: Time series of benchmark returns
            period_start: Start of measurement period
            period_end: End of measurement period

        Returns:
            Dictionary with benchmark statistics
        """
        returns = np.array(benchmark_returns)

        # Basic statistics
        total_return = np.prod(1 + returns) - 1
        annualized_return = (1 + total_return) ** (365.25 / (period_end - period_start).days) - 1
        volatility = np.std(returns, ddof=1) * np.sqrt(252)  # Annualized

        # Risk metrics
        downside_returns = returns[returns < 0]
        downside_deviation = np.std(downside_returns, ddof=1) * np.sqrt(252) if len(downside_returns) > 0 else 0

        # Drawdown analysis
        cumulative_returns = np.cumprod(1 + returns)
        running_max = np.maximum.accumulate(cumulative_returns)
        drawdowns = (cumulative_returns - running_max) / running_max
        max_drawdown = np.min(drawdowns)

        return {
            "total_return": total_return,
            "annualized_return": annualized_return,
            "volatility": volatility,
            "downside_deviation": downside_deviation,
            "max_drawdown": max_drawdown,
            "positive_periods": np.sum(returns > 0) / len(returns),
            "average_positive_return": np.mean(returns[returns > 0]) if np.any(returns > 0) else 0,
            "average_negative_return": np.mean(returns[returns < 0]) if np.any(returns < 0) else 0
        }


if __name__ == "__main__":
    # Comprehensive demonstration
    print("🏛️ GIPS Compliance Module Demo")
    print("=" * 50)

    # Basic GIPS calculation
    result, calculator = create_sample_gips_calculation()

    print(f"Time-Weighted Return: {result.time_weighted_return:.2%}")
    print(f"Money-Weighted Return: {result.money_weighted_return:.2%}")
    print(f"Compliance Level: {result.compliance_level.value}")
    print(f"Validation Notes: {len(result.validation_notes)} items")

    # Performance attribution demo
    print("\n📊 Performance Attribution Analysis:")
    attribution_analyzer = PerformanceAttributionAnalyzer()

    # Sample data for attribution
    portfolio_weights = {"Equities": 0.6, "Bonds": 0.3, "Cash": 0.1}
    portfolio_returns = {"Equities": 0.12, "Bonds": 0.04, "Cash": 0.02}
    benchmark_weights = {"Equities": 0.5, "Bonds": 0.4, "Cash": 0.1}
    benchmark_returns = {"Equities": 0.10, "Bonds": 0.03, "Cash": 0.02}

    attribution = attribution_analyzer.calculate_brinson_attribution(
        portfolio_weights, portfolio_returns, benchmark_weights, benchmark_returns
    )

    print(f"  Allocation Effect: {attribution['allocation_effect']:.2%}")
    print(f"  Selection Effect: {attribution['selection_effect']:.2%}")
    print(f"  Interaction Effect: {attribution['interaction_effect']:.2%}")
    print(f"  Total Attribution: {attribution['total_attribution']:.2%}")

    # Benchmark validation demo
    print("\n🎯 Benchmark Validation:")
    benchmark_standardizer = BenchmarkStandardizer()

    portfolio_chars = {
        "asset_class": "equity",
        "geography": "US",
        "investment_style": "large_cap_growth"
    }

    benchmark_chars = {
        "asset_class": "equity",
        "geography": "US",
        "investment_style": "large_cap_blend"
    }

    is_appropriate, notes = benchmark_standardizer.validate_benchmark_appropriateness(
        portfolio_chars, benchmark_chars
    )

    print(f"  Benchmark Appropriate: {is_appropriate}")
    if notes:
        for note in notes:
            print(f"  - {note}")

    # Generate comprehensive report
    print("\n📋 GIPS Report Summary:")
    report = calculator.generate_gips_report(
        result,
        "Sample Investment Firm",
        "Equity Growth Composite",
        "S&P 500 Index",
        0.095  # 9.5% benchmark return
    )

    for key, value in report.items():
        if key != "compliance_statement":
            print(f"  {key}: {value}")

    print(f"\n✅ GIPS Compliance Statement:")
    print(f"  {report['compliance_statement']}")
