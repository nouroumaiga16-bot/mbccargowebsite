"""Musique « épique et émotionnelle » (composée en code, libre de droits) + effets sonores de la vidéo
« Nafa Digital — Culture sous Serre » (62,5 s). La musique suit le montage :
  0 → 7,2 s    intro émotion : piano en arpèges + cordes qui montent, montée vers la révélation
  7,2 s        « Nafa Digital » : impact + entrée du groove (kick afro, claps, shaker, basse, cordes)
  25,4 → 39,4  les 5 étapes : arpège synthé en plus, ça pousse
  39,4 → 41    respiration (« Pas de théorie ») puis remontée
  46 → 58      final : grand refrain (mélodie principale, chœurs, crashs)
  58,1 s       impact final, accord qui résonne jusqu'à la fin
La voix off ElevenLabs (motion/nafa/voix-off/elevenlabs-voix-off.mp3) est normalisée et la musique baissée dessous.
Usage : python motion/nafa/son_nafa.py  →  motion/nafa/assets/voix-off.m4a, musique.m4a et sfx.m4a
"""
import os, subprocess, tempfile, wave
import numpy as np

ICI = os.path.dirname(os.path.abspath(__file__))
SFX = os.path.join(ICI, "..", "son", "sfx")
SR, D, BPM = 44100, 62.5, 112
BEAT = 60 / BPM; BAR = 4 * BEAT; N = int(SR * D)
rng = np.random.default_rng(62)
hz = lambda m: 440 * 2 ** ((m - 69) / 12)
L = np.zeros(N); R = np.zeros(N)

def add(sig, t0, g=1.0, pan=0.0):
    i = int(t0 * SR)
    if i >= N or i + len(sig) <= 0: return
    a = max(0, -i); i = max(0, i); j = min(N, i + len(sig) - a)
    s = g * sig[a:a + j - i]
    L[i:j] += s * np.sqrt(0.5 * (1 - pan)); R[i:j] += s * np.sqrt(0.5 * (1 + pan))

def tt(d): return np.arange(int(d * SR)) / SR

def passe_bas(x, fc):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); X *= 1 / np.sqrt(1 + (f / fc) ** 4)
    return np.fft.irfft(X, len(x))

def bruit(n, lo, hi):
    s = np.fft.rfft(rng.standard_normal(n)); f = np.fft.rfftfreq(n, 1 / SR); s[(f < lo) | (f > hi)] = 0
    return np.fft.irfft(s, n)

def piano(m, d=1.6):
    t = tt(d); f = hz(m)
    s = sum(np.sin(2 * np.pi * f * k * t * (1 + 0.0004 * k * k)) * np.exp(-t * (1.6 + k * 0.9)) / k ** 1.3 for k in range(1, 7))
    return s * np.minimum(1, t / 0.004)

def scie(f, t, n=12):
    return sum(np.sin(2 * np.pi * f * k * t) / k for k in range(1, n))

def cordes(m, d, att=0.5):  # ensemble de cordes : scies désaccordées filtrées, vibrato lent
    t = tt(d); s = 0
    for det in (-0.08, 0, 0.08):
        f = hz(m + det) * (1 + 0.003 * np.sin(2 * np.pi * 5.2 * t + det * 9))
        s = s + scie(f, t, 10)
    e = np.minimum(1, t / att) * np.clip((d - t) / 0.4, 0, 1)
    return passe_bas(s * e, 2600) / 3

def lead(m, d):  # mélodie : scie + carré doux, vibrato retardé
    t = tt(d); vib = 1 + 0.006 * np.sin(2 * np.pi * 5.5 * t) * np.clip((t - 0.12) / 0.2, 0, 1)
    f = hz(m) * vib
    s = scie(f, t, 8) + 0.5 * np.sign(np.sin(2 * np.pi * f * t)) * 0.4
    e = np.minimum(1, t / 0.015) * np.exp(-t / 1.2) * np.clip((d - t) / 0.06, 0, 1)
    return passe_bas(s * e, 4200)

