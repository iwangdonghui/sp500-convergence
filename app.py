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
    show_info_message, create_metric_cards, generate_summary_report,
    create_professional_report_section
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

            # Compute risk metrics analysis
            risk_metrics_results = processor.compute_risk_metrics_analysis(
                config['start_years'],
                config['windows'],
                data_hash
            )

            # Store results in session state
            st.session_state.analysis_results = {
                'rolling': rolling_results,
                'no_loss': no_loss_results,
                'convergence': convergence_results,
                'risk_metrics': risk_metrics_results,
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


def display_risk_metrics_analysis():
    """Display risk metrics analysis tab."""
    if not st.session_state.analysis_results or 'risk_metrics' not in st.session_state.analysis_results:
        show_info_message("请先运行分析以查看风险指标结果", "info")
        return

    risk_results = st.session_state.analysis_results['risk_metrics']
    config = st.session_state.analysis_results['config']

    st.subheader("⚠️ 风险指标分析结果")

    # Display overall risk metrics for each start year
    st.subheader("📊 整体风险指标")

    # Create metric cards for overall statistics
    overall_metrics = {}
    for start_year, year_data in risk_results.items():
        if 'overall' in year_data and year_data['overall']:
            metrics = year_data['overall']
            overall_metrics[f"{start_year}年起"] = {
                'CAGR': f"{metrics.get('cagr', 0):.2%}",
                '夏普比率': f"{metrics.get('sharpe_ratio', 0):.2f}",
                '最大回撤': f"{metrics.get('max_drawdown', 0):.2%}",
                '波动率': f"{metrics.get('volatility', 0):.2%}"
            }

    if overall_metrics:
        # Display metrics in columns
        cols = st.columns(len(overall_metrics))
        for i, (period, metrics) in enumerate(overall_metrics.items()):
            with cols[i]:
                st.markdown(f"**{period}**")
                for metric, value in metrics.items():
                    st.metric(metric, value)

    # Display detailed risk metrics table
    st.subheader("📋 详细风险指标")

    # Prepare data for detailed table
    detailed_data = []
    for start_year, year_data in risk_results.items():
        if 'overall' in year_data and year_data['overall']:
            metrics = year_data['overall']
            detailed_data.append({
                '起始年份': start_year,
                '期间': f"{metrics.get('start_year', '')}-{metrics.get('end_year', '')}",
                'CAGR': f"{metrics.get('cagr', 0):.2%}",
                '夏普比率': f"{metrics.get('sharpe_ratio', 0):.3f}",
                '索提诺比率': f"{metrics.get('sortino_ratio', 0):.3f}",
                'Calmar比率': f"{metrics.get('calmar_ratio', 0):.3f}",
                '波动率': f"{metrics.get('volatility', 0):.2%}",
                '最大回撤': f"{metrics.get('max_drawdown', 0):.2%}",
                'VaR(95%)': f"{metrics.get('var_95', 0):.2%}",
                'CVaR(95%)': f"{metrics.get('cvar_95', 0):.2%}"
            })

    if detailed_data:
        df = pd.DataFrame(detailed_data)
        st.dataframe(df, use_container_width=True, height=300)


def display_multi_asset_analysis():
    """Display multi-asset analysis tab."""
    st.subheader("🌐 多资产类别比较分析")

    if not st.session_state.data_loaded:
        show_info_message("请先加载S&P 500数据作为基准", "info")
        return

    # Asset selection section
    st.subheader("📋 资产选择")

    # Get available assets
    processor = st.session_state.data_processor
    available_assets = processor.get_available_assets()

    # Create asset selection interface
    selected_assets = []

    # Always include S&P 500 as benchmark
    selected_assets.append('SPY')
    st.info("📌 S&P 500 (SPY) 已自动选择作为基准")

    # Asset class selection
    for asset_class, assets in available_assets.items():
        if asset_class == 'equity' and any(asset['symbol'] == 'SPY' for asset in assets):
            # Skip SPY in equity section since it's already selected
            other_equity_assets = [asset for asset in assets if asset['symbol'] != 'SPY']
            if other_equity_assets:
                st.markdown(f"**{asset_class.upper()} 股票指数**")
                for asset in other_equity_assets:
                    if st.checkbox(f"{asset['name']} ({asset['symbol']})",
                                 help=f"{asset['description']} | 起始年份: {asset['inception_year']}",
                                 key=f"asset_{asset['symbol']}"):
                        selected_assets.append(asset['symbol'])
        else:
            st.markdown(f"**{asset_class.upper()}**")
            for asset in assets:
                if st.checkbox(f"{asset['name']} ({asset['symbol']})",
                             help=f"{asset['description']} | 起始年份: {asset['inception_year']}",
                             key=f"asset_{asset['symbol']}"):
                    selected_assets.append(asset['symbol'])

    if len(selected_assets) < 2:
        st.warning("请至少选择一个额外资产进行比较分析")
        return

    # Analysis period selection
    st.subheader("📅 分析期间")
    col1, col2 = st.columns(2)

    with col1:
        start_year = st.selectbox("起始年份",
                                options=[1990, 2000, 2010, 2015, 2020],
                                index=0,
                                key="multi_asset_start_year")

    with col2:
        end_year = st.selectbox("结束年份",
                              options=[2020, 2021, 2022, 2023],
                              index=3,
                              key="multi_asset_end_year")

    # Run analysis button
    if st.button("🚀 运行多资产分析", use_container_width=True):
        try:
            # Set selected assets
            processor.set_selected_assets(selected_assets)

            # Run analysis
            with st.spinner("正在进行多资产分析..."):
                multi_asset_results = processor.compute_multi_asset_analysis(start_year, end_year)

            # Store results
            st.session_state.multi_asset_results = multi_asset_results
            st.session_state.multi_asset_config = {
                'selected_assets': selected_assets,
                'start_year': start_year,
                'end_year': end_year
            }

            st.success("✅ 多资产分析完成！")

        except Exception as e:
            st.error(f"多资产分析失败: {str(e)}")
            return

    # Display results if available
    if hasattr(st.session_state, 'multi_asset_results') and st.session_state.multi_asset_results:
        display_multi_asset_results()


def display_multi_asset_results():
    """Display multi-asset analysis results."""
    results = st.session_state.multi_asset_results
    config = st.session_state.multi_asset_config

    st.markdown("---")
    st.subheader("📊 分析结果")

    # Individual asset performance
    st.subheader("🎯 个别资产表现")

    # Create performance comparison table
    performance_data = []
    for symbol, asset_data in results['individual_assets'].items():
        asset_info = asset_data['asset_info']
        metrics = asset_data['risk_metrics']

        performance_data.append({
            '资产': f"{asset_info['name']} ({symbol})",
            '资产类别': asset_info['asset_class'],
            'CAGR': f"{metrics.get('cagr', 0):.2%}",
            '夏普比率': f"{metrics.get('sharpe_ratio', 0):.3f}",
            '最大回撤': f"{metrics.get('max_drawdown', 0):.2%}",
            '波动率': f"{metrics.get('volatility', 0):.2%}"
        })

    if performance_data:
        df = pd.DataFrame(performance_data)
        st.dataframe(df, use_container_width=True, height=300)

    # Correlation analysis
    if 'correlation_matrix' in results:
        st.subheader("🔗 相关性分析")

        correlation_matrix = results['correlation_matrix']

        # Create correlation heatmap
        import plotly.graph_objects as go

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
            title="资产相关性矩阵",
            xaxis_title="资产",
            yaxis_title="资产",
            height=500,
            margin=dict(l=80, r=80, t=80, b=80)
        )

        st.plotly_chart(fig, use_container_width=True)

        # Correlation insights
        st.markdown("**相关性洞察：**")

        # Find highest and lowest correlations
        corr_values = []
        for i in range(len(correlation_matrix.columns)):
            for j in range(i+1, len(correlation_matrix.columns)):
                asset1 = correlation_matrix.columns[i]
                asset2 = correlation_matrix.columns[j]
                corr = correlation_matrix.iloc[i, j]
                corr_values.append((asset1, asset2, corr))

        # Sort by correlation
        corr_values.sort(key=lambda x: abs(x[2]), reverse=True)

        if corr_values:
            highest_corr = corr_values[0]
            lowest_corr = min(corr_values, key=lambda x: x[2])

            st.write(f"• 最高相关性: {highest_corr[0]} 与 {highest_corr[1]} ({highest_corr[2]:.3f})")
            st.write(f"• 最低相关性: {lowest_corr[0]} 与 {lowest_corr[1]} ({lowest_corr[2]:.3f})")

    # Asset class summary
    if 'asset_class_summary' in results:
        st.subheader("📈 资产类别汇总")

        asset_class_data = []
        for asset_class, class_data in results['asset_class_summary'].items():
            avg_metrics = class_data['average_metrics']
            asset_class_data.append({
                '资产类别': asset_class.upper(),
                '资产数量': class_data['count'],
                '平均CAGR': f"{avg_metrics.get('cagr', 0):.2%}",
                '平均夏普比率': f"{avg_metrics.get('sharpe_ratio', 0):.3f}",
                '平均最大回撤': f"{avg_metrics.get('max_drawdown', 0):.2%}",
                '平均波动率': f"{avg_metrics.get('volatility', 0):.2%}"
            })

        if asset_class_data:
            df = pd.DataFrame(asset_class_data)
            st.dataframe(df, use_container_width=True)

    # Efficient frontier
    if 'efficient_frontier' in results:
        st.subheader("📊 有效前沿")

        frontier_data = results['efficient_frontier']

        # Create efficient frontier chart
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

        # Find and highlight optimal portfolio (highest Sharpe ratio)
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
            title="有效前沿分析",
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

        st.plotly_chart(fig, use_container_width=True)

        # Show optimal portfolio weights
        optimal_weights = frontier_data['weights'][max_sharpe_idx]
        st.markdown("**最优投资组合权重：**")

        weights_data = []
        for i, symbol in enumerate(config['selected_assets']):
            asset_name = results['individual_assets'][symbol]['asset_info']['name']
            weight = optimal_weights[i]
            weights_data.append({
                '资产': f"{asset_name} ({symbol})",
                '权重': f"{weight:.1%}"
            })

        weights_df = pd.DataFrame(weights_data)
        st.dataframe(weights_df, use_container_width=True, hide_index=True)


