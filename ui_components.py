"""
UI components and visualization functions for the S&P 500 Analysis Tool
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, List, Any
from config import COLORS, CHART_CONFIG, TABLE_CONFIG, CUSTOM_CSS


def apply_custom_css():
    """Apply custom CSS styling."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def create_header():
    """Create the main header section."""
    st.markdown("""
    <div class="main-header">
        <h1>📈 S&P 500 滚动收益率与收敛性分析工具</h1>
        <p>专业的长期投资收益率分析平台</p>
    </div>
    """, unsafe_allow_html=True)


def create_sidebar_config():
    """Create the sidebar configuration panel."""
    st.sidebar.header("🔧 分析配置")

    # Glossary quick access
    with st.sidebar.expander("📚 术语表 / Glossary", expanded=False):
        try:
            from glossary import TERMS
            q = st.text_input("搜索 / Search", key="glossary_search")
            for zh, en, desc in TERMS:
                if q and (q.lower() not in zh.lower() and q.lower() not in en.lower() and q.lower() not in desc.lower()):
                    continue
                st.markdown(f"**{zh} / {en}**\n\n{desc}")
        except Exception:
            st.caption("术语表未加载")
    
    # Data source selection
    st.sidebar.subheader("📊 数据来源")
    data_source = st.sidebar.radio(
        "选择数据来源",
        ["从SlickCharts下载", "上传CSV文件"],
        help="选择数据来源：自动下载最新数据或使用本地文件"
    )
    
    uploaded_file = None
    if data_source == "上传CSV文件":
        uploaded_file = st.sidebar.file_uploader(
            "上传CSV文件",
            type=['csv'],
            help="上传包含年份和收益率数据的CSV文件"
        )
    
    # Analysis parameters
    st.sidebar.subheader("⚙️ 分析参数")
    
    # Start years
    start_years_options = [1926, 1957, 1972, 1985, 1990, 2000]
    start_years = st.sidebar.multiselect(
        "基准起始年份",
        start_years_options,
        default=[1926, 1957, 1972, 1985],
        help="选择分析的基准起始年份"
    )
    
    # Time windows
    window_options = [5, 10, 15, 20, 25, 30]
    windows = st.sidebar.multiselect(
        "时间窗口（年）",
        window_options,
        default=[5, 10, 15, 20, 30],
        help="选择要分析的时间窗口长度"
    )
    
    # Thresholds
    st.sidebar.subheader("📏 收敛性阈值")
    threshold_method = st.sidebar.radio(
        "阈值设置方式",
        ["预设阈值", "自定义范围"]
    )
    
    if threshold_method == "预设阈值":
        threshold_options = [0.0025, 0.005, 0.0075, 0.01, 0.015, 0.02]
        thresholds = st.sidebar.multiselect(
            "选择阈值",
            threshold_options,
            default=[0.0025, 0.005, 0.0075, 0.01],
            format_func=lambda x: f"{x:.1%}"
        )
    else:
        col1, col2 = st.sidebar.columns(2)
        with col1:
            thr_min = st.number_input("最小阈值", value=0.0025, format="%.4f")
        with col2:
            thr_max = st.number_input("最大阈值", value=0.01, format="%.4f")
        
        thr_steps = st.sidebar.slider("阈值数量", min_value=5, max_value=20, value=10)
        thresholds = np.linspace(thr_min, thr_max, thr_steps).tolist()
    
    return {
        'data_source': data_source,
        'uploaded_file': uploaded_file,
        'start_years': start_years,
        'windows': windows,
        'thresholds': thresholds
    }


