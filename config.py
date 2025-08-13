"""
Configuration file for the S&P 500 Analysis UI
"""

# UI Configuration
APP_TITLE = "S&P 500 滚动收益率与收敛性分析工具"
APP_SUBTITLE = "专业的长期投资收益率分析平台"

# Default Analysis Parameters
DEFAULT_WINDOWS = [5, 10, 15, 20, 30]
DEFAULT_START_YEARS = [1926, 1957, 1972, 1985]
DEFAULT_THRESHOLDS = [0.0025, 0.005, 0.0075, 0.01]

# UI Layout Configuration
SIDEBAR_WIDTH = 350
MAIN_CONTENT_WIDTH = 800

# Color Scheme (Professional Finance Palette)
# 参考投研类平台常见配色：深海军蓝 + 青蓝 + 金色强调，配以标准盈亏色
COLORS = {
    'primary':   '#0B3B5A',  # 深海军蓝（品牌主色）
    'secondary': '#0E7490',  # 青蓝（辅助色）
    'accent':    '#F59E0B',  # 琥珀金（强调色）
    'success':   '#16A34A',  # 盈利绿
    'warning':   '#F59E0B',  # 风险橙
    'danger':    '#DC2626',  # 亏损红
    'light':     '#F5F7FA',  # 背景浅灰
    'dark':      '#1F2937'   # 深灰文本
}

# Chart Configuration
CHART_CONFIG = {
    'height': 520,
    'template': 'plotly_white',
    'font_family': 'Inter, SF Pro Text, Roboto, Arial, sans-serif',
    'font_size': 12,
    'title_font_size': 18,
    'margin': {'l': 60, 'r': 60, 't': 80, 'b': 60},
    # 统一的系列颜色序列（避免各处硬编码）
    'colorway': [
        '#0B3B5A',  # primary
        '#0E7490',  # teal
        '#6366F1',  # indigo
        '#F59E0B',  # amber
        '#059669',  # emerald
        '#DC2626',  # red
        '#374151'   # gray
    ],
    # 背景与网格
    'paper_bgcolor': 'white',
    'plot_bgcolor': 'white',
    'gridcolor': '#E5E7EB',
    'zerolinecolor': '#CBD5E1',
}

# Data Display Configuration
TABLE_CONFIG = {
    'height': 400,
    'use_container_width': True,
    'hide_index': True
}

# File Upload Configuration
UPLOAD_CONFIG = {
    'max_file_size': 10,  # MB
    'allowed_types': ['csv'],
    'help_text': "上传包含年份和收益率数据的CSV文件"
}

# Analysis Configuration
ANALYSIS_CONFIG = {
    'min_years_for_analysis': 10,
    'max_window_size': 50,
    'precision_decimals': 4,
    'percentage_format': '{:.2%}'
}

# Footer
FOOTER_TEXT = "S&P 500 Rolling Returns and Convergence Analysis Tool<br/>Data Engineer, 2025"

# UI Messages
MESSAGES = {
    'welcome': """
    欢迎使用S&P 500滚动收益率与收敛性分析工具！
    
    这个工具可以帮助您：
    - 分析不同时间窗口的滚动收益率
    - 计算收益率收敛性指标
    - 找到无损失的最小持有期
    - 生成专业的分析报告
    """,
    'data_loaded': "✅ 数据加载成功！",
    'analysis_complete': "✅ 分析完成！",
    'error_no_data': "❌ 请先加载数据",
    'error_insufficient_data': "❌ 数据不足，无法进行分析",
    'downloading_data': "📥 正在从SlickCharts下载数据...",
    'processing_data': "⚙️ 正在处理数据...",
    'generating_charts': "📊 正在生成图表..."
}

# Help Text
HELP_TEXT = {
    'start_years': "选择分析的基准起始年份。这些年份将作为滚动窗口分析的起点。",
    'thresholds': "设置收敛性分析的阈值。较小的阈值表示更严格的收敛标准。",
    'windows': "选择要分析的时间窗口长度（年）。",
    'data_source': "选择数据来源：从SlickCharts自动下载或上传本地CSV文件。",
    'output_format': "选择输出格式和下载选项。"
}

# CSS Styles
CUSTOM_CSS = """
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

    .main-header {
        background: linear-gradient(90deg, #0B3B5A 0%, #0E7490 100%);
        padding: 2rem;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "Helvetica Neue", Helvetica, Arial, sans-serif;
    }

    .metric-card {
        background: white;
        padding: 1.25rem 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 6px rgba(15, 23, 42, 0.08);
        border-left: 4px solid #0B3B5A;
        margin-bottom: 1rem;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "Helvetica Neue", Helvetica, Arial, sans-serif;
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
    
    .success-message {
        background: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #c3e6cb;
        margin: 1rem 0;
    }
    
    .error-message {
        background: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #f5c6cb;
        margin: 1rem 0;
    }
    
    .info-box {
        background: #e3f2fd;
        color: #0d47a1;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #bbdefb;
        margin: 1rem 0;
    }
    
    /* Streamlit组件字体优化 */
    .stMetric {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "Helvetica Neue", Helvetica, Arial, sans-serif;
    }

    .stMetric > div > div > div {
        font-family: "SF Mono", "Monaco", "Inconsolata", "Roboto Mono", "Source Code Pro", monospace;
        font-weight: 600;
    }

    .stSelectbox > div > div > div {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "Helvetica Neue", Helvetica, Arial, sans-serif;
    }

    .stTextInput > div > div > input {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "Helvetica Neue", Helvetica, Arial, sans-serif;
    }

    /* 表格字体优化 */
    .stDataFrame {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "Helvetica Neue", Helvetica, Arial, sans-serif;
    }

    .stDataFrame table {
        font-size: 0.875rem;
    }

    .stDataFrame th {
        font-weight: 600;
        background-color: #f8fafc;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }

    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
        background-color: #F5F7FA;
        border-radius: 8px 8px 0 0;
        border: 1px solid #E5E7EB;
        border-bottom: none;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "Helvetica Neue", Helvetica, Arial, sans-serif;
        font-weight: 500;
    }

    .stTabs [aria-selected="true"] {
        background-color: #0B3B5A;
        color: white;
        border-color: #0B3B5A;
        font-weight: 600;
    }
</style>
"""
