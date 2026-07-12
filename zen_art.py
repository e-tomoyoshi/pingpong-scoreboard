import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import io
# 🌟 あなたのアイデア通り、別モジュールの和紙職人を呼び出す！
import washi_generator

st.set_page_config(page_title="Zen Art Pro", page_icon="🖌️")
st.title("老子の言葉 × 本格手漉き和紙アート")

quotes = ["上善は水の如し", "足るを知る者は富む", "無為自然", "千里の行も足下に始まる"]
selected_quote = st.selectbox("言葉を選んでください", quotes)
custom_text = st.text_input("または、好きな言葉を入力してください")
display_text = custom_text if custom_text else selected_quote

def generate_zen_image(text):
    # 🌟 1. 別モジュールから、数式で計算された完璧な和紙を1から生成して受け取る
    base_img = washi_generator.generate_pure_washi(width=2000, height=2800)
    width, height = base_img.size
    
    draw = ImageDraw.Draw(base_img)

    # 2. フォント設定 (Mac用)
    font_path = "/System/Library/Fonts/ヒラギノ明朝 ProN.ttc"
    font_size = int(height * 0.06)  # 画面の高さに合わせて文字サイズを自動調整
    font = ImageFont.truetype(font_path, font_size)

    # 縦書きの処理（1文字ずつ改行で繋ぐ）
    vertical_text = "\n".join(list(text))
    
    # 3. 墨の「にじみ」エフェクト
    # 文字の後ろに、わずかにぼかした薄い墨を敷くことで「にじみ」を表現
    shadow_layer = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow_layer)
    
    # 薄い墨色（透明度のある黒）で文字を描く
    shadow_draw.multiline_text((width * 0.8 + 4, height * 0.1 + 4), 
                               vertical_text, font=font, fill=(40, 40, 40, 100), spacing=30)
    # ガウスぼかしをかけて「にじみ」にする
    shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(radius=3))
    base_img.paste(shadow_layer, (0, 0), shadow_layer)
    
    # 本番の文字（少し薄い墨色にすると和紙に馴染みます）
    draw.multiline_text((width * 0.8, height * 0.1), 
                        vertical_text, font=font, fill=(35, 35, 35), spacing=30)

    # 4. 落款（右下に配置）
    stamp_size = int(height * 0.05)
    stamp_font = ImageFont.truetype(font_path, int(stamp_size * 0.8))
    
    # 四角い枠
    draw.rectangle([width*0.8, height*0.8, width*0.8 + stamp_size, height*0.8 + stamp_size], 
                   outline=(180, 0, 0), width=8)
    # 枠の中に「道」
    draw.text((width*0.8 + stamp_size*0.1, height*0.8 + stamp_size*0.05), 
              "道", font=stamp_font, fill=(180, 0, 0))

    return base_img

# --- 画面描画パート ---
if st.button("作品を生成する"):
    with st.spinner("極上和紙を漉き、墨で文字を描いています..."):
        result_img = generate_zen_image(display_text)
        st.image(result_img, use_container_width=True)
        
        # 高解像度ダウンロード用のデータ処理
        buf = io.BytesIO()
        result_img.save(buf, format="PNG")
        st.download_button("高解像度PNGを保存（商用利用・販売自由）", buf.getvalue(), "zen_artwork.png", "image/png")
