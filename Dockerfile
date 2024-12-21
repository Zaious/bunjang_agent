FROM python:3.11-slim

# 安裝必要依賴
RUN apt-get update && apt-get install -y wget gnupg unzip --no-install-recommends && \
    wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    dpkg -i google-chrome-stable_current_amd64.deb || apt-get -f install -y && \
    rm -rf /var/lib/apt/lists/*

# 安裝 Python 依賴
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用代碼
COPY . .

# 啟動應用
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8080"]
