# Estratégia @falaparanaoficial

> Documento vivo. O agente atualiza a seção **Aprendizados** toda segunda-feira com base em `docs/relatorios/`.

## Aprendizados (mais recentes primeiro)
- _(vazio — primeiro relatório após 2 semanas de posts)_

## 1. Posicionamento
**"A voz do Paraná inteiro."** Notícia, história, cultura, cidades e negócios do estado, do litoral ao Noroeste, com Marcelão.
Diferente do @falamarcelao_ (opinião política local): aqui o tom é **jornalístico, curioso e orgulhoso do Paraná**, sem lado partidário.

Público: paranaenses de 20–60 anos, em todo o estado (não só Curitiba), que gostam de saber "o que acontece aqui" e de
histórias da própria cidade; paranaenses que moram fora; empreendedores locais.

## 2. O que o algoritmo premia em 2026 (pesquisa de 11/11/2026)
- **Compartilhamentos por DM e salvamentos** pesam mais que curtidas; tempo de visualização manda nos Reels.
- **Reels = alcance** em quem não segue; **carrosséis = salvamentos e engajamento** de quem segue. Use os dois de propósito.
- Primeiros **3 segundos** decidem o Reel: gancho com número, pergunta ou contraste já no primeiro quadro.
- Desde **30/04/2026**, contas que repostam conteúdo alheio saem das recomendações (vale para fotos e carrosséis). Só conteúdo original.
- Limite de **5 hashtags** por post; hashtag ajuda a classificar, não dá alcance. Legenda com **palavras-chave** (busca do Instagram funciona como SEO).
- **Trial Reels** (testar com não seguidores) liberam com 1.000+ seguidores: usar para testar ganchos.
- Fontes: Buffer, Later, Social Media Today/Planoly, TubeFilter/PetaPixel (abr/2026), documentação da Meta.

## 3. Pilares e mix (por semana)
| Pilar | Editoria no JSON | Formato | Publicação |
|---|---|---|---|
| História do Paraná ("Você sabia?") | `historia` | carrossel + reel derivado | automática |
| Cidade da Semana (399 municípios) | `cultura` | carrossel | automática |
| Cultura, gastronomia, natureza | `cultura` | carrossel / reel | automática |
| Notícia que importa pro estado | `noticia` | post único 4:5 | **aprovação** |
| Negócio paranaense | `negocios` | carrossel | **aprovação** |
| Opinião do Marcelão | `opiniao` | post amarelo / reel falado | **aprovação** |
| Podcast (quando estrear) | `podcast` | capa de vídeo + cortes | **aprovação** |

## 4. Calendário-base (dias úteis, agente roda de manhã)
| Dia | Post | Horário (hipótese) |
|---|---|---|
| Seg | Notícia da semana no Paraná (revisão) + relatório de números | 18h30 |
| Ter | Cidade da Semana (carrossel) | 11h30 |
| Qua | Reel: melhor carrossel da semana anterior virado vídeo | 19h |
| Qui | História do Paraná (carrossel) | 11h30 |
| Sex | Negócio paranaense **ou** opinião do Marcelão (revisão) | 18h30 |
| Datas | Efemérides (aniversário de cidades, 19/12 emancipação, festas regionais) têm prioridade | manhã |

Horários são hipótese (meio de semana, 11h–12h e 18h30–20h30). Após 4–6 semanas, trocar pelos picos reais do Insights.

## 5. Táticas de crescimento
1. **Ponte com o @falamarcelao_** (~20 mil seguidores): stories e um post em colaboração (Collab) apresentando o Fala Paraná.
2. **Série "Cidade da Semana"**: marcar a prefeitura e páginas locais da cidade; convidar a prefeitura para Collab. Pergunta no fim: "qual cidade vem na próxima?"
3. **Comentário como combustível**: todo carrossel termina com pergunta regional ("de qual cidade você é?", "na sua cidade tem isso?").
4. **Conteúdo de salvar**: listas, linhas do tempo, "X coisas que você não sabia", roteiros de viagem pelo estado.
5. **Reels a partir de carrosséis** (sem gravar) + **reels falados do Marcelão** com o kit de edição (legenda no padrão da marca).
6. **Convidados do podcast** → Collab no post do episódio (dobra o alcance inicial).
7. **Trial Reels** a partir de 1.000 seguidores: 2–3 ganchos por semana.

## 6. Métricas e metas
- Principal: **% de compartilhamentos + % de salvamentos sobre o alcance** (meta: 3%+ somados nos carrosséis).
- Reels: retenção média e alcance de não seguidores.
- Crescimento: seguidores/semana. Meta inicial: **1.000 seguidores em 60 dias**, 5.000 em 6 meses (rever após 1º mês).
- Toda segunda: `node tools/insights.mjs --dias 14` → repetir os 2 temas/formatos do topo, cortar o que ficou no fim.

## 7. O que não fazer
- Repostar conteúdo de outros perfis/portais; usar fotos sem direito; mais de 5 hashtags; texto corrido na arte;
  publicar notícia sem fonte primária; misturar a marca com o Fala Marcelão; usar "Quem faz o Paraná acontecer".
