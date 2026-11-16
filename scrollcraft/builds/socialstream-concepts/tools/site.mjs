// node tools/site.mjs   (from this build's folder; the share image comes from tools/og.mjs)
// Builds the live site for https://socialstream.hu, hosted by Pulse CRM. Pulse serves an uploaded folder's files
// exactly as they are, at the domain root (the hosting session's notes, pulse-hosting-bundle.md and
// pulse-site-hosting-answers.md), and serves a folder's index.html at its address with a trailing slash, so this
// writes dist/site/ (cleared first):
//   index.html, en/index.html and every page of site/pages.mjs at <its address>/index.html, each in one language
//                         (site/templates.mjs): the home page is Aurora Mix (concepts/mix.mjs), the others are built
//                         from its parts. Each has its own title, description, canonical address, language
//                         alternates, share tags and structured data (site/head.mjs)
//   base.css mix.css site.css ss.js kit.js logo-anim.js reels.js   the pages' own files, linked from the root
//   assets/               only the files the pages use: named in their markup, styles or scripts, plus the two cuts
//                         of the brand film that kit.js picks between at runtime for Mix's two film frames (the wide
//                         1080 where the opening fills a wide screen, the upright 720 in the card and on phones), in
//                         Hungarian and in English (-en). Mix never asks for hero-540 (a smaller frame elsewhere)
//   favicon.ico favicon.svg apple-touch-icon.png site.webmanifest and the icons the manifest names
//                         the logo kit's web files, at the root, where the pages' head and the manifest ask for them
//   404.html robots.txt sitemap.xml llms.txt
//                         the sitemap lists every page with its language alternates; robots.txt names the AI crawlers
//                         (the doc's draft: the same effect as before, everything allowed); llms.txt is the site's own
//                         (the doc's draft with the pages' real addresses), which Pulse then serves instead of its own
// Real files only, no symlinks. It stops on an em dash in a page's visible words, title or description, if anything
// a page names is missing, if a top-level name is one of Pulse's own paths, or if the folder breaks Pulse's limits
// (60 MB, 1,500 files).
import fs from 'node:fs';
import path from 'node:path';
import { PAGES, ORIGIN, url, IS_DRAFTS } from '../site/pages.mjs';
import { renderPage } from '../site/templates.mjs';

// SS_DRAFTS=1 also builds the draft pages (site/pages.mjs), into their own folder, never into the one that is uploaded
const OUT = IS_DRAFTS ? 'dist/site-drafts' : 'dist/site';
const OG = 'assets/og-image.jpg';
const FILM = ['hero-1080', 'hero-v-720'].flatMap(n => [`assets/${n}.mp4`, `assets/${n}-en.mp4`]);
const LIMIT_MB = 60, LIMIT_FILES = 1500;
// the first path segments Pulse keeps for itself on the domain (pulse-site-hosting-answers.md): a file there would
// hide Pulse's own page or link
const PULSE = ['p', 'form', 'survey', 'survey-assets', 'book', 'a', 'r', 'embed', 'd', 't', 'c', 'o', 'u', 'm', 'chat', 'api', 'fonts', 'page-assets', 'w', 'ct', 'socialstream', 'healthz', '.well-known'];

const read = f => fs.readFileSync(f, 'utf8');
if (!fs.existsSync(OG)) throw new Error(OG + ' is missing: run tools/og.mjs');