def main():
    """Main application function."""
    try:
        # Initialize session state
        initialize_session_state()

        # Apply custom CSS
        apply_custom_css()

        # Create header
        create_header()
    except Exception as e:
        st.error(f"应用初始化失败: {e}")
        st.error(f"错误详情: {traceback.format_exc()}")
        return

    # 环境自检（默认隐藏；当 SHOW_ENV_CHECK=true 时显示；没有 secrets.toml 时忽略）
    show_env_check = False
    try:
        # 安全地检查 secrets 配置，避免 StreamlitSecretNotFoundError
        import streamlit.runtime.secrets as secrets_module
        if hasattr(secrets_module, '_secrets') and secrets_module._secrets is not None:
            show_env_check = bool(st.secrets.get("SHOW_ENV_CHECK", False))
    except (ImportError, AttributeError, Exception):
        # 在没有 secrets 文件或其他错误时，默认不显示环境检查
        show_env_check = False

    if show_env_check:
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
        tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
            "📊 数据概览",
            "📈 滚动分析",
            "🛡️ 无损失分析",
            "🎯 收敛性分析",
            "⚠️ 风险指标",
            "🌐 多资产分析",
            "🏛️ GIPS合规性"
        ])
        
        with tab1:
            display_data_overview()
        
        with tab2:
            display_rolling_analysis()
        
        with tab3:
            display_no_loss_analysis()
        
        with tab4:
            display_convergence_analysis()

        with tab5:
            display_risk_metrics_analysis()

            # Professional report generation section
            if st.session_state.data_loaded and st.session_state.analysis_results:
                st.markdown("---")
                create_professional_report_section(st.session_state.data_processor)

        with tab6:
            display_multi_asset_analysis()

        with tab7:
            display_gips_compliance_analysis()

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


