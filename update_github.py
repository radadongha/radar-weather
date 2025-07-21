import os
import shutil
import subprocess
from datetime import datetime, timedelta
import re

# === CẤU HÌNH ===
RADAR_FOLDER = "rada"
HTML_PATH = "index.html"
MAX_IMAGES = 5
DELETE_OLDER_THAN_DAYS = 1

# === 1. XÓA ẢNH CŨ HƠN 1 NGÀY ===
def delete_old_images():
    now = datetime.now()
    cutoff = now - timedelta(days=DELETE_OLDER_THAN_DAYS)

    for filename in os.listdir(RADAR_FOLDER):
        if filename.lower().endswith(".jpg"):
            filepath = os.path.join(RADAR_FOLDER, filename)
            try:
                filetime = datetime.fromtimestamp(os.path.getmtime(filepath))
                if filetime < cutoff:
                    os.remove(filepath)
                    print(f"🗑️ Đã xóa ảnh cũ: {filename}")
            except Exception as e:
                print(f"❌ Lỗi khi xóa {filename}: {e}")

# === 2. CẬP NHẬT DANH SÁCH ẢNH MỚI NHẤT VÀO index.html ===
def update_image_list_in_html():
    image_files = sorted(
        [f for f in os.listdir(RADAR_FOLDER) if f.lower().endswith(".jpg")],
        key=lambda f: os.path.getmtime(os.path.join(RADAR_FOLDER, f)),
        reverse=True
    )[:MAX_IMAGES]

    image_lines = [f'"{RADAR_FOLDER}/{name}"' for name in image_files]
    new_image_list = ",\n      ".join(image_lines)

    with open(HTML_PATH, "r", encoding="utf-8") as f:
        html = f.read()

    new_html = re.sub(
        r'<!-- IMAGE_LIST_START -->(.*?)<!-- IMAGE_LIST_END -->',
        f'<!-- IMAGE_LIST_START -->\n      {new_image_list}\n      <!-- IMAGE_LIST_END -->',
        html,
        flags=re.DOTALL
    )

    with open(HTML_PATH, "w", encoding="utf-8") as f:
        f.write(new_html)

    print(f"✅ Đã cập nhật danh sách ảnh vào {HTML_PATH}")

# === 3. GIT: ADD + COMMIT + PUSH ===
def git_push():
    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "🛰️ Cập nhật ảnh radar tự động"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("✅ Đã đẩy lên GitHub thành công.")
    except subprocess.CalledProcessError as e:
        print("❌ Lỗi Git:", e)

# === CHẠY CHÍNH ===
if __name__ == "__main__":
    delete_old_images()
    update_image_list_in_html()
    git_push()
