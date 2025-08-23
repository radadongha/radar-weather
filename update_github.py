import os
import shutil
import glob
import datetime
import subprocess
from PIL import Image

SOURCE_DIR = "D:/WinSCP/RADA"
TARGET_DIR = "rada"
HTML_FILE = "index.html"
LEGEND_ORIGINAL = "legend_original.png"
LEGEND_OUTPUT = os.path.join(TARGET_DIR, "legend.png")
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

def resize_legend(input_path, output_path, scale=0.7):
    try:
        img = Image.open(input_path)
        new_size = (int(img.width * scale), int(img.height * scale))
        img = img.resize(new_size, Image.LANCZOS)
        img.save(output_path)
        print("✅ Đã resize ảnh legend.")
    except Exception as e:
        print("❌ Lỗi resize legend:", e)

# Tạo thư mục rada nếu chưa có
os.makedirs(TARGET_DIR, exist_ok=True)

# Resize thang màu
resize_legend(LEGEND_ORIGINAL, LEGEND_OUTPUT)

# Lấy các file radar ảnh .jpg
all_images = sorted(glob.glob(os.path.join(SOURCE_DIR, "*.jpg")), reverse=True)
selected_images = all_images[:NUM_IMAGES]

# Copy ảnh vào thư mục rada
image_infos = []
for src in reversed(selected_images):  # đảo lại cho đúng thứ tự thời gian
    dst = os.path.join(TARGET_DIR, os.path.basename(src))
    shutil.copy2(src, dst)
    dt = extract_datetime(src)
    if dt:
        image_infos.append((os.path.basename(dst), dt.strftime("%d/%m/%Y %H:%M")))

# Xóa ảnh cũ trong rada/
existing_files = glob.glob(os.path.join(TARGET_DIR, "*.jpg"))
keep_files = [os.path.join(TARGET_DIR, os.path.basename(f)) for f, _ in image_infos]
for f in existing_files:
    if f not in keep_files:
        os.remove(f)

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
        display: flex;
        justify-content: center;
        align-items: center;
        max-width: 95vw;
        max-height: 95vh;
        gap: 2px;
    }

    .radar-wrapper {
        position: relative;
    }

    #radar {
        max-height: 90vh;
    }

    #legend {
        max-height: 90vh;
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
    <div class="radar-wrapper">
        <div class="timestamp" id="timestamp"></div>
        <img id="radar" src="" alt="Radar Image">
    </div>
    <img id="legend" src="rada/legend.png" alt="Legend">
</div>

<script>
const images = [
"""

# Thêm danh sách ảnh và thời gian tương ứng
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

# Ghi file index.html
with open(HTML_FILE, "w", encoding="utf-8") as f:
    f.write(html)

print("✅ Đã tạo xong index.html với ảnh radar + timestamp + legend + điều khiển.")

REPO_DIR = os.path.dirname(os.path.abspath(__file__))

def run_git(cmd):
    return subprocess.run(["git"] + cmd, cwd=REPO_DIR, text=True, capture_output=True)

def safe_git_commit():
    try:
        subprocess.run(["git", "add", "."], cwd=REPO_DIR, check=True)
        subprocess.run(["git", "commit", "-m", "🛰️ Cập nhật ảnh radar + thang màu"], cwd=REPO_DIR, check=True)
        subprocess.run(["git", "push", "origin", "main"], cwd=REPO_DIR, check=True)
        print("✅ Commit & push thành công")
    except subprocess.CalledProcessError as e:
        err = e.stderr or e.stdout
        if err and "cannot lock ref 'HEAD'" in err:
            print("⚠️ HEAD bị hỏng → đang khôi phục nhánh main...")
            run_git(["checkout", "--detach"])
            run_git(["branch", "-D", "main"])
            run_git(["fetch", "origin", "main"])
            run_git(["checkout", "-b", "main", "origin/main"])
            run_git(["branch", "--set-upstream-to=origin/main", "main"])
            subprocess.run(["git", "add", "."], cwd=REPO_DIR, check=True)
            subprocess.run(["git", "commit", "-m", "🛰️ Cập nhật ảnh radar + thang màu"], cwd=REPO_DIR, check=True)
            subprocess.run(["git", "push", "origin", "main"], cwd=REPO_DIR, check=True)
            print("✅ Đã khôi phục HEAD và push thành công")
        else:
            print("❌ Lỗi Git khác:", e)

# --- gọi cuối cùng ---
safe_git_commit()


# Gửi lên GitHub (nếu cần)
try:
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "🛰️ Cập nhật ảnh radar + thang màu"], check=True)
    subprocess.run(["git", "push"], check=True)
    print("🚀 Đã đẩy lên GitHub.")
except subprocess.CalledProcessError as e:
    print("❌ Lỗi Git:", e)
