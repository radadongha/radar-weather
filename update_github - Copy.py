import os
import shutil
import glob
import datetime
import subprocess

SOURCE_DIR = "D:/WinSCP/RADA"
TARGET_DIR = "rada"
HTML_FILE = "index.html"

def extract_datetime(filename):
    name = os.path.basename(filename)
    try:
        y = int(name[11:13]) + 2000
        m = int(name[13:15])
        d = int(name[15:17])
        H = int(name[17:19])
        M = int(name[19:21])
        return datetime.datetime(y, m, d, H, M)
    except Exception:
        return None

def get_latest_images(n=5):
    all_images = glob.glob(os.path.join(SOURCE_DIR, "*.MAX*.jpg"))
    sorted_images = sorted(all_images, key=extract_datetime)
    return sorted_images[-n:]

def copy_images_to_target(images):
    os.makedirs(TARGET_DIR, exist_ok=True)
    for img_path in images:
        shutil.copy2(img_path, os.path.join(TARGET_DIR, os.path.basename(img_path)))

def generate_html(image_paths):
    image_files = [os.path.basename(path) for path in image_paths]
    times = []
    for name in image_files:
        dt = extract_datetime(name)
        times.append(dt.strftime("%H:%M %d/%m") if dt else "Không rõ")

    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Radar Thời Tiết</title>
    <meta http-equiv="refresh" content="300">
    <style>
        body {{
            font-family: Arial, sans-serif;
            text-align: center;
            background: #000;
            color: #fff;
        }}
        img {{
            max-width: 120vw;
            max-height: 120vh;
            display: block;
            margin: 10px auto;
        }}
        #time {{
            font-size: 20px;
            margin: 10px;
        }}
        .controls {{
            margin-top: 10px;
        }}
        button {{
            font-size: 20px;
            padding: 10px;
            margin: 5px;
            cursor: pointer;
        }}
    </style>
</head>
<body>
    <h1>Radar Thời Tiết</h1>
    <div id="time">Giờ radar: {times[-1]}</div>
    <img id="radarImage" src="rada/{image_files[-1]}" alt="Radar" />

    <div class="controls">
        <button onclick="prevImage()">⏮️</button>
        <button onclick="togglePlay()" id="playBtn">▶️</button>
        <button onclick="nextImage()">⏭️</button>
    </div>

    <script>
        const imageList = { [f"rada/{img}" for img in image_files] };
        const imageTimes = {times};
        let currentIndex = imageList.length - 1;
        let playing = false;
        let interval;

        const imgElement = document.getElementById("radarImage");
        const timeElement = document.getElementById("time");
        const playBtn = document.getElementById("playBtn");

        function updateImage() {{
            imgElement.src = imageList[currentIndex];
            timeElement.textContent = "Giờ radar: " + imageTimes[currentIndex];
        }}

        function prevImage() {{
            currentIndex = (currentIndex - 1 + imageList.length) % imageList.length;
            updateImage();
        }}

        function nextImage() {{
            currentIndex = (currentIndex + 1) % imageList.length;
            updateImage();
        }}

        function togglePlay() {{
            playing = !playing;
            playBtn.textContent = playing ? "⏸️" : "▶️";
            if (playing) {{
                interval = setInterval(nextImage, 800);
            }} else {{
                clearInterval(interval);
            }}
        }}
    </script>
</body>
</html>
""")

def delete_old_images(days=1):
    now = datetime.datetime.now()
    for f in glob.glob(os.path.join(TARGET_DIR, "*.jpg")):
        t = datetime.datetime.fromtimestamp(os.path.getmtime(f))
        if (now - t).days >= days:
            os.remove(f)

def run_git_commands():
    try:
        subprocess.run(["git", "add", "."], check=True)
        result = subprocess.run(["git", "commit", "-m", "🛰️ Cập nhật ảnh radar tự động"], check=False)
        if result.returncode == 0:
            subprocess.run(["git", "push"], check=True)
            print("✅ Đã đẩy lên GitHub thành công.")
        else:
            print("ℹ️ Không có thay đổi để commit.")
    except subprocess.CalledProcessError as e:
        print("❌ Lỗi Git:", e)

def main():
    print("🚀 Đang cập nhật ảnh radar...")
    latest_images = get_latest_images()
    copy_images_to_target(latest_images)
    delete_old_images()
    generate_html(latest_images)
    print("✅ Đã cập nhật index.html với giờ radar từng ảnh và nút điều khiển")
    run_git_commands()

if __name__ == "__main__":
    main()
