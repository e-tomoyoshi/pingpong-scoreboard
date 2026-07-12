# 1. ベースとして、公式が用意してくれている軽量なPython環境（冷凍パック）を借りてくる
FROM python:3.11-slim

# 2. コンテナ（小部屋）の中の作業フォルダを「/app」に指定
WORKDIR /app

# 3. パソコン側にある「requirements.txt」を、コンテナの中にコピーする
COPY requirements.txt .

# 4. コンテナの中で pip コマンドを実行し、必要なパッケージをすべてインストールする
RUN pip install --no-cache-dir -r requirements.txt

# 5. パソコン側にあるすべてのプログラムコードを、コンテナの中に丸ごとコピーする
COPY . .

# 6. Streamlitが使うポート番号（8501番）をコンテナの窓口として開ける
EXPOSE 8501

# 7. コンテナが起動した瞬間に、Streamlitを自動実行する命令
CMD ["streamlit", "run", "test/fund_tracker.py", "--server.port=8501", "--server.address=0.0.0.0"]
