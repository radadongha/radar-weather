import os
import shutil
import glob
import datetime
import subprocess
from PIL import Image

# Cấu hình
SOURCE_DIR = "D:/WinSCP/RADA"
TARGET_DIR = "rada"
HTML_FILE = "index.html"
LEGEND_ORIGINAL = "legend.png"  # Đặt cùng thư mục với script
LEGEND_RESIZED = os.path.join(TARGET_DIR, "legend.png")
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

def resize_legend(image_path, output_path, scale=1/3):
    if not os.path.exists(image_path):
        print(f"⚠️ Không tìm thấy ảnh thang màu: {image_path}")
        return
    img = Image.open(image_path)
    new_size = (int(img.width * scale), int(img.height * scale))
    img_resized = img.resize(new_size, Image.Resampling.LANCZOS)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img_resized.save(output_path)
    print(f"🖼️ Đã resize thang màu: {output_path}")

def main():
    print("🚀 Đang cập nhật ảnh radar...")

    os.makedirs(TARGET_DIR, exist_ok=True)

    # Lấy 5 ảnh radar mới nhất
    all_images = sorted(glob.glob(os.path.join(SOURCE_DIR, "*.jpg")), reverse=True)
    selected_images = all_images[:NUM_IMAGES]

    if not selected_images:
        print("❌ Không tìm thấy ảnh radar.")
        return

    # Copy và lấy thông tin thời gian
    image_infos = []
    for src in reversed(selected_images):
        dst = os.path.join(TARGET_DIR, os.path.basename(src))
        shutil.copy2(src, dst)
        dt = extract_datetime(src)
        if dt:
            image_infos.append((os.path.basename(dst), dt.strftime("%d/%m/%Y %H:%M")))

    # Xóa ảnh radar cũ không còn dùng
    existing_files = glob.glob(os.path.join(TARGET_DIR, "*.jpg"))
    keep_files = [os.path.join(TARGET_DIR, f) for f, _ in image_infos]
    for f in existing_files:
        if f not in keep_files:
            os.remove(f)

    # Resize ảnh thang màu
    resize_legend(LEGEND_ORIGINAL, LEGEND_RESIZED, scale=1/3)

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
    .legend {
        margin-top: 10px;
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

<div class="legend">
    <img src="rada/legend.png" alt="Thang màu phản hồi">
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

    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(html)

    print("✅ Đã tạo xong index.html với ảnh radar và thang màu.")

    # Tự động đẩy lên GitHub nếu có thay đổi
    try:
        subprocess.run(["git", "add", "."], check=True)
        result = subprocess.run(["git", "diff", "--cached", "--quiet"])
        if result.returncode != 0:
            subprocess.run(["git", "commit", "-m", "🛰️ Cập nhật ảnh radar tự động"], check=True)
            subprocess.run(["git", "push"], check=True)
            print("🚀 Đã đẩy lên GitHub.")
        else:
            print("ℹ️ Không có thay đổi mới để commit.")
    except subprocess.CalledProcessError as e:
        print("❌ Lỗi Git:", e)

if __name__ == "__main__":
    main()
