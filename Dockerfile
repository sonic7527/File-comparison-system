FROM python:3.9-slim

# 設置工作目錄
WORKDIR /app

# 複製依賴文件
COPY requirements.txt .

# 安裝依賴
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用代碼
COPY . .

# 創建 streamlit 目錄並設置權限
RUN mkdir -p /root/.streamlit && \
    chmod 755 /root/.streamlit

# 暴露端口
EXPOSE 8501

# 設置環境變數
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
ENV STREAMLIT_SERVER_ENABLE_CORS=false
ENV STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=false
ENV STREAMLIT_GLOBAL_DEVELOPMENT_MODE=false
ENV STREAMLIT_SERVER_FILE_WATCHER_TYPE=none

# 啟動命令
CMD ["streamlit", "run", "main_app.py", "--server.port=8501", "--server.address=0.0.0.0"] 