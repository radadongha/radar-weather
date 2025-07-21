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

# Ghi file timestamp.txt chứa thời gian cập nhật
with open(os.path.join(dest_dir, 'timestamp.txt'), 'w', encoding='utf-8') as f:
    f.write(datetime.now().strftime('%d/%m/%Y %H:%M'))

# Tạo index.html hiển thị radar loop và thời gian cập nhật
with open(html_file, "w", encoding="utf-8") as f:
    f.write(f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Ảnh Radar Thời Tiết Mới Nhất</title>
    <meta http-equiv="refresh" content="300">
    <style>
        body {{
            background-color: black;
            color: white;
            text-align: center;
            font-family: Arial, sans-serif;
        }}
        img {{
            max-width: 90vw;
            height: auto;
            margin-top: 20px;
        }}
        #last-updated {{
            margin-top: 10px;
            font-size: 1.2em;
            color: #cccccc;
        }}
    </style>
</head>
<body>
    <h2>Ảnh Radar - Tự động cập nhật</h2>
    <img id="radar" src="rada/{latest_images[0]}" alt="Radar" />
    <p id="last-updated">🕒 Cập nhật: đang tải...</p>

    <script>
        const images = [{', '.join(f'"rada/{img}"' for img in reversed(latest_images))}];
        let i = 0;
        setInterval(() => {{
            document.getElementById("radar").src = images[i % images.length];
            i++;
        }}, 1000);

        fetch("rada/timestamp.txt")
            .then(response => response.text())
            .then(data => {{
                document.getElementById("last-updated").textContent = '🕒 Cập nhật: ' + data.trim();
            }})
            .catch(err => {{
                document.getElementById("last-updated").textContent = '🕒 Không thể tải thời gian cập nhật';
            }});
    </script>
</body>
</html>
""")
print("✅ Đã tạo index.html với hiển thị thời gian cập nhật")

# Git add, commit, push
subprocess.run(["git", "add", "."])
subprocess.run(["git", "commit", "-m", f"Cập nhật {latest_images[0]}"])
push_result = subprocess.run(["git", "push"], capture_output=True, text=True)

if push_result.returncode == 0:
    print("🚀 Đã đẩy lên GitHub thành công.")
else:
    print("❌ Lỗi khi đẩy lên GitHub:")
    print(push_result.stderr)
