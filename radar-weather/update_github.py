import os
import shutil
import glob
import datetime
import subprocess
import json

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

def generate_html():
    with open("images.json", "r", encoding="utf-8") as f:
        data = json.load(f)

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
      max-width: 90vw;
      max-height: 80vh;
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
  <div id="time">Đang tải...</div>
  <img id="radarImage" src="" alt="Radar" />
  <div class="controls">
    <button onclick="prevImage()">⏮️</button>
    <button onclick="togglePlay()" id="playBtn">▶️</button>
    <button onclick="nextImage()">⏭️</button>
  </div>

  <script>
    let images = [];
    let currentIndex = 0;
    let playing = false;
    let interval;

    const imgElement = document.getElementById("radarImage");
    const timeElement = document.getElementById("time");
    const playBtn = document.getElementById("playBtn");

    function updateImage() {{
      if (images.length === 0) return;
      imgElement.src = images[currentIndex].src;
      timeElement.textContent = "Giờ radar: " + images[currentIndex].time;
    }}

    function prevImage() {{
      currentIndex = (currentIndex - 1 + images.length) % images.length;
      updateImage();
    }}

    function nextImage() {{
      currentIndex = (currentIndex + 1) % images.length;
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

    fetch("images.json")
      .then(response => response.json())
      .then(data => {{
        images = data;
        currentIndex = images.length - 1;
        updateImage();
      }})
      .catch(error => {{
        console.error("❌ Lỗi tải images.json:", error);
        timeElement.textContent = "Không tải được dữ liệu ảnh.";
      }});
  </script>
</body>
</html>
""")

def generate_json(image_paths):
    image_files = [os.path.basename(p) for p in image_paths]
    times = [extract_datetime(name).strftime("%H:%M %d/%m") if extract_datetime(name) else "Không rõ" for name in image_files]
    data = [{"src": f"rada/{img}", "time": t} for img, t in zip(image_files, times)]
    with open("images.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)

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
    generate_json(latest_images)
    generate_html()
    print("✅ Đã cập nhật index.html và images.json")
    run_git_commands()

if __name__ == "__main__":
    main()