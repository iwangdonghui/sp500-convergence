#!/usr/bin/env python3
"""
测试数据关联逻辑 - 验证左侧选择的起始年份和分析数据是否匹配
"""

from sp500_convergence import SP500Analyzer, download_slickcharts_data
from data_processor import DataProcessor
import pandas as pd


def test_start_year_logic():
    """测试起始年份逻辑"""
    print("🔍 测试起始年份逻辑...")
    
    # 下载数据
    df = download_slickcharts_data()
    analyzer = SP500Analyzer(df)
    
    # 测试不同的起始年份
    test_start_years = [1926, 1957, 1972, 1985, 2000]
    window_size = 10
    
    print(f"\n数据年份范围: {df['year'].min()} - {df['year'].max()}")
    print(f"测试窗口大小: {window_size}年")
    
    for start_year in test_start_years:
        print(f"\n📊 测试起始年份: {start_year}")
        
        # 计算滚动CAGR
        cagrs = analyzer.compute_rolling_cagr(window_size, start_year)
        
        if cagrs:
            print(f"  ✅ 成功计算 {len(cagrs)} 个滚动窗口")
            print(f"  第一个窗口: {start_year}-{cagrs[0][0]} CAGR: {cagrs[0][1]:.2%}")
            print(f"  最后窗口: {start_year + window_size - 1}-{cagrs[-1][0]} CAGR: {cagrs[-1][1]:.2%}")
            
            # 验证逻辑
            expected_first_end = start_year + window_size - 1
            actual_first_end = cagrs[0][0]
            
            if expected_first_end == actual_first_end:
                print(f"  ✅ 窗口计算正确")
            else:
                print(f"  ❌ 窗口计算错误: 期望 {expected_first_end}, 实际 {actual_first_end}")
        else:
            print(f"  ❌ 无法计算 (数据不足)")


def test_data_processor_logic():
    """测试DataProcessor的逻辑"""
    print("\n🔍 测试DataProcessor逻辑...")
    
    # 创建DataProcessor
    processor = DataProcessor()
    df = download_slickcharts_data()
    processor.set_data(df)
    
    # 测试配置
    start_years = [1926, 1957, 1972, 1985]
    windows = [5, 10, 15, 20]
    
    print(f"测试起始年份: {start_years}")
    print(f"测试窗口大小: {windows}")
    
    # 计算滚动分析
    rolling_results = processor.compute_rolling_analysis(start_years, windows)
    
    print(f"\n📊 分析结果:")
    for start_year in start_years:
        print(f"\n起始年份 {start_year}:")
        if start_year in rolling_results:
            for window in windows:
                if window in rolling_results[start_year] and rolling_results[start_year][window]:
                    data = rolling_results[start_year][window]
                    print(f"  {window}年窗口: {data['count']} 个数据点")
                    print(f"    结束年份范围: {min(data['end_years'])} - {max(data['end_years'])}")
                    print(f"    平均CAGR: {data['avg_cagr']:.2%}")
                else:
                    print(f"  {window}年窗口: 无数据")
        else:
            print(f"  ❌ 起始年份 {start_year} 无结果")


def test_specific_case():
    """测试具体案例"""
    print("\n🔍 测试具体案例...")
    
    df = download_slickcharts_data()
    analyzer = SP500Analyzer(df)
    
    # 测试1957年起始，10年窗口
    start_year = 1957
    window_size = 10
    
    print(f"测试案例: {start_year}年起始，{window_size}年窗口")
    
    # 检查数据可用性
    if start_year in analyzer.years:
        start_idx = analyzer.years.index(start_year)
        print(f"起始年份索引: {start_idx}")
        print(f"起始年份数据: {analyzer.years[start_idx]} - {analyzer.returns[start_idx]:.2%}")
        
        # 检查是否有足够数据
        if start_idx + window_size <= len(analyzer.years):
            end_idx = start_idx + window_size
            print(f"第一个窗口数据:")
            for i in range(start_idx, end_idx):
                print(f"  {analyzer.years[i]}: {analyzer.returns[i]:.2%}")
            
            # 计算CAGR
            cagrs = analyzer.compute_rolling_cagr(window_size, start_year)
            if cagrs:
                print(f"\n第一个窗口CAGR: {cagrs[0][1]:.2%}")
                print(f"窗口期间: {start_year}-{cagrs[0][0]}")
                
                # 手动验证计算
                window_returns = analyzer.returns[start_idx:end_idx]
                manual_total = 1.0
                for ret in window_returns:
                    manual_total *= (1 + ret)
                manual_cagr = manual_total ** (1.0 / window_size) - 1
                print(f"手动计算CAGR: {manual_cagr:.2%}")
                
                if abs(cagrs[0][1] - manual_cagr) < 1e-6:
                    print("✅ CAGR计算正确")
                else:
                    print("❌ CAGR计算错误")
            else:
                print("❌ 无法计算CAGR")
        else:
            print("❌ 数据不足")
    else:
        print(f"❌ 起始年份 {start_year} 不在数据中")


def test_ui_config_matching():
    """测试UI配置匹配"""
    print("\n🔍 测试UI配置匹配...")
    
    # 模拟UI配置
    ui_config = {
        'start_years': [1926, 1957, 1972, 1985],
        'windows': [5, 10, 15, 20, 30],
        'thresholds': [0.0025, 0.005, 0.0075, 0.01]
    }
    
    print(f"UI配置:")
    print(f"  起始年份: {ui_config['start_years']}")
    print(f"  时间窗口: {ui_config['windows']}")
    
    # 创建处理器并分析
    processor = DataProcessor()
    df = download_slickcharts_data()
    processor.set_data(df)
    
    rolling_results = processor.compute_rolling_analysis(
        ui_config['start_years'], 
        ui_config['windows']
    )
    
    print(f"\n分析结果验证:")
    for start_year in ui_config['start_years']:
        print(f"\n起始年份 {start_year}:")
        if start_year in rolling_results:
            print(f"  ✅ 有分析结果")
            for window in ui_config['windows']:
                if window in rolling_results[start_year]:
                    if rolling_results[start_year][window]:
                        count = rolling_results[start_year][window]['count']
                        print(f"    {window}年窗口: {count} 个数据点")
                    else:
                        print(f"    {window}年窗口: 无数据 (可能数据不足)")
                else:
                    print(f"    {window}年窗口: 未计算")
        else:
            print(f"  ❌ 无分析结果")


def main():
    """主测试函数"""
    print("🧪 数据关联逻辑测试")
    print("=" * 60)
    
    try:
        # 测试起始年份逻辑
        test_start_year_logic()
        
        # 测试DataProcessor逻辑
        test_data_processor_logic()
        
        # 测试具体案例
        test_specific_case()
        
        # 测试UI配置匹配
        test_ui_config_matching()
        
        print("\n" + "=" * 60)
        print("✅ 所有测试完成")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
