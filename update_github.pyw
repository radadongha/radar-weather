import os
import shutil
import subprocess
from datetime import datetime

# --- Cấu hình ---
source_folder = r'D:/WinSCP/RADA'
repo_folder = r'C:/Users/kttv/Desktop/radar-weather'
target_subfolder = 'rada'
# --- Tìm ảnh mới nhất ---
jpg_files = [f for f in os.listdir(source_folder) if f.endswith('.jpg')]
jpg_files.sort(reverse=True)

if not jpg_files:
    print("❌ Không có ảnh .jpg nào.")
    exit()

latest_image = jpg_files[0]
source_path = os.path.join(source_folder, latest_image)
target_path = os.path.join(repo_folder, target_subfolder, latest_image)

# --- Tạo thư mục nếu chưa có ---
os.makedirs(os.path.dirname(target_path), exist_ok=True)

# --- Copy ảnh vào repo ---
shutil.copy2(source_path, target_path)
print(f"✅ Đã chép ảnh: {latest_image}")

# --- Cập nhật index.html ---
index_html_path = os.path.join(repo_folder, 'index.html')
timestamp = datetime.now().strftime('%H:%M:%S %d/%m/%Y')

html_content = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Radar Thời Tiết Đông Hà</title>
    <meta http-equiv="refresh" content="300">
    <style>
        body {{ text-align: center; font-family: Arial, sans-serif; background-color: #f7f7f7; padding: 50px; }}
        h1 {{ font-size: 2em; color: #111; }}
        img {{ max-width: 90%; height: auto; border: 3px solid #444; margin-top: 20px; }}
        .caption {{ margin-top: 10px; font-size: 1rem; color: #666; }}
    </style>
</head>
<body>
    <h1>Ảnh Radar Thời Tiết Mới Nhất</h1>
    <img src="{target_subfolder}/{latest_image}" alt="Radar thời tiết Đông Hà">
    <div class="caption">Cập nhật: {timestamp}</div>
</body>
</html>
"""

with open(index_html_path, 'w', encoding='utf-8') as f:
    f.write(html_content)
print("✅ Đã cập nhật index.html")

# --- Đẩy lên GitHub ---
os.chdir(repo_folder)

subprocess.run(['git', 'add', '.'])
subprocess.run(['git', 'commit', '-m', f'Cập nhật ảnh radar: {latest_image}'])
subprocess.run(['git', 'push'])
print("🚀 Đã đẩy lên GitHub thành công.")
