TERMS = [
    ("无损失最短持有期", "Min no-loss horizon", "最短的持有年限，使得所有滚动窗口的CAGR均不小于0；衡量避免亏损的最小时间成本。"),
    ("收敛性", "Convergence", "不同滚动窗口的CAGR差值（最大-最小）在某阈值以内，所需的最小持有年限；衡量收益分布趋同稳定。"),
    ("收敛阈值", "Threshold", "衡量\"最大-最小CAGR\"可接受范围的阈值，越小越严格。"),
    ("CAGR", "Compound Annual Growth Rate", "复合年增长率；几何平均增长率，衡量长期增长速度。"),
    ("参考窗口", "Reference window", "优先采用20年窗口；若不可用则采用可用的最大窗口。"),
    ("P10/P50/P90", "P10/P50/P90", "滚动CAGR分布的10%/50%/90%分位数，反映偏保守/中位/偏乐观情景。"),
    ("波动最小窗口", "Lowest volatility window", "标准差σ最小的窗口，代表相对稳定的收益分布。"),
    ("平均收益较优窗口", "Window with higher average CAGR", "平均CAGR最高的窗口，在样本期内长期复合收益较优。"),
    ("稳定性指数", "Stability index", "avg/std 的近似指标，数值越大表明单位波动带来的平均收益越高（非严格Sharpe）。"),
    ("变异系数", "Coefficient of variation", "std/|avg|，相对波动性指标，越小越稳定（平均值接近0时需谨慎解释）。"),
]


def render_glossary_md() -> str:
    lines = ["# 术语表 / Glossary\n"]
    for zh, en, desc in TERMS:
        lines.append(f"- **{zh} / {en}** — {desc}")
    return "\n".join(lines)


def to_csv() -> str:
    import csv
    import io
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["中文", "English", "说明/Description"])
    for zh, en, desc in TERMS:
        writer.writerow([zh, en, desc])
    return buf.getvalue()

