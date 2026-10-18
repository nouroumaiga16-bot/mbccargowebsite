"""Visuels du bracelet LED, sans aucun texte chinois.
- menthe.png / noir.png : bracelet détouré (fond blanc retiré par remplissage depuis les bords)
- photos recadrées hors des zones de texte : poignet, vibration, eau, recharge
Usage : python motion/bracelet/decouper.py
"""
import os
from collections import deque
import numpy as np
from PIL import Image, ImageFilter

ECRAN_X = 330  # au-delà, plus d'écran LED (chiffres blancs à garder)
ICI = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ICI, "sources"); OUT = os.path.join(ICI, "assets")

def detoure(nom, boite):
    im = Image.open(os.path.join(SRC, nom + ".jpg")).convert("RGB").crop(boite)
    a = np.asarray(im).astype(int); H, W, _ = a.shape
    clair = (a.min(axis=2) > 236)
    fond = np.zeros((H, W), bool); q = deque()
    for y in range(H):
        for x in (0, W - 1):
            if clair[y, x] and not fond[y, x]: fond[y, x] = True; q.append((y, x))
    for x in range(W):
        for y in (0, H - 1):
            if clair[y, x] and not fond[y, x]: fond[y, x] = True; q.append((y, x))
    while q:
        y, x = q.popleft()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            yy, xx = y + dy, x + dx
            if 0 <= yy < H and 0 <= xx < W and clair[yy, xx] and not fond[yy, xx]:
                fond[yy, xx] = True; q.append((yy, xx))
    # zones blanches enfermées (l'intérieur de la boucle) : grandes composantes claires hors de l'écran LED
    vu = fond.copy()
    for y0 in range(H):
        for x0 in range(W):
            if clair[y0, x0] and not vu[y0, x0]:
                comp = [(y0, x0)]; vu[y0, x0] = True; k = 0
                while k < len(comp):
                    y, x = comp[k]; k += 1
                    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        yy, xx = y + dy, x + dx
                        if 0 <= yy < H and 0 <= xx < W and clair[yy, xx] and not vu[yy, xx]:
                            vu[yy, xx] = True; comp.append((yy, xx))
                if len(comp) > 1500 and min(c[1] for c in comp) > ECRAN_X:
                    for y, x in comp: fond[y, x] = True
    alpha = Image.fromarray(np.where(fond, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.9))
    im.putalpha(alpha); im.save(os.path.join(OUT, nom + ".png"))
    print(nom, im.size)

detoure("menthe", (600, 270, 1260, 1290))
detoure("noir", (600, 265, 1260, 1290))
for nom, boite in (("poignet", (0, 335, 1320, 1140)), ("vibration", (0, 440, 1320, 1756)),
                   ("eau", (0, 460, 1320, 1766)), ("recharge", (0, 0, 1320, 1470))):
    Image.open(os.path.join(SRC, nom + ".jpg")).convert("RGB").crop(boite).save(os.path.join(OUT, nom + ".jpg"), quality=92)
    print(nom, boite)
