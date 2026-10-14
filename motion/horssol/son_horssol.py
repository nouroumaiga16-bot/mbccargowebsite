"""Musique chaleureuse (composée en code, libre de droits) + effets sonores de la vidéo « La culture hors-sol » (47 s).
La voix off ElevenLabs (motion/horssol/voix-off/elevenlabs-voix-off.mp3) est normalisée et la musique baissée dessous.
Usage : python motion/horssol/son_horssol.py  →  motion/horssol/assets/voix-off.m4a, musique.m4a et sfx.m4a
"""
import os, subprocess, tempfile, wave
import numpy as np

ICI = os.path.dirname(os.path.abspath(__file__))
SFX = os.path.join(ICI, "..", "son", "sfx")
SR, D, BPM = 44100, 47.0, 96
BEAT = 60 / BPM; BAR = 4 * BEAT; N = int(SR * D)
rng = np.random.default_rng(16)
hz = lambda m: 440 * 2 ** ((m - 69) / 12)

def add(buf, sig, t0, g=1.0):
    i = int(t0 * SR)
    if 0 <= i < len(buf):
        j = min(len(buf), i + len(sig)); buf[i:j] += g * sig[: j - i]

def bruit(n, lo, hi):
    s = np.fft.rfft(rng.standard_normal(n)); f = np.fft.rfftfreq(n, 1 / SR); s[(f < lo) | (f > hi)] = 0
    return np.fft.irfft(s, n)

def kalimba(f, n):
    t = np.arange(n) / SR
    return np.sin(2 * np.pi * f * t) * np.exp(-t / 0.4) + 0.3 * np.sin(2 * np.pi * f * 5.4 * t) * np.exp(-t / 0.04)

def marimba(f, n):
    t = np.arange(n) / SR
    return (np.sin(2 * np.pi * f * t) + 0.2 * np.sin(2 * np.pi * f * 4 * t) * np.exp(-t / 0.05)) * np.exp(-t / 0.22)

# ré majeur : Dmaj7 – Bm7 – Gmaj7 – A6 (lumineux, « soleil »), résolution finale sur Dmaj9
PROG = [[62, 66, 69, 73], [59, 62, 66, 69], [55, 59, 62, 66], [57, 61, 64, 66]]
ROOT = [38, 35, 43, 33]
pad = np.zeros(N); kal = np.zeros(N); bass = np.zeros(N); drums = np.zeros(N)
for b in range(int(np.ceil(D / BAR))):
    t0 = b * BAR; ch, rt = PROG[b % 4], ROOT[b % 4]
    fin = t0 + BAR > D - 1.0
    if fin:
        ch, rt = [50, 57, 62, 66, 69, 76], 38
    n = int((BAR + 1.0) * SR); tt = np.arange(n) / SR
    e = np.minimum(1, tt / 0.6) * np.clip((n / SR - tt) / 1.0, 0, 1)
    for m in ch:
        for det in (-0.1, 0.1):
            add(pad, e * (np.sin(2 * np.pi * hz(m + det) * tt) + 0.2 * np.sin(4 * np.pi * hz(m + det) * tt)), t0, 0.045)
    if fin:
        break
    # kalimba en doubles-croches légères (motif qui tourne)
    for k, idx in enumerate([0, 2, 3, 1, 2, 3, 0, 2]):
        if t0 + k * BEAT / 2 < 0.4 or (b % 2 and k in (3, 7)):
            continue
        add(kal, kalimba(hz(ch[idx] + 12), int(1.0 * SR)), t0 + k * BEAT / 2, 0.15 if k % 2 == 0 else 0.1)
    # marimba en réponse (dès la scène du livre)
    if t0 >= 17.0:
        for off, idx in ((2.5, 3), (3.0, 2), (3.5, 1)):
            add(kal, marimba(hz(ch[idx]), int(0.6 * SR)), t0 + off * BEAT, 0.16)
    # basse + batterie (dès 7,5 s, après « sans terre ? »)
    if 7.0 <= t0 < D - 1.5:
        for off, dur in ((0, 0.6), (1.5 * BEAT, 0.3), (2.5 * BEAT, 0.3), (3 * BEAT, 0.45)):
            n = int(dur * SR); tt = np.arange(n) / SR
            sig = (np.sin(2 * np.pi * hz(rt) * tt) + 0.3 * np.sin(4 * np.pi * hz(rt) * tt)) * np.minimum(1, tt / 0.005) * np.exp(-tt / (dur * 0.7))
            add(bass, sig, t0 + off, 0.4)
        for beat in range(4):
            tb = t0 + beat * BEAT
            if beat in (0, 2) or (beat == 3 and b % 2):
                n = int(0.35 * SR); tt = np.arange(n) / SR; f = 46 + 80 * np.exp(-tt / 0.03)
                add(drums, np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt / 0.12), tb, 0.5)
            if beat in (1, 3):
                n = int(0.12 * SR); tt = np.arange(n) / SR
                add(drums, bruit(n, 1500, 5000) * np.exp(-tt / 0.03), tb, 0.18)
        for s16 in range(16):
            n = int(0.06 * SR); tt = np.arange(n) / SR
            add(drums, bruit(n, 5500, 11000) * np.minimum(1, tt / 0.004) * np.exp(-tt / 0.02), t0 + s16 * BEAT / 4, 0.065 if s16 % 4 == 2 else 0.03)
