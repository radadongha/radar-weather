import os
import shutil
import glob
import datetime
import subprocess

SOURCE_DIR = "D:/WinSCP/RADA"
TARGET_DIR = "rada"
HTML_FILE = "index.html"
MAX_IMAGES = 5

def extract_datetime(filename):
    try:
        name = os.path.basename(filename)
        y = int(name[11:13]) + 2000
        m = int(name[13:15])
        d = int(name[15:17])
        h = int(name[17:19])
        mi = int(name[19:21])
        return datetime.datetime(y, m, d, h, mi)
    except:
        return None

def get_latest_images():
    files = glob.glob(os.path.join(SOURCE_DIR, "*.jpg"))
    files.sort(key=lambda x: extract_datetime(x) or datetime.datetime.min)
    return files[-MAX_IMAGES:]

def copy_images_to_target(files):
    if not os.path.exists(TARGET_DIR):
        os.makedirs(TARGET_DIR)
    for file in files:
        shutil.copy(file, os.path.join(TARGET_DIR, os.path.basename(file)))

def delete_old_images():
    now = datetime.datetime.now()
    for file in glob.glob(os.path.join(TARGET_DIR, "*.jpg")):
        dt = extract_datetime(file)
        if dt and (now - dt).days >= 1:
            os.remove(file)

def generate_html(image_paths):
    image_files = [os.path.basename(path) for path in image_paths]
    times = []
    for name in image_files:
        dt = extract_datetime(name)
        times.append(dt.strftime("%H:%M %d/%m/%Y") if dt else "Không rõ")

    image_list_js = str([f"rada/{img}" for img in image_files])
    time_list_js = str(times)

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
            background: #000;
            color: #fff;
            margin: 0;
            padding: 0;
            overflow-x: hidden;
        }}
        .wrapper {{
            display: flex;
            justify-content: center;
            align-items: center;
            margin-top: 20px;
        }}
        #time-display {{
            font-size: 16px;
            background-color: rgba(0, 0, 0, 0.6);
            padding: 8px 14px;
            border-radius: 10px;
            margin-right: 12px;
            text-align: center;
            white-space: nowrap;
        }}
        #radarImage {{
            width: 90vw;
            max-width: 800px;
            height: auto;
        }}
        .controls {{
            display: flex;
            flex-direction: column;
            gap: 10px;
            background: rgba(0, 0, 0, 0.5);
            padding: 8px;
            border-radius: 10px;
            margin-left: 12px;
        }}
        button {{
            font-size: 14px;
            padding: 10px 14px;
            cursor: pointer;
            border: none;
            border-radius: 6px;
            background: #444;
            color: #fff;
        }}
        button:hover {{
            background: #666;
        }}
    </style>
</head>
<body>
    <h2 style="text-align:center;">Radar Thời Tiết</h2>

    <div class="wrapper">
        <div id="time-display">{times[-1]}</div>

        <img id="radarImage" src="rada/{image_files[-1]}" alt="Radar">

        <div class="controls">
            <button onclick="prevImage()">⏮️</button>
            <button onclick="togglePlay()" id="playBtn">▶️</button>
            <button onclick="nextImage()">⏭️</button>
            <button onclick="toggleFullscreen()">🖥️</button>
        </div>
    </div>

    <script>
        const imageList = {image_list_js};
        const imageTimes = {time_list_js};
        let currentIndex = imageList.length - 1;
        let playing = false;
        let interval;

        const imgElement = document.getElementById("radarImage");
        const timeElement = document.getElementById("time-display");
        const playBtn = document.getElementById("playBtn");

        function updateImage() {{
            imgElement.src = imageList[currentIndex];
            timeElement.textContent = imageTimes[currentIndex];
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

        function toggleFullscreen() {{
            const docEl = document.documentElement;
            if (!document.fullscreenElement) {{
                docEl.requestFullscreen().catch(err => {{
                    alert("Không thể vào full màn hình: " + err.message);
                }});
            }} else {{
                document.exitFullscreen();
            }}
        }}

        updateImage();
    </script>
</body>
</html>
""")

def git_commit_and_push():
    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "🛰️ Cập nhật ảnh radar tự động"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("✅ Đã cập nhật lên GitHub")
    except subprocess.CalledProcessError as e:
        print("❌ Lỗi Git:", e)

if __name__ == "__main__":
    print("🚀 Đang cập nhật ảnh radar...")
    latest_images = get_latest_images()
    copy_images_to_target(latest_images)
    delete_old_images()
    generate_html(latest_images)
    git_commit_and_push()
