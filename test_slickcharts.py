#!/usr/bin/env python3
"""
测试SlickCharts下载功能
"""

from data_processor import DataProcessor
from sp500_convergence import download_slickcharts_data
import pandas as pd


def test_direct_download():
    """测试直接下载功能"""
    print("🔍 测试直接下载功能...")
    try:
        df = download_slickcharts_data()
        print(f"✅ 直接下载成功: {len(df)} 行数据")
        print(f"   年份范围: {df['year'].min()} - {df['year'].max()}")
        return True
    except Exception as e:
        print(f"❌ 直接下载失败: {e}")
        return False


def test_data_processor():
    """测试DataProcessor中的下载功能"""
    print("\n🔍 测试DataProcessor下载功能...")
    try:
        processor = DataProcessor()
        df = processor.download_slickcharts_data()
        if df is not None:
            print(f"✅ DataProcessor下载成功: {len(df)} 行数据")
            print(f"   年份范围: {df['year'].min()} - {df['year'].max()}")
            return True
        else:
            print("❌ DataProcessor返回None")
            return False
    except Exception as e:
        print(f"❌ DataProcessor下载失败: {e}")
        return False


def test_data_validation():
    """测试数据验证"""
    print("\n🔍 测试数据验证...")
    try:
        df = download_slickcharts_data()
        
        # 检查数据质量
        print(f"数据质量检查:")
        print(f"  总行数: {len(df)}")
        print(f"  年份列类型: {df['year'].dtype}")
        print(f"  收益率列类型: {df['return'].dtype}")
        print(f"  是否有缺失值: {df.isnull().sum().sum()}")
        print(f"  年份是否连续: {df['year'].is_monotonic_increasing}")
        
        # 检查收益率范围
        min_return = df['return'].min()
        max_return = df['return'].max()
        print(f"  收益率范围: {min_return:.2%} 到 {max_return:.2%}")
        
        # 检查异常值
        extreme_negative = df[df['return'] < -0.5]
        extreme_positive = df[df['return'] > 1.0]
        
        if len(extreme_negative) > 0:
            print(f"  极端负收益率 (<-50%): {len(extreme_negative)} 个")
            for _, row in extreme_negative.iterrows():
                print(f"    {row['year']}: {row['return']:.2%}")
        
        if len(extreme_positive) > 0:
            print(f"  极端正收益率 (>100%): {len(extreme_positive)} 个")
            for _, row in extreme_positive.iterrows():
                print(f"    {row['year']}: {row['return']:.2%}")
        
        # 显示最近几年的数据
        print(f"  最近5年数据:")
        recent_data = df.tail(5)
        for _, row in recent_data.iterrows():
            print(f"    {row['year']}: {row['return']:.2%}")
        
        return True
        
    except Exception as e:
        print(f"❌ 数据验证失败: {e}")
        return False


def main():
    """主测试函数"""
    print("🧪 SlickCharts下载功能测试")
    print("=" * 50)
    
    results = []
    
    # 测试直接下载
    results.append(test_direct_download())
    
    # 测试DataProcessor
    results.append(test_data_processor())
    
    # 测试数据验证
    results.append(test_data_validation())
    
    # 总结结果
    print("\n" + "=" * 50)
    print("📊 测试结果总结")
    print("=" * 50)
    
    test_names = ["直接下载", "DataProcessor下载", "数据验证"]
    for i, (name, result) in enumerate(zip(test_names, results)):
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{i+1}. {name}: {status}")
    
    all_passed = all(results)
    if all_passed:
        print("\n🎉 所有测试通过！SlickCharts下载功能正常工作。")
    else:
        print("\n⚠️  部分测试失败，请检查相关功能。")
    
    return all_passed


if __name__ == "__main__":
    main()
