import os
import shutil
import subprocess
from datetime import datetime, timedelta

# Cấu hình
SOURCE_DIR = "D:/WinSCP/RADA"
TARGET_DIR = "rada"
HTML_FILE = "index.html"
NUM_IMAGES = 5  # số ảnh gần nhất
MAX_IMAGE_AGE_HOURS = 24  # xóa ảnh cũ sau 24 giờ

def get_sorted_images(directory):
    files = [f for f in os.listdir(directory) if f.lower().endswith(".jpg")]
    full_paths = [os.path.join(directory, f) for f in files]
    return sorted(full_paths, key=os.path.getmtime, reverse=True)

def extract_time_str(filename):
    try:
        base = os.path.splitext(filename)[0]
        time_part = base[-12:]                # 250721132004
        tail_part = filename[-6:-4]           # từ MAX0075 → lấy 75

        nam = time_part[0:2]
        thang = time_part[2:4]
        ngay = time_part[4:6]
        gio = time_part[6:8]
        phut = time_part[8:10]
        time_str = f"{nam}:{gio}_{ngay}_{phut}/{thang}/20{ngay}"  # vd: 25:13_21_20/07/2021
        return time_str
    except Exception as e:
        print(f"Lỗi đọc thời gian từ tên file: {filename} → {e}")
        return "Không rõ"

def copy_latest_images():
    os.makedirs(TARGET_DIR, exist_ok=True)
    images = get_sorted_images(SOURCE_DIR)[:NUM_IMAGES]

    copied_files = []
    for img_path in images:
        filename = os.path.basename(img_path)
        dest_path = os.path.join(TARGET_DIR, filename)
        shutil.copy2(img_path, dest_path)
        copied_files.append(filename)

    return copied_files

def clean_old_images():
    now = datetime.now()
    for f in os.listdir(TARGET_DIR):
        path = os.path.join(TARGET_DIR, f)
        if os.path.isfile(path):
            mtime = datetime.fromtimestamp(os.path.getmtime(path))
            if now - mtime > timedelta(hours=MAX_IMAGE_AGE_HOURS):
                os.remove(path)

def create_html(image_list, time_str):
    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Ảnh Radar Mới Nhất</title>
    <style>
        body {{ background: #000; color: #fff; text-align: center; font-family: sans-serif; }}
        img {{ max-width: 90vw; max-height: 90vh; }}
    </style>
</head>
<body>
    <h2>🛰️ Giờ radar: {time_str}</h2>
    <div id="slideshow">
""")
        for filename in image_list:
            f.write(f'        <img src="{TARGET_DIR}/{filename}" style="display:none;">\n')

        f.write("""    </div>
<script>
let imgs = document.querySelectorAll("#slideshow img");
let index = 0;
function showNext() {
    imgs.forEach((img, i) => img.style.display = i === index ? "block" : "none");
    index = (index + 1) % imgs.length;
}
showNext();
setInterval(showNext, 1000);
</script>
</body>
</html>""")

def git_push():
    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "🛰️ Cập nhật ảnh radar tự động"], check=True)
    except subprocess.CalledProcessError:
        print("❌ Không có thay đổi để commit.")
    subprocess.run(["git", "push"], check=True)

if __name__ == "__main__":
    print("🚀 Đang cập nhật ảnh radar...")

    clean_old_images()
    images = copy_latest_images()
    if not images:
        print("❌ Không tìm thấy ảnh radar.")
        exit()

    time_str = extract_time_str(images[0])
    create_html(images, time_str)
    print("✅ Đã cập nhật danh sách ảnh vào index.html")

    try:
        git_push()
        print("✅ Đã đẩy lên GitHub thành công.")
    except subprocess.CalledProcessError as e:
        print("❌ Lỗi Git:", e)
