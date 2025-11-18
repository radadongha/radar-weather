import os
import shutil
import glob
import datetime
import subprocess
from PIL import Image

# --- cấu hình ---
RADARS = {
    "Đông Hà": {
        "source": "D:/WinSCP/RADA",
        "target": "rada_dongha"
    },
    "Tam Kỳ": {
        "source": "D:/WinSCP/tamky/RADA",
        "target": "rada_tamky"
    }
}
HTML_FILE = "index.html"
LEGEND_ORIGINAL = "legend_original.png"
NUM_IMAGES = 5

def extract_datetime(filename):
    name = os.path.basename(filename)
    try:
        # tìm chuỗi số dài >= 10 trong tên file
        import re
        match = re.search(r"(\d{10,12})", name)
        if not match:
            return None
        digits = match.group(1)

        # nếu có 12 số → YYMMDDHHMMSS
        if len(digits) >= 12:
            y = int(digits[0:2]) + 2000
            m = int(digits[2:4])
            d = int(digits[4:6])
            h = int(digits[6:8])
            mi = int(digits[8:10])
            # giây có thể có hoặc không
            return datetime.datetime(y, m, d, h, mi)
        # nếu chỉ có 10 số → YYMMDDHHMM
        elif len(digits) == 10:
            y = int(digits[0:2]) + 2000
            m = int(digits[2:4])
            d = int(digits[4:6])
            h = int(digits[6:8])
            mi = int(digits[8:10])
            return datetime.datetime(y, m, d, h, mi)
        else:
            return None
    except:
        return None


def resize_legend(input_path, output_path, scale=0.7):
    """Resize thang màu"""
    try:
        img = Image.open(input_path)
        new_size = (int(img.width * scale), int(img.height * scale))
        img = img.resize(new_size, Image.LANCZOS)
        img.save(output_path)
        print(f"✅ Đã resize legend cho {output_path}")
    except Exception as e:
        print(f"❌ Lỗi resize legend {output_path}: {e}")

# --- xử lý từng radar ---
all_infos = {}
for radar_name, cfg in RADARS.items():
    os.makedirs(cfg["target"], exist_ok=True)

    # Resize legend
    legend_out = os.path.join(cfg["target"], "legend.png")
    if os.path.exists(LEGEND_ORIGINAL):
        resize_legend(LEGEND_ORIGINAL, legend_out)

    # Lấy ảnh mới nhất
    all_images = sorted(glob.glob(os.path.join(cfg["source"], "*.jpg")), reverse=True)
    selected = all_images[:NUM_IMAGES]

    infos = []
    for src in reversed(selected):
        dst = os.path.join(cfg["target"], os.path.basename(src))
        shutil.copy2(src, dst)
        dt = extract_datetime(src)
        if dt:
            infos.append((os.path.basename(dst), dt.strftime("%d/%m/%Y %H:%M")))
    all_infos[radar_name] = (cfg["target"], infos)

    # Dọn ảnh cũ
    keep_files = [os.path.join(cfg["target"], f) for f, _ in infos]
    for f in glob.glob(os.path.join(cfg["target"], "*.jpg")):
        if f not in keep_files:
            os.remove(f)

def has_changes():
    result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
    return result.stdout.strip() != ""
if has_changes():
    print("🔄 Có thay đổi, tiến hành commit & push...")
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "🛰️ Cập nhật ảnh radar Đông Hà & Tam Kỳ"], check=True)
    subprocess.run(["git", "push"], check=True)
    print("✅ Đã commit & push lên GitHub.")
else:
    print("ℹ️ Không có thay đổi, bỏ qua commit.")

