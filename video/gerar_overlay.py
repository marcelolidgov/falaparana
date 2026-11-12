"""Gera o rodapé fixo FALA PARANÁ para Reels (PNG transparente 1080x1920).

Uso: python3 video/gerar_overlay.py
Saída: video/overlay_rodape_1080x1920.png
Zona reservada: legenda base em y≈1590; logo em y≈1700; @ em y≈1790. Nada de texto em y>1640 além disso
nem em y<220 (interface do Instagram).
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
W, H = 1080, 1920
GRAD_INICIO, GRAD_MAX = 1180, 230
LOGO = ROOT / "brand/logos/horizontal_02-fundo-escuro-amarelo-verde.png"
SAIDA = Path(__file__).resolve().parent / "overlay_rodape_1080x1920.png"


def main():
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for y in range(GRAD_INICIO, H):
        t = (y - GRAD_INICIO) / (H - GRAD_INICIO)
        d.line([(0, y), (W, y)], fill=(20, 32, 28, int(GRAD_MAX * t ** 1.4)))
    lk = Image.open(LOGO).convert("RGBA"); h = 70
    lk = lk.resize((int(lk.width * h / lk.height), h), Image.LANCZOS)
    img.alpha_composite(lk, ((W - lk.width) // 2, 1700 - h // 2))
    f = ImageFont.truetype(str(ROOT / "brand/fontes/Inter-SemiBold.otf"), 32)
    t = "@falaparanaoficial"
    d.text((W / 2 + 2, 1792), t, font=f, fill=(0, 0, 0, 140), anchor="mm")
    d.text((W / 2, 1790), t, font=f, fill=(255, 255, 255, 255), anchor="mm")
    img.save(SAIDA)
    print("ok ->", SAIDA)


if __name__ == "__main__":
    main()
