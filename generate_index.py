import os

# Thư mục chứa ảnh radar
image_folder = 'rada'
image_bounds = [[15.5, 105.5], [18.5, 108.5]]  # tùy chỉnh theo ảnh

# Lấy danh sách file PNG radar, sắp xếp theo tên (tức là theo thời gian)
files = sorted([f for f in os.listdir(image_folder) if f.endswith('.png')])

# Tạo danh sách mã timestamp từ tên file (không có đuôi)
timestamps = [os.path.splitext(f)[0] for f in files]

# Tạo HTML file
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(f"""<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8" />
  <title>Ảnh Radar Đông Hà</title>
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
  <style>
    html, body {{ height: 100%; margin: 0; }}
    #map {{ height: 90%; }}
    #controls {{
      height: 10%;
      display: flex;
      justify-content: center;
      align-items: center;
      background: #f0f0f0;
    }}
    #timeSelect {{
      padding: 6px;
      font-size: 16px;
    }}
  </style>
</head>
<body>
  <div id="map"></div>
  <div id="controls">
    <label for="timeSelect">🕒 Chọn thời điểm radar:</label>
    <select id="timeSelect">
""")
    # Thêm các option
    for name in timestamps:
        time_str = name[-10:-4]  # ví dụ lấy 065004 từ dong-ha-mon250723065004
        f.write(f'      <option value="{name}">{time_str} (VN)</option>\n')

    # Phần JavaScript
    f.write(f"""    </select>
  </div>

  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  <script>
    const radarFolder = '{image_folder}/';
    const imageBounds = {image_bounds};

    const timestamps = {timestamps};

    const map = L.map('map').setView([16.8, 107.1], 7);

    L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
      attribution: '&copy; OpenStreetMap contributors'
    }}).addTo(map);

    let overlay = null;

    function updateRadarImage(filename) {{
      const imageUrl = radarFolder + filename + '.png';
      if (overlay) map.removeLayer(overlay);
      overlay = L.imageOverlay(imageUrl, imageBounds, {{ opacity: 0.6 }});
      overlay.addTo(map);
    }}

    // Tải ảnh đầu tiên
    updateRadarImage(timestamps[0]);

    document.getElementById('timeSelect').addEventListener('change', (e) => {{
      updateRadarImage(e.target.value);
    }});
  </script>
</body>
</html>""")

print("✅ Đã tạo xong file index.html với dropdown ảnh radar.")
