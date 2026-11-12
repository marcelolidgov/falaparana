#!/usr/bin/env bash
# Transforma um carrossel renderizado em Reel 9:16 (sem precisar de gravação):
# cada slide entra centralizado sobre fundo carvão, com zoom lento ("Ken Burns") e transição suave.
# Uso: video/carrossel_para_reel.sh <slug> [segundos_por_slide=4.5] [trilha.mp3|wav]
# Saída: output/<slug>/reel.mp4
# Música: a API não aplica músicas da biblioteca do Instagram. Use trilha própria/livre de direitos
# (ou publique como rascunho e adicione o áudio em alta pelo app).
set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"; ROOT="$(cd "$DIR/.." && pwd)"
SLUG="$1"; DUR="${2:-4.5}"; TRILHA="${3:-}"
SRC="$ROOT/output/$SLUG"; OUT="$SRC/reel.mp4"
mapfile -t SLIDES < <(ls "$SRC"/slide-*.jpg | sort)
N=${#SLIDES[@]}; [ "$N" -gt 0 ] || { echo "sem slides em $SRC"; exit 1; }
FR=30; FRAMES=$(python3 -c "print(int($DUR*$FR))"); XF=0.4
INPUTS=(); FILT=""
for i in "${!SLIDES[@]}"; do
  INPUTS+=(-i "${SLIDES[$i]}")
  FILT+="[$i:v]scale=1080:-2,zoompan=z='min(1+0.0009*on,1.06)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=$FRAMES:s=1080x1350:fps=$FR,"
  FILT+="pad=1080:1920:0:285:color=0x14201C,setsar=1,format=yuv420p[s$i];"
done
PREV="s0"; OFF=0
for ((i=1;i<N;i++)); do
  OFF=$(python3 -c "print(round($i*($DUR-$XF),3))")
  FILT+="[$PREV][s$i]xfade=transition=slideleft:duration=$XF:offset=$OFF[x$i];"; PREV="x$i"
done
FILT="${FILT%;}"
AUD=()
if [ -n "$TRILHA" ]; then
  INPUTS+=(-i "$TRILHA"); AUD=(-map "$N:a" -af "loudnorm=I=-16:TP=-1.5,afade=t=out:st=$(python3 -c "print(max(0,$N*($DUR-$XF)-1.2))"):d=1" -c:a aac -b:a 192k -shortest)
fi
ffmpeg -hide_banner -loglevel error -y "${INPUTS[@]}" -filter_complex "$FILT" -map "[$PREV]" "${AUD[@]}" \
  -c:v libx264 -preset veryfast -crf 20 -pix_fmt yuv420p -r $FR -movflags +faststart "$OUT"
cp "${SLIDES[0]}" "$SRC/capa-reel.jpg"
echo "ok -> $OUT ($(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT")s)"
