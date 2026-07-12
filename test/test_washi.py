import numpy as np
from PIL import Image, ImageFilter, ImageDraw
import streamlit as st
import random

def generate_pure_washi(width=2000, height=2800):
    print("--- [心の実験・完全体] 樹皮繊維入りの和紙を錬成中 ---")
    
    # ① ベースの色（ほんのり温かみのある生成色）
    base_color = (245, 243, 236)
    img_array = np.zeros((height, width, 3), dtype=np.uint8)
    img_array[:, :] = base_color

    # ② 白黒の粗い陰影（紙のベースとなる細かな凹凸感）
    scale = 8
    small_h = height // scale
    small_w = width // scale
    low_res_noise = np.random.randint(-10, 11, (small_h, small_w))
    
    noise_img = Image.fromarray(np.uint8(low_res_noise + 128), mode='L')
    noise_img = noise_img.resize((width, height), Image.Resampling.BILINEAR)
    
    mono_noise = np.array(noise_img).astype(np.int16) - 128
    large_noise = np.stack([mono_noise, mono_noise, mono_noise], axis=-1)
    
    washi_array = np.clip(img_array.astype(np.int16) + large_noise, 0, 255).astype(np.uint8)
    washi_image = Image.fromarray(washi_array)

    # ③ 和紙に散らばる「茶色い植物の繊維」をプログラムで描く
    draw = ImageDraw.Draw(washi_image)
    
    # 繊維の数を60本に制限して上品な余白を作ります
    num_fibers = 60
    
    for _ in range(num_fibers):
        # ランダムな開始位置（X, Y座標）
        x1 = random.randint(0, width)
        y1 = random.randint(0, height)
        
        # 繊維の長さと角度（少し曲がったり細長くなったりするようランダム計算）
        length = random.randint(15, 45)
        angle = random.uniform(0, 2 * np.pi)
        
        # 終了位置の計算
        x2 = int(x1 + length * np.cos(angle))
        y2 = int(y1 + length * np.sin(angle))
        
        # 🌟【チューニング】数値を全体的に引き上げ、繊維の色を「うすい淡い茶色」に調整
        fiber_color = (
            random.randint(170, 200),  # R（赤み）
            random.randint(160, 190),  # G（緑み）
            random.randint(140, 165)   # B（青み）
        )
        
        # 繊維の太さ（2〜4ピクセルでランダムに変えて自然さを出す）
        thickness = random.randint(2, 4)
        
        # キャンバスに繊維を描き込む
        draw.line([(x1, y1), (x2, y2)], fill=fiber_color, width=thickness)

    # ④ 最後に全体をほんの少しぼかして、繊維を紙の奥に馴染ませます
    washi_image = washi_image.filter(ImageFilter.GaussianBlur(radius=1.5))
    
    return washi_image

# --- Streamlitの表示パート ---
st.title("🖌️ 【心の実験】樹皮繊維入り・極上手漉き和紙")
st.write("繊維の色を極限まで淡く調整。紙の奥に繊維が漉き込まれたような静けさを表現しました。")

if st.button("新しい和紙を錬成する"):
    with st.spinner("数式と繊維を計算中..."):
        washi = generate_pure_washi()
        st.image(washi, caption="プログラムが1から自動生成した手漉き和紙", use_container_width=True)
        st.success("🎉 錬成成功！繊維が理想の薄さになったか確かめてみてください。")
