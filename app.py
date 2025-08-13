"""
Streamlit Web Application for S&P 500 Rolling Returns and Convergence Analysis
"""

import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, List, Any
import traceback

# Import custom modules
from data_processor import DataProcessor
from ui_components import (
    apply_custom_css, create_header, create_sidebar_config,
    display_data_summary, create_returns_timeline_chart,
    create_rolling_cagr_chart, create_window_comparison_chart,
    create_convergence_heatmap, create_no_loss_chart,
    display_analysis_table, create_download_section,
    show_info_message, create_metric_cards, generate_summary_report
)
from config import APP_TITLE, MESSAGES, FOOTER_TEXT


# Page configuration
st.set_page_config(
    page_title=APP_TITLE,
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)


def initialize_session_state():
    """Initialize session state variables."""
    if 'data_processor' not in st.session_state:
        st.session_state.data_processor = DataProcessor()
    
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = {}
    
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False

    # 默认语言：中文（非双语）
    if 'bi_lang' not in st.session_state:
        st.session_state.bi_lang = False


def load_data(config: Dict[str, Any]) -> bool:
    """Load data based on configuration."""
    processor = st.session_state.data_processor
    
    try:
        if config['data_source'] == "从SlickCharts下载":
            data = processor.download_slickcharts_data()
        else:
            if config['uploaded_file'] is not None:
                data = processor.load_csv_data(config['uploaded_file'])
            else:
                st.warning("请上传CSV文件")
                return False
        
        if data is not None:
            success = processor.set_data(data)
            if success:
                st.session_state.data_loaded = True
                return True
    
    except Exception as e:
        st.error(f"数据加载失败: {str(e)}")
        st.error(traceback.format_exc())
    
    return False


def run_analysis(config: Dict[str, Any]):
    """Run the complete analysis."""
    if not st.session_state.data_loaded:
        st.warning("请先加载数据")
        return
    
    processor = st.session_state.data_processor
    
    try:
        with st.spinner("正在进行分析..."):
            # Get data hash for cache invalidation
            data_hash = processor.get_data_hash()

            # Compute rolling analysis
            rolling_results = processor.compute_rolling_analysis(
                config['start_years'],
                config['windows'],
                data_hash
            )

            # Compute no-loss analysis
            no_loss_results = processor.compute_no_loss_analysis(
                config['start_years'],
                data_hash
            )

            # Compute convergence analysis
            convergence_results = processor.compute_convergence_analysis(
                config['start_years'],
                config['thresholds'],
                data_hash
            )
            
            # Store results in session state
            st.session_state.analysis_results = {
                'rolling': rolling_results,
                'no_loss': no_loss_results,
                'convergence': convergence_results,
                'config': config
            }
            
            st.success(MESSAGES['analysis_complete'])
    
    except Exception as e:
        st.error(f"分析失败: {str(e)}")
        st.error(traceback.format_exc())


def display_data_overview():
    """Display data overview tab."""
    processor = st.session_state.data_processor
    
    if not st.session_state.data_loaded:
        show_info_message("请先在侧边栏配置数据源并加载数据", "info")
        return
    
    # Display data summary
    summary = processor.get_data_summary()
    display_data_summary(summary)
    
    # Display returns timeline chart
    st.subheader("📊 历年收益率时间线")
    timeline_chart = create_returns_timeline_chart(processor.data)
    st.plotly_chart(timeline_chart, use_container_width=True)
    
    # Display raw data table
    st.subheader("📋 原始数据")
    st.dataframe(
        processor.data,
        use_container_width=True,
        height=400
    )


def display_rolling_analysis():
    """Display rolling CAGR analysis tab."""
    if 'rolling' not in st.session_state.analysis_results:
        show_info_message("请先运行分析", "info")
        return
    
    rolling_results = st.session_state.analysis_results['rolling']
    config = st.session_state.analysis_results['config']
    
    # Display charts for each start year
    for start_year in config['start_years']:
        st.subheader(f"📈 起始年份: {start_year}")
        
        # Rolling CAGR chart
        chart = create_rolling_cagr_chart(rolling_results, start_year)
        if chart:
            st.plotly_chart(chart, use_container_width=True)
        
        # Summary table
        processor = st.session_state.data_processor
        summary_df = processor.create_summary_dataframe(rolling_results, start_year)
        
        if not summary_df.empty:
            format_cols = {
                'best_cagr': 'percentage',
                'worst_cagr': 'percentage',
                'avg_cagr': 'percentage',
                'std_cagr': 'percentage',
                'p10_cagr': 'percentage',
                'median_cagr': 'percentage',
                'p90_cagr': 'percentage',
                'stability_index': 'decimal',
                'variation_coeff': 'decimal'
            }
            display_analysis_table(summary_df, f"窗口统计摘要 - {start_year}", format_cols)
        
        st.divider()
    
    # Window comparison chart
    st.subheader("📊 时间窗口比较")
    comparison_chart = create_window_comparison_chart(rolling_results, config['start_years'])
    st.plotly_chart(comparison_chart, use_container_width=True)