// the pages, each in both languages
const pages = [];
for (const pg of PAGES) for (const l of ['hu', 'en']) {
  const html = renderPage(pg, l), file = pg.path[l].replace(/^\//, '') + 'index.html';
  const visible = html.replace(/<!--[\s\S]*?-->/g, '').replace(/<script type="application\/ld\+json">[\s\S]*?<\/script>/g, '');
  if (/—/.test(visible)) throw new Error(`${file}: an em dash in the visible copy, the title or the description`);
  if (!/^<!doctype html>\s*<html lang="(hu|en)">/i.test(html) || !html.includes(`<html lang="${l}">`)) throw new Error(file + ' is not a complete page in its language');
  for (const need of ['<meta charset="utf-8">', '<meta name="viewport"', '<link rel="icon"', '<link rel="manifest"', `<link rel="canonical" href="${url(pg, l)}">`, 'hreflang="x-default"'])
    if (!html.includes(need)) throw new Error(file + ' has no ' + need);
  // a page in one language carries no words of the other, nor the switch buttons of the concepts
  if (/ data-en(-aria|-alt|-ph)?="/.test(html) || /data-set-lang/.test(html) || html.includes(`data-l="${l === 'hu' ? 'en' : 'hu'}"`)) throw new Error(file + ' still carries the other language');
  pages.push({ pg, l, file, html });
}
const email = (pages[0].html.match(/mailto:([^"?]+)/) || [])[1];
if (!email) throw new Error('the home page has no contact address');

// what the pages need
const local = new Set(), assets = new Set(FILM);
const named = t => [...t.matchAll(/assets\/[A-Za-z0-9._-]+\.(?:webp|jpg|jpeg|png|svg|gif|mp4|webm|woff2?|vtt)/g)].map(m => m[0]);
for (const { html } of pages) {
  for (const m of html.matchAll(/<link rel="stylesheet" href="\/([a-z0-9-]+\.css)">/g)) local.add(m[1]);
  for (const m of html.matchAll(/<script src="\/([a-z0-9-]+\.js)"><\/script>/g)) local.add(m[1]);
  named(html).forEach(a => assets.add(a));
}
for (const f of local) named(read(f)).forEach(a => assets.add(a));
assets.add(OG);
const root = new Set(); for (const { html } of pages) for (const m of html.matchAll(/<link rel="(?:icon|apple-touch-icon|manifest)"[^>]*href="\/([^"]+)"/g)) root.add(m[1]);
for (const i of JSON.parse(read('site.webmanifest')).icons || []) root.add(i.src.replace(/^\//, ''));
const files = [...new Set([...local, ...[...assets].sort(), ...root])];
const missing = files.filter(f => !fs.existsSync(f));
if (missing.length) throw new Error('missing: ' + missing.join(', '));

// write the folder: real copies (realpath, so a linked source still lands as a file)
fs.rmSync(OUT, { recursive: true, force: true });
fs.mkdirSync(OUT + '/assets', { recursive: true });
for (const f of files) fs.copyFileSync(fs.realpathSync(f), path.join(OUT, f));
for (const { file, html } of pages) { fs.mkdirSync(path.join(OUT, path.dirname(file)), { recursive: true }); fs.writeFileSync(path.join(OUT, file), html); }

// robots.txt: the doc's draft, the same effect as before (every crawler allowed), with the AI crawlers named
// (whether to keep them allowed is the founder's call; recommended yes)
fs.writeFileSync(OUT + '/robots.txt', ['*', 'GPTBot', 'OAI-SearchBot', 'ClaudeBot', 'PerplexityBot', 'Google-Extended', 'Applebot-Extended'].map(a => `User-agent: ${a}\nAllow: /\n`).join('\n') + `\nSitemap: ${ORIGIN}/sitemap.xml\n`);

// sitemap.xml: every page, each with its language alternates (the same as its own hreflang links)
const day = new Date().toISOString().slice(0, 10);
fs.writeFileSync(OUT + '/sitemap.xml', `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">
${pages.map(({ pg, l }) => `  <url>
    <loc>${url(pg, l)}</loc>
    <lastmod>${day}</lastmod>
    <xhtml:link rel="alternate" hreflang="hu" href="${url(pg, 'hu')}"/>
    <xhtml:link rel="alternate" hreflang="en" href="${url(pg, 'en')}"/>
    <xhtml:link rel="alternate" hreflang="x-default" href="${url(pg, 'hu')}"/>
  </url>`).join('\n')}
</urlset>
`);

// llms.txt: the doc's draft (facts from the site only), with the pages' own addresses in both languages
const page = id => PAGES.find(pg => pg.id === id);
const plain = s => String(s).replace(/<[^>]+>/g, '');
const link = (id, l) => `- [${plain(page(id).crumb[l])}${page(id).type === 'case' ? (l === 'en' ? ' (case study)' : ' (esettanulmány)') : ''}](${url(page(id), l)})`;
const ids = ['services', ...PAGES.filter(pg => pg.type === 'service').map(pg => pg.id), 'cases', ...PAGES.filter(pg => pg.type === 'case').map(pg => pg.id), 'about', 'audit', 'faq', 'contact'];
const unlisted = PAGES.filter(pg => !ids.includes(pg.id) && pg.id !== 'home').map(pg => pg.id);
if (unlisted.length) throw new Error('llms.txt does not list ' + unlisted.join(', '));
fs.writeFileSync(OUT + '/llms.txt', `# SocialStream

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
Website: ${ORIGIN}/

## Pages in English
- [Home](${ORIGIN}/en/)
${ids.map(id => link(id, 'en')).join('\n')}

## Pages in Hungarian
- [Főoldal](${ORIGIN}/)
${ids.map(id => link(id, 'hu')).join('\n')}
`);

// 404.html: shown for an unknown address at any depth, so everything it links is from the root
fs.writeFileSync(OUT + '/404.html', `<!doctype html>
<html lang="hu">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Nincs ilyen oldal · SocialStream</title>
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
  <h1>Ez az oldal nem létezik.</h1>
  <p>Lehet, hogy elírás van a címben, vagy ez az oldal már nem él.</p>
  <a class="btn" href="/">Vissza a főoldalra</a>
  <p class="en">This page doesn't exist. <a href="/en/">Go to the home page</a>.</p>
</main>
</body>
</html>
`);
if (!fs.existsSync(path.join(OUT, 'assets/socialstream-logo-horizontal-small-dark.svg'))) throw new Error('404.html names a logo the site does not carry');

// check the result the way Pulse will take it
const all = [];
const walk = d => { for (const e of fs.readdirSync(d, { withFileTypes: true })) { const p = path.join(d, e.name); if (e.isSymbolicLink()) throw new Error('symlink in the site: ' + p); if (e.isDirectory()) walk(p); else all.push(p); } };
walk(OUT);
const top = fs.readdirSync(OUT).map(n => n.replace(/\.[^.]+$/, '')).filter(n => PULSE.includes(n));
if (top.length) throw new Error('these top-level names are Pulse\'s own paths: ' + top.join(', '));
const bytes = all.reduce((t, f) => t + fs.statSync(f).size, 0);
if (all.length > LIMIT_FILES || bytes > LIMIT_MB * 1048576) throw new Error(`too big for Pulse: ${all.length} files, ${(bytes / 1048576).toFixed(1)} MB`);
console.log(`${OUT}: ${all.length} files, ${(bytes / 1048576).toFixed(1)} MB (${pages.length} pages, ${assets.size} assets, ${root.size} root icons; contact ${email})`);
