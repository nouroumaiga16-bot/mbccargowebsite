"""Musique de fond + effets sonores de la pub MBC Cargo (45 s).

- Musique : composée ici, en code (numpy), donc libre de droits. 100 BPM, ambiance chaleureuse
  « afro-pop » douce : pad, kalimba en arpèges, basse syncopée, kick léger, shaker, rim.
  Elle est baissée automatiquement sous la voix off (sidechain ffmpeg).
- Effets sonores : bibliothèque intégrée d'HyperFrames (Pixabay Content License, usage
  commercial autorisé), placés sur les transitions et les gestes à l'écran.

Usage : python motion/son/construire_son.py   (depuis la racine du dépôt ; nécessite numpy et ffmpeg)
Sorties : motion/assets/musique.m4a et motion/assets/sfx.m4a, 45 s chacune.
"""
import json, os, subprocess, tempfile, wave
import numpy as np

ICI = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(ICI, "..", "assets")
SFX_DIR = os.path.join(ICI, "sfx")
SR = 44100
DUREE = 45.0
BPM = 100
BEAT = 60 / BPM
BAR = 4 * BEAT
N = int(SR * DUREE)
rng = np.random.default_rng(7)  # déterministe


def hz(midi):
    return 440.0 * 2 ** ((midi - 69) / 12)


def env(n, a, d, s=0.0, r=0.0):
    """Enveloppe attaque / décroissance exponentielle (en secondes)."""
    t = np.arange(n) / SR
    e = np.minimum(1.0, t / max(a, 1e-4)) * np.exp(-t / max(d, 1e-4))
    if r:
        e *= np.clip((n / SR - t) / r, 0, 1)
    return e


def add(buf, sig, t0, gain=1.0):
    i = int(t0 * SR)
    if i >= len(buf):
        return
    j = min(len(buf), i + len(sig))
    buf[i:j] += gain * sig[: j - i]


def lowpass(x, cutoff):
    a = np.exp(-2 * np.pi * cutoff / SR)
    y = np.empty_like(x)
    acc = 0.0
    for k in range(len(x)):  # filtre 1 pôle, suffisant pour adoucir
        acc = (1 - a) * x[k] + a * acc
        y[k] = acc
    return y


def bandnoise(n, lo, hi):
    spec = np.fft.rfft(rng.standard_normal(n))
    f = np.fft.rfftfreq(n, 1 / SR)
    spec[(f < lo) | (f > hi)] = 0
    return np.fft.irfft(spec, n)


# Progression (une mesure par accord) : Fmaj7 – G6 – Em7 – Am7, en boucle, résolution sur Cmaj9
PROG = [[53, 57, 60, 64], [55, 59, 62, 64], [52, 55, 59, 62], [57, 60, 64, 67]]
ROOTS = [41, 43, 40, 45]

pad = np.zeros(N); kal = np.zeros(N); bass = np.zeros(N); drums = np.zeros(N)
nbars = int(np.ceil(DUREE / BAR))
for b in range(nbars):
    t0 = b * BAR
    chord, root = PROG[b % 4], ROOTS[b % 4]
    final = t0 + BAR > 43.2
    if final:
        chord, root = [48, 55, 59, 62, 64], 36
    # Pad : sinus désaccordés, attaque lente
    n = int(BAR * SR) + int(0.8 * SR)
    t = np.arange(n) / SR
    e = np.minimum(1, t / 0.5) * np.clip((n / SR - t) / 0.8, 0, 1)
    for m in chord:
        for det in (-0.12, 0.12):
            f = hz(m + det)
            add(pad, e * (np.sin(2 * np.pi * f * t) + 0.25 * np.sin(4 * np.pi * f * t)), t0, 0.05)
    if final:
        break
    # Kalimba : arpèges en croches (dès 3 s)
    if t0 >= 2.4:
        pattern = [0, 2, 1, 3, 2, 1, 3, 2]
        for k, idx in enumerate(pattern):
            if k in (3, 7) and b % 2:
                continue  # respiration
            m = chord[idx] + 12
            f = hz(m)
            n = int(0.9 * SR); tt = np.arange(n) / SR
            sig = (np.sin(2 * np.pi * f * tt) * np.exp(-tt / 0.32)
                   + 0.35 * np.sin(2 * np.pi * f * 5.95 * tt) * np.exp(-tt / 0.05))
            add(kal, sig, t0 + k * BEAT / 2, 0.16 if k % 2 == 0 else 0.11)
    # Basse syncopée (dès 6 s) : temps 1, « et » du 2, temps 4
    if t0 >= 5.9:
        for off, dur in ((0, 0.55), (1.5 * BEAT, 0.3), (3 * BEAT, 0.4)):
            f = hz(root); n = int(dur * SR); tt = np.arange(n) / SR
            sig = (np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(4 * np.pi * f * tt)) * env(n, 0.005, dur * 0.7, r=0.05)
            add(bass, sig, t0 + off, 0.42)
    # Batterie (6 → 41,5 s, sauf la respiration de 13 à 15 s)
    if 5.9 <= t0 < 41.5 and not (12.9 <= t0 < 15.0):
        for beat in (0, 2):  # kick doux
            n = int(0.35 * SR); tt = np.arange(n) / SR
            f = 48 + 70 * np.exp(-tt / 0.03)
            add(drums, np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt / 0.12), t0 + beat * BEAT, 0.5)
        for beat in (1, 3):  # rim / claquement léger
            n = int(0.12 * SR)
            add(drums, bandnoise(n, 1200, 4000) * env(n, 0.001, 0.03), t0 + beat * BEAT, 0.22)
        for s16 in range(16):  # shaker
            n = int(0.06 * SR)
            g = 0.07 if s16 % 4 == 2 else 0.035
            add(drums, bandnoise(n, 5000, 11000) * env(n, 0.004, 0.02), t0 + s16 * BEAT / 4, g)

