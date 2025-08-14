import os
from PIL import Image, ImageDraw, ImageFont

# Thư mục chứa ảnh
folder = r"D:\anhlambantin"

# Lấy tất cả file thực trong thư mục
files = [os.path.join(folder, f) for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]

if not files:
    raise Exception("Không có file nào trong thư mục.")

# Lấy file mới nhất
latest_file = max(files, key=os.path.getmtime)
print(f"File mới nhất: {latest_file}")

# Lấy tên file không có đuôi
basename = os.path.splitext(os.path.basename(latest_file))[0]

# Giả sử tên file dạng: 20250813_1710
try:
    date_part, time_part = basename.split("_")  # 20250813 và 1710
    year = date_part[:4]
    month = date_part[4:6]
    day = date_part[6:8]
    hour = time_part[:2]
    minute = time_part[2:4]

    timestamp = f"Hình 1. Ảnh Max lúc {hour}h{minute} ngày {day}/{month}/{year}"
except:
    timestamp = "Hình 1. Không xác định thời gian"

# Mở ảnh
img = Image.open(latest_file)

# Tạo dải trắng phía dưới để chèn chữ
draw = ImageDraw.Draw(img)
font_size = int(max(20, img.width // 30) * 1.3)  # tăng 1.3 lần

try:
    font = ImageFont.truetype("arial.ttf", font_size)
except:
    font = ImageFont.load_default()

# Dùng textbbox để tính kích thước chữ
bbox = draw.textbbox((0, 0), timestamp, font=font)
text_width = bbox[2] - bbox[0]
text_height_actual = bbox[3] - bbox[1]

padding = 10  # khoảng cách chữ với viền
text_area_height = text_height_actual + 2 * padding

# Tạo ảnh mới có thêm dải trắng
new_img = Image.new("RGB", (img.width, img.height + text_area_height), "white")
new_img.paste(img, (0, 0))

# Vẽ chữ
draw_new = ImageDraw.Draw(new_img)
x = (img.width - text_width) // 2
y = img.height + padding
draw_new.text((x, y), timestamp, fill="black", font=font)

# Lưu ảnh mới
output_file = os.path.join(folder, f"{basename}_with_time.jpg")
new_img.save(output_file)
print(f"Ảnh đã lưu: {output_file}")
