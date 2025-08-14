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

    timestamp = f"{hour}h{minute} ngày {day}/{month}/{year}"
except:
    timestamp = "Không xác định thời gian"

# Mở ảnh (Pillow cần file có định dạng, nếu không có đuôi có thể thử "JPEG")
img = Image.open(latest_file)

# Tạo dải trắng phía dưới để chèn chữ
text_height = 50
new_img = Image.new("RGB", (img.width, img.height + text_height), "white")
new_img.paste(img, (0, 0))

# Chèn chữ
draw = ImageDraw.Draw(new_img)
font_size = max(20, img.width // 30)
try:
    font = ImageFont.truetype("arial.ttf", font_size)
except:
    font = ImageFont.load_default()

# Sử dụng textbbox để thay textsize
bbox = draw.textbbox((0,0), timestamp, font=font)
text_width = bbox[2] - bbox[0]
text_height_actual = bbox[3] - bbox[1]

x = (img.width - text_width) // 2
y = img.height + (text_height - text_height_actual) // 2
draw.text((x, y), timestamp, fill="black", font=font)

# Lưu ảnh
output_file = os.path.join(folder, "latest_with_time.jpg")
new_img.save(output_file)
print(f"Ảnh đã lưu: {output_file}")
