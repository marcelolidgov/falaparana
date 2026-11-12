#!/usr/bin/env bash
# Confere se o agente Fala Paraná tem tudo para rodar e publicar sozinho.
# Uso: tools/diagnostico.sh
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; cd "$ROOT"
ok(){ printf '  [OK]    %s\n' "$1"; }; falta(){ printf '  [FALTA] %s\n' "$1"; FALTAS=$((FALTAS+1)); }
FALTAS=0
echo "== Criação (artes e vídeo)"
python3 -c "import PIL" 2>/dev/null && ok "Python + Pillow" || falta "Pillow (python3 -m pip install pillow)"
command -v ffmpeg >/dev/null && ok "ffmpeg" || falta "ffmpeg"
command -v node >/dev/null && ok "node" || falta "node"
[ -f brand/fontes/ArchivoBlack.ttf ] && [ -f brand/fontes/Inter-SemiBold.otf ] && ok "fontes da marca" || falta "fontes em brand/fontes"
[ -f brand/marcelao.jpg ] && ok "foto do Marcelão (brand/marcelao.jpg) p/ posts de opinião" || falta "foto do Marcelão em brand/marcelao.jpg (opinião usa um 'M' no lugar)"
python3 -c "import whisper" 2>/dev/null || python3 -c "import faster_whisper" 2>/dev/null && ok "transcrição automática (whisper)" || falta "transcrição automática p/ legendar vídeo gravado (opcional; precisa liberar instalação de pacotes)"

echo "== Publicação (API da Meta)"
[ -n "${IG_ACCESS_TOKEN:-}" ] && ok "IG_ACCESS_TOKEN definido" || falta "IG_ACCESS_TOKEN (secret do ambiente)"
for h in graph.facebook.com graph.instagram.com rupload.facebook.com; do
  c=$(curl -s -m 8 -o /dev/null -w '%{http_code}' "https://$h/" 2>/dev/null)
  [ "$c" != "000" ] && ok "rede liberada: $h" || falta "rede bloqueada: $h (liberar no ambiente)"
done
if [ -n "${IG_ACCESS_TOKEN:-}" ]; then
  u=$(curl -s -m 10 -H "Authorization: Bearer $IG_ACCESS_TOKEN" "https://${IG_GRAPH_HOST:-graph.facebook.com}/v21.0/me/accounts?fields=instagram_business_account%7Busername%7D" | grep -o '"username":"falaparanaoficial"')
  [ -n "$u" ] && ok "token enxerga @falaparanaoficial" || falta "token não enxerga @falaparanaoficial (conta Empresa + Página FB + permissões)"
fi

echo "== Mídia pública (GitHub Pages)"
git ls-remote https://github.com/marcelolidgov/falaparana-midia >/dev/null 2>&1 && ok "repositório falaparana-midia acessível" || falta "repositório público falaparana-midia (criar e conectar na sessão)"

echo "== Repositório"
git ls-remote origin >/dev/null 2>&1 && ok "push no falaparana" || falta "acesso ao repositório falaparana"
echo; [ $FALTAS -eq 0 ] && echo "Tudo pronto: o agente pode publicar sozinho." || echo "$FALTAS item(ns) faltando. Veja docs/CONFIGURAR-META.md."
