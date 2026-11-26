// node tools/site.mjs   (from this build's folder; the share image comes from tools/og.mjs)
// Builds the live sites, hosted by Pulse CRM: https://socialstream.hu (Hungarian at the root, English under /en/) and,
// since 2026-11-26, https://socialstream.es (Spanish at the root; site/pages.mjs ORIGINS and DOMAINS). Pulse serves an
// uploaded folder's files exactly as they are, at its domain's root (the hosting session's notes,
// pulse-hosting-bundle.md and pulse-site-hosting-answers.md), and serves a folder's index.html at its address with a
// trailing slash, so this writes one folder and one ZIP per domain, dist/site/ and dist/site-es/ (each cleared first):
//   index.html and every page of site/pages.mjs at <its address>/index.html, each in one language
//                         (site/templates.mjs): the home page is Aurora Mix (concepts/mix.mjs), the others are built
//                         from its parts. Each has its own title, description, canonical address, language
//                         alternates (across both domains), share tags and structured data (site/head.mjs)
//   base.css mix.css site.css ss.js kit.js logo-anim.js reels.js site.js   the pages' own files, linked from the root
//   assets/               only the files the pages use: named in their markup, styles or scripts. The brand film's
//                         two cuts per language (the wide 1080 where Mix's opening fills a wide screen, the upright
//                         720 in the card and on phones) live in Pulse's Media Storage since v18 and are named by
//                         their address there, on their language's domain (site/films.mjs); a cut not stored yet
//                         travels here as before. Mix never asks for hero-540 (a smaller frame elsewhere)
//   favicon.ico favicon.svg apple-touch-icon.png site.webmanifest and the icons the manifest names
//                         the logo kit's web files, at the root, where the pages' head and the manifest ask for them
//   404.html robots.txt sitemap.xml llms.txt
//                         the sitemap lists its domain's pages with their language alternates on both domains;
//                         robots.txt names the AI crawlers (the doc's draft: everything allowed); llms.txt is the
//                         domain's own (the doc's draft with the pages' real addresses), which Pulse then serves
//                         instead of its own; the 404 page speaks the domain's language
// Real files only, no symlinks. It stops on an em dash in a page's visible words, title or description, if anything
// a page names is missing, if a stored film cut's file is no longer the one Media Storage holds, if a top-level name
// is one of Pulse's own paths, or if a folder breaks Pulse's limits (60 MB, 1,500 files).
import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { PAGES, ORIGINS, DOMAINS, url, IS_DRAFTS } from '../site/pages.mjs';
import { renderPage } from '../site/templates.mjs';
import { ON as ES_ON, TODO as ES_TODO, MISSES, onPage, word } from '../site/es.mjs';
import { FILMS, CUTS, STORED, filmFiles } from '../site/films.mjs';

// the site's languages: Hungarian and English on socialstream.hu, Spanish on socialstream.es (site/es.mjs)
const LANGS = ['hu', 'en', ...(ES_ON ? ['es'] : [])];

const OG = 'assets/og-image.jpg';
// a stored cut must still be the file that was uploaded to Media Storage (site/films.mjs)
for (const l of LANGS) for (const k of CUTS) {
  const c = FILMS[l][k]; if (!c.url) continue;
  if (!STORED.test(c.url)) throw new Error(`site/films.mjs: ${l} ${k} is not a Media Storage address on socialstream.hu or socialstream.es: ${c.url}`);
  const sha = createHash('sha256').update(fs.readFileSync(c.file)).digest('hex');
  if (sha !== c.sha256) throw new Error(`${c.file} is not the file Media Storage holds at ${c.url}: upload it again and change its sha256 and address in site/films.mjs`);
}
// Pulse's limits (services/page-zip.js): the ZIP up to 60 MiB, unpacked up to 250 MiB, at most 1,500 entries
const LIMIT_ZIP = 60 * 1048576, LIMIT_UNPACKED = 250 * 1048576, LIMIT_FILES = 1500;
// the first path segments Pulse keeps for itself on every domain (pulse-site-hosting-answers.md; /portal/ is its Client
// Portal since 2026-11-24): a file there would hide Pulse's own page or link
const PULSE = ['p', 'form', 'survey', 'survey-assets', 'book', 'a', 'r', 'embed', 'd', 't', 'c', 'o', 'u', 'm', 'chat', 'api', 'fonts', 'page-assets', 'w', 'ct', 'socialstream', 'healthz', '.well-known', 'portal'];

