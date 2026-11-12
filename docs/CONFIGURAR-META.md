# Ligar a publicação automática no @falaparanaoficial

Enquanto isto não estiver pronto, o agente cria e renderiza tudo, e você posta manualmente as imagens de `output/`.

## A. Instagram e Facebook (você, no celular, ~10 min)
1. Instagram @falaparanaoficial → Configurações → Tipo de conta → **Conta profissional → Empresa** (Business).
   Empresa é o tipo mais seguro para publicar Reels pela API.
2. Crie (ou use) uma **Página do Facebook "Fala Paraná"** e vincule: Instagram → Configurações → Central de Contas.

## B. App da Meta (pode reaproveitar o do Fala Marcelão)
1. developers.facebook.com → seu app (tipo Business) → produto **Instagram** / "Instagram Graph API".
2. Permissões: `instagram_basic`, `instagram_content_publish`, `instagram_manage_insights`, `pages_show_list`, `pages_read_engagement`.
3. Gere um **token de longa duração** (60 dias, renovável) com acesso à Página Fala Paraná. O script confere sozinho que a conta é @falaparanaoficial.

## C. Ambiente do Claude (onde o agente roda)
1. Configurações do ambiente → **Secrets/variáveis**: `IG_ACCESS_TOKEN` (e, se quiser, `IG_USER_ID`).
2. **Rede** do ambiente: liberar `graph.facebook.com`, `graph.instagram.com` e `rupload.facebook.com`
   (hoje estão bloqueados: o teste de 11/11/2026 deu erro de conexão).

## D. Hospedagem pública das mídias (a API da Meta baixa as imagens de uma URL pública)
1. GitHub → novo repositório **público** `falaparana-midia` (vazio).
2. Settings → Pages → Branch `main`, pasta `/ (root)` → Save.
3. Me avise para eu conectar o repositório na sessão. URL das mídias: `https://marcelolidgov.github.io/falaparana-midia/<slug>/slide-01.jpg`.
   Só vão para lá as artes **já prontas para publicar**, nada de rascunho.

## E. Teste
`node tools/publish_instagram.mjs content/posts/<slug>.json` (dry-run) → depois `--publish` num post de história.
