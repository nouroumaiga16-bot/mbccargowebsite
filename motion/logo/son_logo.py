"""Son de l'animation du logo (6 s) : nappe d'accord Cmaj9 composée en code + effets HyperFrames.
Usage : python motion/logo/son_logo.py   →   motion/logo/assets/son-logo.m4a
"""
import os, subprocess, tempfile, wave
import numpy as np

ICI = os.path.dirname(os.path.abspath(__file__))
SFX = os.path.join(ICI, "..", "son", "sfx")
SR, D = 44100, 6.0
N = int(SR * D)
t = np.arange(N) / SR
rng = np.random.default_rng(3)

def hz(m): return 440 * 2 ** ((m - 69) / 12)
# nappe qui monte avec le logo puis se pose sur l'accord final
pad = np.zeros(N)
for m in (48, 55, 59, 62, 64, 71):
    for det in (-0.1, 0.1):
        f = hz(m + det)
        pad += np.sin(2 * np.pi * f * t) + 0.2 * np.sin(4 * np.pi * f * t)
envp = np.clip(t / 1.2, 0, 1) ** 2 * np.clip((D - t) / 1.6, 0, 1)
pad *= envp
# « cloche » douce sur l'arrivée de MBC (1,15 s) et de la signature (2,6 s)
def cloche(t0, notes, g):
    out = np.zeros(N)
    for m in notes:
        f = hz(m); tt = np.clip(t - t0, 0, None)
        out += (t >= t0) * (np.sin(2 * np.pi * f * tt) * np.exp(-tt / 0.9) + 0.25 * np.sin(2 * np.pi * f * 3.01 * tt) * np.exp(-tt / 0.25))
    return g * out
mix = 0.05 * pad + cloche(1.15, (72, 76, 79), 0.10) + cloche(2.6, (79, 83, 86), 0.07)
irn = int(1.6 * SR); ir = rng.standard_normal(irn) * np.exp(-np.arange(irn) / SR / 0.45); ir /= np.sqrt((ir ** 2).sum())
L = N + irn
mix = mix + 0.25 * np.fft.irfft(np.fft.rfft(mix, L) * np.fft.rfft(ir, L), L)[:N]
mix *= np.clip((D - t) / 0.4, 0, 1)
mix /= np.abs(mix).max() * 1.2
tmp = tempfile.mkdtemp(); pad_wav = os.path.join(tmp, "nappe.wav")
with wave.open(pad_wav, "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype("<i2").tobytes())

cues = [(0.10, "whoosh.mp3", 0.50), (0.70, "whoosh-short.mp3", 0.40), (1.12, "impact-bass-1.mp3", 0.55),
        (2.30, "sparkle.mp3", 0.40), (2.60, "click-soft.mp3", 0.25)]
entrees = ["-i", pad_wav]; filtres = ["[0:a]aformat=sample_rates=48000:channel_layouts=stereo,volume=0.9[p]"]
for i, (t0, f, v) in enumerate(cues, 1):
    entrees += ["-i", os.path.join(SFX, f)]
    filtres.append(f"[{i}:a]aformat=sample_rates=48000:channel_layouts=stereo,volume={v},adelay={int(t0 * 1000)}:all=1[s{i}]")
mixe = "[p]" + "".join(f"[s{i}]" for i in range(1, len(cues) + 1))
subprocess.check_call(["ffmpeg", "-y", "-v", "error", *entrees, "-filter_complex",
    ";".join(filtres) + f";{mixe}amix=inputs={len(cues) + 1}:normalize=0:duration=longest,apad=whole_dur={D},atrim=0:{D},"
    "loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000[out]",
    "-map", "[out]", "-c:a", "aac", "-b:a", "192k", os.path.join(ICI, "assets", "son-logo.m4a")])
print("son-logo.m4a écrit")