def display_gips_compliance_analysis():
    """Display GIPS compliance analysis interface."""
    st.header("🏛️ GIPS合规性分析")
    st.markdown("""
    **全球投资表现标准 (GIPS) 合规性分析**

    GIPS标准确保投资表现结果的公平表述和完整披露，为潜在客户和顾问提供标准化的表现衡量方法。
    """)

    # Initialize session state if needed
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False
    if 'data_processor' not in st.session_state:
        st.session_state.data_processor = DataProcessor()

    if not st.session_state.data_loaded:
        st.warning("⚠️ 请先在数据概览标签页中加载S&P 500数据")
        return

    # Configuration section
    st.subheader("📋 分析配置")

    col1, col2 = st.columns(2)

    with col1:
        firm_name = st.text_input(
            "投资公司名称",
            value="Sample Investment Firm",
            help="输入进行GIPS合规性分析的投资公司名称",
            key="gips_firm_name"
        )

        composite_name = st.text_input(
            "投资组合名称",
            value="S&P 500 Tracking Composite",
            help="输入投资组合或策略的名称",
            key="gips_composite_name"
        )

    with col2:
        benchmark_options = {
            "SPY": "SPDR S&P 500 ETF",
            "QQQ": "Invesco QQQ Trust",
            "IWM": "iShares Russell 2000 ETF"
        }

        benchmark_symbol = st.selectbox(
            "基准指数",
            options=list(benchmark_options.keys()),
            format_func=lambda x: f"{x} - {benchmark_options[x]}",
            help="选择用于比较的基准指数",
            key="gips_benchmark_symbol"
        )

        # Analysis period
        if st.session_state.data_processor and st.session_state.data_processor.data is not None:
            available_years = sorted(st.session_state.data_processor.data['year'].unique())
        else:
            available_years = list(range(2000, 2025))

        start_year = st.selectbox(
            "分析起始年份",
            options=available_years,
            index=0,
            help="选择GIPS分析的起始年份",
            key="gips_start_year"
        )

        end_year_options = [y for y in available_years if y >= start_year]
        end_year = st.selectbox(
            "分析结束年份",
            options=end_year_options,
            index=len(end_year_options) - 1 if end_year_options else 0,
            help="选择GIPS分析的结束年份",
            key="gips_end_year"
        )

    # Run analysis button
    if st.button("🚀 运行GIPS合规性分析", type="primary", key="gips_run_analysis"):
        try:
            with st.spinner("正在进行GIPS合规性分析..."):
                # Run GIPS compliance analysis
                gips_results = st.session_state.data_processor.compute_gips_compliance_analysis(
                    start_year=start_year,
                    end_year=end_year,
                    benchmark_symbol=benchmark_symbol,
                    firm_name=firm_name,
                    composite_name=composite_name
                )

                # Store results in session state
                st.session_state.gips_results = gips_results

                st.success("✅ GIPS合规性分析完成！")

        except Exception as e:
            st.error(f"❌ GIPS分析失败: {str(e)}")
            st.error("请检查数据完整性和参数设置")
            return

    # Display results if available
    if hasattr(st.session_state, 'gips_results') and st.session_state.gips_results:
        display_gips_results(st.session_state.gips_results)


