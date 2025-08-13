#!/usr/bin/env python3
"""
Demo script for GIPS compliance capabilities.

This script demonstrates the new GIPS compliance features
added in Stage 4, including standard return calculations,
performance attribution, and compliance reporting.
"""

import pandas as pd
import numpy as np
from datetime import datetime
from gips_compliance import (
    GIPSCalculator, PerformanceAttributionAnalyzer, BenchmarkStandardizer,
    ReturnCalculationMethod, ComplianceLevel, CashFlow, PortfolioValuation,
    create_sample_gips_calculation
)
from data_processor import DataProcessor


def demo_gips_return_calculations():
    """Demo GIPS-compliant return calculations."""
    print("🏛️ GIPS Return Calculations Demo")
    print("=" * 60)
    
    calculator = GIPSCalculator()
    
    # Create sample portfolio data
    valuations = [
        PortfolioValuation(datetime(2023, 1, 1), 1000000.0),
        PortfolioValuation(datetime(2023, 3, 31), 1025000.0),
        PortfolioValuation(datetime(2023, 6, 30), 1080000.0),
        PortfolioValuation(datetime(2023, 9, 30), 1095000.0),
        PortfolioValuation(datetime(2023, 12, 31), 1150000.0)
    ]
    
    cash_flows = [
        CashFlow(datetime(2023, 2, 15), 50000.0, "contribution", "Client deposit"),
        CashFlow(datetime(2023, 8, 15), -30000.0, "withdrawal", "Client withdrawal"),
        CashFlow(datetime(2023, 11, 15), 25000.0, "contribution", "Additional investment")
    ]
    
    print("Portfolio Valuations:")
    for val in valuations:
        print(f"  {val.date.strftime('%Y-%m-%d')}: ${val.market_value:,.0f}")
    
    print(f"\nCash Flows:")
    for cf in cash_flows:
        flow_type = "+" if cf.amount > 0 else ""
        print(f"  {cf.date.strftime('%Y-%m-%d')}: {flow_type}${cf.amount:,.0f} ({cf.flow_type})")
    
    # Calculate returns
    print(f"\n📊 GIPS Return Calculations:")
    print("-" * 40)
    
    # Time-weighted return
    twr = calculator.calculate_time_weighted_return(valuations, cash_flows)
    print(f"Time-Weighted Return: {twr:.2%}")
    
    # Money-weighted return
    mwr = calculator.calculate_money_weighted_return(valuations, cash_flows)
    print(f"Money-Weighted Return: {mwr:.2%}")
    
    # Modified Dietz return
    dietz_return = calculator.calculate_modified_dietz_return(
        valuations[0].market_value,
        valuations[-1].market_value,
        cash_flows,
        valuations[0].date,
        valuations[-1].date
    )
    print(f"Modified Dietz Return: {dietz_return:.2%}")
    
    # Composite return (single portfolio)
    composite_return = calculator.calculate_composite_return([(twr, 1.0)])
    print(f"Composite Return: {composite_return:.2%}")
    
    return {
        'twr': twr,
        'mwr': mwr,
        'dietz': dietz_return,
        'composite': composite_return
    }


def demo_performance_attribution():
    """Demo performance attribution analysis."""
    print("\n📈 Performance Attribution Analysis Demo")
    print("=" * 60)
    
    analyzer = PerformanceAttributionAnalyzer()
    
    # Sample portfolio and benchmark data
    portfolio_weights = {
        "Technology": 0.35,
        "Healthcare": 0.20,
        "Financials": 0.15,
        "Consumer Discretionary": 0.15,
        "Industrials": 0.10,
        "Cash": 0.05
    }
    
    portfolio_returns = {
        "Technology": 0.18,
        "Healthcare": 0.12,
        "Financials": 0.08,
        "Consumer Discretionary": 0.14,
        "Industrials": 0.10,
        "Cash": 0.02
    }
    
    benchmark_weights = {
        "Technology": 0.30,
        "Healthcare": 0.15,
        "Financials": 0.20,
        "Consumer Discretionary": 0.12,
        "Industrials": 0.18,
        "Cash": 0.05
    }
    
    benchmark_returns = {
        "Technology": 0.15,
        "Healthcare": 0.10,
        "Financials": 0.06,
        "Consumer Discretionary": 0.12,
        "Industrials": 0.08,
        "Cash": 0.02
    }
    
    print("Portfolio vs Benchmark Allocation:")
    print("-" * 50)
    print(f"{'Sector':<20} {'Portfolio':<12} {'Benchmark':<12} {'Difference':<12}")
    print("-" * 50)
    
    for sector in portfolio_weights:
        pw = portfolio_weights[sector]
        bw = benchmark_weights[sector]
        diff = pw - bw
        print(f"{sector:<20} {pw:>10.1%} {bw:>10.1%} {diff:>+10.1%}")
    
    # Calculate Brinson attribution
    attribution = analyzer.calculate_brinson_attribution(
        portfolio_weights, portfolio_returns, benchmark_weights, benchmark_returns
    )
    
    print(f"\n🎯 Brinson Attribution Analysis:")
    print("-" * 40)
    print(f"Allocation Effect:  {attribution['allocation_effect']:>+8.2%}")
    print(f"Selection Effect:   {attribution['selection_effect']:>+8.2%}")
    print(f"Interaction Effect: {attribution['interaction_effect']:>+8.2%}")
    print(f"Total Attribution:  {attribution['total_attribution']:>+8.2%}")
    
    # Risk-adjusted attribution
    np.random.seed(42)
    portfolio_returns_ts = np.random.normal(0.12, 0.18, 252).tolist()
    benchmark_returns_ts = np.random.normal(0.10, 0.15, 252).tolist()
    
    risk_metrics = analyzer.calculate_risk_adjusted_attribution(
        portfolio_returns_ts, benchmark_returns_ts
    )
    
    print(f"\n📊 Risk-Adjusted Metrics:")
    print("-" * 40)
    print(f"Alpha:              {risk_metrics['alpha']:>+8.4f}")
    print(f"Beta:               {risk_metrics['beta']:>8.3f}")
    print(f"Portfolio Sharpe:   {risk_metrics['portfolio_sharpe']:>8.3f}")
    print(f"Benchmark Sharpe:   {risk_metrics['benchmark_sharpe']:>8.3f}")
    print(f"Information Ratio:  {risk_metrics['information_ratio']:>8.3f}")
    print(f"Tracking Error:     {risk_metrics['tracking_error']:>8.2%}")
    print(f"Excess Return:      {risk_metrics['excess_return']:>+8.2%}")
    
    return attribution, risk_metrics


