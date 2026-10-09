"""Musique énergique (composée en code, libre de droits) + effets sonores de la vidéo de l'ensemble running (23 s).
Usage : python motion/tenue/son_tenue.py  →  motion/tenue/assets/musique.m4a et sfx.m4a
"""
import os, subprocess, tempfile, wave
import numpy as np

ICI = os.path.dirname(os.path.abspath(__file__))
SFX = os.path.join(ICI, "..", "son", "sfx")
SR, D, BPM = 44100, 23.0, 124
BEAT = 60 / BPM; BAR = 4 * BEAT; N = int(SR * D)
rng = np.random.default_rng(5)
hz = lambda m: 440 * 2 ** ((m - 69) / 12)

def add(buf, sig, t0, g=1.0):
    i = int(t0 * SR)
    if 0 <= i < len(buf):
        j = min(len(buf), i + len(sig)); buf[i:j] += g * sig[: j - i]

def bruit(n, lo, hi):
    s = np.fft.rfft(rng.standard_normal(n)); f = np.fft.rfftfreq(n, 1 / SR); s[(f < lo) | (f > hi)] = 0
    return np.fft.irfft(s, n)

def saw(f, n):  # dent de scie douce (8 harmoniques)
    t = np.arange(n) / SR
    return sum(np.sin(2 * np.pi * f * k * t) / k for k in range(1, 9))

# la mineur : Am – F – C – G
PROG = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]
ROOT = [33, 29, 36, 31]
mix = np.zeros(N)
for b in range(int(np.ceil(D / BAR))):
    t0 = b * BAR; ch = PROG[b % 4]; rt = ROOT[b % 4]
    fin = t0 > D - 1.5
    for k in range(4):  # kick sur chaque temps (dès 0,2 s), coupé à la fin
        tb = t0 + k * BEAT
        if 0.15 < tb < D - 0.6:
            n = int(0.3 * SR); tt = np.arange(n) / SR; f = 45 + 110 * np.exp(-tt / 0.025)
            add(mix, np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt / 0.13), tb, 0.65)
        if 2.4 < tb < D - 0.6:  # basse en contretemps
            n = int(0.18 * SR); tt = np.arange(n) / SR
            add(mix, saw(hz(rt), n) * np.exp(-tt / 0.09) * 0.5, tb + BEAT / 2, 0.35)
            n = int(0.05 * SR); tt = np.arange(n) / SR
            add(mix, bruit(n, 7000, 12000) * np.exp(-tt / 0.02), tb + BEAT / 2, 0.12)  # charleston ouvert
        if 2.4 < tb < D - 0.6 and k in (1, 3):  # clap
            n = int(0.18 * SR); tt = np.arange(n) / SR
            add(mix, bruit(n, 900, 4500) * np.exp(-tt / 0.05), tb, 0.3)
    # accords plaqués (stabs) sur les « et » du 2 et du 4
    for off in (1.5, 3.5) if 2.4 < t0 < D - 1.5 else ():
        n = int(0.25 * SR); tt = np.arange(n) / SR
        st = sum(saw(hz(m + 12), n) for m in ch) * np.exp(-tt / 0.08)
        add(mix, st, t0 + off * BEAT, 0.05)
    # nappe
    n = int((BAR + 0.5) * SR); tt = np.arange(n) / SR
    e = np.minimum(1, tt / 0.3) * np.clip((n / SR - tt) / 0.5, 0, 1)
    for m in ch:
        add(mix, e * np.sin(2 * np.pi * hz(m) * tt), t0, 0.05)
# « riser » de bruit avant le passage au noir (9,9 s) et le final
for t_hit in (9.9, 19.4):
    n = int(1.5 * SR); tt = np.arange(n) / SR
    add(mix, bruit(n, 2000, 9000) * (tt / 1.5) ** 2, t_hit - 1.5, 0.25)
t = np.arange(N) / SR
mix *= np.clip(t / 0.05, 0, 1) * np.clip((D - t) / 1.0, 0, 1)
mix /= np.abs(mix).max() * 1.1
tmp = tempfile.mkdtemp(); brut = os.path.join(tmp, "m.wav")
with wave.open(brut, "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype("<i2").tobytes())
subprocess.check_call(["ffmpeg", "-y", "-v", "error", "-i", brut, "-af", "loudnorm=I=-15:TP=-1.5:LRA=9,aresample=48000",
                       "-ac", "2", "-c:a", "aac", "-b:a", "192k", os.path.join(ICI, "assets", "musique.m4a")])

CUES = [(0.1, "impact-bass-1.mp3", .5), (0.85, "pop.mp3", .35), (2.35, "whoosh.mp3", .45), (2.45, "whoosh-short.mp3", .3)] + \
       [(3.9 + i * 1.0, "pop.mp3", .3) for i in range(5)] + [(9.9, "whoosh.mp3", .5)] + \
       [(10.6 + i * 0.32, "click-soft.mp3", .3) for i in range(5)] + \
       [(13.3, "whoosh-short.mp3", .35), (14.0, "sparkle.mp3", .35), (15.8, "whoosh-short.mp3", .3),
        (16.5, "whoosh.mp3", .4), (19.3, "whoosh.mp3", .45), (20.4, "impact-bass-2.mp3", .4)]
ent, fil = [], []
for i, (t0, f, v) in enumerate(CUES):
    ent += ["-i", os.path.join(SFX, f)]
    fil.append(f"[{i}:a]aformat=sample_rates=48000:channel_layouts=stereo,volume={v},adelay={int(t0 * 1000)}:all=1[s{i}]")
subprocess.check_call(["ffmpeg", "-y", "-v", "error", *ent, "-filter_complex",
                       ";".join(fil) + ";" + "".join(f"[s{i}]" for i in range(len(CUES))) +
                       f"amix=inputs={len(CUES)}:normalize=0:duration=longest,apad=whole_dur={D},atrim=0:{D}[o]",
                       "-map", "[o]", "-c:a", "aac", "-b:a", "192k", os.path.join(ICI, "assets", "sfx.m4a")])
print(f"musique.m4a + sfx.m4a ({len(CUES)} effets)")
