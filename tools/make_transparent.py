"""
Strip the baked-in checkerboard / black background from the mascot JPEGs and
export clean transparent PNGs. Per-image strategy (see STRATEGY below).
"""
import os
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage

SRC = r"E:\Shreya Mrg\images"
OUT = r"E:\Shreya Mrg\images\png"
os.makedirs(OUT, exist_ok=True)

# method per file
KEEP_AS_IS = {"Together.jpeg"}          # full illustration, own background
BLACK_BG   = {"Engagement.jpeg"}        # solid black background
CONTAINS_GRAY = {"Welcoming.jpeg", "Marriage.jpeg"}  # checker around a framed scene
# everything else -> border-connected + fill holes


def lowsat_light(rgb, min_light=160):
    mx = rgb.max(2); mn = rgb.min(2)
    return ((mx - mn) <= 40) & (mn >= min_light)


def alpha_from_mask(rgb, fg_mask):
    alpha = np.where(fg_mask, 255, 0).astype(np.uint8)
    out = Image.fromarray(np.dstack([rgb, alpha]), "RGBA")
    a = out.getchannel("A").filter(ImageFilter.GaussianBlur(0.8))
    out.putalpha(a)
    return out


def border_connected(rgb, cand, fill_holes=True):
    labeled, _ = ndimage.label(cand)
    border = set(labeled[0]) | set(labeled[-1]) | set(labeled[:, 0]) | set(labeled[:, -1])
    border.discard(0)
    bg = np.isin(labeled, list(border))
    fg = ~bg
    if fill_holes:
        fg = ndimage.binary_fill_holes(fg)
    return fg


def contains_gray(rgb):
    cand = lowsat_light(rgb, 160)
    gray = cand & (rgb.min(2) < 235)        # the gray checker tone (not pure white)
    labeled, n = ndimage.label(cand)
    # A region is background only if it (a) contains the gray checker tone AND
    # (b) is large -- this removes the trapped checkerboard but PROTECTS tiny
    # enclosed light spots such as eye-whites and teeth (which JPEG renders
    # slightly gray and would otherwise be erased).
    min_area = max(900, int(0.0015 * rgb.shape[0] * rgb.shape[1]))
    tot = ndimage.sum(np.ones_like(gray), labeled, index=range(1, n + 1))
    gtot = ndimage.sum(gray, labeled, index=range(1, n + 1))
    frac = np.divide(gtot, tot, out=np.zeros_like(tot), where=tot > 0)
    bg_labels = [i + 1 for i in range(n) if frac[i] > 0.12 and tot[i] >= min_area]
    bg = np.isin(labeled, bg_labels)
    return ~bg


def autocrop(im):
    bbox = im.getbbox()
    return im.crop(bbox) if bbox else im


for f in sorted(os.listdir(SRC)):
    src = os.path.join(SRC, f)
    if not os.path.isfile(src) or not f.lower().endswith((".jpeg", ".jpg", ".png")):
        continue
    slug = {
        "Bride & Groom": "bride-groom", "Bride": "bride", "Groom": "groom",
        "Engagement": "engagement", "Marriage": "marriage",
        "Welcoming": "welcoming", "Together": "together",
    }.get(os.path.splitext(f)[0], os.path.splitext(f)[0].lower().replace(" ", "-"))
    dst = os.path.join(OUT, slug + ".png")

    if f in KEEP_AS_IS:
        Image.open(src).convert("RGBA").save(dst)
        print(f"[keep ] {f}")
        continue

    rgb = np.asarray(Image.open(src).convert("RGB"))

    if f in BLACK_BG:
        cand = rgb.max(2) <= 55
        fg = border_connected(rgb, cand, fill_holes=True)
    elif f in CONTAINS_GRAY:
        fg = contains_gray(rgb)
    else:
        cand = lowsat_light(rgb, 150)
        fg = border_connected(rgb, cand, fill_holes=True)

    out = autocrop(alpha_from_mask(rgb, fg))
    out.save(dst)
    print(f"[clean] {f:20s} -> {out.width}x{out.height}")

print("done ->", OUT)
