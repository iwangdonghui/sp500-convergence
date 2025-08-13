#!/usr/bin/env python3
"""
Demo script for multi-asset analysis capabilities.

This script demonstrates the new multi-asset analysis features
added in Stage 3, including asset class comparison, correlation analysis,
and efficient frontier calculation.
"""

import pandas as pd
import numpy as np
from datetime import datetime
from multi_asset_engine import MultiAssetAnalyzer, ASSET_UNIVERSE, AssetClass
from data_processor import DataProcessor


def demo_asset_universe():
    """Demo the available asset universe."""
    print("🌐 Multi-Asset Analysis Demo")
    print("=" * 60)
    print("Available Asset Universe:")
    print("=" * 60)
    
    # Group assets by class
    assets_by_class = {}
    for symbol, asset_info in ASSET_UNIVERSE.items():
        asset_class = asset_info.asset_class.value
        if asset_class not in assets_by_class:
            assets_by_class[asset_class] = []
        
        assets_by_class[asset_class].append({
            'symbol': symbol,
            'name': asset_info.name,
            'description': asset_info.description,
            'inception_year': asset_info.inception_year
        })
    
    # Display by asset class
    for asset_class, assets in assets_by_class.items():
        print(f"\n📊 {asset_class.upper()}")
        print("-" * 40)
        for asset in assets:
            print(f"  {asset['symbol']:4} | {asset['name']:25} | {asset['description']}")
    
    print(f"\n📈 Total Assets: {len(ASSET_UNIVERSE)}")
    print(f"📋 Asset Classes: {len(assets_by_class)}")


def demo_correlation_analysis():
    """Demo correlation analysis between different asset classes."""
    print("\n" + "=" * 60)
    print("CORRELATION ANALYSIS DEMO")
    print("=" * 60)
    
    # Create analyzer
    analyzer = MultiAssetAnalyzer()
    
    # Add assets
    for symbol, asset_info in ASSET_UNIVERSE.items():
        analyzer.add_asset(asset_info)
    
    # Select diverse portfolio
    selected_assets = ['SPY', 'TLT', 'GLD', 'VNQ', 'EFA']
    print(f"Selected Assets: {selected_assets}")
    
    # Calculate correlation matrix
    correlation_matrix = analyzer.get_correlation_matrix(selected_assets, 2000, 2023)
    
    print(f"\n📊 Correlation Matrix (2000-2023):")
    print("-" * 50)
    print(correlation_matrix.round(3))
    
    # Find interesting correlations
    print(f"\n🔍 Key Insights:")
    
    # SPY vs other assets
    spy_correlations = correlation_matrix.loc['SPY'].drop('SPY')
    highest_corr = spy_correlations.idxmax()
    lowest_corr = spy_correlations.idxmin()
    
    print(f"  • S&P 500 最高相关性: {highest_corr} ({spy_correlations[highest_corr]:.3f})")
    print(f"  • S&P 500 最低相关性: {lowest_corr} ({spy_correlations[lowest_corr]:.3f})")
    
    # Diversification benefits
    avg_correlation = correlation_matrix.values[np.triu_indices_from(correlation_matrix.values, k=1)].mean()
    print(f"  • 平均相关性: {avg_correlation:.3f}")
    
    if avg_correlation < 0.7:
        print("  ✅ 良好的分散化效果")
    else:
        print("  ⚠️  相关性较高，分散化效果有限")


def demo_efficient_frontier():
    """Demo efficient frontier calculation."""
    print("\n" + "=" * 60)
    print("EFFICIENT FRONTIER DEMO")
    print("=" * 60)
    
    # Create analyzer
    analyzer = MultiAssetAnalyzer()
    
    # Add assets
    for symbol, asset_info in ASSET_UNIVERSE.items():
        analyzer.add_asset(asset_info)
    
    # Select portfolio
    selected_assets = ['SPY', 'TLT', 'GLD']
    print(f"Portfolio Assets: {selected_assets}")
    
    # Calculate efficient frontier
    frontier = analyzer.get_efficient_frontier(selected_assets, 2000, 2023, num_portfolios=1000)
    
    # Find optimal portfolio (highest Sharpe ratio)
    max_sharpe_idx = np.argmax(frontier['sharpe_ratio'])
    optimal_return = frontier['returns'][max_sharpe_idx]
    optimal_volatility = frontier['volatility'][max_sharpe_idx]
    optimal_sharpe = frontier['sharpe_ratio'][max_sharpe_idx]
    optimal_weights = frontier['weights'][max_sharpe_idx]
    
    print(f"\n🎯 Optimal Portfolio (Highest Sharpe Ratio):")
    print("-" * 50)
    print(f"  预期收益率: {optimal_return:.2%}")
    print(f"  波动率: {optimal_volatility:.2%}")
    print(f"  夏普比率: {optimal_sharpe:.3f}")
    
    print(f"\n💼 Optimal Weights:")
    for i, symbol in enumerate(selected_assets):
        asset_name = ASSET_UNIVERSE[symbol].name
        weight = optimal_weights[i]
        print(f"  {symbol} ({asset_name}): {weight:.1%}")
    
    # Portfolio statistics
    print(f"\n📊 Frontier Statistics:")
    print(f"  • 最低波动率: {min(frontier['volatility']):.2%}")
    print(f"  • 最高波动率: {max(frontier['volatility']):.2%}")
    print(f"  • 最低收益率: {min(frontier['returns']):.2%}")
    print(f"  • 最高收益率: {max(frontier['returns']):.2%}")
    print(f"  • 最高夏普比率: {max(frontier['sharpe_ratio']):.3f}")


