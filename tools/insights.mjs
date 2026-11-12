// Puxa os números dos últimos posts do @falaparanaoficial e grava um relatório em docs/relatorios/.
// Uso: node tools/insights.mjs [--dias 14]
// Env: IG_ACCESS_TOKEN, IG_USER_ID (opcional), IG_GRAPH_HOST (opcional)
// Métricas que importam (2026): compartilhamentos e salvamentos por alcance, tempo de visualização em reels.
import fs from 'fs';

const ALVO = 'falaparanaoficial';
const dias = Number(process.argv[process.argv.indexOf('--dias') + 1]) || 14;
const H = process.env.IG_ACCESS_TOKEN ? { Authorization: `Bearer ${process.env.IG_ACCESS_TOKEN}` } : {};
const G = `https://${process.env.IG_GRAPH_HOST || 'graph.facebook.com'}/v21.0`;
const get = async (u) => { const j = await (await fetch(u, { headers: H })).json(); if (j.error) throw new Error(JSON.stringify(j.error)); return j; };

let id = process.env.IG_USER_ID;
if (!id) {
  const pages = (await get(`${G}/me/accounts?fields=instagram_business_account%7Bid,username%7D&limit=100`)).data || [];
  id = pages.map(p => p.instagram_business_account).find(a => a?.username === ALVO)?.id;
}
if (!id) { console.error('Conta não encontrada'); process.exit(1); }

const perfil = await get(`${G}/${id}?fields=username,followers_count,media_count`);
const desde = Date.now() - dias * 864e5;
const media = ((await get(`${G}/${id}/media?fields=id,caption,media_type,media_product_type,permalink,timestamp,like_count,comments_count&limit=50`)).data || [])
  .filter(m => new Date(m.timestamp).getTime() >= desde);

const linhas = [];
for (const m of media) {
  const met = m.media_product_type === 'REELS'
    ? 'reach,views,saved,shares,comments,likes,ig_reels_avg_watch_time'
    : 'reach,views,saved,shares,comments,likes';
  let v = {};
  try {
    v = Object.fromEntries(((await get(`${G}/${m.id}/insights?metric=${met}`)).data || []).map(x => [x.name, x.values?.[0]?.value ?? x.total_value?.value]));
  } catch (e) { v = { erro: 1 }; }
  const pct = (a) => v.reach ? ((100 * (a || 0)) / v.reach).toFixed(1) + '%' : '-';
  linhas.push({ data: m.timestamp.slice(0, 10), tipo: m.media_product_type === 'REELS' ? 'reel' : m.media_type.toLowerCase(),
    titulo: (m.caption || '').split('\n')[0].slice(0, 60), alcance: v.reach ?? '-', views: v.views ?? '-',
    salv: v.saved ?? '-', comp: v.shares ?? '-', coment: v.comments ?? '-', salvPct: pct(v.saved), compPct: pct(v.shares),
    watch: v.ig_reels_avg_watch_time ? (v.ig_reels_avg_watch_time / 1000).toFixed(1) + 's' : '', link: m.permalink });
}
linhas.sort((a, b) => (parseFloat(b.compPct) || 0) + (parseFloat(b.salvPct) || 0) - (parseFloat(a.compPct) || 0) - (parseFloat(a.salvPct) || 0));

const hoje = new Date().toISOString().slice(0, 10);
let md = `# Relatório @${perfil.username} — ${hoje}\n\nSeguidores: **${perfil.followers_count}** · posts no perfil: ${perfil.media_count} · janela: ${dias} dias\n\n`;
md += '| Data | Tipo | Post | Alcance | Salv. | % salv | Comp. | % comp | Coment. | Retenção |\n|---|---|---|---|---|---|---|---|---|---|\n';
for (const l of linhas) md += `| ${l.data} | ${l.tipo} | [${l.titulo.replace(/\|/g, '/')}](${l.link}) | ${l.alcance} | ${l.salv} | ${l.salvPct} | ${l.comp} | ${l.compPct} | ${l.coment} | ${l.watch} |\n`;
md += '\nOrdenado por (% compartilhamentos + % salvamentos). Use o topo da lista para decidir o que repetir.\n';
fs.mkdirSync('docs/relatorios', { recursive: true });
fs.writeFileSync(`docs/relatorios/${hoje}.md`, md);
console.log(md);
