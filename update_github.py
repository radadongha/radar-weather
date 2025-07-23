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
    latest_time = extract_datetime(image_files[-1])
    if latest_time:
        radar_time = latest_time.strftime("%H:%M %d/%m/%Y")
    else:
        radar_time = "Không rõ"

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
            margin: 20px auto;
        }}
        #time {{
            font-size: 20px;
            margin-top: 10px;
        }}
    </style>
</head>
<body>
    <h1>  Radar Thời Tiết</h1>
    <div id="time"> Giờ radar: {radar_time}</div>
    <img id="radar" src="rada/{image_files[-1]}" alt="Radar">
    <script>
        const images = [{', '.join([f'"rada/{img}"' for img in image_files])}];
        let index = 0;
        setInterval(() => {{
            index = (index + 1) % images.length;
            document.getElementById("radar").src = images[index];
        }}, 1000);
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
    print("✅ Đã cập nhật danh sách ảnh vào index.html")
    run_git_commands()

if __name__ == "__main__":
    main()
