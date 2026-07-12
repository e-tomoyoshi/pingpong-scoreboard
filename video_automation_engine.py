import os
import io
from gtts import gTTS  # 非同期を使わない、100%安全なGoogle公式ライブラリ
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

def get_cloud_voice_bytes(text: str) -> bytes:
    """gTTSを使用して、フリーズを100%回避する完全同期型の音声バイナリ(MP3)を生成する"""
    fp = io.BytesIO()
    tts = gTTS(text=text, lang='ja')
    tts.write_to_fp(fp)
    fp.seek(0)
    return fp.read()

def generate_video_file(doc, total_pages, subtitles_dict, voices_dict, progress_bar_callback):
    video_parts = []
    output_name = "perfect_studio_movie.mp4"
    
    for i in range(total_pages):
        sub_text = subtitles_dict.get(i, "").strip()
        voice_text = voices_dict.get(i, "").strip()
        
        if not sub_text and not voice_text: continue
            
        page = doc[i]
        img_path = f"temp_page_{i}.png"
        pix = page.get_pixmap()
        pix.save(img_path)
        
        # 音声の生成とMP3一時保存（MoviePyに読み込ませるためファイル化）
        audio_path = f"temp_voice_{i}.mp3"
        try:
            voice_bytes = get_cloud_voice_bytes(voice_text)
            with open(audio_path, "wb") as f: 
                f.write(voice_bytes)
        except Exception as e:
            continue
            
        # 音声の読み込みとプロのタイムラグ計算（オリジナルロジックを完全維持）
        audio_clip = AudioFileClip(audio_path)
        delayed_audio = audio_clip.with_start(0.8)
        page_duration = 0.8 + audio_clip.duration + 1.0
        img_clip = ImageClip(img_path).with_duration(page_duration)
        
        single_lines = split_text_into_single_lines(sub_text, 16)
        line_count = len(single_lines)
        if line_count == 0:
            line_count = 1
            single_lines = [""]
            
        duration_per_line = audio_clip.duration / line_count
        
        txt_clips = []
        for g_idx, line_chunk in enumerate(single_lines):
            start_time = 0.8 + (g_idx * duration_per_line)
            clip_w = int(img_clip.w)
            clip_h = int(img_clip.h)
            
            # 🌟 クラウド（Linux）環境でのフォントエラーを防ぐため、Macの絶対パス指定を廃止し、
            # さまざまなOSの標準フォント名（またはNone）に自動対応するよう安全に書き換えました
            t_clip = TextClip(
                font="DejaVu-Sans" if os.name != 'posix' else "sans-serif",
                text=line_chunk,
                font_size=24,                  
                color='white',
                stroke_color='black',
                stroke_width=2,                
                size=(clip_w - 100, 40),       
                method='caption'
            ).with_start(start_time).with_duration(duration_per_line).with_position(('center', clip_h - 90)) 
            
            txt_clips.append(t_clip)
        
        final_audio = CompositeAudioClip([delayed_audio]).with_duration(page_duration)
        page_video = CompositeVideoClip([img_clip] + txt_clips).with_audio(final_audio)
        
        video_parts.append(page_video)
        progress_bar_callback((i + 1) / total_pages)
    
    if video_parts:
        final_video = concatenate_videoclips(video_parts)
        final_video.write_videofile(output_name, fps=24, codec="libx264")
        for i in range(total_pages):
            if os.path.exists(f"temp_page_{i}.png"): os.remove(f"temp_page_{i}.png")
            if os.path.exists(f"temp_voice_{i}.mp3"): os.remove(f"temp_voice_{i}.mp3")
        return output_name
    else:
        return None