def choeur(m, d):  # « aah » : formants simples sur une scie
    t = tt(d); s = scie(hz(m) * (1 + 0.004 * np.sin(2 * np.pi * 4.8 * t)), t, 30)
    S = np.fft.rfft(s); f = np.fft.rfftfreq(len(s), 1 / SR)
    form = sum(a * np.exp(-((f - fc) / bw) ** 2) for fc, bw, a in ((750, 130, 1.0), (1150, 160, 0.6), (2600, 260, 0.25)))
    s = np.fft.irfft(S * form, len(s))
    return s * np.minimum(1, t / 0.6) * np.clip((d - t) / 0.5, 0, 1)

def kick():
    t = tt(0.4); f = 42 + 120 * np.exp(-t / 0.03)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.16) + 0.3 * bruit(len(t), 2000, 6000) * np.exp(-t / 0.004)

def clap():
    n = int(0.25 * SR); t = np.arange(n) / SR; b = bruit(n, 900, 5000)
    e = sum(np.exp(-np.clip(t - o, 0, None) / 0.008) * (t >= o) for o in (0, 0.011, 0.022)) + 0.6 * np.exp(-t / 0.08)
    return b * e

def crash(d=2.5):
    t = tt(d); return bruit(len(t), 4000, 12000) * np.exp(-t / 0.55) * np.minimum(1, t / 0.003)

def impact():
    t = tt(2.5); f = 30 + 60 * np.exp(-t / 0.15)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.9) + 0.5 * bruit(len(t), 60, 600) * np.exp(-t / 0.25)

def montee(d):  # bruit blanc qui monte + filtre qui s'ouvre
    t = tt(d); n = len(t); b = rng.standard_normal(n)
    out = np.zeros(n); seg = int(0.05 * SR)
    for k in range(0, n, seg):
        fc = 400 + 9000 * (k / n) ** 2
        out[k:k + seg] = passe_bas(b[k:k + seg + 64], fc)[:len(out[k:k + seg])]
    return out * (t / d) ** 2.2

# Progression émotionnelle : Si m – Sol – Ré – La (vi – IV – I – V en ré majeur)
PROG = [[59, 62, 66], [55, 59, 62], [50, 54, 57], [57, 61, 64]]
ROOT = [35, 31, 38, 33]
MELO = [[78, 78, 76, 74, 76, 78, 81, 78], [79, 78, 76, 74, 71, 74, 76, 74],
        [69, 74, 78, 81, 81, 78, 76, 74], [73, 76, 81, 76, 73, 76, 78, 76]]
T_DROP, T_PAUSE, T_REPRISE, T_REFRAIN, T_FIN = 7.2, 39.4, 41.0, 46.0, 58.15

def mesures(t0, t1):  # mesures calées sur le « drop » (7,2 s)
    k = int(np.floor((t0 - T_DROP) / BAR))
    while T_DROP + k * BAR < t1:
        yield k, T_DROP + k * BAR
        k += 1

# ---- intro (0 → 7,2) : piano + cordes qui gonflent
for k, b0 in mesures(T_DROP - 4 * BAR, T_DROP):
    ch = PROG[k % 4]
    for i, idx in enumerate([0, 1, 2, 1, 2, 0, 1, 2]):
        tn = b0 + i * BEAT / 2
        if tn >= 0: add(piano(ch[idx] + 12), tn, 0.28 if i % 2 == 0 else 0.2, pan=-0.3 + 0.6 * (i % 3) / 2)
    if b0 + BAR > 0:
        for m in ch: add(cordes(m, BAR + 0.5, att=1.2), max(0, b0), 0.09 * (1 + k + 4) / 4)
add(montee(3.0), T_DROP - 3.0, 0.35)
add(impact(), T_DROP, 0.9); add(crash(), T_DROP, 0.2, 0.2)