def display_data_summary(summary: Dict[str, Any]):
    """Display data summary statistics."""
    if not summary:
        return
    
    st.subheader("📊 数据概览")
    
    # Create metrics columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "数据年份范围",
            f"{summary['start_year']}-{summary['end_year']}",
            f"共{summary['total_years']}年"
        )
    
    with col2:
        st.metric(
            "平均年收益率",
            f"{summary['mean_return']:.2%}",
            f"标准差: {summary['std_return']:.2%}"
        )
    
    with col3:
        st.metric(
            "最佳年份收益",
            f"{summary['max_return']:.2%}",
            f"正收益年份: {summary['positive_years']}"
        )
    
    with col4:
        st.metric(
            "最差年份收益",
            f"{summary['min_return']:.2%}",
            f"负收益年份: {summary['negative_years']}"
        )


def create_returns_timeline_chart(data: pd.DataFrame):
    """Create a timeline chart of annual returns."""
    fig = go.Figure()
    
    # Create color array based on positive/negative returns
    colors = [COLORS['success'] if ret > 0 else COLORS['danger'] for ret in data['return']]
    
    fig.add_trace(go.Bar(
        x=data['year'],
        y=data['return'],
        marker_color=colors,
        name='年收益率',
        hovertemplate='<b>%{x}</b><br>收益率: %{y:.2%}<extra></extra>'
    ))
    
    fig.update_layout(
        title="S&P 500 历年收益率",
        xaxis_title="年份",
        yaxis_title="收益率",
        yaxis_tickformat='.1%',
        height=CHART_CONFIG['height'],
        template=CHART_CONFIG['template'],
        font=dict(family=CHART_CONFIG['font_family'], size=CHART_CONFIG['font_size']),
        paper_bgcolor=CHART_CONFIG.get('paper_bgcolor','white'),
        plot_bgcolor=CHART_CONFIG.get('plot_bgcolor','white'),
    )

    # Add zero line and grid color
    fig.add_hline(y=0, line_dash="dash", line_color=CHART_CONFIG.get('zerolinecolor', 'gray'), opacity=0.5)
    fig.update_xaxes(gridcolor=CHART_CONFIG.get('gridcolor', '#E5E7EB'))
    fig.update_yaxes(gridcolor=CHART_CONFIG.get('gridcolor', '#E5E7EB'))

    return fig


def create_rolling_cagr_chart(rolling_results: Dict[str, Any], start_year: int):
    """Create rolling CAGR chart for a specific start year."""
    if start_year not in rolling_results:
        return None
    
    year_data = rolling_results[start_year]
    fig = go.Figure()

    # 使用统一色板
    colorway = CHART_CONFIG.get('colorway', [])

    for i, window in enumerate(sorted(year_data.keys())):
        if year_data[window] is not None:
            data = year_data[window]
            color = colorway[i % len(colorway)] if colorway else COLORS['primary']

            fig.add_trace(go.Scatter(
                x=data['end_years'],
                y=data['cagrs'],
                mode='lines+markers',
                name=f'{window}年窗口',
                line=dict(color=color, width=2),
                marker=dict(size=6),
                hovertemplate=f'<b>{window}年窗口</b><br>结束年份: %{{x}}<br>CAGR: %{{y:.2%}}<extra></extra>'
            ))
    
    fig.update_layout(
        title=f"滚动CAGR分析 (起始年份: {start_year})",
        xaxis_title="结束年份",
        yaxis_title="复合年增长率 (CAGR)",
        yaxis_tickformat='.1%',
        height=CHART_CONFIG['height'],
        template=CHART_CONFIG['template'],
        font=dict(family=CHART_CONFIG['font_family'], size=CHART_CONFIG['font_size']),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        paper_bgcolor=CHART_CONFIG.get('paper_bgcolor','white'),
        plot_bgcolor=CHART_CONFIG.get('plot_bgcolor','white'),
        colorway=CHART_CONFIG.get('colorway')
    )

    # Add zero line and grid
    fig.add_hline(y=0, line_dash="dash", line_color=CHART_CONFIG.get('zerolinecolor','gray'), opacity=0.5)
    fig.update_xaxes(gridcolor=CHART_CONFIG.get('gridcolor', '#E5E7EB'))
    fig.update_yaxes(gridcolor=CHART_CONFIG.get('gridcolor', '#E5E7EB'))

    return fig


