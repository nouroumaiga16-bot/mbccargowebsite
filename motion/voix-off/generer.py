"""Voix off MBC Cargo : synthèse vocale locale avec Kokoro (voix française ff_siwis).

Usage (modèles Kokoro téléchargés depuis github.com/thewh1teagle/kokoro-onnx, release model-files-v1.0) :
    pip install kokoro-onnx soundfile
    python motion/voix-off/generer.py <dossier_modeles>
Produit motion/assets/voix-off.m4a (45 s, -16 LUFS), chaque réplique placée à son « start »
de repliques.json, calé sur les plans de motion/src/mbc-cargo.template.html.
"""
import json, os, subprocess, sys, tempfile
import soundfile as sf
from kokoro_onnx import Kokoro

ICI = os.path.dirname(os.path.abspath(__file__))
modeles = sys.argv[1]
k = Kokoro(f"{modeles}/kokoro-v1.0.onnx", f"{modeles}/voices-v1.0.bin")
repliques = json.load(open(f"{ICI}/repliques.json"))
tmp = tempfile.mkdtemp()
entrees, filtres = [], []
for i, r in enumerate(repliques):
    samples, sr = k.create(r["text"], voice="ff_siwis", speed=r.get("speed", 1.0), lang="fr-fr")
    sf.write(f"{tmp}/{r['id']}.wav", samples, sr)
    print(f"{r['id']}  {r['start']:5.2f} s  {len(samples) / sr:.2f} s  {r['text']}")
    entrees += ["-i", f"{tmp}/{r['id']}.wav"]
    filtres.append(f"[{i}:a]adelay={int(r['start'] * 1000)}:all=1[a{i}]")
mix = "".join(f"[a{i}]" for i in range(len(repliques)))
graphe = ";".join(filtres) + (f";{mix}amix=inputs={len(repliques)}:normalize=0:duration=longest,"
                              "apad=whole_dur=45,atrim=0:45,loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000[out]")
subprocess.check_call(["ffmpeg", "-y", "-v", "error", *entrees, "-filter_complex", graphe, "-map", "[out]",
                       "-ac", "2", "-c:a", "aac", "-b:a", "192k", os.path.join(ICI, "..", "assets", "voix-off.m4a")])
