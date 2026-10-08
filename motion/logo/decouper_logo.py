"""Découpe le logo MBC Cargo (assets/logo-source.jpg) en calques PNG transparents pour l'animation.

Chaque calque a la même taille (le cadre du logo), on les empile donc sans recalage :
emblème (courbe extérieure, bateau, traits cyan), lettres M B C, lettres c a r g o, et le logo complet.
Usage : python motion/logo/decouper_logo.py
"""
import json, os
from collections import deque
import numpy as np
from PIL import Image

ICI = os.path.dirname(os.path.abspath(__file__))
src = np.asarray(Image.open(os.path.join(ICI, "assets", "logo-source.jpg")).convert("RGB")).astype(float)
X0, Y0, X1, Y1 = 175, 205, 1115, 445          # cadre du logo dans la capture
img = src[Y0:Y1, X0:X1]
H, W, _ = img.shape
BLEU, CYAN = np.array([21, 102, 167]), np.array([13, 163, 198])

# Opacité : mélange encre / blanc, estimé sur le canal rouge (bas pour les deux couleurs)
alpha = np.clip((255 - img[..., 0]) / (255 - 21), 0, 1)
alpha[alpha < 0.06] = 0
est_cyan = img[..., 1] > 135 + (255 - img[..., 1]) * 0  # vert élevé = cyan (les bords clairs sont filtrés par alpha)
est_cyan = (img[..., 1] - img[..., 0] > 105) & (img[..., 2] > 150)
yy, xx = np.mgrid[0:H, 0:W]
X, Y = xx + X0, yy + Y0

def composantes(mask):
    """Étiquetage 4-connexe simple (BFS)."""
    lab = np.zeros(mask.shape, int); n = 0
    for sy, sx in zip(*np.nonzero(mask)):
        if lab[sy, sx]: continue
        n += 1; lab[sy, sx] = n; q = deque([(sy, sx)])
        while q:
            y, x = q.popleft()
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                v, u = y + dy, x + dx
                if 0 <= v < H and 0 <= u < W and mask[v, u] and not lab[v, u]:
                    lab[v, u] = n; q.append((v, u))
    return lab, n

def calque(nom, sel, couleur):
    rgba = np.zeros((H, W, 4), np.uint8)
    rgba[..., :3] = couleur
    rgba[..., 3] = (alpha * sel * 255).astype(np.uint8)
    Image.fromarray(rgba).save(os.path.join(ICI, "assets", "calques", f"{nom}.png"))

emb = X < 600
# Pièces bleues de l'emblème : courbe extérieure et bateau (composantes connexes)
bleu_emb = emb & ~est_cyan & (alpha > 0.35)
lab, n = composantes(bleu_emb)
tailles = sorted(((np.sum(lab == i), i) for i in range(1, n + 1)), reverse=True)
grandes = [i for t, i in tailles[:2]]
infos = {}
for i in grandes:
    ys, xs = np.nonzero(lab == i)
    infos[i] = xs.min()
courbe, bateau = sorted(grandes, key=lambda i: infos[i])   # la courbe démarre le plus à gauche
def dilate(m, r=2):
    out = m.copy()
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            out |= np.roll(np.roll(m, dy, 0), dx, 1)
    return out
m_courbe, m_bateau = dilate(lab == courbe), dilate(lab == bateau)
calque("emb-courbe", emb & ~est_cyan & m_courbe & ~m_bateau, BLEU)
calque("emb-bateau", emb & ~est_cyan & m_bateau, BLEU)
calque("emb-cyan", emb & est_cyan, CYAN)

# MBC : séparation oblique entre M et B (fente en italique), puis B / C
haut = (X >= 600) & (Y < 345)
coupe_mb = 825 - (Y - 218) * (36 / 112)
calque("l-M", haut & (X < coupe_mb), BLEU)
calque("l-B", haut & (X >= coupe_mb) & (X < 956), BLEU)
calque("l-C", haut & (X >= 956), BLEU)
# cargo : une colonne par lettre
for nom, (a, b) in zip("cargo", [(600, 685), (685, 790), (790, 875), (875, 980), (980, 1110)]):
    calque(f"l-{nom}", (X >= 600) & (Y >= 345) & (X >= a) & (X < b), BLEU)
# Logo complet (masque du reflet lumineux)
couleur = np.where(est_cyan[..., None], CYAN, BLEU)
rgba = np.zeros((H, W, 4), np.uint8); rgba[..., :3] = couleur; rgba[..., 3] = (alpha * 255).astype(np.uint8)
Image.fromarray(rgba).save(os.path.join(ICI, "assets", "calques", "logo-complet.png"))
json.dump({"largeur": W, "hauteur": H}, open(os.path.join(ICI, "assets", "calques", "cadre.json"), "w"))
print("calques :", sorted(os.listdir(os.path.join(ICI, "assets", "calques"))), "cadre", W, "x", H)
