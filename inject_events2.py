import re

with open('doc_with_links.txt', 'r', encoding='utf-8') as f:
    text = f.read()

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
    
    lines = block_text.split('\n')
    if title in lines[0]:
        lines = lines[1:]
        
    blocks.append((title, lines))

def parse_link(line):
    match = re.search(r'\((https?://[^\)]+)\)$', line)
    if match:
        return match.group(1), line[:match.start()].strip()
    # also handle standalone url
    if line.startswith('http'):
        return line, "Tư liệu tham khảo"
    return None, line

events_html = {}
for title, lines in blocks:
    html = []
    in_list = False
    for line in lines:
        line = line.strip()
        if not line: continue
        if line.startswith('Video') or line.startswith('Báo chí'): continue
        
        url, text_part = parse_link(line)
        if url:
            if in_list:
                html.append('</ul>')
                in_list = False
            html.append(f'<div style="margin-top:20px; text-align:center;"><strong style="display:block; margin-bottom:10px;">{text_part}</strong><a href="{url}" target="_blank" style="display:inline-block; margin-top:8px; padding:10px 20px; background:#c0392b; color:#fff; text-decoration:none; border-radius:6px; font-weight:bold; font-size:15px; box-shadow:0 4px 6px rgba(0,0,0,0.3); transition:background 0.2s;">▶ Bấm vào đây để xem</a></div>')
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
    'Hội nghị Bộ Chính trị': '9/1954 – Hội nghị Bộ Chính trị',
    'Giải phóng Hà Nội': '10/10/1954 – Giải phóng Hà Nội',
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
            key = title_map.get(current_event_title)
            if key and events_html.get(key):
                long_c = events_html[key].replace('`', '\\`')
                
                # Check if this item ALREADY has a longContent property. If it does, we need to completely replace it.
                # Since new_lines accumulated it, let's pop until we remove `longContent: \`...\``
                # In my previous code I just popped 2 lines, but longContent can be multiple lines!
                
                # REWRITE: instead of popping from new_lines, let's look backwards.
                # Actually, if longContent is multiline, popping is hard.
                # So let's re-parse index.html using regex.
                pass
            current_event_title = None
    i += 1

# Doing Regex replacement on the entire file content is much safer for replacing multiline `longContent`
with open(r'd:\FPT\VNR\spst\index.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

new_html = html_content
for html_title, key in title_map.items():
    if key not in events_html: continue
    long_content = events_html[key].replace('`', '\\\\`')
    
    # We find the object starting with title: 'html_title'
    # And replace its longContent if it exists, or append it
    
    pattern = r"(title:\s*['\"]" + re.escape(html_title) + r"['\"].*?)(?:,\s*longContent:\s*`.*?`)?(\s*\})"
    
    def replacer(match):
        return match.group(1) + f",\n          longContent: `{long_content}`" + match.group(2)
        
    new_html = re.sub(pattern, replacer, new_html, flags=re.DOTALL)

with open(r'd:\FPT\VNR\spst\index.html', 'w', encoding='utf-8') as f:
    f.write(new_html)

print("Injection complete!")