def display_no_loss_analysis():
    """Display no-loss analysis tab."""
    if 'no_loss' not in st.session_state.analysis_results:
        show_info_message("请先运行分析", "info")
        return
    
    no_loss_results = st.session_state.analysis_results['no_loss']
    
    # Display chart
    chart = create_no_loss_chart(no_loss_results)
    if chart:
        st.plotly_chart(chart, use_container_width=True)
    
    # Display detailed table
    if no_loss_results:
        data_rows = []
        for start_year, result in no_loss_results.items():
            data_rows.append({
                '起始年份': start_year,
                '最小持有期': result['min_holding_years'],
                '最差窗口': result['worst_window'],
                '最差CAGR': result['worst_cagr'],
                '最佳窗口': result['best_window'],
                '最佳CAGR': result['best_cagr'],
                '平均CAGR': result['average_cagr'],
                '检查窗口数': result['num_windows_checked']
            })
        
        df = pd.DataFrame(data_rows)
        format_cols = {
            '最差CAGR': 'percentage',
            '最佳CAGR': 'percentage',
            '平均CAGR': 'percentage'
        }
        display_analysis_table(df, "无损失持有期详细分析", format_cols)


def display_convergence_analysis():
    """Display convergence analysis tab."""
    if 'convergence' not in st.session_state.analysis_results:
        show_info_message("请先运行分析", "info")
        return
    
    convergence_results = st.session_state.analysis_results['convergence']
    config = st.session_state.analysis_results['config']
    
    # Display heatmap
    st.subheader("🔥 收敛性热力图")
    heatmap = create_convergence_heatmap(
        convergence_results,
        config['start_years'],
        config['thresholds']
    )
    st.plotly_chart(heatmap, use_container_width=True)

    # AI-like summary report (local heuristic)
    with st.expander("🧠 生成综合智能总结（滚动 + 无损失 + 收敛）", expanded=False):
        target_thr = st.select_slider(
            "选择目标收敛阈值（用于建议最短持有期）",
            options=[f"{t:.2%}" for t in config['thresholds']] if config.get('thresholds') else ["0.50%"],
            value=(f"{config['thresholds'][len(config['thresholds'])//2]:.2%}" if config.get('thresholds') else "0.50%")
        )
        granularity = st.radio("报告粒度 / Report granularity", ["简版", "标准", "详细"], index=1, horizontal=True)
        bi = st.toggle("中英双语 / Bilingual", value=st.session_state.get("bi_lang", False), key="bi_lang")
        col_a, col_b = st.columns([1, 1])
        with col_a:
            gen_clicked = st.button("✨ 生成/更新总结", key="gen_report")
        with col_b:
            if st.button("🗑️ 清除报告", key="clear_report"):
                st.session_state.pop('ai_report_md', None)
        if gen_clicked:
            # 将选择的字符串阈值转为小数
            try:
                thr = float(target_thr.strip('%'))/100.0
            except Exception:
                thr = None
            depth_map = {"简版": "brief", "标准": "standard", "详细": "detailed"}
            report_md = generate_summary_report(
                st.session_state.analysis_results['rolling'],
                st.session_state.analysis_results['no_loss'],
                st.session_state.analysis_results['convergence'],
                config,
                target_threshold=thr,
                language='bi' if st.session_state.get("bi_lang", True) else 'zh',
                depth=depth_map.get(granularity, 'standard')
            )
            st.session_state['ai_report_md'] = report_md
        # 始终展示已生成的报告与下载区（如有）
        if 'ai_report_md' in st.session_state and st.session_state['ai_report_md']:
            st.markdown(st.session_state['ai_report_md'])
            create_download_section({'ai_report_md': st.session_state['ai_report_md']}, filename_prefix="sp500_ai_summary")

    # Display detailed table
    data_rows = []
    for start_year in config['start_years']:
        if start_year in convergence_results:
            for threshold in config['thresholds']:
                if threshold in convergence_results[start_year]:
                    result = convergence_results[start_year][threshold]
                    data_rows.append({
                        '起始年份': start_year,
                        '阈值': threshold,
                        '最小持有期': result['min_holding_years'],
                        '最佳窗口': result['best_window'],
                        '最佳CAGR': result['best_cagr'],
                        '最差窗口': result['worst_window'],
                        '最差CAGR': result['worst_cagr'],
                        '收益差': result['spread']
                    })
    
    if data_rows:
        df = pd.DataFrame(data_rows)
        format_cols = {
            '阈值': 'percentage',
            '最佳CAGR': 'percentage',
            '最差CAGR': 'percentage',
            '收益差': 'decimal'
        }
        display_analysis_table(df, "收敛性分析详细结果", format_cols)


