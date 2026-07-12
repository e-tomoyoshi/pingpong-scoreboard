import datetime
import plotly.graph_objects as go
import pandas as pd
import streamlit as st
import yfinance as yf

# 画面を横いっぱいに広く使う設定
st.set_page_config(page_title="Market Dashboard Pro", layout="wide")

st.title("📊 世界市場インデックス・ダッシュボード Pro")
st.write("API（yfinance）を使用。表示期間をボタンで自由に切り替えられます。")

# 1. 資産のラインナップ（上部パネル・グラフ共通）
panel_assets = {
    "SOX指数 (半導体)": "^SOX",
    "NASDAQ 100": "^NDX",
    "S&P 500": "^GSPC",
    "ACWI オルカン(ETF)": "ACWI",
    "💥 FANG+ (大企業10社)": "FNGS"
}

# 為替レート（ドル円）のティッカー
forex_ticker = "JPY=X"

# 🌟 2. 【新機能】画面上部に期間選択ボタン（ラジオボタン）を設置
# ユーザーがポチポチ切り替えられるようにします
st.write("### 📅 表示期間の切り替え")
period_choice = st.radio(
    "グラフとパネルの計算基準となる期間を選んでください：",
    options=["直近1ヶ月", "直近3ヶ月", "年初来 (2026年1月1日〜)", "直近1年"],
    horizontal=True, # ボタンを横並びにする設定
    index=2 # 初期状態は「年初来」にチェックを入れておく
)

# 🌟 3. 選択されたボタンに応じて、yfinanceに頼む期間（開始日）を自動計算
current_date = datetime.datetime.now()
current_year = current_date.year

if period_choice == "直近1ヶ月":
    start_date = (current_date - datetime.timedelta(days=30)).strftime("%Y-%m-%d")
elif period_choice == "直近3ヶ月":
    start_date = (current_date - datetime.timedelta(days=90)).strftime("%Y-%m-%d")
elif period_choice == "年初来 (2026年1月1日〜)":
    start_date = f"{current_year}-01-01"
else: # 直近1年
    start_date = (current_date - datetime.timedelta(days=365)).strftime("%Y-%m-%d")

end_date = current_date.strftime("%Y-%m-%d")

# 上部パネル用の横並びカラム（上の資産5個 + ドル円1個 = 6列）
cols = st.columns(len(panel_assets) + 1)

# グラフ用のデータを貯める辞書
historical_data = {}

# 各資産のデータ取得と上部パネルの描画
for idx, (name, ticker_symbol) in enumerate(panel_assets.items()):
    try:
        ticker = yf.Ticker(ticker_symbol)
        # 🌟 選択された開始日から今日までのデータをダウンロード
        df_all = ticker.history(start=start_date, end=end_date)

        if len(df_all) >= 2:
            latest_price = df_all["Close"].iloc[-1]
            previous_price = df_all["Close"].iloc[-2]
            delta_price = latest_price - previous_price
            delta_percent = (delta_price / previous_price) * 100

            # 上部パネルを表示
            with cols[idx]:
                st.metric(
                    label=name,
                    value=f"{latest_price:,.2f}",
                    delta=f"{delta_price:+,.2f} ({delta_percent:+.2f}%)",
                )

            # グラフ用のシリーズデータを保存
            historical_data[name] = df_all["Close"]

    except Exception as e:
        with cols[idx]:
            st.error(f"{name} の取得エラー: {e}")

# ドル円（USD/JPY）データを取得して一番右端（6列目）に表示
try:
    forex_ticker_obj = yf.Ticker(forex_ticker)
    df_forex = forex_ticker_obj.history(period="2d")

    if len(df_forex) >= 2:
        latest_fx = df_forex["Close"].iloc[-1]
        previous_fx = df_forex["Close"].iloc[-2]
        delta_fx = latest_fx - previous_fx
        delta_fx_percent = (delta_fx / previous_fx) * 100

        with cols[-1]:
            st.metric(
                label="米ドル / 円 (USD/JPY)",
                value=f"¥{latest_fx:.2f}",
                delta=f"{delta_fx:+.2f}円 ({delta_fx_percent:+.2f}%)",
            )
except Exception as e:
    with cols[-1]:
        st.error(f"ドル円の取得エラー: {e}")


st.write("---")

# グラフの作成パート
if historical_data:
    # データを一つの表にまとめて、空欄を自動で埋める
    df_trends = pd.DataFrame(historical_data).ffill().bfill()

    # 🌟 選択された期間の「最初の営業日の価格」を基準（0%）としてリターンを計算
    df_returns = pd.DataFrame(index=df_trends.index)
    for name in df_trends.columns:
        first_price = df_trends[name].iloc[0]  # その期間のスタート時の価格
        df_returns[name] = ((df_trends[name] - first_price) / first_price) * 100

    st.write(f"### 📈 選択期間：{period_choice}のリターン（％）比較推移")

    fig = go.Figure()

    for name in df_returns.columns:
        fig.add_trace(
            go.Scatter(
                x=df_returns.index,
                y=df_returns[name],
                mode="lines",
                name=name,
                hovertemplate="%{x}<br>" + name + ": %{y:.2f}%<extra></extra>",
            )
        )

    fig.update_layout(
        hovermode="x unified",
        xaxis_title="日付",
        yaxis_title="リターン (%)",
        yaxis=dict(ticksuffix="%"),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
        ),
        margin=dict(l=0, r=0, t=50, b=0),
        height=500,
    )

    st.plotly_chart(fig, use_container_width=True)

else:
    st.error("グラフ用のデータが集まりませんでした。")
