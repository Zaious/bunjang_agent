# 使用 Python Slim 基礎映像
FROM python:3.11-slim

# 安裝 Google Chrome 和必要工具
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    google-chrome-stable --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# 設置工作目錄
WORKDIR /app

# 複製 Python 依賴文件
COPY requirements.txt requirements.txt

# 安裝 Python 依賴
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用程式代碼
COPY . .

# 默認啟動命令
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8080"]