def demo_asset_class_comparison():
    """Demo asset class performance comparison."""
    print("\n" + "=" * 60)
    print("ASSET CLASS COMPARISON DEMO")
    print("=" * 60)
    
    # Create analyzer
    analyzer = MultiAssetAnalyzer()
    
    # Add assets
    for symbol, asset_info in ASSET_UNIVERSE.items():
        analyzer.add_asset(asset_info)
    
    # Select representative assets from each class
    representative_assets = {
        'EQUITY': 'SPY',
        'BOND': 'TLT', 
        'COMMODITY': 'GLD',
        'REIT': 'VNQ',
        'INTERNATIONAL': 'EFA'
    }
    
    print("Representative Assets by Class:")
    print("-" * 40)
    
    asset_summaries = {}
    for asset_class, symbol in representative_assets.items():
        asset_info = ASSET_UNIVERSE[symbol]
        print(f"  {asset_class}: {asset_info.name} ({symbol})")
        
        # Get asset summary
        summary = analyzer.get_asset_summary(symbol, 2000, 2023)
        asset_summaries[asset_class] = summary
    
    # Compare performance metrics
    print(f"\n📊 Performance Comparison (2000-2023):")
    print("-" * 70)
    print(f"{'Asset Class':<15} {'CAGR':<8} {'Sharpe':<8} {'Max DD':<8} {'Volatility':<10}")
    print("-" * 70)
    
    for asset_class, summary in asset_summaries.items():
        metrics = summary['risk_metrics']
        cagr = metrics.get('cagr', 0)
        sharpe = metrics.get('sharpe_ratio', 0)
        max_dd = metrics.get('max_drawdown', 0)
        volatility = metrics.get('volatility', 0)
        
        print(f"{asset_class:<15} {cagr:>7.2%} {sharpe:>7.3f} {max_dd:>7.2%} {volatility:>9.2%}")
    
    # Find best performers
    best_cagr = max(asset_summaries.items(), key=lambda x: x[1]['risk_metrics'].get('cagr', 0))
    best_sharpe = max(asset_summaries.items(), key=lambda x: x[1]['risk_metrics'].get('sharpe_ratio', 0))
    
    print(f"\n🏆 Best Performers:")
    print(f"  • 最高CAGR: {best_cagr[0]} ({best_cagr[1]['risk_metrics'].get('cagr', 0):.2%})")
    print(f"  • 最高夏普比率: {best_sharpe[0]} ({best_sharpe[1]['risk_metrics'].get('sharpe_ratio', 0):.3f})")


def demo_data_processor_integration():
    """Demo integration with DataProcessor."""
    print("\n" + "=" * 60)
    print("DATA PROCESSOR INTEGRATION DEMO")
    print("=" * 60)
    
    # Create processor
    processor = DataProcessor()
    
    # Create mock S&P 500 data
    years = list(range(1990, 2024))
    np.random.seed(42)
    returns = np.random.normal(0.10, 0.20, len(years))
    sp500_data = pd.DataFrame({'year': years, 'return': returns})
    
    # Set data
    processor.set_data(sp500_data)
    print("✅ S&P 500 baseline data loaded")
    
    # Get available assets
    available_assets = processor.get_available_assets()
    print(f"✅ Available asset classes: {list(available_assets.keys())}")
    
    # Select diverse portfolio
    selected_assets = ['SPY', 'TLT', 'GLD', 'VNQ']
    processor.set_selected_assets(selected_assets)
    print(f"✅ Selected assets: {selected_assets}")
    
    # Run multi-asset analysis
    try:
        results = processor.compute_multi_asset_analysis(2000, 2023)
        print("✅ Multi-asset analysis completed")
        
        # Display key results
        print(f"\n📊 Analysis Results:")
        print(f"  • Individual assets: {len(results['individual_assets'])}")
        print(f"  • Correlation matrix: {results['correlation_matrix'].shape}")
        print(f"  • Asset classes: {len(results['asset_class_summary'])}")
        
        if 'efficient_frontier' in results:
            frontier = results['efficient_frontier']
            print(f"  • Efficient frontier portfolios: {len(frontier['returns'])}")
            print(f"  • Best Sharpe ratio: {max(frontier['sharpe_ratio']):.3f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        return False


def main():
    """Run complete multi-asset analysis demo."""
    print("🚀 S&P 500 Multi-Asset Analysis Demo")
    print("=" * 80)
    print("Stage 3: Multi-Asset Class Comparison Analysis")
    print("=" * 80)
    
    # Demo components
    demos = [
        ("Asset Universe", demo_asset_universe),
        ("Correlation Analysis", demo_correlation_analysis),
        ("Efficient Frontier", demo_efficient_frontier),
        ("Asset Class Comparison", demo_asset_class_comparison),
        ("DataProcessor Integration", demo_data_processor_integration)
    ]
    
    success_count = 0
    
    for demo_name, demo_func in demos:
        try:
            demo_func()
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
        print("✅ Multi-asset analysis system is fully operational!")
        
        print("\n🌐 Next steps:")
        print("  1. Open the web application: http://localhost:8501")
        print("  2. Load S&P 500 data")
        print("  3. Navigate to '🌐 多资产分析' tab")
        print("  4. Select assets and run multi-asset analysis")
        print("  5. Explore correlation matrices and efficient frontiers")
        
    else:
        print("⚠️  Some demos encountered issues. Please check the errors above.")
    
    print("\n" + "=" * 80)
    print("Thank you for trying the Multi-Asset Analysis System!")
    print("=" * 80)


if __name__ == '__main__':
    main()
