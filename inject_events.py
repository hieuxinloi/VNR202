import json
import re
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

import collections
title_indices = []
for title in events_titles:
    idx = text.find(title)
    if idx != -1:
        title_indices.append((idx, title))

title_indices.sort()
blocks = []
for i in range(len(title_indices)):
    start_idx = title_indices[i][0]
    end_idx = title_indices[i+1][0] if i + 1 < len(title_indices) else len(text)
    block_text = text[start_idx:end_idx].strip()
    title = title_indices[i][1]
    
    # split and skip title line
    lines = block_text.split('\n')
    if title in lines[0]:
        lines = lines[1:]
        
    blocks.append((title, lines))

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

title_map = {
    'Hiệp định Giơnevơ': '21/7/1954 – Hiệp định Giơnevơ',
    'Pháp rút quân khỏi miền Bắc': '16/5/1955 – Pháp rút quân hoàn toàn khỏi miền Bắc',
    'Cải cách ruộng đất': '1955–1956 - Cải cách ruộng đất ở miền Bắc',
    'Hội nghị Trung ương 10': '1956 – Hội nghị Trung ương 10',
    'Hoàn thành khôi phục kinh tế': 'Năm 1957 Hoàn thành cơ bản khôi phục kinh tế',
    'Cải tạo xã hội chủ nghĩa': '1958–1960 - Cải tạo xã hội chủ nghĩa',
    'Nghị quyết 15': 'Năm 1959 - Nghị quyết 15 (Trung ương)',
    'Mở đường Hồ Chí Minh': 'Năm 1959 - Nghị quyết 15 (Trung ương)', 
    'Phong trào Đồng Khởi – Bến Tre': '17/1/1960 – Phong trào Đồng Khởi (Bến Tre)',
    'Thành lập Mặt trận DTGPMNVN': '20/12/1960 – Thành lập Mặt trận Dân tộc Giải phóng miền Nam',
    'Đại hội Đảng lần thứ III': '9/1960 – Đại hội Đảng lần III',
    'Chiến lược "Chiến tranh đặc biệt"': 'Năm 1961 - Mỹ thực hiện chiến lược “Chiến tranh đặc biệt”',
    'Chiến tranh hóa học & Ấp chiến lược': 'Năm 1962 - Mỹ đẩy mạnh Ấp chiến lược',
    'Chiến thắng Ấp Bắc': '2/1/1963 – Chiến thắng Ấp Bắc',
    'Đảo chính lật đổ Ngô Đình Diệm': '', 
    'Chiến thắng Bình Giã': 'Năm 1964 - Chiến thắng Bình Giã',
    'Chiến thắng Ba Gia & Đồng Xoài': 'Năm 1965 Các chiến thắng lớn: Ba Gia (1965), Đồng Xoài (1965)'
}

with open(r'd:\FPT\VNR\spst\index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

in_events = False
current_event_title = None

new_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    new_lines.append(line)
    
    if 'const EVENTS = [' in line:
        in_events = True
    elif '];' in line and in_events:
        in_events = False
        
    if in_events:
        if "title: '" in line:
            title_part = line.split("title: '")[1].split("'")[0]
            current_event_title = title_part
            
        if '}' in line and current_event_title in title_map:
            if current_event_title not in ['Hội nghị Bộ Chính trị', 'Giải phóng Hà Nội']:
                key = title_map.get(current_event_title)
                if key and events_html.get(key):
                    long_c = events_html[key].replace('`', '\\`')
                    closing = new_lines.pop()
                    prev_line = new_lines.pop()
                    if not prev_line.strip().endswith(','):
                        prev_line = prev_line.rstrip() + ',\n'
                    new_lines.append(prev_line)
                    new_lines.append(f"          longContent: `{long_c}`\n")
                    new_lines.append(closing)
            current_event_title = None
    i += 1

with open(r'd:\FPT\VNR\spst\index.html', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
print("Injection complete!")
