from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

LOGOS = {
    "KBS1": ("#0066CC", "KBS 1"),
    "KBS2": ("#E67E22", "KBS 2"),
    "MBC":  ("#8E44AD", "MBC"),
    "EBS1": ("#27AE60", "EBS 1"),
    "EBS2": ("#16A085", "EBS 2"),
    "SBS":  ("#0096D6", "SBS"),
}

out = Path("logos")
out.mkdir(exist_ok=True)
font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
font = ImageFont.truetype(font_path, 64)

for name, (bg, label) in LOGOS.items():
    im = Image.new("RGBA", (320, 180), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((10, 12, 310, 169), radius=24, fill=bg)
    box = d.textbbox((0, 0), label, font=font)
    tw, th = box[2]-box[0], box[3]-box[1]
    x = (320 - tw) / 2
    y = (180 - th) / 2 - 5
    d.text((x, y), label, font=font, fill="white")
    im.save(out / f"{name}.png", optimize=True)
