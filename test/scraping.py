import requests
from bs4 import BeautifulSoup
import csv
import datetime
import sys  # --- 1. システムを操る道具を追加 ---

# --- 2. ターミナルからの言葉を受け取る設定 ---
# もし言葉が指定されなかったら、とりあえず「円」にする
if len(sys.argv) > 1:
    keyword = sys.argv[1]
else:
    keyword = "円"

url = "https://news.yahoo.co.jp"
# (以下、これまでのコードと同じ)
response = requests.get(url)
response.encoding = response.apparent_encoding
soup = BeautifulSoup(response.text, 'html.parser')
titles = soup.find_all('a')

today_str = datetime.date.today().strftime('%Y%m%d')
filename = f'news_{keyword}_{today_str}.csv' # ファイル名にキーワードを入れると便利！

with open(filename, 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(["番号", "ニュースタイトル", "URL"])

    count = 0
    for title in titles:
        text = title.get_text()
        if keyword in text:
            count += 1
            link = title.get('href')
            writer.writerow([count, text, link])
            print(f"{count}: {text}")

print(f"\n--- キーワード『{keyword}』で {count}件保存しました ---")
