import os
import shutil
import datetime
import subprocess

# Thư mục chứa ảnh radar
image_dir = "rada"
# Đường dẫn file index.html
index_file = "index.html"
# Số ngày giữ lại ảnh
days_to_keep = 1

def get_latest_image(folder):
    files = [os.path.join(folder, f) for f in os.listdir(folder)
             if f.lower().endswith(('.jpg', '.png', '.gif'))]
    if not files:
        return None
    return max(files, key=os.path.getmtime)

def delete_old_images(folder, days=1):
    now = datetime.datetime.now()
    for filename in os.listdir(folder):
        path = os.path.join(folder, filename)
        if os.path.isfile(path):
            mtime = datetime.datetime.fromtimestamp(os.path.getmtime(path))
            if (now - mtime).days >= days:
                os.remove(path)

def update_html(image_path):
    timestamp = datetime.datetime.now().strftime("%H:%M:%S %d-%m-%Y")
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Ảnh Radar Thời Tiết Mới Nhất</title>
        <meta http-equiv="refresh" content="600">
        <style>
            body {{ background-color: #000; color: #fff; text-align: center; font-family: Arial; }}
            img {{ max-width: 90vw; max-height: 90vh; }}
        </style>
    </head>
    <body>
        <h2>Ảnh Radar Thời Tiết Mới Nhất</h2>
        <p>Cập nhật lúc: {timestamp}</p>
        <img src="{image_path}" alt="Ảnh radar mới nhất">
    </body>
    </html>
    """
    with open(index_file, "w", encoding="utf-8") as f:
        f.write(html_content)

def git_commit_push():
    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "Cập nhật ảnh radar"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("✅ Đã push lên GitHub.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Lỗi Git: {e}")

if __name__ == "__main__":
    # Xóa ảnh cũ
    delete_old_images(image_dir, days=days_to_keep)

    # Lấy ảnh mới nhất
    latest_image = get_latest_image(image_dir)
    if not latest_image:
        print("Không tìm thấy ảnh radar.")
        exit(1)

    # Cập nhật file HTML
    update_html(latest_image)

    # Push lên GitHub
    git_commit_push()