# ---- corps du morceau (7,2 → 58,15)
for k, b0 in mesures(T_DROP, T_FIN):
    ch, rt, mel = PROG[k % 4], ROOT[k % 4], MELO[k % 4]
    pause = T_PAUSE <= b0 < T_REPRISE
    refrain = b0 >= T_REFRAIN
    etapes = 25.4 <= b0 < T_PAUSE
    montee_finale = T_REPRISE <= b0 < T_REFRAIN
    # cordes (toujours), plus larges au refrain
    for m in ch + ([ch[0] + 12] if refrain else []):
        add(cordes(m, BAR + 0.3, att=0.25), b0, 0.10 if refrain else 0.08, pan=(-0.4 if m % 2 else 0.4))
    # piano : accords rythmés (charleston afro) ou arpèges pendant la pause
    if pause:
        for i, idx in enumerate([0, 1, 2, 1, 2, 0, 1, 2]):
            add(piano(ch[idx] + 12), b0 + i * BEAT / 2, 0.24)
        continue
    for off in (0, 1.5, 2.5, 3.5):
        for m in ch: add(piano(m + 12, 0.5), b0 + off * BEAT, 0.09)
    # basse syncopée
    for off, d in ((0, 0.45), (0.75, 0.2), (1.5, 0.35), (2.5, 0.3), (3.25, 0.25)):
        t = tt(d); s = (np.sin(2 * np.pi * hz(rt) * t) + 0.35 * np.sin(4 * np.pi * hz(rt) * t)) * np.minimum(1, t / 0.004) * np.exp(-t / (d * 0.8))
        add(s, b0 + off * BEAT, 0.55)
    # batterie : kick afro, claps sur 2 et 4, shaker en doubles-croches
    for off in ((0, 1, 2, 3) if (refrain or montee_finale) else (0, 1.5, 2, 3.5)):
        add(kick(), b0 + off * BEAT, 0.75)
    for off in (1, 3): add(clap(), b0 + off * BEAT, 0.32, 0.1)
    for s16 in range(16):
        n = int(0.05 * SR); t = np.arange(n) / SR
        add(bruit(n, 6000, 12000) * np.minimum(1, t / 0.003) * np.exp(-t / 0.018), b0 + s16 * BEAT / 4, 0.09 if s16 % 4 == 2 else 0.045, 0.35)
    if k % 4 == 0: add(crash(1.8), b0, 0.05 if not refrain else 0.08, -0.2)
    # arpège synthé (étapes et après)
    if etapes or montee_finale or refrain:
        for i in range(8):
            m = ch[[0, 1, 2, 1][i % 4]] + 24
            t = tt(0.2); s = scie(hz(m), t, 6) * np.exp(-t / 0.08)
            add(s, b0 + i * BEAT / 2, 0.035, pan=(-0.5 if i % 2 else 0.5))
    # mélodie principale au refrain (et en écho discret pendant les étapes)
    if refrain or etapes:
        for i, m in enumerate(mel):
            add(lead(m, BEAT / 2 + 0.05), b0 + i * BEAT / 2, 0.10 if refrain else 0.045)
            if refrain: add(lead(m - 12, BEAT / 2 + 0.05), b0 + i * BEAT / 2, 0.05)
    if refrain:
        for m in ch: add(choeur(m + 12, BAR + 0.3), b0, 0.05)

# montées et respirations
add(montee(BAR), T_PAUSE - BAR, 0.28)
add(montee(T_REFRAIN - T_REPRISE), T_REPRISE, 0.3)
add(impact(), T_REFRAIN, 0.6); add(crash(), T_REFRAIN, 0.18)
add(montee(2.0), T_FIN - 2.0, 0.32)

# ---- final : impact + grand accord qui résonne
add(impact(), T_FIN, 0.95); add(crash(4), T_FIN, 0.2)
for m in [38, 50, 57, 62, 66, 69, 74]:
    add(cordes(m, D - T_FIN, att=0.05), T_FIN, 0.08)
    add(piano(m + 12, 3.5), T_FIN, 0.12)
for m in [62, 66, 69]: add(choeur(m + 12, D - T_FIN), T_FIN, 0.05)

# réverbération stéréo
irn = int(2.2 * SR)
for ch_ in (L, R):
    ir = rng.standard_normal(irn) * np.exp(-np.arange(irn) / SR / 0.55); ir /= np.sqrt((ir ** 2).sum())
    n2 = N + irn; wet = np.fft.irfft(np.fft.rfft(ch_, n2) * np.fft.rfft(ir, n2), n2)[:N]
    ch_ += 0.28 * wet
t = np.arange(N) / SR
env = np.clip(t / 0.3, 0, 1) * np.clip((D - t) / 2.0, 0, 1)
L *= env; R *= env
pk = max(np.abs(L).max(), np.abs(R).max()) * 1.1
st = np.stack([L / pk, R / pk], axis=1)
tmp = tempfile.mkdtemp(); brut = os.path.join(tmp, "m.wav")
with wave.open(brut, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st * 32767).astype("<i2").tobytes())

