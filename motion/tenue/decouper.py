"""Découpe les deux visuels (blanc / noir) : le coureur seul (vignettes effacées) + les 5 vignettes.
Usage : python motion/tenue/decouper.py   →   motion/tenue/assets/{blanc,noir}-*.png|jpg
"""
import os
import numpy as np
from PIL import Image, ImageFilter

ICI = os.path.dirname(os.path.abspath(__file__))
# (x0, y0, x1, y1) des vignettes, bordure blanche comprise — identiques sur les deux visuels
VIGNETTES = {"veste": (30, 35, 232, 271), "tshirt": (30, 284, 232, 520), "short": (30, 533, 232, 754),
             "manches-longues": (571, 157, 790, 399), "legging": (571, 423, 790, 783)}
for coloris in ("blanc", "noir"):
    src = Image.open(os.path.join(ICI, "assets", f"source-{coloris}.jpg")).convert("RGB")
    a = np.asarray(src).astype(float)
    fond = a.copy()
    for nom, (x0, y0, x1, y1) in VIGNETTES.items():
        src.crop((x0, y0, x1, y1)).save(os.path.join(ICI, "assets", f"{coloris}-{nom}.png"))
        # efface la vignette : interpolation horizontale entre les bords gauche et droit
        g, d = max(x0 - 4, 0), min(x1 + 4, 799)
        for y in range(y0 - 2, min(y1 + 3, 800)):
            t = np.linspace(0, 1, d - g + 1)[:, None]
            fond[y, g:d + 1] = (1 - t) * a[y, g] + t * a[y, d]
    img = Image.fromarray(fond.clip(0, 255).astype(np.uint8))
    # léger flou sur les zones effacées seulement
    flou = img.filter(ImageFilter.GaussianBlur(6))
    masque = Image.new("L", img.size, 0)
    for x0, y0, x1, y1 in VIGNETTES.values():
        masque.paste(255, (x0 - 4, y0 - 2, x1 + 4, y1 + 3))
    img.paste(flou, mask=masque)
    img.save(os.path.join(ICI, "assets", f"{coloris}-coureur.jpg"), quality=92)
print("ok")
