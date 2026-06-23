from PIL import Image
im = Image.open(r"E:\Shreya Mrg\images\png\welcoming.png").convert("RGBA")
bg = Image.new("RGBA", im.size, (255, 0, 255, 255))
comp = Image.alpha_composite(bg, im).convert("RGB")
# crop the upper third (faces) and enlarge
w, h = comp.size
faces = comp.crop((0, int(h*0.06), w, int(h*0.42)))
faces.save(r"E:\Shreya Mrg\tools\_check\welcoming_faces.png")
print("faces crop:", faces.size)