def create_window_comparison_chart(rolling_results: Dict[str, Any], start_years: List[int]):
    """Create a comparison chart of different window sizes across start years."""
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=[f"起始年份: {year}" for year in start_years[:4]],
        vertical_spacing=0.1,
        horizontal_spacing=0.1
    )

    # 使用统一色板
    colorway = CHART_CONFIG.get('colorway', [])

    for idx, start_year in enumerate(start_years[:4]):
        row = (idx // 2) + 1
        col = (idx % 2) + 1
        
        if start_year in rolling_results:
            year_data = rolling_results[start_year]
            
            for i, window in enumerate(sorted(year_data.keys())):
                if year_data[window] is not None:
                    data = year_data[window]
                    color = colorway[i % len(colorway)] if colorway else COLORS['primary']

                    fig.add_trace(
                        go.Box(
                            y=data['cagrs'],
                            name=f'{window}年',
                            marker_color=color,
                            showlegend=(idx == 0)  # Only show legend for first subplot
                        ),
                        row=row, col=col
                    )
    
    fig.update_layout(
        title="不同时间窗口的收益率分布比较",
        height=600,
        template=CHART_CONFIG['template'],
        font=dict(family=CHART_CONFIG['font_family'], size=CHART_CONFIG['font_size'])
    )
    
    # Update y-axes to show percentages
    for i in range(1, 5):
        fig.update_yaxes(tickformat='.1%', row=(i-1)//2+1, col=(i-1)%2+1)
    
    return fig


def create_convergence_heatmap(convergence_results: Dict[str, Any], start_years: List[int], thresholds: List[float]):
    """Create a heatmap showing convergence analysis results."""
    # Prepare data for heatmap
    heatmap_data = []

    for start_year in start_years:
        if start_year in convergence_results:
            row = []
            for threshold in thresholds:
                if threshold in convergence_results[start_year]:
                    min_years = convergence_results[start_year][threshold]['min_holding_years']
                    row.append(min_years if min_years != float('inf') else None)
                else:
                    row.append(None)
            heatmap_data.append(row)
        else:
            heatmap_data.append([None] * len(thresholds))

    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data,
        x=[f"{t:.1%}" for t in thresholds],
        y=[str(year) for year in start_years],
        colorscale=[[0, '#FDE68A'], [0.5, '#60A5FA'], [1, '#0B3B5A']],
        hoverongaps=False,
        hovertemplate='起始年份: %{y}<br>阈值: %{x}<br>最小持有期: %{z}年<extra></extra>'
    ))

    fig.update_layout(
        title="收敛性分析热力图 - 最小持有期（年）",
        xaxis_title="收敛阈值",
        yaxis_title="起始年份",
        height=CHART_CONFIG['height'],
        template=CHART_CONFIG['template'],
        font=dict(family=CHART_CONFIG['font_family'], size=CHART_CONFIG['font_size']),
        paper_bgcolor=CHART_CONFIG.get('paper_bgcolor','white'),
        plot_bgcolor=CHART_CONFIG.get('plot_bgcolor','white')
    )

    return fig


