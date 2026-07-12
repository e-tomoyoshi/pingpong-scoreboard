import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io

st.set_page_config(page_title="Zen Art Pro", page_icon="🖌️")
st.title("老子の言葉 × 本格水墨画")

quotes = ["上善は水の如し", "足るを知る者は富む", "柔よく剛を制す", "千里の行も足下に始まる"]
selected_quote = st.selectbox("言葉を選んでください", quotes)
custom_text = st.text_input("または、好きな言葉を入力してください")
display_text = custom_text if custom_text else selected_quote

def generate_zen_image(text):
    # 1. 背景画像を読み込む
    try:
        # 同じフォルダにある background.png を開く
        base_img = Image.open("background.png").convert("RGB")
        # 印刷に耐えるサイズ（例：横2000px）にリサイズ
        # アスペクト比を維持しつつ調整
        base_img.thumbnail((2000, 2800), Image.Resampling.LANCZOS)
        width, height = base_img.size
    except FileNotFoundError:
        # 画像がない場合は、前の和紙色キャンバスを出す（エラー防止）
        width, height = 2000, 2800
        base_img = Image.new('RGB', (width, height), color=(245, 245, 240))

    draw = ImageDraw.Draw(base_img)

    # 2. フォント設定 (Mac用)
    font_path = "/System/Library/Fonts/ヒラギノ明朝 ProN.ttc"
    font_size = int(height * 0.06)  # 画面の高さに合わせて文字サイズを自動調整
    font = ImageFont.truetype(font_path, font_size)

    # 3. 縦書きの処理
    vertical_text = "\n".join(list(text))
    
    # 墨の「にじみ」を表現するために、少しズレた薄い影を重ねる
    shadow_offset = 3
    draw.multiline_text((width * 0.8 + shadow_offset, height * 0.1 + shadow_offset), 
                        vertical_text, font=font, fill=(180, 180, 180), spacing=30)
    
    # 本番の文字（少し薄い墨色にすると馴染みます）
    draw.multiline_text((width * 0.8, height * 0.1), 
                        vertical_text, font=font, fill=(40, 40, 40), spacing=30)

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

if st.button("作品を生成する"):
    result_img = generate_zen_image(display_text)
    st.image(result_img, use_container_width=True)
    
    buf = io.BytesIO()
    result_img.save(buf, format="PNG")
    st.download_button("高解像度PNGを保存", buf.getvalue(), "zen_artwork.png", "image/png")
