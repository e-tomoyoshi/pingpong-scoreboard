import io
import os
from huggingface_hub import InferenceClient
from PIL import Image

# 🌟 余計な日本語を一切入れず、あなたの「hf_...」だけをピタッと貼り付けてください
HF_TOKEN = ""

def paint_suibokuga(subject="dragon"):
    print(f"--- [画像専用AI職人] 『{subject}』をAIで描いています ---")
    
    try:
        # 画像専用のAIクライアントを起動
        client = InferenceClient(
            model="black-forest-labs/FLUX.1-schnell", 
            token=HF_TOKEN
        )
        
        prompt = (
            f"Traditional Japanese sumi-e style ink painting of a powerful {subject}. "
            f"Dynamic black and white brush strokes, completely isolated on a pure white background. no text."
        )
        
        # AIから本物の画像（PNG）を直接ダウンロード
        image_bytes = client.text_to_image(prompt)
        suibokuga_img = Image.open(io.BytesIO(image_bytes))
        return suibokuga_img

    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return None

if __name__ == "__main__":
    img = paint_suibokuga("dragon")
    if img:
        img.save("test_dragon_real.png")
        print("\n🎉 大成功！フォルダに本物のAI水墨画【test_dragon_real.png】を保存しました！")
