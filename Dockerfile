# Python 3.14の軽量イメージを使用
FROM python:3.14-slim

# コンテナ内の作業ディレクトリの設定
WORKDIR /app

# 必要なパッケージをコピーしてインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 手元のプログラム本体（app.py, agent.pyなど）をまるごとコピー
COPY . .

# Cloud Runが標準で使用するポート(8080)を公開
EXPOSE 8080

# StreamlitをCloud Run用の設定で起動
CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]