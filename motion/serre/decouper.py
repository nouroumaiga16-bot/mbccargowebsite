"""Extrait de la maquette fournie : le livre détouré (PNG transparent) et la photo de serre de la couverture.
Usage : python motion/serre/decouper.py
"""
import os
from collections import deque
import numpy as np
from PIL import Image, ImageFilter

ICI = os.path.dirname(os.path.abspath(__file__))
src = Image.open(os.path.join(ICI, "assets", "source-livre.jpg")).convert("RGB")
livre = src.crop((108, 88, 918, 1238))
a = np.asarray(livre).astype(int)
H, W, _ = a.shape
clair = a.sum(axis=2) > 705                      # fond blanc / gris très clair
fond = np.zeros((H, W), bool); q = deque()
for y in range(H):
    for x in (0, W - 1):
        if clair[y, x]: fond[y, x] = True; q.append((y, x))
for x in range(W):
    for y in (0, H - 1):
        if clair[y, x] and not fond[y, x]: fond[y, x] = True; q.append((y, x))
while q:                                         # remplissage depuis les bords : seul le fond est retiré
    y, x = q.popleft()
    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        v, u = y + dy, x + dx
        if 0 <= v < H and 0 <= u < W and clair[v, u] and not fond[v, u]:
            fond[v, u] = True; q.append((v, u))
# opacité : le fond disparaît, l'ombre grise devient une ombre semi-transparente
gris = 765 - a.sum(axis=2)
alpha = np.where(fond, 0, 255).astype(float)
yy, xx = np.mgrid[0:H, 0:W]
hors_livre = (xx < 104) | (yy > 1072 + (W - xx) * 0.075)   # sous et à gauche de la tranche : zone d'ombre
ombre = (~fond) & hors_livre & (a.sum(axis=2) > 560) & (np.abs(a[..., 0] - a[..., 2]) < 14)
alpha[ombre] = np.clip(gris[ombre] / 205 * 255, 0, 255)
m = Image.fromarray(alpha.astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8))
rgba = livre.copy(); rgba.putalpha(m)
rgba.save(os.path.join(ICI, "assets", "livre.png"))
# photo de serre (intérieur de la couverture, hors tranche et pastille)
src.crop((330, 478, 905, 935)).save(os.path.join(ICI, "assets", "serre-photo.jpg"), quality=92)
print("livre.png", rgba.size, "serre-photo.jpg")
