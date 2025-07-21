import os
import shutil
import subprocess
import time
from datetime import datetime

source_dir = "D:/WinSCP/RADA"
dest_dir = "docs/rada"
html_file = "docs/index.html"

# Tạo thư mục nếu chưa có
os.makedirs(dest_dir, exist_ok=True)

# Lấy 3 ảnh radar mới nhất
all_images = sorted([f for f in os.listdir(source_dir) if f.endswith(".jpg")], reverse=True)
latest_images = all_images[:3]

# Sao chép ảnh vào docs/rada
for img in latest_images:
    shutil.copy2(os.path.join(source_dir, img), os.path.join(dest_dir, img))
    print(f"✅ Sao chép: {img}")

# Xoá ảnh cũ hơn 1 ngày
now = time.time()
for f in os.listdir(dest_dir):
    fp = os.path.join(dest_dir, f)
    if f.endswith(".jpg") and os.path.isfile(fp):
        if now - os.path.getmtime(fp) > 86400:
            os.remove(fp)
            print(f"🗑️ Xoá: {f}")

# Tạo timestamp.txt
with open(os.path.join(dest_dir, "timestamp.txt"), "w", encoding="utf-8") as f:
    f.write(datetime.now().strftime("%d/%m/%Y %H:%M"))

# Tạo lại index.html với ảnh mới và timestamp
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
</html>""")

print("✅ Đã tạo index.html hoàn chỉnh!")

# Git push
subprocess.run(["git", "add", "."])
subprocess.run(["git", "commit", "-m", "Cập nhật radar"])
subprocess.run(["git", "push"])
