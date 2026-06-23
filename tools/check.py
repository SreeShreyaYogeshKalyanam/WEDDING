import os
import numpy as np
from PIL import Image

OUT = r"E:\Shreya Mrg\images\png"
CHK = r"E:\Shreya Mrg\tools\_check"
os.makedirs(CHK, exist_ok=True)

for f in os.listdir(OUT):
    if not f.lower().endswith(".png"):
        continue
    im = Image.open(os.path.join(OUT, f)).convert("RGBA")
    a = np.asarray(im.getchannel("A"))
    transparent_pct = (a < 16).mean() * 100
    # composite on magenta to eyeball halos
    bg = Image.new("RGBA", im.size, (255, 0, 255, 255))
    comp = Image.alpha_composite(bg, im).convert("RGB")
    comp.thumbnail((300, 300))
    comp.save(os.path.join(CHK, f.replace(".png", "_onmagenta.png")))
    print(f"{f:22s} {im.width}x{im.height}  transparent={transparent_pct:5.1f}%")
