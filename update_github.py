import os
import glob
import shutil
import subprocess
from datetime import datetime, timedelta
from PIL import Image

# Thư mục chứa ảnh radar và thang màu
RADA_FOLDER = "rada"
LEGEND_ORIGINAL = "legend.png"
LEGEND_RESIZED = os.path.join(RADA_FOLDER, "legend_resized.png")
INDEX_HTML = "index.html"

# --- Hàm tiện ích ---

def get_latest_images(folder, count=5):
    """Lấy 'count' ảnh mới nhất trong thư mục"""
    files = glob.glob(os.path.join(folder, "*.jpg"))
    files.sort(reverse=True)
    return files[:count]

def delete_old_images(folder, days=1):
    """Xóa ảnh radar cũ hơn 'days' ngày"""
    now = datetime.now()
    for file in glob.glob(os.path.join(folder, "*.jpg")):
        mtime = datetime.fromtimestamp(os.path.getmtime(file))
        if now - mtime > timedelta(days=days):
            os.remove(file)
            print(f"🗑️ Đã xóa: {file}")

def resize_legend(input_path, output_path, scale=1/3):
    """Thu nhỏ ảnh thang màu"""
    if not os.path.exists(input_path):
        print(f"⚠️ Không tìm thấy ảnh thang màu: {input_path}")
        return
    img = Image.open(input_path)
    new_size = (int(img.width * scale), int(img.height * scale))
    img_resized = img.resize(new_size, Image.Resampling.LANCZOS)
    img_resized.save(output_path)
    print(f"🖼️ Đã tạo thang màu thu nhỏ: {output_path}")

def generate_index_html(image_files, legend_file):
    """Tạo file index.html để hiển thị ảnh radar và thang màu"""
    html = """
<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8" />
  <title>Ảnh radar thời tiết</title>
  <style>
    body { background: #000; margin: 0; padding: 0; text-align: center; color: white; }
    .container { display: flex; justify-content: center; align-items: flex-start; flex-wrap: wrap; }
    .radar-img { margin: 5px; border: 1px solid #444; }
    .legend { position: fixed; top: 10px; right: 10px; z-index: 10; border: 2px solid #fff; background: rgba(0,0,0,0.3); }
    button { font-size: 16px; padding: 8px 12px; margin: 10px; }
  </style>
</head>
<body>
  <h2>🛰️ Ảnh Radar Thời Tiết Mới Nhất</h2>
  <div class="container">
"""
    for img in image_files:
        html += f'    <img class="radar-img" src="{img}" width="640" height="480" />\n'
    if os.path.exists(legend_file):
        html += f'  </div>\n  <img class="legend" src="{legend_file}" />\n'
    else:
        html += f'  </div>\n  <!-- Không có thang màu -->\n'
    html += """
  <button onclick="document.documentElement.requestFullscreen()">🖥️ Full màn hình</button>
</body>
</html>
"""
    with open(INDEX_HTML, "w", encoding="utf-8") as f:
        f.write(html)
    print("✅ Đã tạo xong index.html với ảnh radar và thang màu.")

def git_commit_and_push():
    """Tự động commit và push ảnh mới"""
    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "🛰️ Cập nhật ảnh radar tự động"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("🚀 Đã push ảnh radar lên GitHub.")
    except subprocess.CalledProcessError as e:
        print("❌ Lỗi Git:", e)

# --- Chương trình chính ---
if __name__ == "__main__":
    print("🚀 Đang cập nhật ảnh radar...")

    # Bước 1: Xóa ảnh cũ
    delete_old_images(RADA_FOLDER)

    # Bước 2: Thu nhỏ thang màu
    resize_legend(LEGEND_ORIGINAL, LEGEND_RESIZED, scale=1/3)

    # Bước 3: Tạo HTML
    latest_images = get_latest_images(RADA_FOLDER, count=5)
    latest_image_files = [os.path.relpath(f) for f in latest_images]
    generate_index_html(latest_image_files, os.path.relpath(LEGEND_RESIZED))

    # Bước 4: Commit & push lên GitHub
    git_commit_and_push()
