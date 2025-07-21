# -*- coding: utf-8 -*-
import os
import glob
import shutil
import subprocess
from datetime import datetime, timedelta
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8', errors='ignore')

# Đường dẫn
SOURCE_FOLDER = r"D:/WinSCP/RADA"
DEST_FOLDER = "rada"
HTML_PATH = "index.html"
MAX_IMAGES = 5

# 1. Lấy ảnh radar mới nhất
image_files = sorted(glob.glob(os.path.join(SOURCE_FOLDER, "*.jpg")), key=os.path.getmtime, reverse=True)
if not image_files:
    print("❌ Không tìm thấy ảnh radar trong thư mục.")
    sys.exit(1)

latest_image_path = image_files[0]
filename = os.path.basename(latest_image_path)
dest_path = os.path.join(DEST_FOLDER, filename)

# 2. Copy nếu ảnh mới chưa có
if not os.path.exists(dest_path):
    shutil.copy2(latest_image_path, dest_path)
    print(f"✅ Đã sao chép ảnh mới: {filename}")
else:
    print(f"ℹ️ Ảnh mới đã tồn tại: {filename}")

# 3. Xóa ảnh cũ hơn 1 ngày
now = datetime.now()
for f in glob.glob(os.path.join(DEST_FOLDER, "*.jpg")):
    t = os.path.getmtime(f)
    if now - datetime.fromtimestamp(t) > timedelta(days=1):
        os.remove(f)
        print(f"🗑️ Đã xóa ảnh cũ: {os.path.basename(f)}")

# 4. Cập nhật index.html
image_list = sorted(glob.glob(os.path.join(DEST_FOLDER, "*.jpg")), reverse=True)[:MAX_IMAGES]
image_list = sorted(image_list)  # để loop đúng thứ tự thời gian

images_html = ""
for img_path in image_list:
    img_name = os.path.basename(img_path)
    images_html += f'<img src="{DEST_FOLDER}/{img_name}" style="display:none;">\n'

# Lấy giờ từ tên file
time_str = ""
try:
    parts = filename.split(".")[0].split("_")[-1]  # ví dụ: dong-ha-mon202507211730
    dt = datetime.strptime(parts[-12:], "%Y%m%d%H%M")
    time_str = dt.strftime("%Y-%m-%d %H:%M")
except:
    time_str = "Không rõ"

with open(HTML_PATH, "r", encoding="utf-8") as f:
    html = f.read()

start_marker = "<!-- IMAGE LOOP START -->"
end_marker = "<!-- IMAGE LOOP END -->"

before = html.split(start_marker)[0]
after = html.split(end_marker)[1]

new_html = f"""{before}{start_marker}
<div id="radar">
{images_html}
</div>
<p>🕒 Giờ radar: {time_str}</p>
{end_marker}{after}"""

with open(HTML_PATH, "w", encoding="utf-8") as f:
    f.write(new_html)

print("✅ Đã cập nhật danh sách ảnh vào index.html")

# 5. Đẩy lên GitHub
try:
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "🛰️ Cập nhật ảnh radar tự động"], check=True)
    subprocess.run(["git", "push"], check=True)
    print("✅ Đã đẩy lên GitHub thành công.")
except subprocess.CalledProcessError as e:
    print("❌ Lỗi Git:", e)
