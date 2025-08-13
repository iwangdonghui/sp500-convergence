# 方案A：推荐 3.11（官方轮子更全，构建更快）
FROM python:3.11-slim

# 基础环境
ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Streamlit 必需设置
ENV STREAMLIT_SERVER_HEADLESS=true \
    HF_HUB_DISABLE_TELEMETRY=1

EXPOSE 7860
CMD ["streamlit", "run", "app.py", "--server.port", "7860", "--server.address", "0.0.0.0", "--browser.gatherUsageStats", "false"]