def create_no_loss_chart(no_loss_results: Dict[str, Any]):
    """Create a chart showing no-loss analysis results."""
    if not no_loss_results:
        return None

    start_years = list(no_loss_results.keys())
    min_holding_years = [no_loss_results[year]['min_holding_years'] for year in start_years]
    avg_cagrs = [no_loss_results[year]['average_cagr'] for year in start_years]

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=["最小无损失持有期", "平均CAGR"],
        specs=[[{"secondary_y": False}, {"secondary_y": False}]]
    )

    # Bar chart for minimum holding years
    fig.add_trace(
        go.Bar(
            x=[str(year) for year in start_years],
            y=min_holding_years,
            name="最小持有期",
            marker_color=COLORS['primary'],
            hovertemplate='起始年份: %{x}<br>最小持有期: %{y}年<extra></extra>'
        ),
        row=1, col=1
    )

    # Bar chart for average CAGR
    fig.add_trace(
        go.Bar(
            x=[str(year) for year in start_years],
            y=avg_cagrs,
            name="平均CAGR",
            marker_color=COLORS['secondary'],
            hovertemplate='起始年份: %{x}<br>平均CAGR: %{y:.2%}<extra></extra>'
        ),
        row=1, col=2
    )

    fig.update_layout(
        title="无损失持有期分析",
        height=CHART_CONFIG['height'],
        template=CHART_CONFIG['template'],
        font=dict(family=CHART_CONFIG['font_family'], size=CHART_CONFIG['font_size']),
        showlegend=False
    )

    # Update y-axes
    fig.update_yaxes(title_text="年数", row=1, col=1)
    fig.update_yaxes(title_text="CAGR", tickformat='.1%', row=1, col=2)

    return fig


def display_analysis_table(df: pd.DataFrame, title: str, format_columns: Dict[str, str] = None):
    """Display a formatted analysis table."""
    if df.empty:
        st.warning(f"没有可显示的{title}数据")
        return

    st.subheader(title)

    # Format specific columns if specified
    if format_columns:
        df_display = df.copy()
        for col, fmt in format_columns.items():
            if col in df_display.columns:
                if fmt == 'percentage':
                    df_display[col] = df_display[col].apply(lambda x: f"{x:.2%}" if pd.notna(x) else "")
                elif fmt == 'decimal':
                    df_display[col] = df_display[col].apply(lambda x: f"{x:.4f}" if pd.notna(x) else "")
    else:
        df_display = df

    st.dataframe(
        df_display,
        use_container_width=TABLE_CONFIG['use_container_width'],
        hide_index=TABLE_CONFIG['hide_index'],
        height=TABLE_CONFIG['height']
    )


def create_download_section(data_dict: Dict[str, Any], filename_prefix: str = "sp500_analysis", layout: str = "desktop"):
    """Create download buttons for analysis results.
    - 桌面端默认：数据导出在左侧垂直排列；AI 报告导出在右侧。
    - 若只存在一类导出项，则全部左侧展示。
    """
    st.subheader("📥 下载分析结果 / Download Results")

    has_rolling = 'rolling_cagr' in data_dict
    has_summary = 'summary' in data_dict
    has_convergence = 'convergence' in data_dict
    has_report = ('ai_report_md' in data_dict and data_dict['ai_report_md'])

    if not any([has_rolling, has_summary, has_convergence, has_report]):
        st.caption("暂无可下载内容 / Nothing to download")
        return

    left, right = st.columns([3, 2]) if layout == 'desktop' else st.columns(1)

    # 左侧：数据类导出按钮（竖排）
    with left:
        if has_rolling:
            csv_data = pd.DataFrame(data_dict['rolling_cagr']).to_csv(index=False)
            st.download_button("下载滚动CAGR数据", csv_data, file_name=f"{filename_prefix}_rolling_cagr.csv", mime="text/csv")
        if has_summary:
            csv_data = pd.DataFrame(data_dict['summary']).to_csv(index=False)
            st.download_button("下载统计摘要", csv_data, file_name=f"{filename_prefix}_summary.csv", mime="text/csv")
        if has_convergence:
            csv_data = pd.DataFrame(data_dict['convergence']).to_csv(index=False)
            st.download_button("下载收敛性分析", csv_data, file_name=f"{filename_prefix}_convergence.csv", mime="text/csv")

    # 右侧：AI 报告导出
    target = right if layout == 'desktop' else left
    with target:
        if has_report:
            md_text = data_dict['ai_report_md']
            st.download_button("导出AI报告为Markdown (.md)", md_text, file_name=f"{filename_prefix}_ai_report.md", mime="text/markdown")
            html_text = f"""<html><head><meta charset='utf-8'></head><body><pre style='white-space:pre-wrap;font-family:system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;'>{md_text}</pre></body></html>"""
            st.download_button("导出AI报告为HTML (.html)", html_text, file_name=f"{filename_prefix}_ai_report.html", mime="text/html")

            # PDF（有依赖才显示）
            try:
                from pdf_utils import render_plain_text_to_pdf  # type: ignore
                plain = md_text.replace('#','').replace('*','').replace('`','')
                pdf_data = render_plain_text_to_pdf(
                    plain,
                    title="S&P 500 Rolling Returns & Convergence - AI Summary",
                    footer="Generated by S&P 500 Analysis UI",
                    color_hex="#0B3B5A",
                )
                st.download_button("导出AI报告为PDF / Export AI Report (PDF)", pdf_data, file_name=f"{filename_prefix}_ai_report.pdf", mime="application/pdf")
            except Exception as e:
                st.caption("PDF导出不可用：未安装 reportlab 或被网络阻断。可先下载 HTML 并在浏览器中打印为 PDF。")


