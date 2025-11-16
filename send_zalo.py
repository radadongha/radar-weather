import os
import time
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
import pyautogui
import win32clipboard
import win32con
import io
import pygetwindow as gw

# === CẤU HÌNH ===
RADA_FOLDER = r"D:\WinSCP\RADA"          # Thư mục chứa ảnh radar
FONT_PATH = r"C:\Windows\Fonts\arial.ttf" # Font chữ
INTERVAL_HOURS = 1                        # Gửi lại mỗi 1 giờ
GROUP_NAME = "CQ Quân"                    # Tên hội thoại cần gửi (chỉ cần chứa chuỗi này)

# === HÀM TÌM ẢNH MỚI NHẤT ===
def get_latest_image(folder):
    files = [f for f in os.listdir(folder) if f.lower().endswith((".jpg", ".png"))]
    if not files:
        return None
    files.sort(key=lambda x: os.path.getmtime(os.path.join(folder, x)), reverse=True)
    return os.path.join(folder, files[0])

# === HÀM THÊM DẢI TRẮNG + CHÚ THÍCH ===
def add_caption(image_path):
    try:
        img = Image.open(image_path)
        width, height = img.size
        new_img = Image.new("RGB", (width, height + 60), "white")
        new_img.paste(img, (0, 0))

        basename = os.path.basename(image_path)
        digits = ''.join([c for c in basename if c.isdigit()])
        caption = "Ảnh radar mới nhất"

        if len(digits) >= 12:
            try:
                radar_time = datetime.strptime(digits[:12], "%y%m%d%H%M%S")
                radar_time = radar_time + timedelta(hours=7)  # giờ VN
                caption = f"Ảnh Max lúc {radar_time.strftime('%H:%M')} ngày {radar_time.strftime('%d/%m/%Y')}"
            except Exception:
                pass

        draw = ImageDraw.Draw(new_img)
        try:
            font = ImageFont.truetype(FONT_PATH, 26)
        except:
            font = ImageFont.load_default()

        try:
            bbox = draw.textbbox((0, 0), caption, font=font)
            text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        except AttributeError:
            text_w, text_h = draw.textsize(caption, font=font)

        draw.text(((width - text_w) / 2, height + (60 - text_h) / 2), caption, fill="black", font=font)

        out_path = os.path.join(os.path.dirname(image_path), "zalo_send_temp.jpg")
        new_img.save(out_path, "JPEG")
        return out_path

    except Exception as e:
        print(f"⚠️ add_caption lỗi: {e}")
        return image_path

# === HÀM COPY ẢNH VÀO CLIPBOARD ===
def copy_image_to_clipboard(image_path):
    image = Image.open(image_path)
    output = io.BytesIO()
    image.convert("RGB").save(output, "BMP")
    data = output.getvalue()[14:]
    output.close()
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardData(win32con.CF_DIB, data)
    win32clipboard.CloseClipboard()
    print("📋 Ảnh đã được copy vào clipboard.")

# === HÀM TÌM CỬA SỔ ZALO GẦN GIỐNG ===
def find_zalo_window(partial_title):
    windows = gw.getAllTitles()
    for title in windows:
        if partial_title.lower() in title.lower():
            return title
    return None

# === HÀM GỬI ẢNH QUA ZALO ===
def send_image_to_zalo(window_title, image_path):
    zalo_title = find_zalo_window(window_title)
    if not zalo_title:
        print(f"❌ Không tìm thấy cửa sổ chứa: '{window_title}'")
        print("👉 Hãy mở sẵn cửa sổ chat Zalo và thử lại.\n")
        return False

    win = gw.getWindowsWithTitle(zalo_title)[0]
    if win.isMinimized:
        win.restore()
    win.activate()
    time.sleep(1)

    copy_image_to_clipboard(image_path)
    pyautogui.hotkey("ctrl", "v")
    time.sleep(1.2)
    pyautogui.press("enter")
    time.sleep(0.5)

    print(f"✅ Ảnh đã gửi qua Zalo: {zalo_title}\n")
    return True

# === CHƯƠNG TRÌNH CHÍNH ===
def main():
    print(f"\n🚀 Auto gửi ảnh radar qua Zalo mỗi {INTERVAL_HOURS} giờ.")
    print(f"🪪 Tên hội thoại (tìm gần đúng): {GROUP_NAME}\n")

    while True:
        try:
            latest_image = get_latest_image(RADA_FOLDER)
            if not latest_image:
                print("⚠️ Không tìm thấy ảnh radar trong thư mục.")
            else:
                print(f"🛰️ Ảnh mới nhất: {os.path.basename(latest_image)}")
                processed = add_caption(latest_image)
                print("🖼️ Đã thêm dải trắng và chú thích...")
                send_image_to_zalo(GROUP_NAME, processed)

            time.sleep(INTERVAL_HOURS * 3600)

        except Exception as e:
            print(f"⚠️ Lỗi: {e}")
            time.sleep(30)

if __name__ == "__main__":
    main()
