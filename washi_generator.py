import numpy as np
from PIL import Image, ImageFilter, ImageDraw
import random

def generate_pure_washi(width=2000, height=2800):
    print("--- 樹皮繊維入りの和紙を自動生成中 ---")
    
    # ① ベースの色（生成色）
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

    # ③ 和紙に散らばる「茶色い植物の繊維」を描く
    draw = ImageDraw.Draw(washi_image)
    num_fibers = 60
    
    for _ in range(num_fibers):
        x1 = random.randint(0, width)
        y1 = random.randint(0, height)
        length = random.randint(15, 45)
        angle = random.uniform(0, 2 * np.pi)
        
        x2 = int(x1 + length * np.cos(angle))
        y2 = int(y1 + length * np.sin(angle))
        
        fiber_color = (
            random.randint(170, 200),
            random.randint(160, 190),
            random.randint(140, 165)
        )
        thickness = random.randint(2, 4)
        draw.line([(x1, y1), (x2, y2)], fill=fiber_color, width=thickness)

    # ④ 最後に全体をほんの少しぼかす
    washi_image = washi_image.filter(ImageFilter.GaussianBlur(radius=1.5))
    
    return washi_image
