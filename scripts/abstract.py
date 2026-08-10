"""把普桑画作处理成高度抽象的印刷残片 / 印章。

工艺链: 裁剪 → 低分辨率 → 抖动成 1-bit 网点 → 放大成粗颗粒 →
噪声侵蚀 (缺墨) → 单色油墨 + 轻微套印错位。
另产出一枚圆形干墨印章 (透明 PNG) 作为首页锚点。
"""

from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageOps
import os

SRC = os.path.join(os.path.dirname(__file__), "..", "public", "art")
OUT = os.path.join(SRC, "abstract")
os.makedirs(OUT, exist_ok=True)

PAPER = (244, 239, 227)
INK = (33, 30, 24)
CLAY = (191, 59, 27)
SEPIA = (94, 78, 54)


def crop_rel(path, crop):
    im = Image.open(os.path.join(SRC, path))
    w, h = im.size
    box = tuple(int(v * s) for v, s in zip(crop, (w, h, w, h)))
    return im.crop(box)


def dither_mask(img, small_w=170, contrast=1.5, out_w=1100):
    """低清抖动 → 粗网点油墨遮罩 (255 = 有墨)。"""
    g = ImageOps.autocontrast(img.convert("L"), cutoff=5)
    sw, sh = small_w, max(1, int(g.size[1] * small_w / g.size[0]))
    g = g.resize((sw, sh), Image.LANCZOS)
    g = ImageEnhance.Contrast(g).enhance(contrast)
    bw = g.convert("1")  # Floyd–Steinberg 抖动
    bw = bw.resize((out_w, int(sh * out_w / sw)), Image.NEAREST)
    return ImageOps.invert(bw.convert("L"))


def erode(mask, sigma=48, blur=7, cut=160):
    """噪声侵蚀: 手工印刷的缺墨与不均匀压力。"""
    noise = Image.effect_noise(mask.size, sigma).filter(ImageFilter.GaussianBlur(blur))
    keep = noise.point(lambda v: 0 if v > cut else 255)
    return ImageChops.multiply(mask, keep)


def scale_mask(mask, factor):
    return mask.point(lambda v: int(v * factor))


def print_sheet(name, src, crop, ink, small_w=170, misreg=(0, 0)):
    """平印残片: 纸底 + 单色粗网点, 可选套印错位的第二道墨。"""
    mask = erode(dither_mask(crop_rel(src, crop), small_w=small_w))
    sheet = Image.new("RGB", mask.size, PAPER)
    if misreg != (0, 0):
        ghost = ImageChops.offset(scale_mask(mask, 0.35), *misreg)
        sheet.paste(INK, (0, 0), ghost)
    sheet.paste(ink, (0, 0), mask)
    sheet.save(os.path.join(OUT, name), quality=88)
    print(name, sheet.size)


def seal(name, src, crop, ink, size=900, small_w=130):
    """圆形干墨印章: 透明 PNG, 环形边框 + 抖动图像, 统一磨损。"""
    img = crop_rel(src, crop)
    side = min(img.size)
    img = img.crop(((img.size[0] - side) // 2, (img.size[1] - side) // 2,
                    (img.size[0] + side) // 2, (img.size[1] + side) // 2))
    mask = dither_mask(img, small_w=small_w, out_w=size)
    mask = mask.crop((0, 0, size, size))

    circle = Image.new("L", (size, size), 0)
    d = ImageDraw.Draw(circle)
    m = int(size * 0.055)
    d.ellipse([m, m, size - m, size - m], fill=255)
    inner = ImageChops.multiply(mask, circle)

    ring = Image.new("L", (size, size), 0)
    d = ImageDraw.Draw(ring)
    rw = int(size * 0.016)
    d.ellipse([2, 2, size - 3, size - 3], outline=255, width=rw)
    gap = int(size * 0.03)
    d.ellipse([m - gap, m - gap, size - m + gap, size - m + gap],
              outline=255, width=max(2, rw // 2))

    total = erode(ImageChops.lighter(inner, ring), sigma=52, blur=6, cut=150)
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    layer = Image.new("RGBA", (size, size), ink + (255,))
    out.paste(layer, (0, 0), total)
    out.save(os.path.join(OUT, name))
    print(name, out.size)


# ——— 印章: 牧人辨认碑文, 陶土红干墨 ———
seal("arcadia-seal.png", "arcadia.jpg", (0.30, 0.24, 0.72, 0.86), CLAY)

# ——— 残片 (文章封面, 高抽象) ———
print_sheet("arcadia-ink.jpg", "arcadia.jpg", (0.18, 0.22, 0.62, 0.95), INK, misreg=(5, 3))
print_sheet("arcadia-clay.jpg", "arcadia.jpg", (0.18, 0.22, 0.62, 0.95), CLAY, misreg=(5, 3))
print_sheet("calm-ink.jpg", "calm.jpg", (0.05, 0.18, 0.95, 0.62), INK, small_w=200)
print_sheet("orpheus-ink.jpg", "orpheus.jpg", (0.08, 0.05, 0.52, 0.72), INK, misreg=(4, 2))
print_sheet("patmos-sepia.jpg", "patmos.jpg", (0.12, 0.25, 0.72, 0.92), SEPIA)
print_sheet("printemps-ink.jpg", "printemps.jpg", (0.25, 0.05, 0.85, 0.7), INK)
print("done")