def main():
    """Main application function."""
    # Initialize session state
    initialize_session_state()
    
    # Apply custom CSS
    apply_custom_css()
    
    # Create header
    create_header()

    # 环境自检（默认隐藏，仅当在 secrets 中设置 SHOW_ENV_CHECK=true 时显示）
    if st.secrets.get("SHOW_ENV_CHECK", False):
        try:
            import reportlab  # type: ignore
            st.sidebar.success("PDF 组件：reportlab 可用")
        except Exception:
            st.sidebar.warning(
                "PDF 组件不可用：未安装 reportlab 或网络阻断。\n\n"
                "安装建议：\n"
                "1) pip install -i https://pypi.tuna.tsinghua.edu.cn/simple reportlab==3.6.13\n"
                "2) pip install --upgrade pip certifi setuptools wheel && pip install reportlab==3.6.13\n"
            )

    # Create sidebar configuration
    config = create_sidebar_config()

    # Check if configuration has changed
    config_changed = False
    if 'last_config' in st.session_state:
        if st.session_state.last_config != config:
            config_changed = True
            st.session_state.last_config = config
    else:
        st.session_state.last_config = config

    # If config changed and we have analysis results, show warning
    if config_changed and st.session_state.analysis_results:
        st.warning("⚠️ 分析参数已更改，请重新运行分析以获取最新结果")

    # Main content area
    col1, col2 = st.columns([3, 1])
    
    with col2:
        st.subheader("🎛️ 操作面板")
        
        # Load data button
        if st.button("📥 加载数据", use_container_width=True):
            load_data(config)
        
        # Run analysis button
        if st.button("🚀 运行分析", use_container_width=True, disabled=not st.session_state.data_loaded):
            run_analysis(config)

        # Force re-analysis button (clears cache)
        if st.button("🔄 强制重新分析", use_container_width=True, disabled=not st.session_state.data_loaded):
            st.cache_data.clear()  # Clear all cached data
            run_analysis(config)

        # Clear results button
        if st.button("🗑️清除结果", use_container_width=True):
            st.session_state.analysis_results = {}
            st.session_state.data_loaded = False
            st.cache_data.clear()
            st.rerun()
    
    with col1:
        # Create tabs for different views
        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 数据概览", 
            "📈 滚动分析", 
            "🛡️ 无损失分析", 
            "🎯 收敛性分析"
        ])
        
        with tab1:
            display_data_overview()
        
        with tab2:
            display_rolling_analysis()
        
        with tab3:
            display_no_loss_analysis()
        
        with tab4:
            display_convergence_analysis()
            # 术语表下载区
            with st.expander("📚 术语表 / Glossary", expanded=False):
                try:
                    from glossary import render_glossary_md, to_csv
                    md = render_glossary_md()
                    st.markdown(md)
                    # 下载按钮（CSV / Markdown / PDF）
                    import io
                    st.download_button(
                        label="下载术语表 CSV",
                        data=to_csv(),
                        file_name="glossary.csv",
                        mime="text/csv"
                    )
                    st.download_button(
                        label="下载术语表 Markdown",
                        data=md,
                        file_name="glossary.md",
                        mime="text/markdown"
                    )
                    # PDF 导出（基础文本）
                    try:
                        from pdf_utils import render_plain_text_to_pdf
                        plain = md.replace('#','').replace('*','').replace('`','')
                        pdf_data = render_plain_text_to_pdf(
                            plain,
                            title="S&P 500 Analysis - Glossary",
                            footer="Generated by S&P 500 Analysis UI",
                            color_hex="#0B3B5A",
                        )
                        st.download_button(
                            label="下载术语表 PDF",
                            data=pdf_data,
                            file_name="glossary.pdf",
                            mime="application/pdf"
                        )
                    except Exception as e:
                        st.caption(f"术语表PDF导出不可用: {e}")
                except Exception as e:
                    st.caption(f"无法加载术语表: {e}")

    # Footer
    st.markdown(
        "<hr style='margin:2rem 0; opacity:0.2' />"
        f"<div style='text-align:center; color:#6B7280; font-size:12px;'>"
        f"{FOOTER_TEXT}"
        "</div>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
