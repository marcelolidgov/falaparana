#!/usr/bin/env bash
# Render final de Reel no padrão FALA PARANÁ (adaptado do kit "edição estilo Jorginho" do Fala Marcelão).
# Uso: video/render_reel.sh entrada.mp4 legenda.ass saida.mp4 [--sem-rodape]
# - 1080x1920 (9:16), 30 fps, preenche a tela
# - rodapé com logo + @ e legenda .ass (video/templates/legenda_modelo.ass)
# - áudio normalizado em -14 LUFS (padrão Reels)
set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"; ROOT="$(cd "$DIR/.." && pwd)"
IN="$1"; ASS="$2"; OUT="$3"; MODE="${4:-}"
OVERLAY="$DIR/overlay_rodape_1080x1920.png"
FONTS="$ROOT/brand/fontes"
[ -f "$OVERLAY" ] || python3 "$DIR/gerar_overlay.py"
ASS_ESC=$(printf '%s' "$ASS" | sed "s/\\\\/\\\\\\\\/g; s/:/\\\\:/g; s/'/\\\\'/g")
BASE="[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,setsar=1"
if [ "$MODE" = "--sem-rodape" ]; then
  FC="$BASE,subtitles='$ASS_ESC':fontsdir='$FONTS'[v]"; INPUTS=(-i "$IN")
else
  FC="$BASE[b];[b][1:v]overlay=0:0:shortest=1,subtitles='$ASS_ESC':fontsdir='$FONTS'[v]"; INPUTS=(-i "$IN" -loop 1 -i "$OVERLAY")
fi
HAS_AUDIO=$(ffprobe -v error -select_streams a -show_entries stream=index -of csv=p=0 "$IN" | head -1)
AUDIO=()
[ -n "$HAS_AUDIO" ] && AUDIO=(-map 0:a:0 -af "loudnorm=I=-14:TP=-1:LRA=11" -c:a aac -b:a 192k -ar 48000)
ffmpeg -hide_banner -y "${INPUTS[@]}" -filter_complex "$FC" -map "[v]" "${AUDIO[@]}" \
  -c:v libx264 -preset veryfast -crf 19 -profile:v high -pix_fmt yuv420p -shortest -movflags +faststart "$OUT"
echo "ok -> $OUT"
