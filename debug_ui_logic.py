#!/usr/bin/env python3
"""
调试UI逻辑 - 检查配置传递和缓存问题
"""

import streamlit as st
from data_processor import DataProcessor
from ui_components import create_sidebar_config
import pandas as pd


def debug_config_flow():
    """调试配置流程"""
    st.title("🔍 配置流程调试")
    
    # 创建侧边栏配置
    config = create_sidebar_config()
    
    st.subheader("📋 当前配置")
    st.write("**数据源:**", config['data_source'])
    st.write("**起始年份:**", config['start_years'])
    st.write("**时间窗口:**", config['windows'])
    st.write("**阈值:**", config['thresholds'])
    
    # 检查session state
    st.subheader("🔧 Session State")
    if 'data_loaded' in st.session_state:
        st.write("**数据已加载:**", st.session_state.data_loaded)
    else:
        st.write("**数据已加载:** False (未初始化)")
    
    if 'analysis_results' in st.session_state:
        if st.session_state.analysis_results:
            st.write("**分析结果存在:** True")
            if 'config' in st.session_state.analysis_results:
                stored_config = st.session_state.analysis_results['config']
                st.write("**存储的配置:**")
                st.json(stored_config)
                
                # 比较配置
                if stored_config['start_years'] != config['start_years']:
                    st.error("⚠️ 配置不匹配！存储的起始年份与当前选择不同")
                else:
                    st.success("✅ 配置匹配")
            else:
                st.warning("分析结果中没有配置信息")
        else:
            st.write("**分析结果存在:** False (空)")
    else:
        st.write("**分析结果存在:** False (未初始化)")
    
    # 测试按钮
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 清除缓存"):
            st.cache_data.clear()
            st.success("缓存已清除")
            st.rerun()
    
    with col2:
        if st.button("🗑️ 清除Session State"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.success("Session State已清除")
            st.rerun()
    
    with col3:
        if st.button("📊 重新分析"):
            if 'data_processor' in st.session_state and st.session_state.data_processor.analyzer:
                processor = st.session_state.data_processor
                
                with st.spinner("重新分析中..."):
                    rolling_results = processor.compute_rolling_analysis(
                        config['start_years'], 
                        config['windows']
                    )
                    
                    st.session_state.analysis_results = {
                        'rolling': rolling_results,
                        'config': config
                    }
                
                st.success("重新分析完成")
                st.rerun()
            else:
                st.error("请先加载数据")


def debug_data_flow():
    """调试数据流程"""
    st.subheader("📊 数据流程调试")
    
    if 'data_processor' in st.session_state and st.session_state.data_processor.data is not None:
        processor = st.session_state.data_processor
        data_summary = processor.get_data_summary()
        
        st.write("**数据摘要:**")
        st.json(data_summary)
        
        # 显示原始数据的前几行和后几行
        st.write("**数据前5行:**")
        st.dataframe(processor.data.head())
        
        st.write("**数据后5行:**")
        st.dataframe(processor.data.tail())
        
    else:
        st.warning("没有加载数据")


def debug_analysis_results():
    """调试分析结果"""
    st.subheader("🔬 分析结果调试")
    
    if 'analysis_results' in st.session_state and st.session_state.analysis_results:
        results = st.session_state.analysis_results
        
        if 'rolling' in results:
            rolling_results = results['rolling']
            st.write("**滚动分析结果结构:**")
            
            for start_year in rolling_results.keys():
                st.write(f"起始年份 {start_year}:")
                if rolling_results[start_year]:
                    for window in rolling_results[start_year].keys():
                        if rolling_results[start_year][window]:
                            count = rolling_results[start_year][window]['count']
                            avg_cagr = rolling_results[start_year][window]['avg_cagr']
                            st.write(f"  {window}年窗口: {count} 个数据点, 平均CAGR: {avg_cagr:.2%}")
                        else:
                            st.write(f"  {window}年窗口: 无数据")
                else:
                    st.write(f"  无数据")
        
        if 'config' in results:
            st.write("**分析时使用的配置:**")
            st.json(results['config'])
    else:
        st.warning("没有分析结果")


def main():
    """主函数"""
    st.set_page_config(
        page_title="UI逻辑调试",
        page_icon="🔍",
        layout="wide"
    )
    
    # 初始化session state
    if 'data_processor' not in st.session_state:
        st.session_state.data_processor = DataProcessor()
    
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = {}
    
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False
    
    # 调试界面
    debug_config_flow()
    
    st.divider()
    
    debug_data_flow()
    
    st.divider()
    
    debug_analysis_results()
    
    # 快速加载数据按钮
    st.divider()
    st.subheader("🚀 快速操作")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📥 快速加载SlickCharts数据"):
            processor = st.session_state.data_processor
            try:
                data = processor.download_slickcharts_data()
                if data is not None:
                    success = processor.set_data(data)
                    if success:
                        st.session_state.data_loaded = True
                        st.success("数据加载成功")
                        st.rerun()
                    else:
                        st.error("数据设置失败")
                else:
                    st.error("数据下载失败")
            except Exception as e:
                st.error(f"加载失败: {e}")
    
    with col2:
        if st.button("🔄 重置所有状态"):
            # 清除所有状态
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.cache_data.clear()
            st.success("所有状态已重置")
            st.rerun()


if __name__ == "__main__":
    main()
