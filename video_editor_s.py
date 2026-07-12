import streamlit as st
import fitz
from PIL import Image
import io, os, json, base64
import slide_pdf_exporter
import video_automation_engine

st.set_page_config(page_title="Slide Video Generator", layout="wide")
st.title("🎬 スライド動画・錬成スタジオ Pro")

SAVE_FILE = "script_save_data.json"
uploaded_file = st.file_uploader("研修用PDFをアップロードしてください", type=["pdf"])

if uploaded_file:
    pdf_bytes = uploaded_file.read()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    total_pages = len(doc)
    st.success(f"PDFの読み込み成功（全 {total_pages} ページ）")
    
    if "subtitles" not in st.session_state: st.session_state.subtitles = {}
    if "voices" not in st.session_state: st.session_state.voices = {}

    st.write("### 💾 データ一括管理（セーブ／ロード／一括クリア）")
    col_save1, col_save2 = st.columns(2)
    
    with col_save1:
        if st.button("💾 現在の入力内容をMacに保存する（セーブ）"):
            save_data = {"subtitles": st.session_state.subtitles, "voices": st.session_state.voices}
            with open(SAVE_FILE, "w", encoding="utf-8") as f:
                json.dump(save_data, f, ensure_ascii=False, indent=4)
            st.success(f"🎉 成功！データを 『{SAVE_FILE}』 に保存しました！")
            
    with col_save2:
        if st.button("📂 前回の保存データを読み込む（ロード）"):
            if os.path.exists(SAVE_FILE):
                with open(SAVE_FILE, "r", encoding="utf-8") as f: loaded_data = json.load(f)
                st.session_state.subtitles = {int(k): v for k, v in loaded_data.get("subtitles", {}).items()}
                st.session_state.voices = {int(k): v for k, v in loaded_data.get("voices", {}).items()}
                for k, v in st.session_state.subtitles.items(): st.session_state[f"sub_{k}"] = v
                for k, v in st.session_state.voices.items(): st.session_state[f"voice_{k}"] = v
                st.success("🎉 保存データを復元しました！")
                st.rerun()
            else:
                st.sidebar.warning("保存データが見つかりませんでした。")

    col_clear1, col_clear2 = st.columns(2)
    with col_clear1:
        if st.button("🗑️ すべてのページの『字幕（テロップ）』を全削除する"):
            st.session_state.subtitles = {}
            for k in list(st.session_state.keys()):
                if k.startswith("sub_"): del st.session_state[k]
            st.success("字幕をすべてクリアしました！")
            st.rerun()
            
    with col_clear2:
        if st.button("🗑️ すべてのページの『音声読み上げ原稿』を全削除する"):
            st.session_state.voices = {}
            for k in list(st.session_state.keys()):
                if k.startswith("voice_"): del st.session_state[k]
            st.success("音声原稿をすべてクリアしました！")
            st.rerun()

    st.write("---")
    st.write("### 📥 テロップ・原稿の一括インポート（1行＝1ページ）")
    st.info("💡 メモ帳やExcel（CSV）で作成した文章を貼り付けると、改行（行番号）を元に各ページへ一気に流し込めます。")
    
    import_text = st.text_area("ここに1行ずつ文章を貼り付けてください", height=150)
    
    if st.button("⚡ 貼り付けた文章を全ページに一括反映する"):
        if import_text.strip():
            lines = import_text.split("\n")
            for idx, line in enumerate(lines):
                if idx < total_pages:
                    clean_line = line.strip()
                    st.session_state.subtitles[idx] = clean_line
                    st.session_state.voices[idx] = clean_line
                    st.session_state[f"sub_{idx}"] = clean_line
                    st.session_state[f"voice_{idx}"] = clean_line
            st.success(f"🎉 成功！ 一括反映しました。")
            st.rerun()

    st.write("---")
    st.write("## 📝 全ページ一括編集（スクロールして入力してください）")
    st.write("---")

    for current in range(total_pages):
        st.write(f"### 📄 第 {current + 1} / {total_pages} ページ目")
        col_left, col_right = st.columns(2)
        
        with col_left:
            page = doc[current]
            pix = page.get_pixmap()
            img_data = pix.tobytes("png")
            img = Image.open(io.BytesIO(img_data))
            st.image(img, use_container_width=True) 
            
        with col_right:
            sub_key = f"sub_{current}"
            if sub_key not in st.session_state: 
                st.session_state[sub_key] = st.session_state.subtitles.get(current, "")
            subtitle_input = st.text_area("動画の画面上に表示される字幕（テロップ）です", key=sub_key)
            st.session_state.subtitles[current] = subtitle_input

            st.write("") 

            voice_key = f"voice_{current}"
            if voice_key not in st.session_state or not st.session_state[voice_key].strip():
                st.session_state[voice_key] = subtitle_input
                
            voice_input = st.text_area("AIが読み上げる原稿です（テロップと同じ文字が自動連動します）", key=voice_key)
            st.session_state.voices[current] = voice_input

            if st.button("🔊 このページの音声を試聴する", key=f"btn_{current}"):
                if voice_input.strip():
                    with st.spinner("Googleクラウドが喋っています..."):
                        try:
                            # 🌟 成功したbase64突破ロジックをここに完全移植！
                            v_bytes = video_automation_engine.get_cloud_voice_bytes(voice_input)
                            b64_audio = base64.b64encode(v_bytes).decode()
                            audio_html = f'<audio controls src="data:audio/mp3;base64,{b64_audio}" style="width: 100%;"></audio>'
                            st.markdown(audio_html, unsafe_allow_html=True)
                        except Exception as e:
                            st.error(f"音声の取得に失敗しました: {e}")
                else:
                    st.warning("音声原稿が空っぽです。")
        st.write("---")

    if st.button("🖨 A4縦の台本付きスライド資料を錬成する"):
        with st.spinner("📄 PDFを綺麗にレイアウト中..."):
            try:
                pdf_name = slide_pdf_exporter.generate_script_pdf(doc, total_pages, st.session_state.subtitles)
                st.success(f"🎉 成功！ 資料PDF 『{pdf_name}』 を生成しました！")
            except Exception as e:
                st.error(f"PDF生成中にエラーが発生しました: {e}")

    if st.button("🚀 この台本で字幕付き動画の自動錬成を開始する"):
        progress_bar = st.progress(0)
        with st.spinner("🎬 動画の合成を実行中..."):
            try:
                def update_progress(val): progress_bar.progress(val)
                video_name = video_automation_engine.generate_video_file(
                    doc, total_pages, st.session_state.subtitles, st.session_state.voices, update_progress
                )
                if video_name:
                    st.success(f"🎉 完璧です！動画 『{video_name}』 が完成しました！")
                else:
                    st.warning("台本が入力されているページがありませんでした。")
            except Exception as e:
                st.error(f"錬成中にエラーが発生しました: {e}")
