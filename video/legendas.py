"""Gera legenda .ass no padrão FALA PARANÁ a partir da transcrição (palavras c/ tempo) e do corte.

Uso: python3 video/legendas.py transcricao.json corte.json saida.ass [extras.ass]
corte.json: {"cortes": [[ini_fonte, fim_fonte], ...],
             "negrito": ["palavra", ...], "destaque": ["frase exata", ...],
             "trocas": {"errado": "certo"}}
- agrupa 2–6 palavras (quebra em pontuação/pausa, máx ~32 caracteres)
- remapeia tempos da fonte para a linha do tempo do vídeo cortado
- extras.ass: eventos adicionais (ex.: contador) anexados ao final
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MAX_CH, MAX_W, MIN_W = 28, 6, 2


def ts(t):
    t = max(0, t)
    return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"


def fim_corte(t, cortes):
    acc = 0.0
    for a, b in cortes:
        if a <= t <= b:
            return acc + (b - a)
        acc += b - a
    return None


def remap(t, cortes):
    acc = 0.0
    for a, b in cortes:
        if a <= t <= b:
            return acc + (t - a)
        acc += b - a
    return None


def main():
    trans = json.load(open(sys.argv[1])); cfg = json.load(open(sys.argv[2]))
    cortes = cfg["cortes"]; trocas = cfg.get("trocas", {})
    neg = {w.lower() for w in cfg.get("negrito", [])}
    dest = [d.lower() for d in cfg.get("destaque", [])]
    words = []
    for seg in trans:
        for w in seg["words"]:
            s, e = remap(w["s"], cortes), remap(w["e"], cortes)
            if s is None:
                continue
            if e is None:
                e = fim_corte(w["s"], cortes)
            txt = w["w"].strip()
            for k, v in trocas.items():
                txt = re.sub(rf"\b{re.escape(k)}\b", v, txt, flags=re.I) if not k.startswith("=") else (v if txt == k[1:] else txt)
            if txt:
                words.append([txt, s, e])
    # grupos
    grupos, cur = [], []
    for i, w in enumerate(words):
        cur.append(w)
        texto = " ".join(x[0] for x in cur)
        prox = words[i + 1] if i + 1 < len(words) else None
        pausa = prox is None or prox[1] - w[2] > 0.35
        pont = w[0][-1] in ".,!?;:"
        cheio = len(cur) >= MAX_W or (prox and len(texto) + 1 + len(prox[0]) > MAX_CH)
        fimfrase = w[0][-1] in ".!?"
        if pausa or cheio or fimfrase or (pont and len(cur) >= MIN_W):
            grupos.append(cur); cur = []
    if cur:
        grupos.append(cur)
    ev = []
    for j, g in enumerate(grupos):
        ini = g[0][1]
        fim = g[-1][2] + 0.15
        if j + 1 < len(grupos):
            fim = min(fim + 0.25, grupos[j + 1][0][1])
        texto = " ".join(x[0] for x in g)
        for k, v in cfg.get("trocas_frase", {}).items():
            texto = re.sub(re.escape(k), v, texto, flags=re.I)
        if j == 0 or grupos[j - 1][-1][0][-1] in ".!?":
            texto = texto[0].upper() + texto[1:]
        low = texto.lower()
        marcado = None
        for d in dest:
            k = low.find(d)
            if k >= 0:
                marcado = texto[:k] + "{\\fnArchivo Black\\fs50\\c&H05B7F2&}" + texto[k:k + len(d)] + "{\\r}" + texto[k + len(d):]
                break
        if marcado is None:
            partes = []
            for tok in texto.split(" "):
                limpo = re.sub(r"[^\wÀ-ú@]", "", tok).lower()
                partes.append("{\\b1}" + tok + "{\\b0}" if limpo in neg else tok)
            marcado = " ".join(partes)
        ev.append(f"Dialogue: 0,{ts(ini)},{ts(fim)},Legenda,,0,0,0,,{{\\fad(60,0)}}{marcado}")
    cab = open(Path(__file__).resolve().parent / "templates" / "legenda_modelo.ass", encoding="utf-8").read().split("[Events]")[0]
    corpo = "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n" + "\n".join(ev) + "\n"
    if len(sys.argv) > 4:
        extra = open(sys.argv[4], encoding="utf-8").read()
        corpo += "\n".join(l for l in extra.splitlines() if l.startswith("Dialogue:")) + "\n"
    open(sys.argv[3], "w", encoding="utf-8").write(cab + corpo)
    print(f"ok -> {sys.argv[3]} ({len(ev)} legendas)")


if __name__ == "__main__":
    main()