# --- tạo index.html song song ---
html = """<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<title>Radar Thời Tiết Đông Hà & Tam Kỳ</title>
<meta http-equiv="refresh" content="600">
<style>
body {font-family: Arial; background:#000; color:#fff; margin:0;}
.container {display:flex; justify-content:space-around; align-items:flex-start; gap:20px; padding:10px;}
.radar-block {flex:1; text-align:center;}
.image-container {display:flex; justify-content:center; align-items:center; max-width:95%; gap:5px;}
.radar-wrapper {position:relative;}
.timestamp {position:absolute; top:10px; left:50%; transform:translateX(-50%); background:rgba(0,0,0,0.7); padding:4px 12px; border-radius:10px; font-size:16px;}
#legend {max-height:90vh;}
.controls {margin:10px; font-size:20px;}
button {font-size:18px; padding:4px 8px; margin:0 3px; border-radius:6px; border:none; background:#333; color:#fff; cursor:pointer;}
button:hover {background:#555;}
</style>
</head>
<body>
<h2 style="text-align:center;">🛰️ Ảnh Radar Đông Hà & Tam Kỳ</h2>
<div class="container">
"""

for radar_name, (target, infos) in all_infos.items():
    html += f"""<div class="radar-block">
    <h3>{radar_name}</h3>
    <div class="controls">
        <button onclick="prevImage('{target}')">⏮️</button>
        <button onclick="togglePlay('{target}')">⏯️</button>
        <button onclick="nextImage('{target}')">⏭️</button>
        <button onclick="openFullscreen()">🖥️</button>
    </div>
    <div class="image-container">
        <div class="radar-wrapper">
            <div class="timestamp" id="timestamp_{target}"></div>
            <img id="radar_{target}" src="" alt="Radar Image" style="max-height:70vh;">
        </div>
        <img id="legend" src="{target}/legend.png" alt="Legend" style="max-height:70vh;">
    </div>
</div>
"""

html += "</div>\n"

# --- JS cho cả 2 radar ---
html += "<script>\n"
for radar_name, (target, infos) in all_infos.items():
    html += f"const images_{target} = [\n"
    for fn, dt in infos:
        html += f'["{target}/{fn}", "{dt}"],\n'
    html += "];\n"
    html += f"""
let current_{target} = 0;
let playing_{target} = true;
let interval_{target} = setInterval(()=>nextImage('{target}'), 1000);

function updateImage(id) {{
  const imgs = eval("images_"+id);
  const cur = eval("current_"+id);
  document.getElementById("radar_"+id).src = imgs[cur][0];
  document.getElementById("timestamp_"+id).innerText = imgs[cur][1];
}}
function nextImage(id) {{
  const imgs = eval("images_"+id);
  let cur = eval("current_"+id);
  cur = (cur+1) % imgs.length;
  eval("current_"+id+"=cur");
  updateImage(id);
}}
function prevImage(id) {{
  const imgs = eval("images_"+id);
  let cur = eval("current_"+id);
  cur = (cur-1+imgs.length) % imgs.length;
  eval("current_"+id+"=cur");
  updateImage(id);
}}
function togglePlay(id) {{
  let playing = eval("playing_"+id);
  if (playing) {{
    clearInterval(eval("interval_"+id));
  }} else {{
    eval("interval_"+id+"=setInterval(()=>nextImage(id),1000)");
  }}
  eval("playing_"+id+"=!playing");
}}
updateImage("{target}");
"""
html += "</script>\n</body></html>"

with open(HTML_FILE,"w",encoding="utf-8") as f:
    f.write(html)

print("✅ Đã tạo index.html song song cho Đông Hà & Tam Kỳ.")

# --- Git commit & push ---
def run_git(cmd):
    return subprocess.run(["git"] + cmd, cwd=os.path.dirname(os.path.abspath(__file__)), text=True, capture_output=True)

def safe_git_commit():
    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "🛰️ Cập nhật ảnh radar Đông Hà & Tam Kỳ"], check=True)
        subprocess.run(["git", "push", "origin", "main"], check=True)
        print("✅ Đã commit & push lên GitHub")
    except subprocess.CalledProcessError as e:
        print("❌ Lỗi Git:", e)

safe_git_commit()
