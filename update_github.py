import os
import shutil
import datetime
import subprocess

SOURCE_FOLDER = "D:/WinSCP/RADA"
DEST_FOLDER = "rada"
HTML_FILE = "index.html"
MAX_IMAGES = 5
IMAGE_EXT = ".jpg"

def list_images(folder):
    return sorted(
        [f for f in os.listdir(folder) if f.endswith(IMAGE_EXT)],
        key=lambda x: os.path.getmtime(os.path.join(folder, x)),
        reverse=True
    )

def copy_latest_images():
    images = list_images(SOURCE_FOLDER)[:MAX_IMAGES]
    os.makedirs(DEST_FOLDER, exist_ok=True)
    for img in images:
        src = os.path.join(SOURCE_FOLDER, img)
        dst = os.path.join(DEST_FOLDER, img)
        shutil.copy2(src, dst)
    return images

def delete_old_images(folder, keep_list):
    for f in os.listdir(folder):
        if f.endswith(IMAGE_EXT) and f not in keep_list:
            os.remove(os.path.join(folder, f))

def generate_html(image_list):
    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write("""<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <title>Ảnh Radar Thời Tiết</title>
  <style>
    body { background-color: black; color: white; text-align: center; font-family: Arial, sans-serif; }
    img { max-width: 90%%; max-height: 90%%; margin: 0 auto; display: block; }
    #timestamp { margin-top: 10px; font-size: 1.2em; color: #ccc; }
  </style>
</head>
<body>
  <h1>🛰️ Ảnh Radar Mới Nhất</h1>
  <img id="radar-image" src="rada/%s">
  <div id="timestamp">🕒 Giờ radar: Không rõ</div>
  <script>
    const images = [%s];
    let current = 0;
    const imgTag = document.getElementById("radar-image");
    function updateImage() {
      imgTag.src = images[current];
      current = (current + 1) %% images.length;
    }
    setInterval(updateImage, 1000);
    const lastImage = images[images.length - 1];
    const match = lastImage.match(/(\\d{12})\\.MAX\\d{4}/);
    if (match) {
      const timePart = match[1];
      const nam = timePart.slice(0,2);
      const thang = timePart.slice(2,4);
      const ngay = timePart.slice(4,6);
      const gio = timePart.slice(6,8);
      const phut = timePart.slice(8,10);
      const giay = timePart.slice(10,12);
      document.getElementById("timestamp").innerText = 
        `🕒 Giờ radar: ${gio}:${phut}:${giay} ngày ${ngay}/${thang}/20${nam}`;
    }
  </script>
</body>
</html>""" % (image_list[-1], ', '.join([f'"rada/{img}"' for img in image_list])))

def git_commit_push():
    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "🛰️ Cập nhật ảnh radar tự động"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("✅ Đã đẩy lên GitHub thành công.")
    except subprocess.CalledProcessError as e:
        print("❌ Lỗi Git:", e)

def main():
    print("🚀 Đang cập nhật ảnh radar...")
    latest_images = copy_latest_images()
    delete_old_images(DEST_FOLDER, latest_images)
    generate_html(latest_images)
    print("✅ Đã cập nhật danh sách ảnh vào index.html")
    git_commit_push()

if __name__ == "__main__":
    main()
