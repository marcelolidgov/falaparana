#!/usr/bin/env python3
"""Renderiza posts do Fala Paraná a partir de um JSON de pauta.

Uso:
    python3 tools/render.py content/posts/<slug>.json [--formato 4:5|3:4]

Saída: output/<slug>/slide-01.jpg ... + output/<slug>/previa.jpg
- 4:5 (1080x1350) é o padrão: é o formato aceito pela API de publicação da Meta.
- 3:4 (1080x1440) só para postar manualmente pelo app.

Tipos de slide (campo "tipo"):
  capa, conteudo, fechamento        -> carrossel
  noticia, opiniao, video           -> post único
  reel_capa                         -> capa de reel 1080x1920
Texto entre *asteriscos* sai em AMARELO (destaque).
"""
import json, sys, argparse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parent.parent
FONTES = ROOT / "brand" / "fontes"
LOGOS = ROOT / "brand" / "logos"

# ---------- marca ----------
VERDE, AZUL, AMARELO, NEVE, CARVAO = "#0F4D3A", "#1B3F8B", "#F2B705", "#F7F4EC", "#14201C"
BRANCO, CINZA_TXT, CAIXA = "#FFFFFF", "#3C4741", "#22322C"
HANDLE = "@falaparanaoficial"
M = 90  # margem


def rgb(h):
    h = h.lstrip("#"); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def AB(s): return ImageFont.truetype(str(FONTES / "ArchivoBlack.ttf"), s)
def IN(s, peso="SemiBold"): return ImageFont.truetype(str(FONTES / f"Inter-{peso}.otf"), s)


_logo_cache = {}
def logo(nome, altura=None, largura=None):
    if nome not in _logo_cache:
        _logo_cache[nome] = Image.open(LOGOS / f"{nome}.png").convert("RGBA")
    im = _logo_cache[nome]
    if altura: r = altura / im.height
    else: r = largura / im.width
    return im.resize((int(im.width * r), int(im.height * r)), Image.LANCZOS)

LOCK_ESCURO = "horizontal_02-fundo-escuro-amarelo-verde"   # p/ fundo verde/carvão/azul
LOCK_CLARO = "horizontal_01-principal-verde-amarelo"       # p/ fundo neve
SIMB_AMARELO = "simbolo_02-fundo-escuro-amarelo-verde"     # balão amarelo
SIMB_VERDE = "simbolo_01-principal-verde-amarelo"          # balão verde


# ---------- texto ----------
def tw(font, t, track=0):
    return sum(font.getlength(c) + track for c in t) - (track if t else 0)


def draw_t(d, t, font, x, y, color, track=0):
    """y = linha de base."""
    for c in t:
        d.text((x, y), c, font=font, fill=rgb(color), anchor="ls"); x += font.getlength(c) + track
    return x


def tokens(texto):
    """'abc *def ghi*' -> [('abc',False),('def',True),('ghi',True)]"""
    out, dest = [], False
    for w in texto.split():
        ini = w.startswith("*"); fim = w.endswith("*") and len(w) > 1
        w2 = w.strip("*")
        if ini: dest = True
        out.append((w2, dest))
        if fim or (ini and w.count("*") == 2): dest = False
    return out


def wrap_tokens(toks, font, maxw, track=0):
    linhas, cur = [], []
    for w, dest in toks:
        teste = " ".join(x for x, _ in cur + [(w, dest)])
        if cur and tw(font, teste, track) > maxw:
            linhas.append(cur); cur = [(w, dest)]
        else:
            cur.append((w, dest))
    if cur: linhas.append(cur)
    return linhas


def bloco(d, texto, fonte_fn, x, y_topo, maxw, max_h, cor, cor_dest=AMARELO,
          tam_max=110, tam_min=40, entrelinha=1.08, track_em=-0.015, max_linhas=None):
    """Escreve texto que cabe em (maxw x max_h), reduzindo o corpo se preciso. Retorna y final."""
    toks = tokens(texto)
    for tam in range(tam_max, tam_min - 1, -2):
        f = fonte_fn(tam); tr = track_em * tam
        linhas = wrap_tokens(toks, f, maxw, tr)
        lh = tam * entrelinha
        if (max_linhas is None or len(linhas) <= max_linhas) and len(linhas) * lh <= max_h:
            break
    cap = tam * 0.72
    y = y_topo + cap
    for ln in linhas:
        xx = x
        for i, (w, dest) in enumerate(ln):
            s = w + (" " if i < len(ln) - 1 else "")
            xx = draw_t(d, s, f, xx, y, cor_dest if dest else cor, tr)
        y += lh
    return y - lh + (tam * 0.28)