def display_gips_results(results: Dict):
    """Display GIPS compliance analysis results."""
    st.subheader("📊 GIPS合规性分析结果")

    # Main performance metrics with improved styling
    gips_calc = results['gips_calculation']

    # Create a container with custom styling
    st.markdown('<div class="gips-result-container">', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            f"""
            <div style="text-align: center; padding: 1rem;">
                <div class="gips-metric-title">时间加权收益率</div>
                <div class="gips-metric-value">{gips_calc['time_weighted_return']:.2%}</div>
                <div style="font-size: 0.75rem; color: #64748b; margin-top: 0.25rem;">GIPS标准要求的核心指标</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        if gips_calc['money_weighted_return'] is not None:
            st.markdown(
                f"""
                <div style="text-align: center; padding: 1rem;">
                    <div class="gips-metric-title">资金加权收益率</div>
                    <div class="gips-metric-value">{gips_calc['money_weighted_return']:.2%}</div>
                    <div style="font-size: 0.75rem; color: #64748b; margin-top: 0.25rem;">内部收益率(IRR)</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"""
                <div style="text-align: center; padding: 1rem;">
                    <div class="gips-metric-title">资金加权收益率</div>
                    <div class="gips-metric-value" style="color: #94a3b8;">N/A</div>
                    <div style="font-size: 0.75rem; color: #64748b; margin-top: 0.25rem;">计算失败或不适用</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    with col3:
        compliance_level = gips_calc['compliance_level']
        compliance_config = {
            'full_compliance': {'icon': '✅', 'text': 'Full Compliance', 'class': 'compliance-full'},
            'partial_compliance': {'icon': '⚠️', 'text': 'Partial Compliance', 'class': 'compliance-partial'},
            'non_compliant': {'icon': '❌', 'text': 'Non Compliance', 'class': 'compliance-none'}
        }

        config = compliance_config.get(compliance_level, {'icon': '❓', 'text': 'Unknown', 'class': 'compliance-none'})

        st.markdown(
            f"""
            <div style="text-align: center; padding: 1rem;">
                <div class="gips-metric-title">合规性等级</div>
                <div class="gips-compliance-status {config['class']}" style="margin: 0.5rem 0;">
                    {config['icon']} {config['text']}
                </div>
                <div style="font-size: 0.75rem; color: #64748b;">GIPS合规性评估</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col4:
        period_summary = results['period_summary']
        st.markdown(
            f"""
            <div style="text-align: center; padding: 1rem;">
                <div class="gips-metric-title">分析期间</div>
                <div class="gips-metric-value" style="font-size: 1.25rem; line-height: 1.3;">{period_summary['start_date']} 至 {period_summary['end_date']}</div>
                <div style="font-size: 0.75rem; color: #64748b; margin-top: 0.25rem;">GIPS分析时间范围</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown('</div>', unsafe_allow_html=True)

    # Compliance report
    st.subheader("📋 合规性报告")

    compliance_report = results['compliance_report']

    # Create two columns for the report
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**基本信息**")
        st.write(f"**公司名称:** {compliance_report['firm_name']}")
        st.write(f"**投资组合:** {compliance_report['composite_name']}")
        st.write(f"**基准指数:** {compliance_report.get('benchmark_name', 'N/A')}")
        st.write(f"**计算方法:** {compliance_report['calculation_method']}")

        if 'benchmark_return' in compliance_report:
            st.write(f"**基准收益率:** {compliance_report['benchmark_return']}")
            st.write(f"**超额收益:** {compliance_report['excess_return']}")

    with col2:
        st.markdown("**投资组合统计**")
        st.write(f"**投资组合数量:** {compliance_report['number_of_portfolios']}")
        st.write(f"**总资产:** {compliance_report['total_assets']}")
        st.write(f"**时间加权收益率:** {compliance_report['time_weighted_return']}")

        if 'money_weighted_return' in compliance_report:
            st.write(f"**资金加权收益率:** {compliance_report['money_weighted_return']}")

    # Validation notes
    if gips_calc['validation_notes']:
        st.markdown("**⚠️ 验证说明**")
        for note in gips_calc['validation_notes']:
            st.warning(note)

    # Performance attribution analysis
    st.subheader("📈 表现归因分析")

    attribution = results['attribution_analysis']

    if 'risk_adjusted_metrics' in attribution:
        risk_metrics = attribution['risk_adjusted_metrics']

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**风险调整指标**")

            metrics_data = {
                "指标": ["Alpha", "Beta", "夏普比率", "信息比率", "跟踪误差", "超额收益"],
                "投资组合": [
                    f"{risk_metrics['alpha']:.4f}",
                    f"{risk_metrics['beta']:.3f}",
                    f"{risk_metrics['portfolio_sharpe']:.3f}",
                    f"{risk_metrics['information_ratio']:.3f}",
                    f"{risk_metrics['tracking_error']:.4f}",
                    f"{risk_metrics['excess_return']:.4f}"
                ],
                "基准": [
                    "0.0000",
                    "1.000",
                    f"{risk_metrics['benchmark_sharpe']:.3f}",
                    "0.000",
                    "0.0000",
                    "0.0000"
                ]
            }

            st.dataframe(pd.DataFrame(metrics_data), use_container_width=True)

        with col2:
            if 'sector_attribution' in attribution:
                st.markdown("**行业归因分析**")

                sector_attr = attribution['sector_attribution']

                attribution_data = {
                    "归因组件": ["配置效应", "选择效应", "交互效应", "总归因"],
                    "贡献 (%)": [
                        f"{sector_attr['allocation_effect']:.2%}",
                        f"{sector_attr['selection_effect']:.2%}",
                        f"{sector_attr['interaction_effect']:.2%}",
                        f"{sector_attr['total_attribution']:.2%}"
                    ]
                }

                st.dataframe(pd.DataFrame(attribution_data), use_container_width=True)

    # Benchmark validation
    st.subheader("🎯 基准验证")

    benchmark_validation = results['benchmark_validation']

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**基准适当性评估**")

        if benchmark_validation['is_appropriate']:
            st.success("✅ 基准选择适当")
        else:
            st.error("❌ 基准选择可能不适当")

        if benchmark_validation['validation_notes']:
            st.markdown("**验证说明:**")
            for note in benchmark_validation['validation_notes']:
                st.write(f"• {note}")

    with col2:
        st.markdown("**特征比较**")

        portfolio_chars = benchmark_validation['portfolio_characteristics']
        benchmark_chars = benchmark_validation['benchmark_characteristics']

        comparison_data = {
            "特征": ["资产类别", "地理区域", "投资风格", "市值重点"],
            "投资组合": [
                portfolio_chars.get('asset_class', 'N/A'),
                portfolio_chars.get('geography', 'N/A'),
                portfolio_chars.get('investment_style', 'N/A'),
                portfolio_chars.get('market_cap_focus', 'N/A')
            ],
            "基准": [
                benchmark_chars.get('asset_class', 'N/A'),
                benchmark_chars.get('geography', 'N/A'),
                benchmark_chars.get('investment_style', 'N/A'),
                benchmark_chars.get('market_cap_focus', 'N/A')
            ]
        }

        st.dataframe(pd.DataFrame(comparison_data), use_container_width=True)

    # GIPS compliance statement
    st.subheader("📜 GIPS合规性声明")

    compliance_statement = compliance_report.get('compliance_statement', '')

    if 'claims compliance' in compliance_statement:
        st.success(compliance_statement)
    else:
        st.warning(compliance_statement)

    # Download report option
    st.subheader("📥 报告下载")

    if st.button("📄 生成详细报告"):
        # Generate comprehensive report
        report_content = generate_gips_report_content(results)

        st.download_button(
            label="下载GIPS合规性报告",
            data=report_content,
            file_name=f"GIPS_Compliance_Report_{compliance_report['composite_name'].replace(' ', '_')}.txt",
            mime="text/plain"
        )


def generate_gips_report_content(results: Dict) -> str:
    """Generate comprehensive GIPS compliance report content."""
    gips_calc = results['gips_calculation']
    compliance_report = results['compliance_report']
    attribution = results['attribution_analysis']
    benchmark_validation = results['benchmark_validation']

    report_lines = [
        "=" * 80,
        "GIPS合规性分析报告",
        "Global Investment Performance Standards Compliance Report",
        "=" * 80,
        "",
        f"报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "基本信息",
        "-" * 40,
        f"投资公司: {compliance_report['firm_name']}",
        f"投资组合: {compliance_report['composite_name']}",
        f"分析期间: {compliance_report['period_start']} 至 {compliance_report['period_end']}",
        f"基准指数: {compliance_report.get('benchmark_name', 'N/A')}",
        "",
        "表现指标",
        "-" * 40,
        f"时间加权收益率: {compliance_report['time_weighted_return']}",
        f"基准收益率: {compliance_report.get('benchmark_return', 'N/A')}",
        f"超额收益: {compliance_report.get('excess_return', 'N/A')}",
        f"计算方法: {compliance_report['calculation_method']}",
        "",
        "合规性评估",
        "-" * 40,
        f"合规性等级: {gips_calc['compliance_level']}",
        ""
    ]

    if gips_calc['validation_notes']:
        report_lines.extend([
            "验证说明:",
            *[f"• {note}" for note in gips_calc['validation_notes']],
            ""
        ])

    # Add attribution analysis
    if 'risk_adjusted_metrics' in attribution:
        risk_metrics = attribution['risk_adjusted_metrics']
        report_lines.extend([
            "风险调整指标",
            "-" * 40,
            f"Alpha: {risk_metrics['alpha']:.4f}",
            f"Beta: {risk_metrics['beta']:.3f}",
            f"夏普比率: {risk_metrics['portfolio_sharpe']:.3f}",
            f"信息比率: {risk_metrics['information_ratio']:.3f}",
            f"跟踪误差: {risk_metrics['tracking_error']:.4f}",
            ""
        ])

    # Add compliance statement
    report_lines.extend([
        "GIPS合规性声明",
        "-" * 40,
        compliance_report.get('compliance_statement', ''),
        "",
        "=" * 80,
        "报告结束"
    ])

    return "\n".join(report_lines)


if __name__ == "__main__":
    main()
