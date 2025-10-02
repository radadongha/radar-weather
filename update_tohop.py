import os
import numpy as np
from PIL import Image
import json
import subprocess
from datetime import datetime
import glob

# tìm file radar mới nhất trong thư mục
def get_latest_file(folder):
    files = glob.glob(os.path.join(folder, "*.png"))
    if not files:
        return None
    return max(files, key=os.path.getmtime)

# danh sách thư mục radar cần ghép
radar_folders = ["rada_dongha", "rada_tamky"]

radar_images = []
for folder in radar_folders:
    latest = get_latest_file(folder)
    if latest:
        radar_images.append(latest)
    else:
        print(f"⚠️ Không tìm thấy ảnh trong {folder}")

output_composite = "composite.png"
color_map_file = "color_to_dbz.json"
repo_path = "C:/Users/kttv/Desktop/radar-weather"

# ====== Load bảng màu dBZ ======
with open(color_map_file, "r", encoding="utf-8-sig") as f:
    color_to_dbz = json.load(f)

# Màu -> dBZ
def color_to_value(rgb):
    return color_to_dbz.get(str(tuple(rgb[:3])), np.nan)

# dBZ -> Màu
dbz_to_color = {v: eval(k) for k, v in color_to_dbz.items()}
def value_to_color(dbz):
    if np.isnan(dbz):
        return (0, 0, 0, 0)  # trong suốt
    return dbz_to_color.get(int(dbz), (0, 0, 0)) + (255,)

# ====== Đọc & chuyển ảnh radar ======
dbz_arrays = []
for img_path in radar_images:
    if not os.path.exists(img_path):
        print(f"⚠️ Không tìm thấy {img_path}, bỏ qua.")
        continue
    img = np.array(Image.open(img_path).convert("RGB"))
    dbz = np.array([[color_to_value(px) for px in row] for row in img])
    dbz_arrays.append(dbz)

if not dbz_arrays:
    raise FileNotFoundError("❌ Không có ảnh radar nào để tổ hợp.")

# ====== Chuẩn hóa kích thước ======
h = max(arr.shape[0] for arr in dbz_arrays)
w = max(arr.shape[1] for arr in dbz_arrays)

def pad_to_size(arr, h, w):
    out = np.full((h, w), np.nan)
    out[:arr.shape[0], :arr.shape[1]] = arr
    return out

dbz_arrays = [pad_to_size(arr, h, w) for arr in dbz_arrays]

# ====== Tổ hợp: lấy max dBZ ======
dbz_composite = np.nanmax(dbz_arrays, axis=0)

# ====== Xuất ảnh composite ======
img_composite = np.zeros((h, w, 4), dtype=np.uint8)
for i in range(h):
    for j in range(w):
        img_composite[i, j] = value_to_color(dbz_composite[i, j])

Image.fromarray(img_composite, mode="RGBA").save(os.path.join(repo_path, output_composite))
print(f"✅ Đã tạo {output_composite}")

# ====== Tạo index.html ======
html_content = f"""
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Ảnh Composite Radar</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            text-align: center;
            background: #111;
            color: white;
        }}
        img {{
            max-width: 90%;
            height: auto;
            margin-top: 20px;
            border: 2px solid white;
        }}
    </style>
</head>
<body>
    <h2>🛰️ Ảnh Composite Radar (Đông Hà + Tam Kỳ)</h2>
    <p>Cập nhật: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}</p>
    <img src="{output_composite}?v={datetime.now().timestamp()}" alt="Radar Composite">
</body>
</html>
"""

with open(os.path.join(repo_path, "index.html"), "w", encoding="utf-8") as f:
    f.write(html_content)

print("✅ Đã tạo index.html")

# ====== Commit & Push lên GitHub ======
os.chdir(repo_path)
try:
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "🛰️ Cập nhật ảnh composite radar"], check=True)
    subprocess.run(["git", "push"], check=True)
    print("🚀 Đã cập nhật website trên GitHub Pages")
except subprocess.CalledProcessError as e:
    print(f"❌ Lỗi Git: {e}")
