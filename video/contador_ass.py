"""Gera eventos ASS de contador animado (ex.: 0 -> 20.000 seguidores).
Uso: python3 video/contador_ass.py saida.ass --ate 20000 --ini 0.3 --dur 1.6 --fim 4.5
"""
import argparse
ap = argparse.ArgumentParser()
ap.add_argument("saida"); ap.add_argument("--ate", type=int, default=20000)
ap.add_argument("--ini", type=float, default=0.3); ap.add_argument("--dur", type=float, default=1.6)
ap.add_argument("--fim", type=float, default=4.5); ap.add_argument("--y", type=int, default=620)
a = ap.parse_args()
cab = open(__import__("pathlib").Path(__file__).resolve().parent / "templates" / "legenda_modelo.ass", encoding="utf-8").read().split("[Events]")[0]
def ts(t):
    h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"
fmt = lambda n: f"{n:,}".replace(",", ".")
ev = []
fps = 30; n = int(a.dur * fps)
for i in range(n):
    p = i / (n - 1); e = 1 - (1 - p) ** 3
    t0 = a.ini + i / fps; t1 = t0 + 1 / fps
    ev.append(f"Dialogue: 1,{ts(t0)},{ts(t1)},ImpactoAmarelo,,0,0,0,,{{\\pos(540,{a.y})\\fs210}}{fmt(int(a.ate*e))}")
tf = a.ini + a.dur
ev.append(f"Dialogue: 1,{ts(tf)},{ts(a.fim)},ImpactoAmarelo,,0,0,0,,{{\\pos(540,{a.y})\\fs210\\t(0,120,\\fscx118\\fscy118)\\t(120,300,\\fscx100\\fscy100)}}{fmt(a.ate)}")
ev.append(f"Dialogue: 1,{ts(a.ini)},{ts(a.fim)},Impacto,,0,0,0,,{{\\pos(540,{a.y+150})\\fs80\\fad(150,0)}}SEGUIDORES")
ev.append(f"Dialogue: 1,{ts(tf)},{ts(a.fim)},Destaque,,0,0,0,,{{\\pos(540,{a.y+250})\\fs84\\fad(120,0)}}muito obrigado!")
open(a.saida, "w", encoding="utf-8").write(cab + "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n" + "\n".join(ev) + "\n")
print("ok ->", a.saida)