def demo_benchmark_validation():
    """Demo benchmark validation and standardization."""
    print("\n🎯 Benchmark Validation Demo")
    print("=" * 60)
    
    standardizer = BenchmarkStandardizer()
    
    # Test different portfolio-benchmark combinations
    test_cases = [
        {
            "name": "US Large Cap Growth vs S&P 500",
            "portfolio": {
                "asset_class": "equity",
                "geography": "US",
                "investment_style": "large_cap_growth",
                "market_cap_focus": "large_cap"
            },
            "benchmark": {
                "asset_class": "equity",
                "geography": "US",
                "investment_style": "large_cap_blend",
                "market_cap_focus": "large_cap"
            }
        },
        {
            "name": "International Equity vs MSCI EAFE",
            "portfolio": {
                "asset_class": "equity",
                "geography": "International",
                "investment_style": "large_cap_blend",
                "market_cap_focus": "large_cap"
            },
            "benchmark": {
                "asset_class": "equity",
                "geography": "International",
                "investment_style": "large_cap_blend",
                "market_cap_focus": "large_cap"
            }
        },
        {
            "name": "Fixed Income vs Bond Index",
            "portfolio": {
                "asset_class": "bond",
                "geography": "US",
                "investment_style": "investment_grade",
                "duration": "intermediate"
            },
            "benchmark": {
                "asset_class": "equity",  # Mismatch!
                "geography": "US",
                "investment_style": "large_cap_blend",
                "market_cap_focus": "large_cap"
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print("-" * 50)
        
        is_appropriate, validation_notes = standardizer.validate_benchmark_appropriateness(
            test_case['portfolio'], test_case['benchmark']
        )
        
        status = "✅ Appropriate" if is_appropriate else "❌ Not Appropriate"
        print(f"Status: {status}")
        
        if validation_notes:
            print("Validation Notes:")
            for note in validation_notes:
                print(f"  • {note}")
    
    # Benchmark statistics demo
    print(f"\n📊 Benchmark Statistics Example:")
    print("-" * 40)
    
    np.random.seed(42)
    benchmark_returns = np.random.normal(0.08, 0.15, 252).tolist()
    
    stats = standardizer.calculate_benchmark_statistics(
        benchmark_returns,
        datetime(2023, 1, 1),
        datetime(2023, 12, 31)
    )
    
    print(f"Total Return:        {stats['total_return']:>8.2%}")
    print(f"Annualized Return:   {stats['annualized_return']:>8.2%}")
    print(f"Volatility:          {stats['volatility']:>8.2%}")
    print(f"Max Drawdown:        {stats['max_drawdown']:>8.2%}")
    print(f"Positive Periods:    {stats['positive_periods']:>8.1%}")
    
    return test_cases, stats


def demo_compliance_reporting():
    """Demo GIPS compliance reporting."""
    print("\n📋 GIPS Compliance Reporting Demo")
    print("=" * 60)
    
    # Create sample GIPS calculation
    result, calculator = create_sample_gips_calculation()
    
    # Generate comprehensive report
    report = calculator.generate_gips_report(
        result,
        "Acme Investment Management",
        "US Large Cap Growth Composite",
        "S&P 500 Growth Index",
        0.095  # 9.5% benchmark return
    )
    
    print("📄 GIPS Compliance Report:")
    print("-" * 40)
    
    # Display key report sections
    key_sections = [
        ('firm_name', 'Firm Name'),
        ('composite_name', 'Composite Name'),
        ('period_start', 'Period Start'),
        ('period_end', 'Period End'),
        ('time_weighted_return', 'Time-Weighted Return'),
        ('benchmark_return', 'Benchmark Return'),
        ('excess_return', 'Excess Return'),
        ('number_of_portfolios', 'Number of Portfolios'),
        ('total_assets', 'Total Assets'),
        ('compliance_level', 'Compliance Level')
    ]
    
    for key, label in key_sections:
        if key in report:
            print(f"{label:<25}: {report[key]}")
    
    print(f"\n📜 Compliance Statement:")
    print("-" * 40)
    print(report.get('compliance_statement', 'No statement available'))
    
    # Validation notes
    if result.validation_notes:
        print(f"\n⚠️  Validation Notes:")
        print("-" * 40)
        for note in result.validation_notes:
            print(f"• {note}")
    
    return report


def demo_data_processor_integration():
    """Demo integration with DataProcessor."""
    print("\n🔧 DataProcessor Integration Demo")
    print("=" * 60)
    
    # Create processor and load sample data
    processor = DataProcessor()
    
    # Create mock S&P 500 data
    years = list(range(2000, 2024))
    np.random.seed(42)
    returns = np.random.normal(0.10, 0.20, len(years))
    sp500_data = pd.DataFrame({'year': years, 'return': returns})
    
    processor.set_data(sp500_data)
    print("✅ Sample S&P 500 data loaded")
    
    # Run GIPS compliance analysis
    try:
        results = processor.compute_gips_compliance_analysis(
            start_year=2010,
            end_year=2020,
            benchmark_symbol="SPY",
            firm_name="Demo Investment Firm",
            composite_name="S&P 500 Tracking Strategy"
        )
        
        print("✅ GIPS compliance analysis completed")
        
        # Display key results
        gips_calc = results['gips_calculation']
        print(f"\n📊 Key Results:")
        print(f"  Time-Weighted Return: {gips_calc['time_weighted_return']:.2%}")
        print(f"  Compliance Level: {gips_calc['compliance_level']}")
        
        attribution = results['attribution_analysis']
        if 'risk_adjusted_metrics' in attribution:
            risk_metrics = attribution['risk_adjusted_metrics']
            print(f"  Alpha: {risk_metrics['alpha']:.4f}")
            print(f"  Beta: {risk_metrics['beta']:.3f}")
            print(f"  Information Ratio: {risk_metrics['information_ratio']:.3f}")
        
        benchmark_validation = results['benchmark_validation']
        status = "✅" if benchmark_validation['is_appropriate'] else "❌"
        print(f"  Benchmark Appropriate: {status}")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False


def main():
    """Run complete GIPS compliance demo."""
    print("🏛️ S&P 500 GIPS Compliance Demo")
    print("=" * 80)
    print("Stage 4: GIPS Compliance Implementation")
    print("=" * 80)
    
    # Demo components
    demos = [
        ("GIPS Return Calculations", demo_gips_return_calculations),
        ("Performance Attribution", demo_performance_attribution),
        ("Benchmark Validation", demo_benchmark_validation),
        ("Compliance Reporting", demo_compliance_reporting),
        ("DataProcessor Integration", demo_data_processor_integration)
    ]
    
    success_count = 0
    
    for demo_name, demo_func in demos:
        try:
            result = demo_func()
            success_count += 1
        except Exception as e:
            print(f"\n❌ {demo_name} demo failed: {e}")
            import traceback
            traceback.print_exc()
    
    # Summary
    print("\n" + "=" * 80)
    print("DEMO SUMMARY")
    print("=" * 80)
    
    print(f"✅ Completed demos: {success_count}/{len(demos)}")
    
    if success_count == len(demos):
        print("🎉 All demos completed successfully!")
        print("✅ GIPS compliance system is fully operational!")
        
        print("\n🏛️ GIPS Compliance Features:")
        print("  • Time-weighted return calculations (GIPS standard)")
        print("  • Money-weighted return calculations (IRR)")
        print("  • Modified Dietz return approximation")
        print("  • Brinson-Hood-Beebower attribution analysis")
        print("  • Risk-adjusted performance metrics")
        print("  • Benchmark appropriateness validation")
        print("  • Comprehensive compliance reporting")
        print("  • Full integration with existing analysis tools")
        
        print("\n🌐 Next steps:")
        print("  1. Open the web application: http://localhost:8501")
        print("  2. Load S&P 500 data")
        print("  3. Navigate to '🏛️ GIPS合规性' tab")
        print("  4. Configure analysis parameters")
        print("  5. Run GIPS compliance analysis")
        print("  6. Review compliance report and attribution analysis")
        
    else:
        print("⚠️  Some demos encountered issues. Please check the errors above.")
    
    print("\n" + "=" * 80)
    print("Thank you for trying the GIPS Compliance System!")
    print("=" * 80)


if __name__ == '__main__':
    main()
