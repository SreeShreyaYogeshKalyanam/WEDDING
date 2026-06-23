import os, numpy as np
from PIL import Image
SRC = r"E:\Shreya Mrg\images"
for f in ["Welcoming.jpeg", "Marriage.jpeg", "Groom.jpeg"]:
    a = np.asarray(Image.open(os.path.join(SRC, f)).convert("RGB"))
    mn = a.min(2); mx = a.max(2); sat = mx - mn
    lowsat = sat <= 38
    light = mn >= 150
    cand = a[lowsat & light]
    # histogram of the min-channel value among low-sat light pixels
    vals = cand.min(1) if len(cand) else np.array([])
    print(f.split('.')[0])
    if len(vals):
        for lo in range(150, 256, 10):
            pct = ((vals >= lo) & (vals < lo+10)).mean()*100
            bar = "#" * int(pct/2)
            print(f"  {lo:3d}-{lo+9:3d}: {pct:5.1f}% {bar}")
