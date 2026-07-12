import streamlit as st
from gtts import gTTS
import base64
import io

st.title("🔈 音声再生テスト（Safari対応版）")

# 1. テキスト入力欄
text_input = st.text_input("テスト用の文字", value="テスト。これから研修を始めます。")

# 2. ボタンを押したら音声を生成して、Safariが拒否できない形に変換して再生
if st.button("🔊 音声を生成して再生"):
    with st.spinner("生成中..."):
        try:
            # メモリ上にMP3を生成（Mac内にファイルを保存しないので極めて安全で高速）
            fp = io.BytesIO()
            tts = gTTS(text=text_input, lang='ja')
            tts.write_to_fp(fp)
            fp.seek(0)
            audio_bytes = fp.read()
            
            # 🌟 Safariのブロックを回避するため、データをテキスト(base64)に変換
            b64_audio = base64.b64encode(audio_bytes).decode()
            
            # HTMLのオーディオタグを使って、画面にプレイヤーを強制埋め込み
            audio_html = f'<audio controls autoplay src="data:audio/mp3;base64,{b64_audio}" style="width: 100%;"></audio>'
            st.markdown(audio_html, unsafe_allow_html=True)
            
            st.success("Safariのセキュリティを突破して音声を埋め込みました！再生ボタンを押してください。")
            
        except Exception as e:
            st.error(f"エラーが発生しました: {e}")
