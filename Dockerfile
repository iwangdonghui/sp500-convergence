FROM python:3.11-slim
WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 拷贝代码
COPY . .

# 运行环境
ENV STREAMLIT_SERVER_HEADLESS=true \
    HF_HUB_DISABLE_TELEMETRY=1 \
    PYTHONPATH=/app/src \
    APP_FILE=src/app.py

EXPOSE 7860
CMD ["bash", "-lc", "streamlit run \"$APP_FILE\" --server.port 7860 --server.address 0.0.0.0 --browser.gatherUsageStats false"]