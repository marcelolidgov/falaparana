// Publica no @falaparanaoficial pela API oficial da Meta (Instagram Graph API).
//
// Uso:
//   node tools/publish_instagram.mjs content/posts/<slug>.json            -> DRY-RUN (não publica)
//   node tools/publish_instagram.mjs content/posts/<slug>.json --publish  -> publica de verdade
//   [--base-url https://marcelolidgov.github.io/falaparana-midia]  (ou env IMAGE_BASE_URL)
//
// Env (secrets do ambiente, NUNCA no repositório): IG_ACCESS_TOKEN, IG_USER_ID (opcional), IG_GRAPH_HOST (opcional)
//
// TRAVA DO MODO MISTO (decisão do Marcelão, 11/11/2026):
//   - editoria "historia" ou "cultura" com status "pronto"   -> pode sair sozinho
//   - qualquer outra editoria (noticia, politica, opiniao...) -> só com status "aprovado" (aprovado pelo Marcelão)
//   - sem fontes -> nunca publica
import fs from 'fs';
import path from 'path';

const AUTO_EDITORIAS = new Set(['historia', 'cultura']);
const ALVO = 'falaparanaoficial';
const MAX_HASHTAGS = 5;

const args = process.argv.slice(2);
const file = args[0];
const doPublish = args.includes('--publish');
const iBase = args.indexOf('--base-url');
const baseUrl = ((iBase >= 0 ? args[iBase + 1] : '') || process.env.IMAGE_BASE_URL || '').replace(/\/$/, '');
if (!file) { console.error('Informe o JSON da pauta.'); process.exit(1); }

const spec = JSON.parse(fs.readFileSync(file, 'utf8'));
const slug = spec.slug || path.basename(file, '.json');
const outDir = path.join(path.dirname(file), '..', '..', 'output', slug);

// ---------- validações ----------
const erros = [];
if (!Array.isArray(spec.fontes) || spec.fontes.length === 0) erros.push('sem fontes');
const tags = spec.hashtags || [];
if (tags.length > MAX_HASHTAGS) erros.push(`mais de ${MAX_HASHTAGS} hashtags (limite do Instagram)`);
const caption = [spec.legenda, tags.join(' ')].filter(Boolean).join('\n\n');
if (caption.length > 2200) erros.push('legenda passa de 2.200 caracteres');
const isReel = spec.formato === 'reel';
const midias = isReel
  ? ['reel.mp4']
  : fs.existsSync(outDir) ? fs.readdirSync(outDir).filter(f => /^slide-\d+\.jpg$/.test(f)).sort() : [];
if (midias.length === 0) erros.push(`nada renderizado em ${outDir} (rode tools/render.py)`);
if (midias.length > 20) erros.push('carrossel com mais de 20 itens');

const liberado = spec.status === 'aprovado' || (spec.status === 'pronto' && AUTO_EDITORIAS.has(spec.editoria));
if (!liberado) erros.push(`status "${spec.status}" / editoria "${spec.editoria}" exige aprovação do Marcelão (status "aprovado")`);
if (spec.status === 'publicado') erros.push('já publicado');

const urls = midias.map(m => `${baseUrl}/${slug}/${m}`);
console.log(`Pauta: ${slug}  |  editoria: ${spec.editoria}  |  status: ${spec.status}`);
console.log('Legenda:\n' + caption + '\n');
console.log('Mídia:\n' + urls.join('\n'));

if (!doPublish) {
  console.log('\nDRY-RUN: nada foi publicado.' + (erros.length ? '\nBloqueios: ' + erros.join('; ') : '\nPronto para --publish.'));
  process.exit(0);
}
if (erros.length) { console.error('\nNÃO PUBLICADO: ' + erros.join('; ')); process.exit(2); }
if (!baseUrl) { console.error('Falta --base-url (URL pública das mídias).'); process.exit(1); }

// ---------- API ----------
const { IG_ACCESS_TOKEN } = process.env;
const H = IG_ACCESS_TOKEN ? { Authorization: `Bearer ${IG_ACCESS_TOKEN}` } : {};
const G = `https://${process.env.IG_GRAPH_HOST || 'graph.facebook.com'}/v21.0`;
const get = async (u) => (await fetch(u, { headers: H })).json();
async function post(endpoint, params) {
  const r = await fetch(`${G}/${endpoint}`, { method: 'POST', body: new URLSearchParams(params), headers: H });
  const j = await r.json();
  if (!r.ok || j.error) throw new Error(JSON.stringify(j));
  return j;
}

let IG_USER_ID = process.env.IG_USER_ID;
if (!IG_USER_ID) {
  const pages = (await get(`${G}/me/accounts?fields=name,instagram_business_account%7Bid,username%7D&limit=100`)).data || [];
  IG_USER_ID = pages.map(p => p.instagram_business_account).find(a => a?.username === ALVO)?.id;
} else {
  const u = (await get(`${G}/${IG_USER_ID}?fields=username`)).username;
  if (u !== ALVO) { console.error(`IG_USER_ID aponta para @${u}, não @${ALVO}. Abortando.`); process.exit(1); }
}
if (!IG_USER_ID) { console.error(`Conta @${ALVO} não encontrada no token.`); process.exit(1); }

async function esperar(id) {
  for (let i = 0; i < 40; i++) {
    const s = await get(`${G}/${id}?fields=status_code`);
    if (s.status_code === 'FINISHED') return;
    if (s.status_code === 'ERROR') throw new Error('Meta recusou a mídia: ' + JSON.stringify(s));
    await new Promise(r => setTimeout(r, 6000));
  }
  throw new Error('Tempo esgotado processando mídia');
}

let creation;
if (isReel) {
  const c = await post(`${IG_USER_ID}/media`, { media_type: 'REELS', video_url: urls[0], caption, share_to_feed: 'true',
    ...(spec.capa_reel ? { cover_url: `${baseUrl}/${slug}/${spec.capa_reel}` } : {}) });
  await esperar(c.id); creation = c.id;
} else if (urls.length === 1) {
  creation = (await post(`${IG_USER_ID}/media`, { image_url: urls[0], caption })).id;
} else {
  const children = [];
  for (const u of urls) children.push((await post(`${IG_USER_ID}/media`, { image_url: u, is_carousel_item: 'true' })).id);
  const c = await post(`${IG_USER_ID}/media`, { media_type: 'CAROUSEL', children: children.join(','), caption });
  await esperar(c.id); creation = c.id;
}
const res = await post(`${IG_USER_ID}/media_publish`, { creation_id: creation });
const info = await get(`${G}/${res.id}?fields=permalink,timestamp`);

spec.status = 'publicado';
spec.publicado = { media_id: res.id, permalink: info.permalink, em: info.timestamp };
fs.writeFileSync(file, JSON.stringify(spec, null, 2) + '\n');
console.log(`Publicado! ${info.permalink}`);
