#!/usr/bin/env bash
# Copia as mídias renderizadas de uma pauta para o repositório PÚBLICO de mídia (GitHub Pages),
# porque a API da Meta só aceita imagens/vídeos em URL pública.
# Uso: tools/subir_midia.sh <slug>
# Pré-requisito: repositório público marcelolidgov/falaparana-midia com GitHub Pages ativo (branch main, raiz).
# URL resultante: https://marcelolidgov.github.io/falaparana-midia/<slug>/slide-01.jpg
set -euo pipefail
SLUG="$1"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MIDIA="${MIDIA_DIR:-$ROOT/../falaparana-midia}"
[ -d "$MIDIA/.git" ] || git clone --depth 1 https://github.com/marcelolidgov/falaparana-midia "$MIDIA"
mkdir -p "$MIDIA/$SLUG"
cp "$ROOT/output/$SLUG"/slide-*.jpg "$MIDIA/$SLUG/" 2>/dev/null || true
cp "$ROOT/output/$SLUG"/*.mp4 "$MIDIA/$SLUG/" 2>/dev/null || true
cp "$ROOT/output/$SLUG"/capa*.jpg "$MIDIA/$SLUG/" 2>/dev/null || true
touch "$MIDIA/.nojekyll"
cd "$MIDIA"
git add -A && git commit -qm "midia: $SLUG" && git push -q origin HEAD:main
echo "ok -> https://marcelolidgov.github.io/falaparana-midia/$SLUG/ (aguarde ~1-2 min o GitHub Pages atualizar antes de publicar)"
