import os
import shutil
import glob
import time
import subprocess
import io
import sys
from datetime import datetime, timedelta

# Đảm bảo in ra Unicode được
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# === Cấu hình ===
RADAR_DIR = "rada"
HTML_PATH = "index.html"
MAX_IMAGES = 5
DELETE_OLDER_THAN_DAYS = 1

# === Lấy danh sách ảnh radar mới nhất ===
def get_latest_images():
    images = sorted(glob.glob(f"{RADAR_DIR}/*.jpg"), reverse=True)
    return images[:MAX_IMAGES]

# === Xóa ảnh cũ hơn 1 ngày ===
def delete_old_images():
    now = time.time()
    for img in glob.glob(f"{RADAR_DIR}/*.jpg"):
        if os.stat(img).st_mtime < now - DELETE_OLDER_THAN_DAYS * 86400:
            os.remove(img)
            print(f"🗑️ Đã xóa ảnh cũ: {img}")

# === Cập nhật file HTML (index.html) ===
def update_html(image_list):
    try:
        with open(HTML_PATH, "r", encoding="utf-8") as f:
            html = f.read()
    except FileNotFoundError:
        html = "<html><head><meta charset='utf-8'></head><body><div id='loop'></div><div id='time'></div></body></html>"

    # Tạo danh sách thẻ <img> cho loop
    image_tags = "\n".join(
        f'<img src="{img}" style="display:none; max-width:90vw; max-height:90vh;" />'
        for img in image_list
    )

    # Lấy giờ từ ảnh mới nhất
    timestamp = os.path.basename(image_list[0]).replace(".jpg", "")
    try:
        dt = datetime.strptime(timestamp, "%Y%m%d%H%M")
        formatted_time = dt.strftime("Giờ radar: %H:%M, ngày %d/%m/%Y")
    except Exception:
        formatted_time = f"Ảnh mới nhất: {timestamp}"

    # Cập nhật nội dung
    new_body = f"""
<div id="loop">
{image_tags}
</div>
<div id="time" style="margin-top:10px; font-weight:bold;">{formatted_time}</div>

<script>
let imgs = document.querySelectorAll('#loop img');
let index = 0;
setInterval(() => {{
    imgs.forEach((img, i) => img.style.display = i === index ? 'block' : 'none');
    index = (index + 1) % imgs.length;
}}, 1000);
</script>
"""

    # Ghi lại vào file HTML
    html = html.replace(
        re_between_tags(html, "<body>", "</body>"), f"<body>{new_body}</body>"
    )
    with open(HTML_PATH, "w", encoding="utf-8") as f:
        f.write(html)
    print("✅ Đã cập nhật danh sách ảnh vào index.html")

# === Hàm hỗ trợ thay thế nội dung giữa 2 thẻ ===
def re_between_tags(text, start_tag, end_tag):
    start = text.find(start_tag)
    end = text.find(end_tag, start)
    return text[start:end + len(end_tag)] if start != -1 and end != -1 else ""

# === Đẩy lên GitHub ===
def git_push():
    try:
        subprocess.run(["git", "add", "."], check=True)

        result = subprocess.run(
            ["git", "commit", "-m", "🛰️ Cập nhật ảnh radar tự động"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if "nothing to commit" in result.stderr.lower():
            print("ℹ️ Không có thay đổi để commit.")
        else:
            subprocess.run(["git", "push"], check=True)
            print("✅ Đã đẩy lên GitHub thành công.")

    except subprocess.CalledProcessError as e:
        print("❌ Lỗi Git:", e)

# === Chạy chính ===
if __name__ == "__main__":
    delete_old_images()
    latest_images = get_latest_images()
    if latest_images:
        update_html(latest_images)
        git_push()
    else:
        print("⚠️ Không tìm thấy ảnh radar nào.")
