# =====================================================================
# 📁 slide_pdf_exporter.py
# 【役割】A4縦の台本付きスライド資料（PDF）を錬成する専門の職人
# =====================================================================
import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont

# ReportLab内蔵の公式日本語ゴシック体を登録
pdfmetrics.registerFont(UnicodeCIDFont('HeiseiKakuGo-W5'))

def split_text_by_length(text, length=35):
    """指定文字数ごとに行を折り返す関数"""
    lines = []
    for line in text.split("\n"):
        while len(line) > length:
            lines.append(line[:length])
            line = line[length:]
        if line:
            lines.append(line)
    return lines

def generate_script_pdf(doc, total_pages, subtitles_dict):
    """台本付きスライド資料PDFを錬成してファイルとして保存する関数"""
    output_filename = "slide_script_note.pdf"
    a4_w, a4_h = A4
    c = canvas.Canvas(output_filename, pagesize=A4)
    
    for i in range(total_pages):
        page = doc[i]
        temp_img_path = f"kanpe_temp_{i}.png"
        
        # 🌟 クラウド環境（Linuxサーバー）でのグラフィックエラーを防ぐためのディフェンス設定
        # DPI（画質）を明示的に指定することで、サーバーの描画バグを未然に回避します
        pix = page.get_pixmap(dpi=150)
        pix.save(temp_img_path)
        
        # 上半分にスライド画像を配置 (左右マージン40)
        img_w = a4_w - 80 
        img_h = img_w * (pix.height / pix.width) 
        c.drawImage(temp_img_path, 40, a4_h - img_h - 40, width=img_w, height=img_h)
        
        # フォントを設定してページ情報を印字
        c.setFont('HeiseiKakuGo-W5', 14)
        c.drawString(50, a4_h - img_h - 75, f"Page: {i + 1} / {total_pages}")
        c.drawString(50, a4_h - img_h - 95, "----------------------------------------------------------------------------------------------------")
        
        # 字幕テキストの書き込み
        sub_text = subtitles_dict.get(i, "")
        text_obj = c.beginText(50, a4_h - img_h - 130)
        text_obj.setLeading(22) 
        
        if sub_text.strip():
            for line in sub_text.split("\n"):
                formatted_lines = split_text_by_length(line, 35)
                for fl in formatted_lines:
                    text_obj.textLine(fl)
        else:
            text_obj.textLine("(台本が未入力です)")
            
        c.drawText(text_obj)
        c.showPage()
        
        # 一時保存した画像を削除
        if os.path.exists(temp_img_path): 
            os.remove(temp_img_path)
        
    c.save()
    return output_filename