voix_src = os.path.join(ICI, "voix-off", "elevenlabs-voix-off.mp3")
musique = os.path.join(ICI, "assets", "musique.m4a")
if os.path.exists(voix_src):
    voix = os.path.join(ICI, "assets", "voix-off.m4a")
    subprocess.check_call(["ffmpeg", "-y", "-v", "error", "-i", voix_src, "-af",
                           f"adelay=100:all=1,apad=whole_dur={D},atrim=0:{D},loudnorm=I=-15:TP=-1.5:LRA=11,aresample=48000",
                           "-ac", "2", "-c:a", "aac", "-b:a", "192k", voix])
    subprocess.check_call(["ffmpeg", "-y", "-v", "error", "-i", brut, "-i", voix, "-filter_complex",
                           "[0:a]loudnorm=I=-13:TP=-1.5:LRA=9,aresample=48000,aformat=channel_layouts=stereo[m];"
                           "[1:a]aformat=channel_layouts=stereo[v];[m][v]sidechaincompress=threshold=0.03:ratio=3:attack=40:release=500[o]",
                           "-map", "[o]", "-t", str(D), "-c:a", "aac", "-b:a", "192k", musique])
else:  # musique seule : niveau plein (ne devrait pas arriver ici)
    subprocess.check_call(["ffmpeg", "-y", "-v", "error", "-i", brut, "-af", "loudnorm=I=-16:TP=-1.5:LRA=9,aresample=48000",
                           "-ac", "2", "-t", str(D), "-c:a", "aac", "-b:a", "192k", musique])

CUES = [(0.1, "whoosh-short.mp3", .3), (0.4, "sparkle.mp3", .25), (3.0, "whoosh-short.mp3", .25), (3.5, "click-soft.mp3", .25),
        (6.25, "whoosh.mp3", .4), (7.2, "impact-bass-1.mp3", .55), (7.25, "sparkle.mp3", .35), (8.4, "whoosh-short.mp3", .3),
        (10.2, "whoosh.mp3", .4), (10.8, "sparkle.mp3", .3), (11.95, "whoosh.mp3", .45), (14.85, "impact-bass-2.mp3", .5),
        (15.6, "whoosh-short.mp3", .3), (16.0, "whoosh-short.mp3", .25), (17.9, "pop.mp3", .3), (18.25, "ping.mp3", .2),
        (19.15, "pop.mp3", .3), (19.4, "click-soft.mp3", .25), (20.3, "pop.mp3", .3), (20.75, "click.mp3", .3), (20.7, "chime.mp3", .3),
        (21.1, "whoosh.mp3", .4), (22.1, "whoosh-short.mp3", .25), (24.1, "ping.mp3", .3), (25.15, "whoosh.mp3", .4)] + \
       [(t0 + 0.05, "pop.mp3", .32) for t0 in (27.0, 29.02, 31.85, 34.24, 36.73)] + \
       [(39.15, "whoosh.mp3", .4), (40.25, "error.mp3", .25), (41.02, "sparkle.mp3", .3), (44.14, "pop.mp3", .35),
        (45.65, "whoosh.mp3", .4), (46.06, "click.mp3", .25)] + \
       [(t0 + 0.15, "chime.mp3", .25) for t0 in (47.1, 50.88, 55.14)] + \
       [(57.85, "whoosh.mp3", .4), (58.7, "impact-bass-2.mp3", .55), (58.8, "sparkle.mp3", .3), (59.7, "pop.mp3", .3)]
ent, fil = [], []
for i, (t0, f, v) in enumerate(CUES):
    ent += ["-i", os.path.join(SFX, f)]
    fil.append(f"[{i}:a]aformat=sample_rates=48000:channel_layouts=stereo,volume={v},adelay={int(t0 * 1000)}:all=1[s{i}]")
subprocess.check_call(["ffmpeg", "-y", "-v", "error", *ent, "-filter_complex",
                       ";".join(fil) + ";" + "".join(f"[s{i}]" for i in range(len(CUES))) +
                       f"amix=inputs={len(CUES)}:normalize=0:duration=longest,apad=whole_dur={D},atrim=0:{D}[o]",
                       "-map", "[o]", "-c:a", "aac", "-b:a", "192k", os.path.join(ICI, "assets", "sfx.m4a")])
print(f"musique.m4a + sfx.m4a ({len(CUES)} effets)")
