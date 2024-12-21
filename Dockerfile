FROM python:3.11-slim

# 安裝必要工具和 Google Chrome
RUN apt-get update && apt-get install -y \
    wget unzip curl gnupg --no-install-recommends && \
    wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    dpkg -i google-chrome-stable_current_amd64.deb || apt-get -f install -y && \
    rm -rf /var/lib/apt/lists/* google-chrome-stable_current_amd64.deb

# 安裝 Python 依賴
COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用程式代碼
COPY . /app

# 設置默認執行命令
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8080"]