def show_info_message(message: str, message_type: str = "info"):
    """Display an info message with appropriate styling."""
    if message_type == "success":
        st.markdown(f'<div class="success-message">{message}</div>', unsafe_allow_html=True)
    elif message_type == "error":
        st.markdown(f'<div class="error-message">{message}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="info-box">{message}</div>', unsafe_allow_html=True)


def create_metric_cards(metrics: Dict[str, Any]):
    """Create metric cards for key statistics."""
    cols = st.columns(len(metrics))

    for i, (label, value) in enumerate(metrics.items()):
        with cols[i]:
            st.markdown(f"""
            <div class="metric-card">
                <h3>{label}</h3>
                <h2>{value}</h2>
            </div>
            """, unsafe_allow_html=True)


def generate_summary_report(rolling_results: Dict[str, Any], no_loss_results: Dict[str, Any], convergence_results: Dict[str, Any], config: Dict[str, Any], language: str = 'zh', depth: str = 'standard', include_recommendation: bool = True, target_threshold: float | None = None) -> str:
    """生成综合智能总结（滚动 + 无损失 + 收敛），支持 zh / en / bi。"""
    try:
        def L(zh: str, en: str) -> str:
            if language == 'en':
                return en
            if language == 'bi':
                return zh + "\n" + en
            return zh

        start_years = config.get('start_years', [])
        thresholds = config.get('thresholds', [])
        windows = config.get('windows', [])
        lines = []
        lines.append(L("### 综合智能总结（滚动 + 无损失 + 收敛）", "### Integrated Summary (Rolling + No-loss + Convergence)"))

        # 若未指定目标阈值，尝试使用阈值列表中位数
        if target_threshold is None and thresholds:
            import numpy as np
            target_threshold = float(np.median(thresholds))

        # 每个起始年份的要点
        for sy in start_years:
            section = []
            roll = rolling_results.get(sy, {}) if rolling_results else {}
            nl = no_loss_results.get(sy, {}) if no_loss_results else {}
            conv = convergence_results.get(sy, {}) if convergence_results else {}

            # 无损失
            min_no_loss = nl.get('min_holding_years')
            avg_cagr_overall = nl.get('average_cagr')

            # 滚动窗口稳定性与收益
            stable_window = None
            stable_std = None
            best_avg_window = None
            best_avg_val = None
            for w in sorted(roll.keys()):
                datum = roll[w]
                if not datum:
                    continue
                std = datum.get('std_cagr')
                avg = datum.get('avg_cagr')
                if isinstance(std, (int, float)):
                    if stable_std is None or std < stable_std:
                        stable_std = float(std)
                        stable_window = w
                if isinstance(avg, (int, float)):
                    if best_avg_val is None or avg > best_avg_val:
                        best_avg_val = float(avg)
                        best_avg_window = w

            # 参考窗口：优先20年
            ref_window = 20 if 20 in roll else (max(roll.keys()) if roll else None)
            ref_avg = roll.get(ref_window, {}).get('avg_cagr') if ref_window else None
            ref_stats = None
            if ref_window and roll.get(ref_window):
                import numpy as np
                cagrs = roll[ref_window]['cagrs']
                if cagrs:
                    p10 = float(np.percentile(cagrs, 10))
                    p50 = float(np.percentile(cagrs, 50))
                    p90 = float(np.percentile(cagrs, 90))
                    ref_stats = (p10, p50, p90, roll[ref_window].get('best_cagr'), roll[ref_window].get('worst_cagr'))

            # 收敛：目标阈值下的年限（fallback：该起始年份的阈值中位数）
            conv_years = None
            if target_threshold is not None and sy in convergence_results and target_threshold in convergence_results[sy]:
                conv_years = convergence_results[sy][target_threshold]['min_holding_years']
            else:
                vals = [conv[t]['min_holding_years'] for t in thresholds if t in conv]
                vals = [v for v in vals if isinstance(v, (int, float)) and v != float('inf')]
                if vals:
                    import numpy as np
                    conv_years = int(np.median(vals))

            # 建议最短持有期（取无损失期与收敛期的较大者）
            rec_years = None
            if isinstance(min_no_loss, (int, float)) and isinstance(conv_years, (int, float)):
                rec_years = int(max(min_no_loss, conv_years))
            elif isinstance(min_no_loss, (int, float)):
                rec_years = int(min_no_loss)
            elif isinstance(conv_years, (int, float)):
                rec_years = int(conv_years)

            section.append(L(f"- 起始年份 {sy}：", f"- Start year {sy}:"))
            if isinstance(min_no_loss, (int, float)):
                if isinstance(avg_cagr_overall, (int, float)):
                    section.append(L(
                        f"  - 无损失最短持有期 ≈ {min_no_loss} 年；对应期内平均CAGR ≈ {avg_cagr_overall:.2%}",
                        f"  - Min no-loss horizon ≈ {min_no_loss} yrs; average CAGR over windows ≈ {avg_cagr_overall:.2%}"
                    ))
                else:
                    section.append(L(
                        f"  - 无损失最短持有期 ≈ {min_no_loss} 年",
                        f"  - Min no-loss horizon ≈ {min_no_loss} yrs"
                    ))
            if isinstance(ref_avg, (int, float)) and ref_window:
                section.append(L(
                    f"  - 参考{ref_window}年期平均CAGR ≈ {ref_avg:.2%}",
                    f"  - Reference {ref_window}-year average CAGR ≈ {ref_avg:.2%}"
                ))
            if ref_stats is not None:
                p10, p50, p90, best_c, worst_c = ref_stats
                section.append(L(
                    f"  - {ref_window}年期分布：P10≈{p10:.2%} / P50≈{p50:.2%} / P90≈{p90:.2%}；最佳≈{best_c:.2%} / 最差≈{worst_c:.2%}",
                    f"  - {ref_window}-yr distribution: P10≈{p10:.2%} / P50≈{p50:.2%} / P90≈{p90:.2%}; Best≈{best_c:.2%} / Worst≈{worst_c:.2%}"
                ))
            if stable_window is not None and stable_std is not None:
                section.append(L(
                    f"  - 稳定性：波动最小窗口 ≈ {stable_window} 年（σ ≈ {stable_std:.2%}）",
                    f"  - Stability: lowest volatility window ≈ {stable_window} yrs (σ ≈ {stable_std:.2%})"
                ))
            if best_avg_window is not None and best_avg_val is not None:
                section.append(L(
                    f"  - 收益性：平均CAGR较优窗口 ≈ {best_avg_window} 年（≈ {best_avg_val:.2%}）",
                    f"  - Return: window with higher average CAGR ≈ {best_avg_window} yrs (≈ {best_avg_val:.2%})"
                ))
            if isinstance(conv_years, (int, float)) and target_threshold is not None:
                section.append(L(
                    f"  - 收敛性：在目标阈值 {target_threshold:.2%} 下约 {conv_years} 年达到稳定",
                    f"  - Convergence: reaches stability in ≈ {conv_years} yrs at target threshold {target_threshold:.2%}"
                ))
            if rec_years is not None:
                section.append(L(
                    f"  - 建议最短持有期（综合无损失与收敛）≈ {rec_years} 年",
                    f"  - Suggested minimum holding (max of no-loss and convergence) ≈ {rec_years} yrs"
                ))
            lines.extend(section)

        # 跨时期对比
        lines.append(L("\n#### 跨时期对比", "\n#### Cross-period comparison"))
        # 最短无损
        shortest = None
        for sy in start_years:
            nl = no_loss_results.get(sy, {}) if no_loss_results else {}
            if 'min_holding_years' in nl:
                val = nl['min_holding_years']
                if isinstance(val, (int, float)):
                    if shortest is None or val < shortest[1]:
                        shortest = (sy, val)
        if shortest:
            lines.append(L(
                f"- 最快达到‘不亏损’：{shortest[0]}（约 {shortest[1]} 年）",
                f"- Fastest to reach no-loss: {shortest[0]} (≈ {shortest[1]} yrs)"
            ))

        # 收敛速度（中位）
        stability = []
        for sy in start_years:
            conv = convergence_results.get(sy, {}) if convergence_results else {}
            vals = [conv[t]['min_holding_years'] for t in thresholds if t in conv]
            vals = [v for v in vals if isinstance(v, (int, float)) and v != float('inf')]
            if vals:
                import numpy as np
                stability.append((sy, float(np.median(vals))))
        if stability:
            stability.sort(key=lambda x: x[1])
            lines.append(L(
                f"- 收敛速度整体较快：{stability[0][0]}（各阈值中位最短持有期 ≈ {stability[0][1]} 年）",
                f"- Overall quicker convergence: {stability[0][0]} (median min holding across thresholds ≈ {stability[0][1]} yrs)"
            ))

        # 长期收益参考（以20年或最大窗口的平均CAGR排序）
        longrun = []
        for sy in start_years:
            roll = rolling_results.get(sy, {}) if rolling_results else {}
            ref_window = 20 if 20 in roll else (max(roll.keys()) if roll else None)
            if ref_window and roll.get(ref_window):
                longrun.append((sy, ref_window, float(roll[ref_window]['avg_cagr'])))
        if longrun:
            longrun.sort(key=lambda x: x[2], reverse=True)
            top = longrun[0]
            lines.append(L(
                f"- 长期平均收益（参考{top[1]}年）较优：{top[0]}（≈ {top[2]:.2%}）",
                f"- Higher long-run average (ref {top[1]} yrs): {top[0]} (≈ {top[2]:.2%})"
            ))

        if include_recommendation:
            lines.append(L("\n#### 观察与提示（非投资建议）", "\n#### Notes (not investment advice)"))
            tips = []
            if shortest:
                tips.append(L(
                    "- 若追求尽快降低回撤风险，可重点参考无损期更短的起始时期",
                    "- To reduce drawdown risk faster, consider start periods with shorter no-loss horizons"
                ))
            if stability:
                tips.append(L(
                    "- 若关注收益分布收敛稳定性，可优先参考收敛期更短的起始时期",
                    "- If prioritizing stability, prefer periods with shorter convergence horizons"
                ))
            if longrun:
                tips.append(L(
                    "- 若更重视长期复合收益，可参考长期平均CAGR更高的起始时期",
                    "- If prioritizing long-term compounding, consider periods with higher long-run average CAGR"
                ))
            if not tips:
                tips.append(L(
                    "- 建议结合多窗口（10/20/30年）与不同阈值共同评估长期稳定性",
                    "- Consider multiple windows (10/20/30 yrs) and thresholds to assess long-term stability"
                ))
            lines.extend(tips)

        return "\n".join(lines)
    except Exception as e:
        return L(f"生成报告时出现问题：{e}", f"Error generating report: {e}")

