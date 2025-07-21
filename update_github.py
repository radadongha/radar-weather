# update_github.py
# -*- coding: utf-8 -*-
import os
import shutil
import glob
import time
import subprocess
from datetime import datetime, timedelta

IMAGE_DIR = "rada"
HTML_PATH = "index.html"
MAX_IMAGES = 5  # số ảnh loop
GIT_COMMIT_MSG = "🛰️ Cập nhật ảnh radar tự động"

# Đảm bảo encoding khi in ra terminal
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='ignore')

# Xóa ảnh cũ hơn 1 ngày
now = time.time()
for f in glob.glob(os.path.join(IMAGE_DIR, "*.jpg")):
    if os.stat(f).st_mtime < now - 86400:
        os.remove(f)

# Tìm ảnh mới nhất
images = sorted(glob.glob(os.path.join(IMAGE_DIR, "*.jpg")))
if not images:
    print("❌ Không tìm thấy ảnh nào trong thư mục.")
    exit()

latest_image = images[-1]
timestamp = os.path.basename(latest_image).split(".")[0]
# Tên ảnh giả sử: 202507211730.jpg

# Tạo nội dung HTML mới
image_tags = ""
for img in images[-MAX_IMAGES:]:
    image_tags += f'<img src="{img}" style="display:none;" />\n'

html_content = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Ảnh Radar</title>
    <style>
        body {{ margin: 0; background: black; color: white; text-align: center; }}
        img {{ max-width: 90vw; max-height: 90vh; }}
        #time {{ margin-top: 10px; font-size: 18px; }}
    </style>
</head>
<body>
    <h2>Ảnh Radar Thời Tiết</h2>
    <div id="time">Giờ radar: {timestamp[:4]}-{timestamp[4:6]}-{timestamp[6:8]} {timestamp[8:10]}:{timestamp[10:]}</div>
    <img id="radar" src="{images[-1]}" />
    <script>
        const images = [{', '.join(f'"{os.path.basename(i)}"' for i in images[-MAX_IMAGES:])}];
        let i = 0;
        setInterval(() => {{
            i = (i + 1) % images.length;
            document.getElementById("radar").src = "{IMAGE_DIR}/" + images[i];
        }}, 1000);
    </script>
</body>
</html>"""

# Ghi vào file index.html
with open(HTML_PATH, "w", encoding="utf-8") as f:
    f.write(html_content)

print("✅ Đã cập nhật danh sách ảnh vào index.html")

# Push Git
try:
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", GIT_COMMIT_MSG], check=True)
    subprocess.run(["git", "push"], check=True)
    print("✅ Đã đẩy lên GitHub thành công.")
except subprocess.CalledProcessError as e:
    print("❌ Lỗi Git:", e)
