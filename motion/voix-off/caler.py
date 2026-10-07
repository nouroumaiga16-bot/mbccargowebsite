"""Cale la voix off ElevenLabs sur les plans de la vidéo.

Chaque réplique est découpée dans elevenlabs-voix-off.mp3 (de « de » à « a », coupes dans les
silences), éventuellement accélérée (« tempo »), puis placée à « start » secondes.
Sortie : motion/assets/voix-off.m4a (45 s, -16 LUFS).   Usage : python motion/voix-off/caler.py
"""
import json, os, subprocess

ICI = os.path.dirname(os.path.abspath(__file__))
src = os.path.join(ICI, "elevenlabs-voix-off.mp3")
repliques = json.load(open(os.path.join(ICI, "repliques.json")))
filtres = []
for i, r in enumerate(repliques):
    tempo = f",atempo={r['tempo']}" if r.get("tempo") else ""
    filtres.append(f"[0:a]atrim={r['de']}:{r['a']},asetpts=PTS-STARTPTS,afade=t=in:d=0.03,"
                   f"afade=t=out:st={r['a'] - r['de'] - 0.06:.2f}:d=0.06{tempo},adelay={int(r['start'] * 1000)}:all=1[a{i}]")
mix = "".join(f"[a{i}]" for i in range(len(repliques)))
graphe = ";".join(filtres) + (f";{mix}amix=inputs={len(repliques)}:normalize=0:duration=longest,"
                              "apad=whole_dur=45,atrim=0:45,loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000[out]")
subprocess.check_call(["ffmpeg", "-y", "-v", "error", "-i", src, "-filter_complex", graphe, "-map", "[out]",
                       "-ac", "2", "-c:a", "aac", "-b:a", "192k", os.path.join(ICI, "..", "assets", "voix-off.m4a")])
for r in repliques:
    fin = r["start"] + (r["a"] - r["de"]) / r.get("tempo", 1)
    print(f"{r['id']:>2}  {r['start']:5.2f} → {fin:5.2f} s  {r['text']}")
