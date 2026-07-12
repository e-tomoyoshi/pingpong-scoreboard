import requests
from bs4 import BeautifulSoup
import datetime
import csv
import os

# 1. ターゲット（iFreeNEXT FANG+）のURL
url = "https://finance.yahoo.co.jp"

# 2. サイトの情報を取得（ブラウザのふりをする「ユーザーエージェント」を追加）
headers = {"User-Agent": "Mozilla/5.0"}
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

# 3. 基準価額が書かれている場所を探す
# Yahooファイナンスの「基準価額」という文字の隣にある数字を探す作戦
price = None

# 方法A: 以前のクラス名で探す
price_element = soup.find("span", class_="_3rXW_f9Q")

# 方法B: もしAで見つからなければ、特定のパターンで探す
if not price_element:
    # 基準価額の数字は、大きな文字で表示されていることが多いので
    # ページ内の「span」タグを全部調べて、カンマを含む数字っぽいものを探してみる
    spans = soup.find_all("span")
    for span in spans:
        text = span.get_text()
        # カンマを含み、かつ中身が数字（5桁〜）っぽいものを探す
        if "," in text and text.replace(",", "").isdigit():
            price = text.replace(",", "")
            break
else:
    price = price_element.get_text().replace(",", "")

if price:
    today = datetime.date.today().strftime('%Y-%m-%d')
    print(f"本日({today})の基準価額: {price}円")

    # 4. CSVファイルに追記
    filename = 'fang_history.csv'
    file_exists = os.path.isfile(filename)
    with open(filename, 'a', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["date", "price"])
        writer.writerow([today, price])
    print(f"データを {filename} に記録しました。")
else:
    # デバッグ用：中身がどうなっているか少しだけ表示
    print("価格が見つかりません。サイトの構造を再確認します。")
    print("取得したテキストの一部:", soup.text[:100].replace("\n", ""))
