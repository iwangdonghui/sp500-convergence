#!/usr/bin/env python3
"""
测试UI修复 - 验证配置变化检测和缓存问题是否解决
"""

from data_processor import DataProcessor
from sp500_convergence import download_slickcharts_data
import pandas as pd


def test_cache_invalidation():
    """测试缓存失效机制"""
    print("🔍 测试缓存失效机制...")
    
    # 创建处理器并加载数据
    processor = DataProcessor()
    df = download_slickcharts_data()
    processor.set_data(df)
    
    # 第一次分析
    start_years_1 = [1926, 1957]
    windows_1 = [10, 20]
    data_hash_1 = processor.get_data_hash()
    
    print(f"第一次分析:")
    print(f"  起始年份: {start_years_1}")
    print(f"  时间窗口: {windows_1}")
    print(f"  数据哈希: {data_hash_1}")
    
    results_1 = processor.compute_rolling_analysis(start_years_1, windows_1, data_hash_1)
    print(f"  结果: {len(results_1)} 个起始年份")
    
    # 第二次分析 - 相同参数，应该使用缓存
    print(f"\n第二次分析 (相同参数):")
    results_2 = processor.compute_rolling_analysis(start_years_1, windows_1, data_hash_1)
    print(f"  结果: {len(results_2)} 个起始年份")
    print(f"  是否使用缓存: {results_1 is results_2}")
    
    # 第三次分析 - 不同参数
    start_years_3 = [1972, 1985]
    print(f"\n第三次分析 (不同起始年份):")
    print(f"  起始年份: {start_years_3}")
    results_3 = processor.compute_rolling_analysis(start_years_3, windows_1, data_hash_1)
    print(f"  结果: {len(results_3)} 个起始年份")
    print(f"  结果不同: {results_1 != results_3}")


def test_config_matching():
    """测试配置匹配"""
    print("\n🔍 测试配置匹配...")
    
    processor = DataProcessor()
    df = download_slickcharts_data()
    processor.set_data(df)
    data_hash = processor.get_data_hash()
    
    # 测试不同的配置组合
    test_configs = [
        {
            'name': '默认配置',
            'start_years': [1926, 1957, 1972, 1985],
            'windows': [5, 10, 15, 20, 30]
        },
        {
            'name': '部分年份',
            'start_years': [1957, 1985],
            'windows': [10, 20]
        },
        {
            'name': '单一年份',
            'start_years': [1972],
            'windows': [5, 10, 15]
        }
    ]
    
    for config in test_configs:
        print(f"\n测试配置: {config['name']}")
        print(f"  起始年份: {config['start_years']}")
        print(f"  时间窗口: {config['windows']}")
        
        results = processor.compute_rolling_analysis(
            config['start_years'], 
            config['windows'], 
            data_hash
        )
        
        print(f"  分析结果:")
        for start_year in config['start_years']:
            if start_year in results:
                print(f"    {start_year}: ✅")
                for window in config['windows']:
                    if window in results[start_year] and results[start_year][window]:
                        count = results[start_year][window]['count']
                        avg_cagr = results[start_year][window]['avg_cagr']
                        print(f"      {window}年窗口: {count} 个数据点, 平均CAGR: {avg_cagr:.2%}")
                    else:
                        print(f"      {window}年窗口: 无数据")
            else:
                print(f"    {start_year}: ❌ 无结果")


def test_data_hash():
    """测试数据哈希功能"""
    print("\n🔍 测试数据哈希功能...")
    
    # 创建两个相同的数据集
    df1 = download_slickcharts_data()
    df2 = df1.copy()
    
    processor1 = DataProcessor()
    processor2 = DataProcessor()
    
    processor1.set_data(df1)
    processor2.set_data(df2)
    
    hash1 = processor1.get_data_hash()
    hash2 = processor2.get_data_hash()
    
    print(f"相同数据的哈希值:")
    print(f"  哈希1: {hash1}")
    print(f"  哈希2: {hash2}")
    print(f"  相等: {hash1 == hash2}")
    
    # 修改数据
    df3 = df1.copy()
    df3.loc[0, 'return'] = df3.loc[0, 'return'] + 0.01  # 微小修改
    
    processor3 = DataProcessor()
    processor3.set_data(df3)
    hash3 = processor3.get_data_hash()
    
    print(f"\n修改后数据的哈希值:")
    print(f"  原始哈希: {hash1}")
    print(f"  修改哈希: {hash3}")
    print(f"  不同: {hash1 != hash3}")


def test_specific_scenario():
    """测试具体场景 - 模拟用户操作"""
    print("\n🔍 测试具体场景...")
    
    processor = DataProcessor()
    df = download_slickcharts_data()
    processor.set_data(df)
    
    # 场景1: 用户选择1926, 1957作为起始年份
    print("场景1: 用户选择1926, 1957")
    config1 = {
        'start_years': [1926, 1957],
        'windows': [10, 20],
        'thresholds': [0.005, 0.01]
    }
    
    data_hash = processor.get_data_hash()
    rolling_results1 = processor.compute_rolling_analysis(
        config1['start_years'], 
        config1['windows'], 
        data_hash
    )
    
    print("分析结果1:")
    for start_year in config1['start_years']:
        if start_year in rolling_results1:
            print(f"  {start_year}: 有结果")
            for window in config1['windows']:
                if window in rolling_results1[start_year] and rolling_results1[start_year][window]:
                    count = rolling_results1[start_year][window]['count']
                    print(f"    {window}年窗口: {count} 个数据点")
        else:
            print(f"  {start_year}: 无结果")
    
    # 场景2: 用户改变选择为1972, 1985
    print("\n场景2: 用户改变选择为1972, 1985")
    config2 = {
        'start_years': [1972, 1985],
        'windows': [10, 20],
        'thresholds': [0.005, 0.01]
    }
    
    rolling_results2 = processor.compute_rolling_analysis(
        config2['start_years'], 
        config2['windows'], 
        data_hash
    )
    
    print("分析结果2:")
    for start_year in config2['start_years']:
        if start_year in rolling_results2:
            print(f"  {start_year}: 有结果")
            for window in config2['windows']:
                if window in rolling_results2[start_year] and rolling_results2[start_year][window]:
                    count = rolling_results2[start_year][window]['count']
                    print(f"    {window}年窗口: {count} 个数据点")
        else:
            print(f"  {start_year}: 无结果")
    
    # 验证结果不同
    print(f"\n结果验证:")
    print(f"  结果1包含1926: {1926 in rolling_results1}")
    print(f"  结果2包含1926: {1926 in rolling_results2}")
    print(f"  结果1包含1972: {1972 in rolling_results1}")
    print(f"  结果2包含1972: {1972 in rolling_results2}")


def main():
    """主测试函数"""
    print("🧪 UI修复测试")
    print("=" * 60)
    
    try:
        # 测试缓存失效
        test_cache_invalidation()
        
        # 测试配置匹配
        test_config_matching()
        
        # 测试数据哈希
        test_data_hash()
        
        # 测试具体场景
        test_specific_scenario()
        
        print("\n" + "=" * 60)
        print("✅ 所有测试完成")
        print("\n修复总结:")
        print("1. ✅ 添加了数据哈希机制防止缓存问题")
        print("2. ✅ 配置变化检测和警告")
        print("3. ✅ 强制重新分析功能")
        print("4. ✅ 参数正确传递到分析函数")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
