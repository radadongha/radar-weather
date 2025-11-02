import os
import time
import io
import re
from datetime import datetime, timedelta, timezone
from PIL import Image, ImageDraw, ImageFont
import pyautogui
import win32clipboard
import win32con
import schedule

# === Cấu hình ===
RADA_FOLDER = r"D:\WinSCP\RADA"
GROUP_NAME = "CQ Quân"   # 👈 chỉnh lại tên nhóm
INTERVAL_HOURS = 1                     # gửi lại mỗi bao lâu (giờ)

# === Lấy ảnh mới nhất ===
def get_latest_image(folder):
    images = [os.path.join(folder, f) for f in os.listdir(folder)
              if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    if not images:
        return None
    return max(images, key=os.path.getmtime)

# === Tách thời gian từ tên file ===
def extract_time_from_filename(filename):
    m = re.search(r'(\d{6})(\d{6})', filename)
    if not m:
        return None
    date_part, time_part = m.groups()
    try:
        dt = datetime.strptime(date_part + time_part, "%y%m%d%H%M%S")
        return dt
    except Exception:
        return None

# === Chèn chú thích vào ảnh ===
def add_caption(image_path, save_path):
    img = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(img)

    # Lấy thời gian từ tên file
    fname = os.path.basename(image_path)
    dt = extract_time_from_filename(fname)
    if dt:
        # chuyển sang giờ Việt Nam (UTC+7)
        vn_time = dt.replace(tzinfo=timezone.utc) + timedelta(hours=7)
        caption = f"Ảnh Max lúc {vn_time.strftime('%H:%M')} ngày {vn_time.strftime('%d/%m/%Y')}"
    else:
        caption = "Ảnh radar mới nhất"

    # Font chữ
    try:
        font = ImageFont.truetype("arial.ttf", 28)
    except:
        font = ImageFont.load_default()

    # Tính kích thước chữ bằng textbbox (thay cho textsize)
    bbox = draw.textbbox((0, 0), caption, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    pad = 10
    new_h = img.height + text_h + pad * 2
    new_img = Image.new("RGB", (img.width, new_h), (255, 255, 255))
    new_img.paste(img, (0, 0))

    draw2 = ImageDraw.Draw(new_img)
    text_x = (img.width - text_w) // 2
    text_y = img.height + pad
    draw2.text((text_x, text_y), caption, fill=(0, 0, 0), font=font)

    new_img.save(save_path)
    return save_path

# === Đưa ảnh vào clipboard ===
def image_to_clipboard(img_path):
    img = Image.open(img_path).convert("RGB")
    output = io.BytesIO()
    img.save(output, "BMP")
    data = output.getvalue()[14:]
    output.close()
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardData(win32con.CF_DIB, data)
    win32clipboard.CloseClipboard()

# === Gửi qua Zalo ===
def send_to_zalo():
    latest = get_latest_image(RADA_FOLDER)
    if not latest:
        print("⚠️ Không tìm thấy ảnh radar.")
        return

    print(f"🛰️ Ảnh mới nhất: {latest}")
    out_img = os.path.join(RADA_FOLDER, "send_temp.jpg")
    add_caption(latest, out_img)
    image_to_clipboard(out_img)
    time.sleep(0.3)

    # Chuyển qua Zalo
    pyautogui.hotkey('alt', 'tab')
    time.sleep(0.8)

    # Nếu muốn tự tìm nhóm (bỏ comment dưới và chỉnh tên)
    # import pyperclip
    # pyautogui.hotkey('ctrl', 'f')
    # time.sleep(0.4)
    # pyperclip.copy(GROUP_NAME)
    # pyautogui.hotkey('ctrl', 'v')
    # time.sleep(0.4)
    # pyautogui.press('enter')
    # time.sleep(0.6)

    pyautogui.hotkey('ctrl', 'v')
    time.sleep(1)
    pyautogui.press('enter')
    print("✅ Đã gửi ảnh có chú thích:", os.path.basename(out_img))

# === Lên lịch ===
schedule.every(INTERVAL_HOURS).hours.do(send_to_zalo)

print(f"🚀 Auto gửi ảnh radar mỗi {INTERVAL_HOURS} giờ. Đảm bảo Zalo đang mở sẵn.")
send_to_zalo()  # chạy ngay lần đầu

while True:
    schedule.run_pending()
    time.sleep(10)
