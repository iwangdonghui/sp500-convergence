#!/usr/bin/env python3
"""
Demo script to showcase font improvements in the GIPS compliance interface.
This script creates a standalone demo of the improved font styling.
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime


def apply_demo_css():
    """Apply the improved CSS styles for demonstration."""
    st.markdown("""
    <style>
        /* 全局字体设置 */
        .stApp {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "Helvetica Neue", Helvetica, Arial, sans-serif;
        }
        
        /* 中文字体优化 */
        .stMarkdown, .stText, .stSelectbox, .stTextInput {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "Helvetica Neue", Helvetica, Arial, sans-serif;
        }
        
        /* 数字和百分比字体优化 */
        .metric-value {
            font-family: "SF Mono", "Monaco", "Inconsolata", "Roboto Mono", "Source Code Pro", monospace;
            font-weight: 600;
            font-size: 1.5rem;
            line-height: 1.2;
        }
        
        /* 标题字体优化 */
        h1, h2, h3, h4, h5, h6 {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "Helvetica Neue", Helvetica, Arial, sans-serif;
            font-weight: 600;
            line-height: 1.3;
        }
        
        /* GIPS合规性分析结果样式 */
        .gips-result-container {
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 1.5rem;
            margin: 1rem 0;
        }
        
        .gips-metric-title {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "Helvetica Neue", Helvetica, Arial, sans-serif;
            font-size: 0.875rem;
            font-weight: 500;
            color: #64748b;
            margin-bottom: 0.25rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        .gips-metric-value {
            font-family: "SF Mono", "Monaco", "Inconsolata", "Roboto Mono", "Source Code Pro", monospace;
            font-size: 1.875rem;
            font-weight: 700;
            color: #1e293b;
            line-height: 1.1;
            margin-bottom: 0.5rem;
        }
        
        .gips-compliance-status {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "Helvetica Neue", Helvetica, Arial, sans-serif;
            font-size: 1.125rem;
            font-weight: 600;
            padding: 0.5rem 1rem;
            border-radius: 6px;
            display: inline-block;
        }
        
        .compliance-full {
            background-color: #dcfce7;
            color: #166534;
            border: 1px solid #bbf7d0;
        }
        
        .compliance-partial {
            background-color: #fef3c7;
            color: #92400e;
            border: 1px solid #fde68a;
        }
        
        .compliance-none {
            background-color: #fee2e2;
            color: #991b1b;
            border: 1px solid #fecaca;
        }
        
        .demo-section {
            background: white;
            padding: 2rem;
            border-radius: 12px;
            box-shadow: 0 2px 6px rgba(15, 23, 42, 0.08);
            margin: 1rem 0;
        }
    </style>
    """, unsafe_allow_html=True)


def demo_before_after():
    """Show before and after comparison."""
    st.header("🎨 字体改进对比演示")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("❌ 改进前")
        st.markdown("""
        <div style="background: #f5f5f5; padding: 1rem; border-radius: 8px;">
            <div style="font-family: Arial; font-size: 0.8rem; color: #666;">时间加权收益率</div>
            <div style="font-family: Arial; font-size: 1.2rem; font-weight: normal;">25.02%</div>
            <div style="font-family: Arial; font-size: 0.8rem; color: #666;">合规性等级</div>
            <div style="font-family: Arial; font-size: 1rem;">Full Compliance</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("**问题:**")
        st.markdown("- 中文字体显示不够清晰")
        st.markdown("- 数字字体不够专业")
        st.markdown("- 视觉层次不明确")
        st.markdown("- 缺乏视觉吸引力")
    
    with col2:
        st.subheader("✅ 改进后")
        st.markdown("""
        <div class="gips-result-container">
            <div style="text-align: center; padding: 1rem;">
                <div class="gips-metric-title">时间加权收益率</div>
                <div class="gips-metric-value">25.02%</div>
                <div style="font-size: 0.75rem; color: #64748b; margin-top: 0.25rem;">GIPS标准要求的核心指标</div>
            </div>
            <div style="text-align: center; padding: 1rem; margin-top: 1rem;">
                <div class="gips-metric-title">合规性等级</div>
                <div class="gips-compliance-status compliance-full" style="margin: 0.5rem 0;">
                    ✅ Full Compliance
                </div>
                <div style="font-size: 0.75rem; color: #64748b;">GIPS合规性评估</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("**改进:**")
        st.markdown("- 优化的中文字体栈")
        st.markdown("- 专业的等宽数字字体")
        st.markdown("- 清晰的视觉层次")
        st.markdown("- 彩色状态标签")


def demo_gips_results():
    """Demo the improved GIPS results display."""
    st.header("🏛️ GIPS合规性分析结果演示")
    
    # Create sample data
    sample_data = {
        'time_weighted_return': 0.2502,
        'money_weighted_return': 0.2034,
        'compliance_level': 'full_compliance',
        'period': '1926-01-01 至 2024-12-31'
    }
    
    st.markdown('<div class="gips-result-container">', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(
            f"""
            <div style="text-align: center; padding: 1rem;">
                <div class="gips-metric-title">时间加权收益率</div>
                <div class="gips-metric-value">{sample_data['time_weighted_return']:.2%}</div>
                <div style="font-size: 0.75rem; color: #64748b; margin-top: 0.25rem;">GIPS标准要求的核心指标</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col2:
        st.markdown(
            f"""
            <div style="text-align: center; padding: 1rem;">
                <div class="gips-metric-title">资金加权收益率</div>
                <div class="gips-metric-value">{sample_data['money_weighted_return']:.2%}</div>
                <div style="font-size: 0.75rem; color: #64748b; margin-top: 0.25rem;">内部收益率(IRR)</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col3:
        st.markdown(
            f"""
            <div style="text-align: center; padding: 1rem;">
                <div class="gips-metric-title">合规性等级</div>
                <div class="gips-compliance-status compliance-full" style="margin: 0.5rem 0;">
                    ✅ Full Compliance
                </div>
                <div style="font-size: 0.75rem; color: #64748b;">GIPS合规性评估</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col4:
        st.markdown(
            f"""
            <div style="text-align: center; padding: 1rem;">
                <div class="gips-metric-title">分析期间</div>
                <div class="gips-metric-value" style="font-size: 1.25rem; line-height: 1.3;">{sample_data['period']}</div>
                <div style="font-size: 0.75rem; color: #64748b; margin-top: 0.25rem;">GIPS分析时间范围</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    st.markdown('</div>', unsafe_allow_html=True)


def demo_compliance_statuses():
    """Demo different compliance status displays."""
    st.header("🎯 合规性状态演示")
    
    statuses = [
        {'level': 'full_compliance', 'icon': '✅', 'text': 'Full Compliance', 'class': 'compliance-full'},
        {'level': 'partial_compliance', 'icon': '⚠️', 'text': 'Partial Compliance', 'class': 'compliance-partial'},
        {'level': 'non_compliance', 'icon': '❌', 'text': 'Non Compliance', 'class': 'compliance-none'}
    ]
    
    col1, col2, col3 = st.columns(3)
    
    for i, status in enumerate(statuses):
        with [col1, col2, col3][i]:
            st.markdown(
                f"""
                <div class="demo-section" style="text-align: center;">
                    <div class="gips-metric-title">{status['level'].replace('_', ' ').title()}</div>
                    <div class="gips-compliance-status {status['class']}" style="margin: 1rem 0;">
                        {status['icon']} {status['text']}
                    </div>
                    <div style="font-size: 0.75rem; color: #64748b;">示例状态显示</div>
                </div>
                """,
                unsafe_allow_html=True
            )


def demo_font_features():
    """Demo specific font features."""
    st.header("🔤 字体特性演示")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("中文字体优化")
        st.markdown("""
        <div class="demo-section">
            <h3>标题层次演示</h3>
            <h4>这是四级标题</h4>
            <h5>这是五级标题</h5>
            <p>这是正文内容，使用优化的中文字体栈，包括PingFang SC、Microsoft YaHei等字体，确保在不同操作系统上都有良好的显示效果。</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.subheader("数字字体优化")
        st.markdown("""
        <div class="demo-section">
            <div class="gips-metric-title">数字显示示例</div>
            <div class="gips-metric-value">123,456.78</div>
            <div class="gips-metric-value">-45.67%</div>
            <div class="gips-metric-value">$1,234,567</div>
            <div style="font-size: 0.75rem; color: #64748b; margin-top: 1rem;">
                使用等宽字体确保数字对齐和专业外观
            </div>
        </div>
        """, unsafe_allow_html=True)


def main():
    """Main demo function."""
    st.set_page_config(
        page_title="字体改进演示",
        page_icon="🎨",
        layout="wide"
    )
    
    # Apply custom CSS
    apply_demo_css()
    
    st.title("🎨 GIPS合规性界面字体改进演示")
    st.markdown("---")
    
    # Demo sections
    demo_before_after()
    st.markdown("---")
    
    demo_gips_results()
    st.markdown("---")
    
    demo_compliance_statuses()
    st.markdown("---")
    
    demo_font_features()
    st.markdown("---")
    
    # Summary
    st.header("📋 改进总结")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("✨ 主要改进")
        improvements = [
            "优化的中文字体栈 (PingFang SC, Microsoft YaHei)",
            "专业的等宽数字字体 (SF Mono, Roboto Mono)",
            "清晰的视觉层次和字体权重",
            "彩色的合规性状态标签",
            "改善的可读性和对比度",
            "跨平台字体兼容性",
            "响应式设计支持"
        ]
        
        for improvement in improvements:
            st.markdown(f"• {improvement}")
    
    with col2:
        st.subheader("🎯 用户体验提升")
        benefits = [
            "更清晰的中文文本显示",
            "更专业的数字和百分比显示",
            "更直观的合规性状态识别",
            "更好的视觉层次结构",
            "更高的整体可读性",
            "更一致的跨设备体验",
            "更符合现代设计标准"
        ]
        
        for benefit in benefits:
            st.markdown(f"• {benefit}")
    
    st.success("🎉 字体改进已成功应用到GIPS合规性分析界面！")


if __name__ == '__main__':
    main()
