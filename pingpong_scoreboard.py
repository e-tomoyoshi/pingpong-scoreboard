import streamlit as st

# 1. ページ構成
st.set_page_config(layout="wide")

# 2. CSS：配置のバランス調整と機能の維持
css = """
<style>
.stApp { background: #000 !important; overflow: hidden !important; }
header { display: none !important; }

/* 全体レイアウト */
.main .block-container {
    padding: 10px 20px !important;
    height: 100vh !important;
    display: flex;
    flex-direction: column;
}

/* 要素間の基本隙間 */
div[data-testid="stVerticalBlock"] { gap: 10px !important; }

/* 📊 ボードの設定：高さを統一 */
.board-box, .g-box-mini {
    width: 100% !important; 
    height: 48vh !important; 
    background: #111 !important;
    border: 2px solid #222 !important; 
    border-radius: 15px !important;
    display: flex !important; 
    align-items: center !important; 
    justify-content: center !important;
    margin-top: 8px !important; /* ＋ボタンとの隙間 */
}

/* スコア表示（通常は白） */
.p-score { font-size: min(32vh, 260px) !important; font-weight: 700; color: #fff; line-height: 1 !important; }
/* 🔥 10点以上の黄色表示（維持） */
.p-score-climax { color: #f7d138 !important; text-shadow: 0 0 30px rgba(247,209,56,0.4); }

/* ゲーム数（青色：維持） */
.g-score-mini { font-size: min(15vh, 100px) !important; font-weight: 700 !important; color: #00d4ff !important; }

/* コロンの調整 */
.colon-container {
    height: 48vh !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    margin-top: 8px !important;
}

/* 🔴 ーボタンの位置をさらに下げて、上下の余白バランスを統一 */
.minus-container {
    margin-top: 30px !important;
}

/* ボタン：スタイル維持 */
div[data-testid="stButton"] button {
    height: 52px !important;
    font-size: 24px !important;
    font-weight: 700 !important;
    background-color: #1a1a1a !important;
    border: 1px solid #333 !important;
    border-radius: 10px !important;
}

/* プレイヤー名・サーブライン */
.r-line { height: 6px; background: #ff4b4b; width: 100%; border-radius: 3px; margin-top: 5px; }
.e-line { height: 6px; width: 100%; margin-top: 5px; }
div[data-testid="stHorizontalBlock"] input {
    background: transparent !important; color: #fff !important;
    font-size: 26px !important; font-weight: 700 !important; text-align: center !important;
}
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# 3. セッション管理
if "player_a" not in st.session_state: st.session_state.player_a = "プレイヤーA"
if "player_b" not in st.session_state: st.session_state.player_b = "プレイヤーB"
if "score_a" not in st.session_state: st.session_state.score_a = 0
if "score_b" not in st.session_state: st.session_state.score_b = 0
if "game_a" not in st.session_state: st.session_state.game_a = 0
if "game_b" not in st.session_state: st.session_state.game_b = 0
if "initial_server" not in st.session_state: st.session_state.initial_server = "左"
if "swap_version" not in st.session_state: st.session_state.swap_version = 0

# 4. 試合ロジック（維持）
s_a, s_b = st.session_state.score_a, st.session_state.score_b
if (s_a >= 11 or s_b >= 11) and abs(s_a - s_b) >= 2:
    if s_a > s_b: st.session_state.game_a += 1
    else: st.session_state.game_b += 1
    st.session_state.score_a, st.session_state.score_b = 0, 0
    st.rerun()

pts = s_a + s_b
if s_a >= 10 and s_b >= 10:
    srv_a = (pts % 2 == 0) if st.session_state.initial_server == "左" else (pts % 2 != 0)
else:
    srv_a = ((pts // 2) % 2 == 0) if st.session_state.initial_server == "左" else ((pts // 2) % 2 != 0)

# --- UI 描画 ---
st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
c1, c2, c3 = st.columns([2, 1, 2])
with c1:
    st.session_state.player_a = st.text_input("L", st.session_state.player_a, key=f"ia_{st.session_state.swap_version}", label_visibility="collapsed")
    st.markdown("<div class='r-line'></div>" if srv_a else "<div class='e-line'></div>", unsafe_allow_html=True)
with c2:
    if st.button("⇄ Court", use_container_width=True):
        st.session_state.player_a, st.session_state.player_b = st.session_state.player_b, st.session_state.player_a
        st.session_state.score_a, st.session_state.score_b = st.session_state.score_b, st.session_state.score_a
        st.session_state.game_a, st.session_state.game_b = st.session_state.game_b, st.session_state.game_a
        st.session_state.initial_server = "右" if st.session_state.initial_server == "左" else "左"
        st.session_state.swap_version += 1; st.rerun()
    if st.button("🔥 Serve", use_container_width=True):
        st.session_state.initial_server = "右" if st.session_state.initial_server == "左" else "左"; st.rerun()
with c3:
    st.session_state.player_b = st.text_input("R", st.session_state.player_b, key=f"ib_{st.session_state.swap_version}", label_visibility="collapsed")
    st.markdown("<div class='r-line'></div>" if not srv_a else "<div class='e-line'></div>", unsafe_allow_html=True)

# 2段目：5列構造
st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
cols = st.columns([1.5, 0.6, 0.2, 0.6, 1.5])

with cols[0]:
    if st.button("＋", key="pa+", use_container_width=True): st.session_state.score_a += 1; st.rerun()
    st.markdown(f"<div class='board-box'><span class=\"{'p-score p-score-climax' if s_a >= 10 else 'p-score'}\">{s_a}</span></div>", unsafe_allow_html=True)
    st.markdown("<div class='minus-container'>", unsafe_allow_html=True)
    if st.button("ー", key="pa-", use_container_width=True):
        if st.session_state.score_a > 0: st.session_state.score_a -= 1; st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

with cols[1]:
    if st.button("＋", key="ga+", use_container_width=True): st.session_state.game_a += 1; st.rerun()
    st.markdown(f"<div class='g-box-mini'><span class='g-score-mini'>{st.session_state.game_a}</span></div>", unsafe_allow_html=True)
    st.markdown("<div class='minus-container'>", unsafe_allow_html=True)
    if st.button("ー", key="ga-", use_container_width=True):
        if st.session_state.game_a > 0: st.session_state.game_a -= 1; st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

with cols[2]:
    st.markdown("<div style='height:52px'></div>", unsafe_allow_html=True)
    st.markdown("<div class='colon-container'><span style='color:#444; font-size:30px; font-weight:bold;'>:</span></div>", unsafe_allow_html=True)

with cols[3]:
    if st.button("＋", key="gb+", use_container_width=True): st.session_state.game_b += 1; st.rerun()
    st.markdown(f"<div class='g-box-mini'><span class='g-score-mini'>{st.session_state.game_b}</span></div>", unsafe_allow_html=True)
    st.markdown("<div class='minus-container'>", unsafe_allow_html=True)
    if st.button("ー", key="gb-", use_container_width=True):
        if st.session_state.game_b > 0: st.session_state.game_b -= 1; st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

with cols[4]:
    if st.button("＋", key="pb+", use_container_width=True): st.session_state.score_b += 1; st.rerun()
    st.markdown(f"<div class='board-box'><span class=\"{'p-score p-score-climax' if s_b >= 10 else 'p-score'}\">{s_b}</span></div>", unsafe_allow_html=True)
    st.markdown("<div class='minus-container'>", unsafe_allow_html=True)
    if st.button("ー", key="pb-", use_container_width=True):
        if st.session_state.score_b > 0: st.session_state.score_b -= 1; st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# 3段目
st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
if st.button("🔄 Reset All", use_container_width=True):
    st.session_state.update(score_a=0, score_b=0, game_a=0, game_b=0, initial_server="左", swap_version=st.session_state.swap_version+1)
    st.rerun()