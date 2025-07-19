import os
import shutil
import time
import subprocess
from datetime import datetime, timedelta

# Cấu hình
source_dir = "D:/WinSCP/RADA"         # Thư mục chứa ảnh gốc radar
target_dir = "rada"                   # Thư mục trong repo Git chứa ảnh sẽ hiển thị trên web
max_age_days = 1                      # Số ngày giữ lại ảnh radar

# Tạo thư mục rada nếu chưa có
os.makedirs(target_dir, exist_ok=True)

# Lọc các file .jpg từ source_dir
jpg_files = sorted(
    [f for f in os.listdir(source_dir) if f.endswith(".jpg")],
    reverse=True
)

if not jpg_files:
    print("⚠️ Không tìm thấy ảnh radar trong thư mục nguồn.")
    exit(1)

# Lấy file mới nhất
latest_image = jpg_files[0]
source_image_path = os.path.join(source_dir, latest_image)
target_image_path = os.path.join(target_dir, latest_image)

# Sao chép ảnh mới nhất vào thư mục rada
shutil.copy2(source_image_path, target_image_path)
print(f"✅ Đã sao chép ảnh: {latest_image} vào thư mục rada/")

# Xóa ảnh cũ hơn 1 ngày trong thư mục rada
now = time.time()
deleted = 0
for f in os.listdir(target_dir):
    path = os.path.join(target_dir, f)
    if os.path.isfile(path):
        file_age = now - os.path.getmtime(path)
        if file_age > max_age_days * 86400:
            os.remove(path)
            deleted += 1
if deleted > 0:
    print(f"🗑️ Đã xóa {deleted} ảnh cũ hơn {max_age_days} ngày.")

# Tạo lại index.html
with open("index.html", "w", encoding="utf-8") as f:
    f.write(f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Ảnh Radar Thời Tiết Mới Nhất</title>
</head>
<body>
    <h2>Ảnh Radar Thời Tiết Mới Nhất</h2>
    <img src="rada/{latest_image}" width="640" height="640">
</body>
</html>
""")
print("✅ Đã cập nhật index.html")

# Git add, commit, push
try:
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", f"Cập nhật ảnh radar: {latest_image}"], check=True)
    subprocess.run(["git", "push"], check=True)
    print("🚀 Đã đẩy lên GitHub thành công.")
except subprocess.CalledProcessError:
    print("❌ Lỗi khi thực hiện Git push.")
