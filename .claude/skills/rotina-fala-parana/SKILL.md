---
name: rotina-fala-parana
description: Rotina diária do agente Fala Paraná — pesquisar pauta do Paraná, criar arte/vídeo no padrão da marca, revisar, publicar (história/cultura) ou mandar para aprovação (demais), registrar e medir. Use quando pedirem "rotina", "post do dia", "rodar o agente" ou numa execução agendada.
---

# Rotina do dia — Fala Paraná

Siga `CLAUDE.md` (regras inegociáveis). Passo a passo:

## 1. Contexto (2 min)
- `git pull`. Leia `docs/ESTRATEGIA.md` (calendário + Aprendizados), o relatório mais recente em `docs/relatorios/` e `content/pautas/BACKLOG.md`.
- Veja que dia é hoje e qual formato o calendário pede. Datas comemorativas/efemérides do Paraná vêm antes.
- Pautas já prontas com `data_publicacao` de hoje (ou atrasada) têm prioridade: publique-as (respeitando a trava).
- Liste `content/posts/*.json` com status `revisao`/`aprovado`: se o Marcelão aprovou algo (status `aprovado`), publique primeiro.

## 2. Pauta e apuração
- Pesquise na web (AEN pr.gov.br, IBGE Cidades, IPARDES, ALEP, prefeituras, universidades). Mínimo 1 fonte primária por fato.
- Escolha um ângulo que gere **compartilhamento** ("manda pra quem é de X") ou **salvamento** (lista, linha do tempo, guia).
- Nada de copiar texto: escreva com suas palavras.

## 3. Roteiro (JSON em `content/posts/AAAA-MM-DD_slug.json`)
- Campos: `slug`, `data_publicacao`, `editoria`, `formato`, `status`, `objetivo`, `fontes`, `legenda`, `hashtags` (≤5), `slides`.
- Capa: gancho em ≤10 palavras com `*destaque*`. Miolo: 1 ideia/slide, ≤40 palavras. Fecho: `pergunta` regional.
- Legenda: 1ª linha = gancho; palavras-chave do tema (busca); CTA de salvar/compartilhar/comentar; até ~1.200 caracteres.

## 4. Arte e vídeo (você é o designer)
- `python3 tools/render.py <json>` → **abra `output/<slug>/previa.jpg` e cada slide com Read**. Corrija qualquer problema e renderize de novo.
- Quarta-feira (ou quando o carrossel for forte): `video/carrossel_para_reel.sh <slug>` e um JSON irmão com `"formato": "reel"`.
- Se o Marcelão enviou gravação: transcreva (se houver ferramenta), gere `.ass` com `video/legendas.py` e renderize com `video/render_reel.sh`.

## 5. Publicar ou pedir aprovação
- `historia`/`cultura`: checklist ok → `"status": "pronto"` → `tools/subir_midia.sh <slug>` → aguarde ~2 min →
  `node tools/publish_instagram.mjs <json> --publish --base-url https://marcelolidgov.github.io/falaparana-midia`.
- Outras editorias: `"status": "revisao"`; envie ao Marcelão a prévia (arquivo), legenda e fontes, e pare ali.
- Se a publicação estiver indisponível (sem token/rede — ver `docs/CONFIGURAR-META.md`), entregue os JPGs prontos para postar manualmente.

## 6. Fechar
- Segunda: `node tools/insights.mjs --dias 14` e atualize "Aprendizados" em `docs/ESTRATEGIA.md` (3 bullets, com números).
- Marque a pauta no BACKLOG, `git add -A && git commit -m "conteudo: <slug>" && git push`.
- Resumo final curto: publicado (link), aguardando aprovação (prévia), bloqueios, próxima pauta.