const read = f => fs.readFileSync(f, 'utf8');
if (!fs.existsSync(OG)) throw new Error(OG + ' is missing: run tools/og.mjs');

// the pages, each in every language
const pages = [];
for (const pg of PAGES) for (const l of LANGS) {
  onPage(pg.path[l]);
  const html = renderPage(pg, l), file = pg.path[l].replace(/^\//, '') + 'index.html';
  const visible = html.replace(/<!--[\s\S]*?-->/g, '').replace(/<script type="application\/ld\+json">[\s\S]*?<\/script>/g, '');
  if (/—/.test(visible)) throw new Error(`${file}: an em dash in the visible copy, the title or the description`);
  if (!/^<!doctype html>\s*<html lang="(hu|en|es)">/i.test(html) || !html.includes(`<html lang="${l}">`)) throw new Error(file + ' is not a complete page in its language');
  for (const need of ['<meta charset="utf-8">', '<meta name="viewport"', '<link rel="icon"', '<link rel="manifest"', `<link rel="canonical" href="${url(pg, l)}">`, 'hreflang="x-default"'])
    if (!html.includes(need)) throw new Error(file + ' has no ' + need);
  // a page in one language carries no words of the other, nor the switch buttons of the concepts
  if (/ data-en(-aria|-alt|-ph)?="/.test(html) || /data-set-lang/.test(html) || LANGS.some(x => x !== l && html.includes(`data-l="${x}"`))) throw new Error(file + ' still carries another language');
  // a Spanish page shows the English page's euros, never forints
  if (l === 'es' && /\d\s?(M\s?)?Ft\b/.test(visible.replace(/<[^>]+>/g, ' '))) throw new Error(file + ': a figure in forints on a Spanish page');
  pages.push({ pg, l, file, html });
}
// every word a Spanish page needs must be in site/es-words.mjs; SS_ES_TODO=1 lists the missing ones instead
if (ES_ON && MISSES.size) {
  if (ES_TODO) {
    fs.mkdirSync('dist', { recursive: true });
    fs.writeFileSync('dist/es-todo.mjs', '// the English words the Spanish pages still need (copy them into site/es-words.mjs with their Spanish)\nexport const TODO = [\n' + [...MISSES].map(([en, at]) => `  // ${[...at].slice(0, 3).join(' ')}${at.size > 3 ? ' …' : ''}\n  [${JSON.stringify(en)}, ''],`).join('\n') + '\n];\n');
    console.log(`dist/es-todo.mjs: ${MISSES.size} English words without their Spanish`);
    process.exit(0);
  }
  throw new Error(`the Spanish pages miss ${MISSES.size} words (SS_ES_TODO=1 lists them), the first: ${[...MISSES.keys()].slice(0, 3).map(x => JSON.stringify(x.slice(0, 60))).join(', ')}`);
}

// llms.txt lists every page (the doc's draft, facts from the site only), each with its own address
const page = id => PAGES.find(pg => pg.id === id);
const plain = s => String(s).replace(/<[^>]+>/g, '');
const link = (id, l) => `- [${plain(word(page(id).crumb, l))}${page(id).type === 'case' ? ({ en: ' (case study)', hu: ' (esettanulmány)', es: ' (caso de éxito)' })[l] : ''}](${url(page(id), l)})`;
const ids = ['services', ...PAGES.filter(pg => pg.type === 'service').map(pg => pg.id), 'cases', ...PAGES.filter(pg => pg.type === 'case').map(pg => pg.id), 'about', 'audit', 'faq', 'contact'];
const unlisted = PAGES.filter(pg => !ids.includes(pg.id) && pg.id !== 'home').map(pg => pg.id);
if (unlisted.length) throw new Error('llms.txt does not list ' + unlisted.join(', '));
const HOME = { hu: 'Főoldal', en: 'Home', es: 'Inicio' };
const pagesIn = l => `## Pages in ${({ hu: 'Hungarian', en: 'English', es: 'Spanish' })[l]}
- [${HOME[l]}](${url(page('home'), l)})
${ids.map(id => link(id, l)).join('\n')}`;
const llms = (origin, langs, email) => `# SocialStream

> Interest media agency: we make the video, run the ads on Meta, TikTok and Google,
> and measure what they bring in. Founded in 2022. Works from Budapest and Tenerife.

## What we do
- Video production: hooks, creative direction, shooting and editing for ads and reels
- Social media presence: Feed, Stories, Reels and TikTok; content calendar, community management, copywriting
- Paid advertising: Meta, TikTok and Google campaigns with daily optimisation, A/B testing and scaling
- Websites and landing pages built for mobile and for conversion
- Automation and email: lead follow-up, email sequences, automated funnels
- Growth strategy: campaign strategy, funnel audit, market positioning

## Results from client campaigns
- 81x ROAS for a door webshop (Google Performance Max)
- 79M Ft (about EUR 216K) revenue in one week for an industrial hall builder (Meta, B2B)
- 23x ROAS for a watch webshop's Christmas campaign, over 8M Ft revenue
- About 5,700 registrants for a healthcare webinar from 600K Ft: 105 Ft each
- 300M+ Ft of ad budget managed since 2022

## Who we work with
Webshops, B2B companies, webinars and events, local services and experiences.
At most two new partners a month.

## Free audit
A free 30-minute review of your ads, campaigns, landing page and offer.

## Contact
Email: ${email}
Website: ${origin}/
${DOMAINS.filter(D => D.origin !== origin && D.langs.some(l => LANGS.includes(l))).map(D => `Website in ${D.langs.filter(l => LANGS.includes(l)).map(l => ({ hu: 'Hungarian', en: 'English', es: 'Spanish' })[l]).join(' and ')}: ${D.origin}/`).join('\n')}

${(langs.includes('en') ? ['en', ...langs.filter(l => l !== 'en')] : langs).map(pagesIn).join('\n\n')}
`;

// the 404 page in a domain's language: shown for an unknown address at any depth, so everything it links is from the root
const NOT_FOUND = {
  hu: { title: 'Nincs ilyen oldal', h1: 'Ez az oldal nem létezik.', p: 'Lehet, hogy elírás van a címben, vagy ez az oldal már nem él.', btn: 'Vissza a főoldalra' },
  es: { title: 'Esta página no existe', h1: 'Esta página no existe.', p: 'Puede que haya un error en la dirección o que esta página ya no exista.', btn: 'Volver a la página de inicio' },
};
const notFound = (lang, others) => `<!doctype html>
<html lang="${lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${NOT_FOUND[lang].title} · SocialStream</title>
<meta name="robots" content="noindex">
<meta name="theme-color" content="#05070f">
<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<style>
  :root { color-scheme: dark; }
  html, body { height: 100%; margin: 0; }
  body { display: grid; place-items: center; padding: 24px; box-sizing: border-box; color: #eef1f8; font: 17px/1.6 system-ui, -apple-system, "Segoe UI", sans-serif;
    background: radial-gradient(60% 70% at 8% 110%, rgba(66, 92, 255, 0.34), transparent 60%), radial-gradient(50% 60% at 96% -10%, rgba(136, 78, 255, 0.22), transparent 60%), #05070f; }
  main { display: grid; gap: 18px; justify-items: start; max-width: 34rem; }
  img { width: 220px; height: auto; }
  h1 { margin: 10px 0 0; font-size: clamp(1.8rem, 6vw, 2.6rem); line-height: 1.1; letter-spacing: -0.02em; }
  p { margin: 0; color: #b9c1d6; }
  a { color: #d9d6ff; }
  a.btn { display: inline-block; margin-top: 6px; padding: 14px 22px; border-radius: 999px; background: #6a4dff; color: #fff; font-weight: 700; text-decoration: none; }
  a:focus-visible { outline: 2px solid #d9d6ff; outline-offset: 3px; }
  .en { font-size: 14px; color: #8a94ad; }
</style>
</head>
<body>
<main>
  <img src="/assets/socialstream-logo-horizontal-small-dark.svg" alt="SocialStream">
  <h1>${NOT_FOUND[lang].h1}</h1>
  <p>${NOT_FOUND[lang].p}</p>
  <a class="btn" href="/">${NOT_FOUND[lang].btn}</a>
${others.join('\n')}
</main>
</body>
</html>
`;
const NOT_FOUND_LINES = {
  hu: lang => `  <p class="en" lang="hu">Ez az oldal nem létezik. <a href="${hrefFrom('/', 'hu', lang)}">Ugrás a magyar főoldalra</a>.</p>`,
  en: lang => `  <p class="en" lang="en">This page doesn't exist. <a href="${hrefFrom('/en/', 'en', lang)}">Go to the home page</a>.</p>`,
  es: lang => `  <p class="en" lang="es">Esta página no existe. <a href="${hrefFrom('/', 'es', lang)}">Ir a la página de inicio</a>.</p>`,
};
const hrefFrom = (p, l, from) => (ORIGINS[l] === ORIGINS[from] ? p : ORIGINS[l] + p);

// one folder and one ZIP per domain; SS_DRAFTS=1 writes each next to it with -drafts, never the folders that are uploaded
const day = new Date().toISOString().slice(0, 10);
for (const D of DOMAINS) {
  const langs = D.langs.filter(l => LANGS.includes(l));
  if (!langs.length) continue;
  const OUT = D.out + (IS_DRAFTS ? '-drafts' : '');
  const mine = pages.filter(x => langs.includes(x.l));
  const email = (mine[0].html.match(/mailto:([^"?]+)/) || [])[1];
  if (!email) throw new Error(OUT + ': the home page has no contact address');

  // what the pages need
  const local = new Set(), assets = new Set(filmFiles(langs));
  const named = t => [...t.matchAll(/assets\/[A-Za-z0-9._-]+\.(?:webp|jpg|jpeg|png|svg|gif|mp4|webm|woff2?|vtt)/g)].map(m => m[0]);
  for (const { html } of mine) {
    for (const m of html.matchAll(/<link rel="stylesheet" href="\/([a-z0-9-]+\.css)">/g)) local.add(m[1]);
    for (const m of html.matchAll(/<script src="\/([a-z0-9-]+\.js)"><\/script>/g)) local.add(m[1]);
    named(html).forEach(a => assets.add(a));
  }
  for (const f of local) named(read(f)).forEach(a => assets.add(a));
  assets.add(OG);
  assets.add('assets/socialstream-logo-horizontal-small-dark.svg'); // the 404 page's logo
  const root = new Set(); for (const { html } of mine) for (const m of html.matchAll(/<link rel="(?:icon|apple-touch-icon|manifest)"[^>]*href="\/([^"]+)"/g)) root.add(m[1]);
  for (const i of JSON.parse(read('site.webmanifest')).icons || []) root.add(i.src.replace(/^\//, ''));
  const files = [...new Set([...local, ...[...assets].sort(), ...root])];
  const missing = files.filter(f => !fs.existsSync(f));
  if (missing.length) throw new Error(OUT + ': missing: ' + missing.join(', '));

  // write the folder: real copies (realpath, so a linked source still lands as a file)
  fs.rmSync(OUT, { recursive: true, force: true });
  fs.mkdirSync(OUT + '/assets', { recursive: true });
  for (const f of files) fs.copyFileSync(fs.realpathSync(f), path.join(OUT, f));
  for (const { file, html } of mine) { fs.mkdirSync(path.join(OUT, path.dirname(file)), { recursive: true }); fs.writeFileSync(path.join(OUT, file), html); }

  // robots.txt: the doc's draft, the same effect as before (every crawler allowed), with the AI crawlers named
  // (whether to keep them allowed is the founder's call; recommended yes)
  fs.writeFileSync(OUT + '/robots.txt', ['*', 'GPTBot', 'OAI-SearchBot', 'ClaudeBot', 'PerplexityBot', 'Google-Extended', 'Applebot-Extended'].map(a => `User-agent: ${a}\nAllow: /\n`).join('\n') + `\nSitemap: ${D.origin}/sitemap.xml\n`);

  // sitemap.xml: the domain's pages, each with its language alternates on both domains (the same as its hreflang links)
  fs.writeFileSync(OUT + '/sitemap.xml', `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">
${mine.map(({ pg, l }) => `  <url>
    <loc>${url(pg, l)}</loc>
    <lastmod>${day}</lastmod>
${LANGS.filter(x => pg.path[x]).map(x => `    <xhtml:link rel="alternate" hreflang="${x}" href="${url(pg, x)}"/>`).join('\n')}
    <xhtml:link rel="alternate" hreflang="x-default" href="${url(pg, 'hu')}"/>
  </url>`).join('\n')}
</urlset>
`);

  fs.writeFileSync(OUT + '/llms.txt', llms(D.origin, langs, email));

  const lang = langs[0];
  fs.writeFileSync(OUT + '/404.html', notFound(lang, LANGS.filter(x => x !== lang).map(x => NOT_FOUND_LINES[x](lang))));
  if (!fs.existsSync(path.join(OUT, 'assets/socialstream-logo-horizontal-small-dark.svg'))) throw new Error('404.html names a logo the site does not carry');

  // check the result the way Pulse will take it
  const all = [];
  const walk = d => { for (const e of fs.readdirSync(d, { withFileTypes: true })) { const p = path.join(d, e.name); if (e.isSymbolicLink()) throw new Error('symlink in the site: ' + p); if (e.isDirectory()) walk(p); else all.push(p); } };
  walk(OUT);
  const top = fs.readdirSync(OUT).map(n => n.replace(/\.[^.]+$/, '')).filter(n => PULSE.includes(n));
  if (top.length) throw new Error(OUT + ': these top-level names are Pulse\'s own paths: ' + top.join(', '));
  const bytes = all.reduce((t, f) => t + fs.statSync(f).size, 0);
  if (all.length > LIMIT_FILES || bytes > LIMIT_UNPACKED) throw new Error(`${OUT} is too big for Pulse: ${all.length} files, ${(bytes / 1048576).toFixed(1)} MB unpacked`);
  // the ZIP as it is uploaded (the folder's files at the top, no ./), measured against Pulse's 60 MiB
  const ZIP = path.resolve(OUT + '.zip');
  fs.rmSync(ZIP, { force: true });
  execFileSync('zip', ['-rXq', ZIP, '.'], { cwd: OUT });
  const zipBytes = fs.statSync(ZIP).size;
  if (zipBytes > LIMIT_ZIP) throw new Error(`${OUT}.zip is too big for Pulse: ${(zipBytes / 1048576).toFixed(2)} MiB of 60`);
  console.log(`${OUT} (${D.origin}): ${all.length} files, ${(bytes / 1048576).toFixed(1)} MB (${mine.length} pages, ${assets.size} assets, ${root.size} root icons; contact ${email}); ZIP ${OUT}.zip ${(zipBytes / 1048576).toFixed(2)} of 60 MiB`);
}
