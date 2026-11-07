from io import BytesIO
from pathlib import Path
import requests
from PIL import Image
import cairosvg

# 실제 방송사 CI 형태를 사용하되, 사용자가 지정한 채널 색상을 적용한다.
SOURCES = {
    "KBS1": ("https://commons.wikimedia.org/wiki/Special:Redirect/file/KBS_1_logo.svg", "#0066CC", True),
    "KBS2": ("https://commons.wikimedia.org/wiki/Special:Redirect/file/KBS_2_logo.svg", "#E67E22", True),
    "MBC":  ("https://commons.wikimedia.org/wiki/Special:Redirect/file/MBC_logo.png", "#8E44AD", True),
    "EBS1": ("https://commons.wikimedia.org/wiki/Special:Redirect/file/EBS_1TV_Logo.svg", "#27AE60", True),
    "EBS2": ("https://commons.wikimedia.org/wiki/Special:Redirect/file/EBS_2TV_Logo.svg", "#16A085", True),
    # SBS는 사용자가 제공한 공식 CI와 동일한 원래 멀티컬러를 유지한다.
    "SBS":  ("https://commons.wikimedia.org/wiki/Special:Redirect/file/Seoul_Broadcasting_System_logo.svg", None, False),
}

OUT_W, OUT_H = 600, 200
MAX_W, MAX_H = 540, 150
UA = {"User-Agent": "TrokyPlexLogoBuilder/1.0"}

def fetch_image(url: str) -> Image.Image:
    r = requests.get(url, headers=UA, timeout=30, allow_redirects=True)
    r.raise_for_status()
    data = r.content
    ctype = (r.headers.get("content-type") or "").lower()
    if "svg" in ctype or data.lstrip().startswith(b"<svg") or b"<svg" in data[:500]:
        data = cairosvg.svg2png(bytestring=data, output_width=1600)
    return Image.open(BytesIO(data)).convert("RGBA")

def recolor(img: Image.Image, hex_color: str) -> Image.Image:
    target = tuple(int(hex_color[i:i+2], 16) for i in (1, 3, 5))
    px = img.load()
    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = px[x, y]
            if a == 0:
                continue
            # CI 내부의 흰색 요소는 유지하고 나머지 유색/회색 요소만 지정색으로 변경한다.
            if r >= 245 and g >= 245 and b >= 245:
                px[x, y] = (255, 255, 255, a)
            else:
                px[x, y] = (*target, a)
    return img

def normalize(img: Image.Image) -> Image.Image:
    alpha = img.getchannel("A")
    bbox = alpha.getbbox()
    if bbox:
        img = img.crop(bbox)

    scale = min(MAX_W / img.width, MAX_H / img.height)
    nw = max(1, round(img.width * scale))
    nh = max(1, round(img.height * scale))
    img = img.resize((nw, nh), Image.Resampling.LANCZOS)

    canvas = Image.new("RGBA", (OUT_W, OUT_H), (0, 0, 0, 0))
    canvas.alpha_composite(img, ((OUT_W - nw) // 2, (OUT_H - nh) // 2))
    return canvas

out = Path("logos")
out.mkdir(exist_ok=True)

for name, (url, color, do_recolor) in SOURCES.items():
    img = fetch_image(url)
    if do_recolor and color:
        img = recolor(img, color)
    img = normalize(img)
    img.save(out / f"{name}.png", optimize=True)
    print(f"{name}: {img.size}")
