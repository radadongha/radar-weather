import os
import shutil
import datetime
import subprocess

# === Cấu hình ===
SOURCE_FOLDER = "D:/WinSCP/RADA"  # Giữ nguyên thư mục ảnh nguồn trong WinSCP
TARGET_FOLDER = "C:/Users/kttv/Desktop/radar-weather/rada"  # Thư mục ảnh radar trong repo GitHub
REPO_FOLDER = "C:/Users/kttv/Desktop/radar-weather"  # Thư mục gốc repo

# === 1. Tìm và copy ảnh radar mới nhất ===
files = [f for f in os.listdir(SOURCE_FOLDER) if f.lower().endswith(".jpg")]
if not files:
    print("❌ Không tìm thấy ảnh radar trong thư mục nguồn.")
    exit()

files.sort(reverse=True)
latest_file = files[0]

source_path = os.path.join(SOURCE_FOLDER, latest_file)
target_path = os.path.join(TARGET_FOLDER, latest_file)

# Tạo thư mục rada nếu chưa có
if not os.path.exists(TARGET_FOLDER):
    os.makedirs(TARGET_FOLDER)

shutil.copy2(source_path, target_path)
print(f"✅ Đã copy ảnh mới nhất: {latest_file}")

# === 2. Xóa ảnh cũ hơn 1 ngày trong rada/ ===
now = datetime.datetime.now()
deleted_count = 0

for f in os.listdir(TARGET_FOLDER):
    path = os.path.join(TARGET_FOLDER, f)
    if os.path.isfile(path) and f.lower().endswith(".jpg"):
        file_time = datetime.datetime.fromtimestamp(os.path.getmtime(path))
        if (now - file_time).days >= 1:
            os.remove(path)
            deleted_count += 1

print(f"🗑️ Đã xóa {deleted_count} ảnh cũ.")

# === 3. Commit và push lên GitHub ===
os.chdir(REPO_FOLDER)

subprocess.run(["git", "add", "."], shell=True)
subprocess.run(["git", "commit", "-m", f"Update: {latest_file}"], shell=True)
subprocess.run(["git", "push"], shell=True)

print("🚀 Đã đẩy lên GitHub thành công.")
