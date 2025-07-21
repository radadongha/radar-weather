import os
import shutil
import time
import subprocess
from datetime import datetime, timedelta
import re

# Cấu hình
SOURCE_FOLDER = "D:/WinSCP/RADA"
TARGET_FOLDER = "rada"
MAX_IMAGES = 5
DELETE_AFTER_DAYS = 1

def parse_datetime_from_filename(filename):
    match = re.search(r'(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})', filename)
    if match:
        yy, MM, dd, HH, mm = match.groups()
        try:
            dt = datetime.strptime(f"20{yy}-{MM}-{dd} {HH}:{mm}", "%Y-%m-%d %H:%M")
            return dt.strftime("%Y-%m-%d %H:%M")
        except:
            return "Không rõ"
    return "Không rõ"

def get_latest_images():
    files = [f for f in os.listdir(TARGET_FOLDER) if f.endswith(".jpg")]
    files.sort(reverse=True)
    return files[:MAX_IMAGES]

def copy_new_images():
    all_files = sorted(
        [f for f in os.listdir(SOURCE_FOLDER) if f.endswith(".jpg")],
        reverse=True
    )
    latest_files = all_files[:MAX_IMAGES]
    copied = []
    for file in latest_files:
        src = os.path.join(SOURCE_FOLDER, file)
        dst = os.path.join(TARGET_FOLDER, file)
        if not os.path.exists(dst):
            shutil.copy2(src, dst)
            copied.append(file)
    return copied

def delete_old_images():
    now = time.time()
    for f in os.listdir(TARGET_FOLDER):
        path = os.path.join(TARGET_FOLDER, f)
        if os.path.isfile(path):
            if now - os.path.getmtime(path) > DELETE_AFTER_DAYS * 86400:
                os.remove(path)

def generate_html(image_list):
    latest_time = parse_datetime_from_filename(image_list[-1]) if image_list else "Không rõ"
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(f"""<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="refresh" content="300">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Ảnh Radar Thời Tiết</title>
  <style>
    body {{
      background-color: black;
      color: white;
      font-family: Arial, sans-serif;
      text-align: center;
      margin: 0;
      padding: 0;
    }}
    img {{
      max-width: 90vw;
      max-height: 90vh;
      display: block;
      margin: 0 auto;
    }}
    #time {{
      font-size: 1.5rem;
      margin: 1rem;
    }}
  </style>
</head>
<body>
  <div id="time">🕒 Giờ radar: {latest_time}</div>
  <img id="radar" src="rada/{image_list[-1]}" alt="Ảnh radar mới nhất">
  <script>
    const images = [{', '.join([f'"rada/{img}"' for img in image_list])}];
    let index = 0;
    setInterval(() => {{
      index = (index + 1) % images.length;
      document.getElementById('radar').src = images[index];
    }}, 1000);
  </script>
</body>
</html>""")

def run_git_commands():
    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "🛰️ Cập nhật ảnh radar tự động"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("✅ Đã đẩy lên GitHub thành công.")
    except subprocess.CalledProcessError as e:
        print("❌ Lỗi Git:", e)

def main():
    print("🚀 Đang cập nhật ảnh radar...")
    os.makedirs(TARGET_FOLDER, exist_ok=True)
    delete_old_images()
    copied = copy_new_images()
    latest_images = get_latest_images()
    generate_html(latest_images)
    print("✅ Đã cập nhật danh sách ảnh vào index.html")
    run_git_commands()

if __name__ == "__main__":
    main()
