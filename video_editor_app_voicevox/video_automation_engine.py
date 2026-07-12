import os
import requests
import json
from moviepy import ImageClip, AudioFileClip, concatenate_videoclips, TextClip, CompositeVideoClip
from moviepy.audio.AudioClip import CompositeAudioClip

def split_text_into_single_lines(text, length=16):
    lines = []
    for chunk in text.split("\n"):
        chunk = chunk.strip()
        if not chunk: continue
        while len(chunk) > length:
            lines.append(chunk[:length])
            chunk = chunk[length:]
        if chunk: lines.append(chunk)
    return lines

def analyze_slides_with_ai(doc, total_pages, api_key, progress_callback):
    ai_subtitles = {}
    ai_voices = {}
    for i in range(total_pages):
        ai_subtitles[i] = ""
        ai_voices[i] = ""
        progress_callback((i + 1) / total_pages)
    return ai_subtitles, ai_voices

def generate_video_file(doc, total_pages, subtitles_dict, voices_dict, progress_bar_callback):
    video_parts = []
    base_url = "http://localhost:50021"
    speaker_id = 2  
    output_name = "perfect_studio_movie.mp4"
    
    for i in range(total_pages):
        sub_text = subtitles_dict.get(i, "").strip()
        voice_text = voices_dict.get(i, "").strip()
        
        if not sub_text and not voice_text: continue
            
        page = doc[i]
        img_path = f"temp_page_{i}.png"
        pix = page.get_pixmap()
        pix.save(img_path)
        
        res1 = requests.post(f"{base_url}/audio_query", params={"text": voice_text, "speaker": speaker_id})
        query_data = res1.json()
        res2 = requests.post(f"{base_url}/synthesis", params={"speaker": speaker_id}, data=json.dumps(query_data))
        audio_path = f"temp_voice_{i}.wav"
        with open(audio_path, "wb") as f: f.write(res2.content)
            
        # 🔊 音声の読み込みと「プロのタイムラグ」の計算
        audio_clip = AudioFileClip(audio_path)
        
        # 🌟 講師の技①：音声のスタート位置をあえて「0.8秒後ろ」にズラす
        delayed_audio = audio_clip.with_start(0.8)
        
        # 🌟 講師の技②：スライド全体の長さを「前後の余白」を含めた時間に引き伸ばす
        # ページ全体の表示時間 ＝【最初の余白 0.8秒】＋【本来の音声の長さ】＋【話し終わりの余白 1.0秒】
        page_duration = 0.8 + audio_clip.duration + 1.0
        
        # スライド画像の表示時間を設定（全体の長さに合わせる）
        img_clip = ImageClip(img_path).with_duration(page_duration)
        
        single_lines = split_text_into_single_lines(sub_text, 16)
        line_count = len(single_lines)
        if line_count == 0:
            line_count = 1
            single_lines = [""]
            
        # 🌟 字幕（テロップ）が表示される長さは、無音の余白を含まない「音声が鳴っている間だけ（audio_clip.duration）」にする設計
        duration_per_line = audio_clip.duration / line_count
        
        txt_clips = []
        for g_idx, line_chunk in enumerate(single_lines):
            # 🌟 字幕の開始位置も、最初の余白「0.8秒」を足すことで、音声が喋り始めるタイミングと寸分狂わずシンクロさせます
            start_time = 0.8 + (g_idx * duration_per_line)
            
            clip_w = int(img_clip.w)
            clip_h = int(img_clip.h)
            
            t_clip = TextClip(
                font="/System/Library/Fonts/ヒラギノ角ゴシック W4.ttc",
                text=line_chunk,
                font_size=24,                  
                color='white',
                stroke_color='black',
                stroke_width=2,                
                size=(clip_w - 100, 40),       
                method='caption'
            ).with_start(start_time).with_duration(duration_per_line).with_position(('center', clip_h - 90)) 
            
            txt_clips.append(t_clip)
        
        # ズラした音声と余白をガッチャンコして合成
        final_audio = CompositeAudioClip([delayed_audio]).with_duration(page_duration)
        page_video = CompositeVideoClip([img_clip] + txt_clips).with_audio(final_audio)
        
        video_parts.append(page_video)
        progress_bar_callback((i + 1) / total_pages)
    
    if video_parts:
        final_video = concatenate_videoclips(video_parts)
        final_video.write_videofile(output_name, fps=24, codec="libx264")
        for i in range(total_pages):
            if os.path.exists(f"temp_page_{i}.png"): os.remove(f"temp_page_{i}.png")
            if os.path.exists(f"temp_voice_{i}.wav"): os.remove(f"temp_voice_{i}.wav")
        return output_name
    else:
        return None
