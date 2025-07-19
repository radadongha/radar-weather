import os
import shutil
from datetime import datetime, timedelta

# Cấu hình thư mục
SOURCE_FOLDER = "RARA"
DEST_FOLDER = "rada"
MAX_FILE_AGE_DAYS = 1

# Tìm file ảnh mới nhất trong thư mục nguồn
def get_latest_file(folder):
    files = [os.path.join(folder, f) for f in os.listdir(folder) if f.lower().endswith('.jpg')]
    if not files:
        return None
    latest = max(files, key=os.path.getmtime)
    return latest

# Xóa ảnh cũ hơn X ngày
def delete_old_files(folder, max_age_days):
    now = datetime.now()
    deleted = 0
    for filename in os.listdir(folder):
        filepath = os.path.join(folder, filename)
        if os.path.isfile(filepath):
            file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
            if (now - file_time).days >= max_age_days:
                os.remove(filepath)
                deleted += 1
    return deleted

# Copy file mới vào thư mục rada/
def copy_new_file():
    latest = get_latest_file(SOURCE_FOLDER)
    if not latest:
        print("⚠️ Không tìm thấy file ảnh nào trong thư mục RARA.")
        return None

    basename = os.path.basename(latest)
    dest_path = os.path.join(DEST_FOLDER, basename)

    if not os.path.exists(DEST_FOLDER):
        os.makedirs(DEST_FOLDER)

    shutil.copy2(latest, dest_path)
    print(f"✅ Đã copy ảnh mới nhất: {basename}")
    return basename

# Thực hiện git commit & push
def git_commit_push(filename):
    os.system("git add rada")
    commit_msg = f'Update: {filename}'
    os.system(f'git commit -m "{commit_msg}"')

    # Kéo code mới nhất từ GitHub
    pull_result = os.system("git pull origin main --rebase")
    if pull_result != 0:
        print("⚠️ Gặp lỗi khi git pull. Dừng lại.")
        return

    push_result = os.system("git push origin main")
    if push_result == 0:
        print("🚀 Đã đẩy lên GitHub thành công.")
    else:
        print("❌ Lỗi: Không thể đẩy lên GitHub. Có thể do xung đột hoặc chưa xác thực.")

# === CHẠY CHÍNH ===
if __name__ == "__main__":
    filename = copy_new_file()
    if filename:
        deleted = delete_old_files(DEST_FOLDER, MAX_FILE_AGE_DAYS)
        print(f"🗑️ Đã xóa {deleted} ảnh cũ.")
        git_commit_push(filename)
