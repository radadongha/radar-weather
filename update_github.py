import os
import subprocess
import datetime
import configparser

# Đọc cấu hình
config = configparser.ConfigParser()
config.read("config.ini", encoding="utf-8")
SOURCE_FOLDER = config["paths"]["source_folder"]

# Lấy danh sách ảnh và sắp xếp theo thời gian sửa đổi (mới nhất trước)
def get_image_files(folder):
    files = [f for f in os.listdir(folder) if f.lower().endswith((".jpg", ".png", ".gif"))]
    return sorted(files, key=lambda f: os.path.getmtime(os.path.join(folder, f)), reverse=True)

# Xóa ảnh cũ hơn 1 ngày
def delete_old_images(folder, days=1):
    now = datetime.datetime.now()
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        if os.path.isfile(file_path):
            mtime = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
            if (now - mtime).days >= days:
                os.remove(file_path)
                print(f"Đã xóa ảnh cũ: {filename}")

# Cập nhật index.html để hiển thị ảnh mới nhất
def update_index_html(latest_image):
    now = datetime.datetime.now().strftime("%H:%M:%S %d/%m/%Y")
    html_content = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Radar Thời Tiết Đông Hà</title>
    <meta http-equiv="refresh" content="300">
    <style>
        body {{ text-align: center; font-family: Arial, sans-serif; background-color: #f7f7f7; padding: 50px; }}
        h1 {{ font-size: 2em; color: #111; }}
        img {{ max-width: 90%; height: auto; border: 3px solid #444; margin-top: 20px; }}
        .caption {{ margin-top: 10px; font-size: 1rem; color: #666; }}
    </style>
</head>
<body>
    <h1>Ảnh Radar Thời Tiết Mới Nhất</h1>
    <img src="{SOURCE_FOLDER}/{latest_image}" alt="Radar thời tiết Đông Hà">
    <div class="caption">Cập nhật: {now}</div>
</body>
</html>"""
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("Đã cập nhật index.html")

# Commit và push lên GitHub
def git_commit_and_push(message):
    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", message], check=True)
        subprocess.run(["git", "push"], check=True)
        print("Đã đẩy lên GitHub thành công.")
    except subprocess.CalledProcessError as e:
        print("Lỗi khi chạy lệnh Git:", e)

# ================== CHẠY ==================

# Xóa ảnh cũ
delete_old_images(SOURCE_FOLDER)

# Cập nhật file index.html với ảnh mới nhất
images = get_image_files(SOURCE_FOLDER)
if not images:
    print("Không tìm thấy ảnh radar.")
else:
    latest = images[0]
    update_index_html(latest)
    git_commit_and_push(f"Cập nhật ảnh radar: {latest}")
