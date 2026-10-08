"""Musique (composée en code, libre de droits) + effets sonores de la vidéo du groupe (34 s).
Usage : python motion/groupe/son_groupe.py  →  motion/groupe/assets/musique.m4a et sfx.m4a
"""
import os, subprocess, tempfile, wave
import numpy as np

ICI = os.path.dirname(os.path.abspath(__file__))
SFX = os.path.join(ICI, "..", "son", "sfx")
SR, D, BPM = 44100, 34.0, 104
BEAT = 60 / BPM; BAR = 4 * BEAT; N = int(SR * D)
rng = np.random.default_rng(11)
hz = lambda m: 440 * 2 ** ((m - 69) / 12)

def add(buf, sig, t0, g=1.0):
    i = int(t0 * SR)
    if i < len(buf):
        j = min(len(buf), i + len(sig)); buf[i:j] += g * sig[: j - i]

def bruit(n, lo, hi):
    s = np.fft.rfft(rng.standard_normal(n)); f = np.fft.rfftfreq(n, 1 / SR); s[(f < lo) | (f > hi)] = 0
    return np.fft.irfft(s, n)

# Ré majeur, progression positive I – V – vi – IV
PROG = [[62, 66, 69, 73], [57, 61, 64, 69], [59, 62, 66, 69], [55, 59, 62, 66]]
ROOT = [38, 33, 35, 31]
pad = np.zeros(N); arp = np.zeros(N); bass = np.zeros(N); drums = np.zeros(N)
for b in range(int(np.ceil(D / BAR))):
    t0 = b * BAR; ch = PROG[b % 4]; rt = ROOT[b % 4]
    fin = t0 + BAR > D - 1.6
    if fin: ch, rt = [62, 66, 69, 74, 78], 38
    n = int((BAR + 1.0) * SR); t = np.arange(n) / SR
    e = np.minimum(1, t / 0.4) * np.clip((n / SR - t) / 1.0, 0, 1)
    for m in ch:
        for det in (-0.1, 0.1):
            f = hz(m + det); add(pad, e * (np.sin(2 * np.pi * f * t) + 0.22 * np.sin(4 * np.pi * f * t)), t0, 0.045)
    if fin: break
    if t0 >= 0.8:  # arpège « marimba » en doubles croches légères
        for k in range(8):
            m = ch[[0, 2, 1, 3, 2, 3, 1, 2][k]] + 12; f = hz(m); n2 = int(0.7 * SR); tt = np.arange(n2) / SR
            sig = np.sin(2 * np.pi * f * tt) * np.exp(-tt / 0.22) + 0.3 * np.sin(2 * np.pi * f * 4 * tt) * np.exp(-tt / 0.04)
            add(arp, sig, t0 + k * BEAT / 2, 0.14 if k % 2 == 0 else 0.09)
    if t0 >= 4.0:  # basse
        for off, d in ((0, 0.5), (1.5 * BEAT, 0.28), (2.5 * BEAT, 0.28), (3 * BEAT, 0.35)):
            f = hz(rt); n2 = int(d * SR); tt = np.arange(n2) / SR
            add(bass, (np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(4 * np.pi * f * tt)) * np.exp(-tt / (d * 0.7)) * np.clip((d - tt) / 0.04, 0, 1), t0 + off, 0.4)
    if 4.0 <= t0 < D - 2.4:  # batterie
        for bt in (0, 2):
            n2 = int(0.32 * SR); tt = np.arange(n2) / SR; f = 50 + 75 * np.exp(-tt / 0.03)
            add(drums, np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt / 0.11), t0 + bt * BEAT, 0.5)
        for bt in (1, 3):
            n2 = int(0.15 * SR); tt = np.arange(n2) / SR
            add(drums, bruit(n2, 900, 5000) * np.exp(-tt / 0.045), t0 + bt * BEAT, 0.28)
        for s in range(16):
            n2 = int(0.05 * SR); tt = np.arange(n2) / SR
            add(drums, bruit(n2, 6000, 11000) * np.exp(-tt / 0.018), t0 + s * BEAT / 4, 0.06 if s % 4 == 2 else 0.03)
mix = pad + arp + bass + drums
irn = int(1.3 * SR); ir = rng.standard_normal(irn) * np.exp(-np.arange(irn) / SR / 0.32); ir /= np.sqrt((ir ** 2).sum())
L = N + irn; mix = mix + 0.2 * np.fft.irfft(np.fft.rfft(mix, L) * np.fft.rfft(ir, L), L)[:N]
t = np.arange(N) / SR
mix *= np.clip(t / 0.5, 0, 1) * np.clip((D - t) / 1.2, 0, 1)
mix /= np.abs(mix).max() * 1.15
tmp = tempfile.mkdtemp(); brut = os.path.join(tmp, "m.wav")
with wave.open(brut, "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype("<i2").tobytes())
subprocess.check_call(["ffmpeg", "-y", "-v", "error", "-i", brut, "-af", "loudnorm=I=-17:TP=-2:LRA=11,aresample=48000",
                       "-ac", "2", "-c:a", "aac", "-b:a", "192k", os.path.join(ICI, "assets", "musique.m4a")])

CUES = [(0.1, "whoosh.mp3", .45), (1.75, "whoosh-short.mp3", .3), (3.1, "whoosh-short.mp3", .3),
        (4.25, "impact-bass-1.mp3", .45), (4.95, "sparkle.mp3", .35), (5.6, "click-soft.mp3", .25),
        (8.0, "whoosh.mp3", .4), (8.3, "pop.mp3", .35), (8.9, "pop.mp3", .25), (9.15, "pop.mp3", .25), (9.4, "pop.mp3", .25),
        (12.25, "whoosh.mp3", .4)] + [(13.0 + i * 1.12, "pop.mp3", .28) for i in range(5)] + [
        (19.3, "whoosh.mp3", .4)] + [(19.65 + i * 0.12, "click-soft.mp3", .22) for i in range(6)] + [
        (21.2, "sparkle.mp3", .3), (23.45, "whoosh.mp3", .4), (24.0, "click.mp3", .28), (24.45, "click.mp3", .28),
        (24.9, "error.mp3", .22), (25.75, "impact-bass-2.mp3", .5), (26.9, "whoosh.mp3", .4), (27.25, "ping.mp3", .3),
        (28.1, "whoosh-short.mp3", .3), (28.7, "pop.mp3", .38), (29.3, "click-soft.mp3", .25), (30.6, "chime.mp3", .3), (6.4, "pop.mp3", .32)]
ent, fil = [], []
for i, (t0, f, v) in enumerate(CUES):
    ent += ["-i", os.path.join(SFX, f)]
    fil.append(f"[{i}:a]aformat=sample_rates=48000:channel_layouts=stereo,volume={v},adelay={int(t0 * 1000)}:all=1[s{i}]")
subprocess.check_call(["ffmpeg", "-y", "-v", "error", *ent, "-filter_complex",
                       ";".join(fil) + ";" + "".join(f"[s{i}]" for i in range(len(CUES))) +
                       f"amix=inputs={len(CUES)}:normalize=0:duration=longest,apad=whole_dur={D},atrim=0:{D}[o]",
                       "-map", "[o]", "-c:a", "aac", "-b:a", "192k", os.path.join(ICI, "assets", "sfx.m4a")])
print(f"musique.m4a + sfx.m4a ({len(CUES)} effets)")
