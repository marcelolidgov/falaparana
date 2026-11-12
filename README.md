# Fala Paraná — agente de conteúdo

Agente que planeja, pesquisa, cria (artes, carrosséis e reels) e publica no Instagram **@falaparanaoficial**.

- Regras do agente: [CLAUDE.md](CLAUDE.md)
- Estratégia e calendário: [docs/ESTRATEGIA.md](docs/ESTRATEGIA.md)
- Identidade visual: [docs/MARCA.md](docs/MARCA.md) · logos em `brand/`
- Ligar a publicação automática: [docs/CONFIGURAR-META.md](docs/CONFIGURAR-META.md)
- Fila de pautas: [content/pautas/BACKLOG.md](content/pautas/BACKLOG.md)

## Estrutura
```
brand/          logos (PNG/SVG), fontes (Archivo Black, Inter), modelos de referência
content/posts/  uma pauta por JSON (roteiro + legenda + fontes + status)
content/fotos/  fotos com direito de uso (próprias, AEN com crédito, licença livre)
tools/          render.py (artes), publish_instagram.mjs (API Meta, trava de aprovação), insights.mjs, subir_midia.sh
video/          kit de Reels (adaptado do "estilo Jorginho" do Fala Marcelão): legendas, rodapé, render, carrossel→reel
docs/           estratégia, marca, configuração, relatórios
```

## Modo de publicação (misto)
História e cultura saem sozinhas depois do checklist. Notícia, política, opinião, negócios e podcast só saem com aprovação do Marcelão.

## Comandos rápidos
```bash
python3 tools/render.py content/posts/2026-12-19_aniversario-do-parana.json
video/carrossel_para_reel.sh 2026-12-19_aniversario-do-parana
node tools/publish_instagram.mjs content/posts/2026-12-19_aniversario-do-parana.json   # dry-run
```
