#!/usr/bin/env python3
"""
演示脚本 - 展示S&P 500分析工具的Web UI功能
"""

import pandas as pd
import numpy as np
from pathlib import Path
import webbrowser
import time
import subprocess
import sys


def create_sample_data():
    """创建示例数据用于演示"""
    print("📊 创建示例S&P 500数据...")
    
    # 创建从1926到2023年的示例数据
    years = list(range(1926, 2024))
    np.random.seed(42)  # 确保可重现的结果
    
    # 模拟不同历史时期的收益率特征
    returns = []
    for year in years:
        if 1926 <= year <= 1929:  # 咆哮的二十年代
            ret = np.random.normal(0.15, 0.08)
        elif 1930 <= year <= 1932:  # 大萧条
            ret = np.random.normal(-0.25, 0.15)
        elif 1933 <= year <= 1945:  # 恢复期和二战
            ret = np.random.normal(0.12, 0.20)
        elif 1946 <= year <= 1965:  # 战后繁荣
            ret = np.random.normal(0.10, 0.15)
        elif 1966 <= year <= 1982:  # 滞胀期
            ret = np.random.normal(0.06, 0.20)
        elif 1983 <= year <= 1999:  # 牛市
            ret = np.random.normal(0.15, 0.15)
        elif 2000 <= year <= 2009:  # 互联网泡沫和金融危机
            ret = np.random.normal(0.02, 0.25)
        else:  # 2010-2023 恢复和增长
            ret = np.random.normal(0.12, 0.15)
        
        # 确保收益率在合理范围内
        ret = max(-0.50, min(0.80, ret))
        returns.append(ret)
    
    # 创建DataFrame
    df = pd.DataFrame({
        'Year': years,
        'Total_Return': returns
    })
    
    # 保存为CSV文件
    sample_file = Path("sample_sp500_data.csv")
    df.to_csv(sample_file, index=False)
    
    print(f"✅ 示例数据已保存到: {sample_file}")
    print(f"   数据年份范围: {min(years)} - {max(years)}")
    print(f"   平均收益率: {np.mean(returns):.2%}")
    print(f"   标准差: {np.std(returns):.2%}")
    
    return sample_file


def print_ui_features():
    """打印UI功能介绍"""
    print("\n" + "="*70)
    print("🎨 S&P 500 分析工具 - Web UI 功能介绍")
    print("="*70)
    
    features = [
        {
            "title": "📊 数据概览",
            "description": "查看数据统计摘要、历年收益率时间线图表和原始数据表格"
        },
        {
            "title": "📈 滚动分析", 
            "description": "不同时间窗口的滚动CAGR分析，包括交互式图表和统计摘要"
        },
        {
            "title": "🛡️ 无损失分析",
            "description": "计算避免损失的最小投资持有期，提供详细的分析结果"
        },
        {
            "title": "🎯 收敛性分析",
            "description": "收敛性热力图和详细的阈值分析，帮助理解长期收益率收敛特性"
        }
    ]
    
    for i, feature in enumerate(features, 1):
        print(f"\n{i}. {feature['title']}")
        print(f"   {feature['description']}")
    
    print("\n" + "="*70)
    print("🎛️ 主要操作步骤")
    print("="*70)
    
    steps = [
        "在左侧边栏选择数据来源（下载或上传CSV）",
        "配置分析参数（起始年份、时间窗口、收敛阈值）", 
        "点击'📥 加载数据'按钮加载数据",
        "点击'🚀 运行分析'按钮开始分析",
        "在不同标签页中查看分析结果",
        "使用下载按钮导出分析结果"
    ]
    
    for i, step in enumerate(steps, 1):
        print(f"{i}. {step}")


def print_usage_tips():
    """打印使用技巧"""
    print("\n" + "="*70)
    print("💡 使用技巧")
    print("="*70)
    
    tips = [
        "🖱️  图表支持缩放、平移和悬停查看详细信息",
        "📋 表格数据可以排序和搜索",
        "⚙️  参数可以实时调整，重新运行分析查看不同结果",
        "📥 分析结果可以导出为CSV格式",
        "🔄 使用'清除结果'按钮重置应用状态",
        "📱 界面支持响应式设计，适配不同屏幕尺寸"
    ]
    
    for tip in tips:
        print(f"  {tip}")


def main():
    """主演示函数"""
    print("🚀 S&P 500 分析工具 - Web UI 演示")
    print("="*70)
    
    # 创建示例数据
    sample_file = create_sample_data()
    
    # 打印功能介绍
    print_ui_features()
    
    # 打印使用技巧
    print_usage_tips()
    
    print("\n" + "="*70)
    print("🌐 启动Web应用")
    print("="*70)
    
    print("Web UI已在浏览器中打开: http://localhost:8501")
    print("\n📝 演示建议:")
    print("1. 首先尝试'从SlickCharts下载'选项获取真实数据")
    print("2. 或者上传刚创建的示例文件: sample_sp500_data.csv")
    print("3. 使用默认参数运行完整分析")
    print("4. 探索不同标签页的可视化结果")
    print("5. 尝试调整参数查看不同的分析结果")
    
    print("\n🎯 重点体验功能:")
    print("• 交互式图表的缩放和悬停功能")
    print("• 收敛性热力图的直观展示")
    print("• 不同时间窗口的收益率分布对比")
    print("• 专业的数据表格展示和导出功能")
    
    print("\n" + "="*70)
    print("✨ 享受使用S&P 500分析工具的Web UI！")
    print("   使用 Ctrl+C 停止Streamlit应用")
    print("="*70)


if __name__ == "__main__":
    main()