def pill(d, x, y, texto, bg, fg, tam=34):
    f = AB(tam); w = tw(f, texto, 3) + 60; h = tam + 36
    d.rounded_rectangle((x, y, x + w, y + h), radius=h // 2, fill=rgb(bg))
    draw_t(d, texto, f, x + 30, y + h / 2 + tam * 0.36, fg, 3)
    return w, h


# ---------- imagem ----------
def tela(cor, w, h): return Image.new("RGBA", (w, h), rgb(cor) + (255,))


def foto_em(p, caminho, caixa, credito=None):
    x0, y0, x1, y1 = caixa
    im = Image.open(ROOT / caminho if not Path(caminho).is_absolute() else caminho)
    im = ImageOps.exif_transpose(im).convert("RGB")
    im = ImageOps.fit(im, (x1 - x0, y1 - y0), Image.LANCZOS, centering=(0.5, 0.4))
    p.paste(im, (x0, y0))
    if credito:
        d = ImageDraw.Draw(p); f = IN(22, "Medium"); t = credito
        w = tw(f, t) + 24
        d.rounded_rectangle((x1 - w - 16, y1 - 50, x1 - 16, y1 - 16), radius=8, fill=(0, 0, 0, 150))
        d.text((x1 - w - 4, y1 - 33), t, font=f, fill=(235, 235, 235), anchor="lm")


def degrade(w, h, inicio=0.35, maxa=235):
    g = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(g)
    for y in range(h):
        t = max(0.0, (y / h - inicio) / (1 - inicio)); a = int(maxa * min(1, t) ** 1.2)
        d.line([(0, y), (w, y)], fill=(20, 32, 28, a))
    return g


def rodape(p, d, lock, direita, cor):
    W, H = p.size
    lk = logo(lock, altura=76); p.alpha_composite(lk, (M, H - M - lk.height))
    f = IN(34, "SemiBold"); draw_t(d, direita, f, W - M - tw(f, direita), H - M - 22, cor)


def seta_arraste(d, x, y, cor_txt):
    f = IN(40, "Bold"); draw_t(d, "Arraste", f, x, y, cor_txt)
    ax = x + tw(f, "Arraste") + 26; cy = y - 14
    d.ellipse((ax, cy - 40, ax + 80, cy + 40), fill=rgb(AMARELO))
    d.line((ax + 22, cy, ax + 58, cy), fill=rgb(CARVAO), width=7)
    d.line((ax + 42, cy - 16, ax + 58, cy, ax + 42, cy + 16), fill=rgb(CARVAO), width=7, joint="curve")


# ---------- layouts ----------
def capa(s, W, H, **_):
    if s.get("foto"):
        p = tela(VERDE, W, H); d = ImageDraw.Draw(p)
        fh = int(H * 0.50)
        foto_em(p, s["foto"], (0, 0, W, fh), s.get("credito"))
        d.rectangle((0, fh, W, fh + 14), fill=rgb(AMARELO))
        pill(d, M, 80, s.get("etiqueta", "FALA PARANÁ").upper(), AMARELO, CARVAO)
        bloco(d, s["titulo"].upper(), AB, M, fh + 70, W - 2 * M, H - fh - 70 - 200, BRANCO, tam_max=96)
        sb = logo(SIMB_AMARELO, altura=96); p.alpha_composite(sb, (W - M - sb.width, H - M - sb.height + 10))
    else:
        p = tela(s.get("fundo", VERDE), W, H); d = ImageDraw.Draw(p)
        pill(d, M, 100, s.get("etiqueta", "FALA PARANÁ").upper(), AMARELO, CARVAO)
        sb = logo(SIMB_AMARELO, altura=130); p.alpha_composite(sb, (W - M - sb.width, 80))
        sub = s.get("subtitulo")
        y = bloco(d, s["titulo"].upper(), AB, M, int(H * 0.27), W - 2 * M, int(H * (0.42 if sub else 0.48)), BRANCO, tam_max=118)
        if sub:
            bloco(d, sub, lambda t: IN(t, "Medium"), M, y + 50, W - 2 * M, 110,
                  "#D5DDD8", tam_max=40, tam_min=30, entrelinha=1.35, track_em=0)
    seta_arraste(d, M, H - M - 10, BRANCO)
    return p


def conteudo(s, W, H, idx=0, total=0, **_):
    p = tela(NEVE, W, H); d = ImageDraw.Draw(p)
    num = s.get("numero", f"{idx:02d}")
    if s.get("foto"):
        fh = int(H * 0.42)
        foto_em(p, s["foto"], (0, 0, W, fh), s.get("credito"))
        y = fh + 60
        f = AB(120); draw_t(d, num, f, M - 6, y + 100, VERDE, -3)
        d.rectangle((M + tw(f, num, -3) + 30, y + 52, M + tw(f, num, -3) + 190, y + 64), fill=rgb(AMARELO))
        y = bloco(d, s["ponto"].upper(), AB, M, y + 150, W - 2 * M, 190, CARVAO, cor_dest=VERDE, tam_max=60, tam_min=40)
        if s.get("texto"):
            bloco(d, s["texto"], lambda t: IN(t, "Medium"), M, y + 30, W - 2 * M, H - y - 30 - 190,
                  CINZA_TXT, cor_dest=VERDE, tam_max=38, tam_min=28, entrelinha=1.4, track_em=0)
    else:
        f = AB(220); draw_t(d, num, f, M - 10, 330, VERDE, -4)
        d.rectangle((M, 390, M + 220, 402), fill=rgb(AMARELO))
        y = bloco(d, s["ponto"].upper(), AB, M, 470, W - 2 * M, 330, CARVAO, cor_dest=VERDE, tam_max=76, tam_min=44)
        if s.get("texto"):
            bloco(d, s["texto"], lambda t: IN(t, "Medium"), M, y + 50, W - 2 * M, H - y - 50 - 200,
                  CINZA_TXT, cor_dest=VERDE, tam_max=46, tam_min=30, entrelinha=1.4, track_em=0)
    rodape(p, d, LOCK_CLARO, f"{idx + 1}/{total}", CARVAO)
    return p


def fechamento(s, W, H, **_):
    p = tela(CARVAO, W, H); d = ImageDraw.Draw(p)
    sb = logo(SIMB_AMARELO, altura=200); p.alpha_composite(sb, (M, 110))
    y = bloco(d, s.get("titulo", "GOSTOU?").upper(), AB, M, 400, W - 2 * M, 260, BRANCO, tam_max=140, tam_min=60)
    linhas = s.get("acoes", [["SEGUE", HANDLE], ["SALVA", "pra ler depois"], ["COMPARTILHA", "com quem precisa saber"]])
    if s.get("pergunta"):
        linhas = [["COMENTA", s["pergunta"]]] + linhas[:2]
    y = max(y + 60, int(H * 0.50))
    bh, gap = 140, 22
    for a, b in linhas:
        d.rounded_rectangle((M, y, W - M, y + bh), radius=28, fill=rgb(CAIXA))
        draw_t(d, a, AB(42), M + 40, y + 62, AMARELO, 1)
        fb = IN(34, "SemiBold")
        while tw(fb, b) > W - 2 * M - 80 and fb.size > 22: fb = IN(fb.size - 2, "SemiBold")
        draw_t(d, b, fb, M + 40, y + 112, BRANCO)
        y += bh + gap
    return p


def noticia(s, W, H, **_):
    p = tela(CARVAO, W, H); d = ImageDraw.Draw(p)
    fh = int(H * 0.56)
    if s.get("foto"): foto_em(p, s["foto"], (0, 0, W, fh), s.get("credito"))
    else: p.alpha_composite(tela(VERDE, W, fh), (0, 0))
    d.rectangle((0, fh, W, fh + 14), fill=rgb(AMARELO))
    pill(d, M, 80, s.get("etiqueta", "NOTÍCIA").upper(), AMARELO, CARVAO)
    bloco(d, s["manchete"].upper(), AB, M, fh + 70, W - 2 * M, H - fh - 70 - 200, BRANCO, tam_max=78, tam_min=44)
    rodape(p, d, LOCK_ESCURO, HANDLE, BRANCO)
    return p


def opiniao(s, W, H, **_):
    p = tela(AMARELO, W, H); d = ImageDraw.Draw(p)
    pill(d, M, 100, s.get("etiqueta", "OPINIÃO").upper(), CARVAO, AMARELO)
    draw_t(d, "“", AB(440), M - 20, 560, VERDE)
    bloco(d, s["frase"].upper(), AB, M, int(H * 0.40), W - 2 * M, int(H * 0.36), CARVAO, cor_dest=VERDE, tam_max=84, tam_min=46)
    r = 160; y0 = H - M - r
    autor_foto = s.get("foto_autor", "brand/marcelao.jpg")
    if (ROOT / autor_foto).exists():
        im = ImageOps.fit(Image.open(ROOT / autor_foto).convert("RGB"), (r, r), Image.LANCZOS)
        mk = Image.new("L", (r, r), 0); ImageDraw.Draw(mk).ellipse((0, 0, r - 1, r - 1), fill=255)
        p.paste(im, (M, y0), mk)
    else:
        d.ellipse((M, y0, M + r, y0 + r), fill=rgb(VERDE))
        draw_t(d, "M", AB(80), M + 52, y0 + 112, AMARELO)
    draw_t(d, s.get("autor", "MARCELÃO").upper(), AB(46), M + r + 36, y0 + 74, CARVAO, 1)
    draw_t(d, s.get("cargo", "Apresentador do Fala Paraná"), IN(32, "Medium"), M + r + 36, y0 + 124, CARVAO)
    sb = logo(SIMB_VERDE, altura=110); p.alpha_composite(sb, (W - M - sb.width, H - M - sb.height - 20))
    return p


def video(s, W, H, **_):
    p = tela(CARVAO, W, H)
    if s.get("foto"): foto_em(p, s["foto"], (0, 0, W, H), s.get("credito"))
    p.alpha_composite(degrade(W, H, 0.25))
    d = ImageDraw.Draw(p)
    pill(d, M, 80, s.get("etiqueta", "NOVO VÍDEO").upper(), AMARELO, CARVAO)
    cx, cy = W // 2, int(H * 0.36)
    d.ellipse((cx - 105, cy - 105, cx + 105, cy + 105), fill=rgb(AMARELO))
    d.polygon([(cx - 34, cy - 54), (cx - 34, cy + 54), (cx + 60, cy)], fill=rgb(CARVAO))
    y = bloco(d, s["titulo"].upper(), AB, M, int(H * 0.58), W - 2 * M, int(H * 0.20), BRANCO, tam_max=84, tam_min=46)
    if s.get("convidado"):
        bloco(d, ("COM " + s["convidado"]).upper(), AB, M, y + 24, W - 2 * M, 60, AMARELO, tam_max=44, tam_min=30, max_linhas=1)
    rodape(p, d, LOCK_ESCURO, s.get("rodape", "Link na bio"), BRANCO)
    return p


def reel_capa(s, W, H, **_):
    W, H = 1080, 1920
    p = tela(CARVAO, W, H)
    if s.get("foto"): foto_em(p, s["foto"], (0, 0, W, H))
    p.alpha_composite(degrade(W, H, 0.2, 245)); d = ImageDraw.Draw(p)
    # área segura do grid (corte 3:4 no perfil): y 240..1680
    pill(d, M, 690, s.get("etiqueta", "FALA PARANÁ").upper(), AMARELO, CARVAO)
    bloco(d, s["titulo"].upper(), AB, M, 800, W - 2 * M, 420, BRANCO, tam_max=124, tam_min=70)
    lk = logo(LOCK_ESCURO, altura=84); p.alpha_composite(lk, (M, 1290))
    return p


LAYOUTS = dict(capa=capa, conteudo=conteudo, fechamento=fechamento, noticia=noticia,
               opiniao=opiniao, video=video, reel_capa=reel_capa)


def render(spec_path, formato="4:5"):
    spec = json.loads(Path(spec_path).read_text(encoding="utf-8"))
    slug = spec.get("slug") or Path(spec_path).stem
    W, H = (1080, 1350) if formato == "4:5" else (1080, 1440)
    out = ROOT / "output" / slug; out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("slide-*.jpg"): old.unlink()
    slides = spec["slides"]; arquivos = []
    for i, s in enumerate(slides):
        im = LAYOUTS[s["tipo"]](s, W, H, idx=i, total=len(slides)).convert("RGB")
        f = out / f"slide-{i + 1:02d}.jpg"; im.save(f, "JPEG", quality=92, optimize=True)
        arquivos.append(f)
    # prévia
    th = 420; ims = [Image.open(f) for f in arquivos]
    ims = [im.resize((int(im.width * th / im.height), th), Image.LANCZOS) for im in ims]
    prev = Image.new("RGB", (sum(i.width for i in ims) + 12 * (len(ims) + 1), th + 24), (236, 233, 224))
    x = 12
    for im in ims: prev.paste(im, (x, 12)); x += im.width + 12
    prev.save(out / "previa.jpg", quality=88)
    print(f"ok -> {out} ({len(arquivos)} imagens, {W}x{H})")
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("spec"); ap.add_argument("--formato", default="4:5")
    a = ap.parse_args(); render(a.spec, a.formato)
