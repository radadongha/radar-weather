import os
import shutil
import glob
import datetime
import subprocess
from PIL import Image

SOURCE_DIR = "D:/WinSCP/RADA"
TARGET_DIR = "rada"
HTML_FILE = "index.html"
COLORBAR_PATH = "colorbar.png"
NUM_IMAGES = 5

def extract_datetime(filename):
    name = os.path.basename(filename)
    try:
        y = int(name[11:13]) + 2000
        m = int(name[13:15])
        d = int(name[15:17])
        h = int(name[17:19])
        mi = int(name[19:21])
        return datetime.datetime(y, m, d, h, mi)
    except:
        return None

def append_colorbar(radar_path, colorbar_img, output_path):
        radar_img = Image.open(radar_path).convert("RGBA")
    radar_width, radar_height = radar_img.size

    # Resize thang màu theo 1/3 chiều cao và chiều rộng
    cb_width, cb_height = colorbar_img.size
    new_cb_height = int(radar_height / 3)
    new_cb_width = int(cb_width * (new_cb_height / cb_height))
    resized_cb = colorbar_img.resize((new_cb_width, new_cb_height), Image.Resampling.LANCZOS)

    # Ghép ảnh: ảnh mới cao bằng radar, rộng hơn 1 chút để thêm thang màu
    combined = Image.new("RGBA", (radar_width + new_cb_width, radar_height), (0, 0, 0, 0))
    combined.paste(radar_img, (0, 0))

    # Căn giữa theo chiều cao
    y_offset = (radar_height - new_cb_height) // 2
    combined.paste(resized_cb, (radar_width, y_offset), resized_cb)

    combined.save(output_path)


# Tạo thư mục rada nếu chưa có
os.makedirs(TARGET_DIR, exist_ok=True)

# Kiểm tra thang màu
if not os.path.exists(COLORBAR_PATH):
    print(f"❌ Không tìm thấy ảnh thang màu: {COLORBAR_PATH}")
    exit(1)

colorbar_img = Image.open(COLORBAR_PATH).convert("RGBA")

# Lấy các file radar ảnh .jpg
all_images = sorted(glob.glob(os.path.join(SOURCE_DIR, "*.jpg")), reverse=True)
selected_images = all_images[:NUM_IMAGES]

# Xóa ảnh cũ trong rada/
for f in glob.glob(os.path.join(TARGET_DIR, "*.png")):
    os.remove(f)

# Copy ảnh vào thư mục rada, xử lý ghép thang màu
image_infos = []
for src in reversed(selected_images):  # đảo lại thứ tự cũ -> mới
    base_name = os.path.splitext(os.path.basename(src))[0]
    dst_png = os.path.join(TARGET_DIR, base_name + ".png")

    # Ghép thang màu và lưu
    append_colorbar(src, colorbar_img, dst_png)
    dt = extract_datetime(src)
    if dt:
        image_infos.append((os.path.basename(dst_png), dt.strftime("%d/%m/%Y %H:%M")))

# Tạo file index.html
html = """<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<title>Radar Thời Tiết</title>
<meta http-equiv="refresh" content="600">
<style>
    body {
        font-family: Arial, sans-serif;
        text-align: center;
        background-color: #000;
        color: #fff;
        margin: 0;
        padding: 0;
    }

    .image-container {
        position: relative;
        display: inline-block;
        max-width: 95vw;
        max-height: 95vh;
    }

    .timestamp {
        position: absolute;
        top: 10px;
        left: 50%;
        transform: translateX(-50%);
        background-color: rgba(0,0,0,0.7);
        padding: 4px 12px;
        border-radius: 10px;
        font-size: 18px;
        z-index: 10;
    }

    img {
        max-width: 90vw;
        max-height: 90vh;
    }

    .controls {
        margin: 10px;
        font-size: 24px;
    }

    button {
        font-size: 20px;
        padding: 6px 10px;
        margin: 0 5px;
        border-radius: 8px;
        border: none;
        background-color: #333;
        color: white;
        cursor: pointer;
    }

    button:hover {
        background-color: #555;
    }
</style>
</head>
<body>
<h2>🛰️ Ảnh Radar Thời Tiết</h2>

<div class="controls">
    <button onclick="prevImage()">⏮️</button>
    <button onclick="togglePlay()">⏯️</button>
    <button onclick="nextImage()">⏭️</button>
    <button onclick="openFullscreen()">🖥️</button>
</div>

<div class="image-container">
    <div class="timestamp" id="timestamp"></div>
    <img id="radar" src="" alt="Radar Image">
</div>

<script>
const images = [
"""

for filename, dt in image_infos:
    html += f'    ["{TARGET_DIR}/{filename}", "{dt}"],\n'

html += """];
let current = 0;
let playing = true;
let interval = setInterval(nextImage, 1000);

function updateImage() {
    document.getElementById("radar").src = images[current][0];
    document.getElementById("timestamp").innerText = images[current][1];
}

function nextImage() {
    current = (current + 1) % images.length;
    updateImage();
}

function prevImage() {
    current = (current - 1 + images.length) % images.length;
    updateImage();
}

function togglePlay() {
    playing = !playing;
    if (playing) {
        interval = setInterval(nextImage, 1000);
    } else {
        clearInterval(interval);
    }
}

function openFullscreen() {
    const elem = document.documentElement;
    if (elem.requestFullscreen) {
        elem.requestFullscreen();
    }
}
updateImage();
</script>

</body>
</html>
"""

# Ghi file HTML
with open(HTML_FILE, "w", encoding="utf-8") as f:
    f.write(html)

print("✅ Đã tạo xong index.html với ảnh radar và thang màu.")

# Gửi lên GitHub nếu có
try:
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "🛰️ Cập nhật ảnh radar + thang màu"], check=True)
    subprocess.run(["git", "push"], check=True)
    print("🚀 Đã đẩy lên GitHub.")
except subprocess.CalledProcessError as e:
    print("❌ Lỗi Git:", e)