mix = 0.9 * pad + kal + bass + drums
# Réverbération simple (réponse impulsionnelle bruitée exponentielle)
irn = int(1.4 * SR)
ir = rng.standard_normal(irn) * np.exp(-np.arange(irn) / SR / 0.35)
ir /= np.sqrt(np.sum(ir ** 2))
L = len(mix) + irn
wet = np.fft.irfft(np.fft.rfft(mix, L) * np.fft.rfft(ir, L), L)[: len(mix)]
mix = mix + 0.22 * wet
mix = lowpass(mix, 9000)
fade = np.ones(N); fi = int(0.6 * SR); fo = int(1.2 * SR)
fade[:fi] = np.linspace(0, 1, fi); fade[-fo:] = np.linspace(1, 0, fo)
mix *= fade
mix /= np.max(np.abs(mix)) * 1.12

tmp = tempfile.mkdtemp()
brut = os.path.join(tmp, "musique.wav")
with wave.open(brut, "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix * 32767).astype("<i2").tobytes())

# Musique : niveau de fond (-24 LUFS) et baisse automatique sous la voix off
subprocess.check_call([
    "ffmpeg", "-y", "-v", "error", "-i", brut, "-i", os.path.join(ASSETS, "voix-off.m4a"), "-filter_complex",
    "[0:a]loudnorm=I=-24:TP=-3:LRA=11,aresample=48000,aformat=channel_layouts=stereo[m];"
    "[1:a]aformat=channel_layouts=stereo[v];"
    "[m][v]sidechaincompress=threshold=0.03:ratio=4:attack=40:release=450:makeup=1[out]",
    "-map", "[out]", "-t", str(DUREE), "-c:a", "aac", "-b:a", "192k", os.path.join(ASSETS, "musique.m4a")])

# Effets sonores : (moment, fichier, volume)
CUES = json.load(open(os.path.join(ICI, "sfx.json")))
entrees, filtres = [], []
for i, c in enumerate(CUES):
    entrees += ["-i", os.path.join(SFX_DIR, c["fichier"])]
    coupe = f",atrim=0:{c['duree']},afade=t=out:st={c['duree'] - 0.08}:d=0.08" if c.get("duree") else ""
    filtres.append(f"[{i}:a]aformat=sample_rates=48000:channel_layouts=stereo{coupe},volume={c['volume']},"
                   f"adelay={int(c['t'] * 1000)}:all=1[s{i}]")
mixs = "".join(f"[s{i}]" for i in range(len(CUES)))
subprocess.check_call(["ffmpeg", "-y", "-v", "error", *entrees, "-filter_complex",
                       ";".join(filtres) + f";{mixs}amix=inputs={len(CUES)}:normalize=0:duration=longest,"
                       f"apad=whole_dur={DUREE},atrim=0:{DUREE}[out]",
                       "-map", "[out]", "-c:a", "aac", "-b:a", "192k", os.path.join(ASSETS, "sfx.m4a")])
print(f"musique.m4a et sfx.m4a ({len(CUES)} effets) écrits dans motion/assets/")
