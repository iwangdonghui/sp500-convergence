#!/usr/bin/env python3
"""
Test script for chart layout fixes.

This script tests the improved chart layouts for multi-asset analysis,
specifically the efficient frontier and correlation matrix visualizations.
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from multi_asset_engine import MultiAssetAnalyzer, ASSET_UNIVERSE


def test_correlation_heatmap_layout():
    """Test correlation heatmap with improved layout."""
    print("🔍 Testing Correlation Heatmap Layout")
    print("=" * 50)
    
    # Create analyzer
    analyzer = MultiAssetAnalyzer()
    
    # Add assets
    for symbol, asset_info in ASSET_UNIVERSE.items():
        analyzer.add_asset(asset_info)
    
    # Select test assets
    selected_assets = ['SPY', 'TLT', 'GLD', 'VNQ']
    
    # Calculate correlation matrix
    correlation_matrix = analyzer.get_correlation_matrix(selected_assets, 2000, 2023)
    
    # Create heatmap with improved layout
    fig = go.Figure(data=go.Heatmap(
        z=correlation_matrix.values,
        x=correlation_matrix.columns,
        y=correlation_matrix.index,
        colorscale='RdBu',
        zmid=0,
        text=correlation_matrix.round(3).values,
        texttemplate="%{text}",
        textfont={"size": 10},
        hoverongaps=False
    ))
    
    fig.update_layout(
        title="资产相关性矩阵 (布局测试)",
        xaxis_title="资产",
        yaxis_title="资产",
        height=500,
        margin=dict(l=80, r=80, t=80, b=80)
    )
    
    # Save as HTML for testing
    fig.write_html("test_correlation_heatmap.html")
    print("✅ Correlation heatmap saved as 'test_correlation_heatmap.html'")
    print(f"   Matrix shape: {correlation_matrix.shape}")
    print(f"   Assets: {list(correlation_matrix.columns)}")


def test_efficient_frontier_layout():
    """Test efficient frontier chart with improved layout."""
    print("\n🎯 Testing Efficient Frontier Layout")
    print("=" * 50)
    
    # Create analyzer
    analyzer = MultiAssetAnalyzer()
    
    # Add assets
    for symbol, asset_info in ASSET_UNIVERSE.items():
        analyzer.add_asset(asset_info)
    
    # Select test assets
    selected_assets = ['SPY', 'TLT', 'GLD']
    
    # Calculate efficient frontier
    frontier_data = analyzer.get_efficient_frontier(selected_assets, 2000, 2023, num_portfolios=500)
    
    # Create chart with improved layout
    fig = go.Figure()
    
    # Add scatter plot of portfolios
    fig.add_trace(go.Scatter(
        x=frontier_data['volatility'],
        y=frontier_data['returns'],
        mode='markers',
        marker=dict(
            size=6,
            color=frontier_data['sharpe_ratio'],
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(
                title="夏普比率",
                x=1.02,
                len=0.8,
                thickness=15
            )
        ),
        text=[f"夏普比率: {sr:.3f}" for sr in frontier_data['sharpe_ratio']],
        hovertemplate="收益率: %{y:.2%}<br>波动率: %{x:.2%}<br>%{text}<extra></extra>",
        name="投资组合"
    ))
    
    # Find and highlight optimal portfolio
    max_sharpe_idx = np.argmax(frontier_data['sharpe_ratio'])
    fig.add_trace(go.Scatter(
        x=[frontier_data['volatility'][max_sharpe_idx]],
        y=[frontier_data['returns'][max_sharpe_idx]],
        mode='markers',
        marker=dict(size=15, color='red', symbol='star'),
        name="最优投资组合",
        hovertemplate="最优组合<br>收益率: %{y:.2%}<br>波动率: %{x:.2%}<extra></extra>"
    ))
    
    fig.update_layout(
        title="有效前沿分析 (布局测试)",
        xaxis_title="波动率 (年化)",
        yaxis_title="预期收益率 (年化)",
        height=500,
        margin=dict(l=60, r=120, t=80, b=60),
        showlegend=True,
        legend=dict(
            x=1.02,
            y=0.5,
            xanchor="left",
            yanchor="middle"
        )
    )
    
    # Save as HTML for testing
    fig.write_html("test_efficient_frontier.html")
    print("✅ Efficient frontier chart saved as 'test_efficient_frontier.html'")
    print(f"   Portfolios: {len(frontier_data['returns'])}")
    print(f"   Best Sharpe ratio: {max(frontier_data['sharpe_ratio']):.3f}")
    
    # Display optimal portfolio
    optimal_weights = frontier_data['weights'][max_sharpe_idx]
    print(f"\n💼 Optimal Portfolio:")
    for i, symbol in enumerate(selected_assets):
        asset_name = ASSET_UNIVERSE[symbol].name
        weight = optimal_weights[i]
        print(f"   {symbol} ({asset_name}): {weight:.1%}")


def test_layout_improvements():
    """Test overall layout improvements."""
    print("\n📊 Layout Improvements Summary")
    print("=" * 50)
    
    improvements = [
        "✅ Correlation heatmap: Added proper margins (80px all sides)",
        "✅ Efficient frontier: Moved colorbar outside plot area",
        "✅ Efficient frontier: Positioned legend to avoid overlap",
        "✅ Efficient frontier: Increased right margin for colorbar",
        "✅ Both charts: Improved title and axis spacing"
    ]
    
    for improvement in improvements:
        print(f"   {improvement}")
    
    print(f"\n🎯 Key Layout Fixes:")
    print(f"   • Colorbar positioned at x=1.02 (outside plot)")
    print(f"   • Legend positioned at x=1.02, y=0.5")
    print(f"   • Right margin increased to 120px")
    print(f"   • Colorbar thickness reduced to 15px")
    print(f"   • Colorbar length set to 80% of plot height")


def main():
    """Run all layout tests."""
    print("🎨 Chart Layout Fix Testing")
    print("=" * 80)
    print("Testing improved layouts for multi-asset analysis charts")
    print("=" * 80)
    
    try:
        # Test correlation heatmap
        test_correlation_heatmap_layout()
        
        # Test efficient frontier
        test_efficient_frontier_layout()
        
        # Summary
        test_layout_improvements()
        
        print(f"\n🎉 All layout tests completed successfully!")
        print(f"📁 Generated test files:")
        print(f"   • test_correlation_heatmap.html")
        print(f"   • test_efficient_frontier.html")
        print(f"\n🌐 Next steps:")
        print(f"   1. Open the web application: http://localhost:8501")
        print(f"   2. Navigate to '🌐 多资产分析' tab")
        print(f"   3. Run multi-asset analysis to see improved layouts")
        print(f"   4. Verify that text and legends no longer overlap")
        
    except Exception as e:
        print(f"❌ Layout test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
