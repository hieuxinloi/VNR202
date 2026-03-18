import re
import json
import os
import zipfile
import xml.etree.ElementTree as ET

def get_text_from_docx(file_path):
    try:
        import docx
        doc = docx.Document(file_path)
        return '\n'.join(p.text for p in doc.paragraphs)
    except Exception as e:
        with zipfile.ZipFile(file_path) as zf:
            xml_content = zf.read('word/document.xml')
        tree = ET.fromstring(xml_content)
        return ''.join(node.text for node in tree.iter() if node.text)

text = get_text_from_docx('doc.docx')

events_titles = [
    "21/7/1954 – Hiệp định Giơnevơ",
    "9/1954 – Hội nghị Bộ Chính trị",
    "10/10/1954 – Giải phóng Hà Nội",
    "16/5/1955 – Pháp rút quân hoàn toàn khỏi miền Bắc",
    "1955–1956 - Cải cách ruộng đất ở miền Bắc",
    "1956 – Hội nghị Trung ương 10",
    "Năm 1957 Hoàn thành cơ bản khôi phục kinh tế",
    "1958–1960 - Cải tạo xã hội chủ nghĩa",
    "Năm 1959 - Nghị quyết 15 (Trung ương)",
    "17/1/1960 – Phong trào Đồng Khởi (Bến Tre)",
    "20/12/1960 – Thành lập Mặt trận Dân tộc Giải phóng miền Nam",
    "9/1960 – Đại hội Đảng lần III",
    "Năm 1961 - Mỹ thực hiện chiến lược “Chiến tranh đặc biệt”",
    "Năm 1962 - Mỹ đẩy mạnh Ấp chiến lược",
    "2/1/1963 – Chiến thắng Ấp Bắc",
    "Năm 1964 - Chiến thắng Bình Giã",
    "Năm 1965 Các chiến thắng lớn: Ba Gia (1965), Đồng Xoài (1965)"
]

blocks = []
current_block = []
current_title = events_titles[0]
title_idx = 1

for line in text.split('\n'):
    if title_idx < len(events_titles) and events_titles[title_idx] in line:
        blocks.append((current_title, current_block))
        current_title = events_titles[title_idx]
        title_idx += 1
        current_block = []
    else:
        current_block.append(line)
blocks.append((current_title, current_block))

events_html = {}

for title, lines in blocks:
    html = []
    in_list = False
    for line in lines:
        line = line.strip()
        if not line: continue
        if line.startswith('Video') or line.startswith('Báo chí'): continue
        if line.startswith('http'):
            html.append(f'<div style="margin-top:20px; text-align:center;"><a href="{line}" target="_blank" style="display:inline-block; margin-top:8px; padding:10px 20px; background:#c0392b; color:#fff; text-decoration:none; border-radius:6px; font-weight:bold; font-size:15px; box-shadow:0 4px 6px rgba(0,0,0,0.3); transition:background 0.2s;">▶ Bấm vào đây để xem Tư liệu</a></div>')
            continue
        
        if re.match(r'^\d+\.', line):
            if in_list:
                html.append('</ul>')
                in_list = False
            html.append(f'<h4>{line}</h4>')
        else:
            if ':' in line and len(line.split(':')[0]) < 50:
                if not in_list:
                    html.append('<ul>')
                    in_list = True
                parts = line.split(':', 1)
                html.append(f'<li><strong>{parts[0].strip("* -")}:</strong>{parts[1]}</li>')
            else:
                if in_list:
                    html.append('</ul>')
                    in_list = False
                html.append(f'<p>{line}</p>')
    if in_list:
        html.append('</ul>')
    events_html[title] = '\n'.join(html)

with open('events_parsed.json', 'w', encoding='utf-8') as f:
    json.dump(events_html, f, ensure_ascii=False, indent=2)
print("Finished parsing and generating events_parsed.json")
