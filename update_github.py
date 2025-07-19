import os
import shutil
import subprocess
import time
from datetime import datetime, timedelta

# Cấu hình thư mục
source_dir = "D:/WinSCP/RADA"
dest_dir = "rada"
html_file = "index.html"

# Tạo thư mục rada nếu chưa có
if not os.path.exists(dest_dir):
    os.makedirs(dest_dir)

# Lấy danh sách ảnh radar mới nhất
all_images = sorted(
    [f for f in os.listdir(source_dir) if f.endswith(".jpg")],
    reverse=True
)
latest_images = all_images[:3]  # 3 ảnh mới nhất

# Sao chép ảnh mới sang rada/
for img in latest_images:
    src = os.path.join(source_dir, img)
    dst = os.path.join(dest_dir, img)
    shutil.copy2(src, dst)
    print(f"✅ Đã sao chép ảnh: {img} vào thư mục rada/")

# Xóa ảnh trong rada/ cũ hơn 1 ngày
now = time.time()
deleted = 0
for f in os.listdir(dest_dir):
    file_path = os.path.join(dest_dir, f)
    if f.endswith(".jpg") and os.path.isfile(file_path):
        if now - os.path.getmtime(file_path) > 86400:
            os.remove(file_path)
            deleted += 1
print(f"🗑️ Đã xóa {deleted} ảnh cũ hơn 1 ngày trong rada/")

# Tạo file index.html hiển thị ảnh dạng loop
with open(html_file, "w", encoding="utf-8") as f:
    f.write(f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Ảnh Radar Thời Tiết Mới Nhất</title>
    <meta http-equiv="refresh" content="300">
    <style>
        body {{ text-align: center; background: #000; color: #fff; }}
        img {{ max-width: 90vw; max-height: 90vh; }}
    </style>
</head>
<body>
    <h2>Ảnh Radar - Tự động cập nhật</h2>
    <img id="radar" src="rada/{latest_images[0]}" alt="Radar" />
    <script>
        const images = [{', '.join(f'"rada/{img}"' for img in reversed(latest_images))}];
        let i = 0;
        setInterval(() => {{
            document.getElementById("radar").src = images[i % images.length];
            i++;
        }}, 1000);
    </script>
</body>
</html>
""")
print("✅ Đã cập nhật index.html")

# Git add, commit, push
subprocess.run(["git", "add", "."])
subprocess.run(["git", "commit", "-m", f"Cập nhật {latest_images[0]}"])
push_result = subprocess.run(["git", "push"], capture_output=True, text=True)

if push_result.returncode == 0:
    print("🚀 Đã đẩy lên GitHub thành công.")
else:
    print("❌ Lỗi khi đẩy lên GitHub:")
    print(push_result.stderr)
