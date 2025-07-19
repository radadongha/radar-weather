import os
import shutil
import subprocess
from datetime import datetime

# ==== 1. Đường dẫn ====
source_dir = "D:/WinSCP/RADA"
target_dir = "rada"  # Thư mục trong repo radar-weather

# ==== 2. Tạo thư mục đích nếu chưa có ====
os.makedirs(target_dir, exist_ok=True)

# ==== 3. Lấy ảnh radar mới nhất trong thư mục nguồn ====
images = sorted(
    [f for f in os.listdir(source_dir) if f.endswith(".jpg")],
    key=lambda x: os.path.getmtime(os.path.join(source_dir, x)),
    reverse=True
)

if not images:
    print("⚠️ Không tìm thấy ảnh radar trong thư mục nguồn.")
    exit()

latest_image = images[0]
src_path = os.path.join(source_dir, latest_image)
dst_path = os.path.join(target_dir, latest_image)

# ==== 4. Sao chép ảnh ====
shutil.copy2(src_path, dst_path)
print(f"✅ Đã sao chép ảnh: {latest_image} vào thư mục rada/")

# ==== 5. Cập nhật index.html nếu cần ====
with open("index.html", "w", encoding="utf-8") as f:
    f.write(f"""
    <html>
        <head><title>Ảnh Radar Thời Tiết Mới Nhất</title></head>
        <body style="text-align:center">
            <h2>Radar</h2>
            <img src="rada/{latest_image}" width="640">
        </body>
    </html>
    """)
print("✅ Đã cập nhật index.html")

# ==== 6. Commit và Push lên GitHub ====
subprocess.run(["git", "add", "."])
subprocess.run(["git", "commit", "-m", f"Cập nhật ảnh radar: {latest_image}"])
subprocess.run(["git", "push"])
print("🚀 Đã đẩy lên GitHub thành công.")