# « riser » avant le livre et avant le prix
riser = np.zeros(N)
for t_hit in (6.35, 35.2):
    n = int(1.4 * SR); tt = np.arange(n) / SR
    add(riser, bruit(n, 2500, 9000) * (tt / 1.4) ** 2, t_hit - 1.4, 0.22)
t = np.arange(N) / SR
drums *= 1 - 0.85 * ((t > 32.4) & (t < 33.0))
mix = pad + kal + bass + drums + riser
irn = int(1.5 * SR); ir = rng.standard_normal(irn) * np.exp(-np.arange(irn) / SR / 0.4); ir /= np.sqrt((ir ** 2).sum())
L = N + irn
mix = mix + 0.24 * np.fft.irfft(np.fft.rfft(mix, L) * np.fft.rfft(ir, L), L)[:N]
mix *= np.clip(t / 0.4, 0, 1) * np.clip((D - t) / 1.3, 0, 1)
mix /= np.abs(mix).max() * 1.1
tmp = tempfile.mkdtemp(); brut = os.path.join(tmp, "m.wav")
with wave.open(brut, "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype("<i2").tobytes())

voix_src = os.path.join(ICI, "voix-off", "elevenlabs-voix-off.mp3")
musique = os.path.join(ICI, "assets", "musique.m4a")
if os.path.exists(voix_src):
    voix = os.path.join(ICI, "assets", "voix-off.m4a")
    subprocess.check_call(["ffmpeg", "-y", "-v", "error", "-i", voix_src, "-af",
                           f"adelay=100:all=1,apad=whole_dur={D},atrim=0:{D},loudnorm=I=-15:TP=-1.5:LRA=11,aresample=48000",
                           "-ac", "2", "-c:a", "aac", "-b:a", "192k", voix])
    subprocess.check_call(["ffmpeg", "-y", "-v", "error", "-i", brut, "-i", voix, "-filter_complex",
                           "[0:a]loudnorm=I=-21:TP=-2:LRA=9,aresample=48000,aformat=channel_layouts=stereo[m];"
                           "[1:a]aformat=channel_layouts=stereo[v];[m][v]sidechaincompress=threshold=0.03:ratio=5:attack=30:release=350[o]",
                           "-map", "[o]", "-t", str(D), "-c:a", "aac", "-b:a", "192k", musique])
else:  # musique seule : niveau plein (ne devrait pas arriver ici)
    subprocess.check_call(["ffmpeg", "-y", "-v", "error", "-i", brut, "-af", "loudnorm=I=-16:TP=-1.5:LRA=9,aresample=48000",
                           "-ac", "2", "-t", str(D), "-c:a", "aac", "-b:a", "192k", musique])

CUES = [(0.1, "impact-bass-1.mp3", .35), (0.1, "whoosh-short.mp3", .3), (1.5, "pop.mp3", .3), (2.65, "pop.mp3", .3),
        (4.3, "whoosh-short.mp3", .3), (6.3, "impact-bass-2.mp3", .5), (6.35, "whoosh.mp3", .45),
        (7.65, "sparkle.mp3", .3), (9.65, "pop.mp3", .3), (10.9, "click-soft.mp3", .3), (11.05, "click-soft.mp3", .3), (11.2, "click-soft.mp3", .3),
        (13.0, "whoosh-short.mp3", .3), (14.4, "chime.mp3", .25), (15.3, "sparkle.mp3", .3), (16.95, "whoosh.mp3", .4)] + \
       [(t0 + 0.05, "pop.mp3", .32) for t0 in (18.47, 19.9, 21.78, 23.78, 26.24)] + \
       [(28.15, "chime.mp3", .3), (28.75, "whoosh.mp3", .4), (29.24, "click.mp3", .25), (30.75, "click.mp3", .25), (31.6, "click.mp3", .25),
        (32.45, "whoosh-short.mp3", .35), (32.9, "impact-bass-1.mp3", .4), (35.2, "whoosh.mp3", .4), (36.2, "sparkle.mp3", .3)] + \
       [(38.9 + i * 0.55, "pop.mp3", .3) for i in range(3)] + \
       [(41.0, "whoosh-short.mp3", .3), (41.85, "impact-bass-2.mp3", .55), (41.95, "sparkle.mp3", .3), (44.2, "pop.mp3", .3)]
ent, fil = [], []
for i, (t0, f, v) in enumerate(CUES):
    ent += ["-i", os.path.join(SFX, f)]
    fil.append(f"[{i}:a]aformat=sample_rates=48000:channel_layouts=stereo,volume={v},adelay={int(t0 * 1000)}:all=1[s{i}]")
subprocess.check_call(["ffmpeg", "-y", "-v", "error", *ent, "-filter_complex",
                       ";".join(fil) + ";" + "".join(f"[s{i}]" for i in range(len(CUES))) +
                       f"amix=inputs={len(CUES)}:normalize=0:duration=longest,apad=whole_dur={D},atrim=0:{D}[o]",
                       "-map", "[o]", "-c:a", "aac", "-b:a", "192k", os.path.join(ICI, "assets", "sfx.m4a")])
print(f"musique.m4a + sfx.m4a ({len(CUES)} effets)")
