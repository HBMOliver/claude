// node lab/sitecheck.mjs dist/site http://localhost:4565/ dist/site-es http://localhost:4566/
//   (after tools/site.mjs, each folder served as a root; or against the live domains:
//    node lab/sitecheck.mjs dist/site https://socialstream.hu/ dist/site-es https://socialstream.es/)
// The live-site checks for socialstream.hu (Hungarian, English) and socialstream.es (Spanish, since 2026-11-26), each
// folder with the address it is served at; a folder's domain comes from its own sitemap. Every page from the sitemaps:
// - every file answers 200, and every page answers 200 at its own address (with the trailing slash)
// - each page's head: its language, one h1, a title and a description used by no other page, the canonical address
//   (its own), the language alternates (hu, en, es where the page has it, x-default) pointing both ways across the two
//   domains, the share tags, and structured data that parses, names the page, and has what the kind of page needs
//   (breadcrumb, service, FAQ, team)
// - no words of another language and no switch buttons left in a page, no em dash in what a page shows, no forints
//   on a Spanish page
// - every link inside a site goes to a page or file that exists (an address ends in "/"), every #part to a part, and
//   every link to the other domain to a page there
// - each domain's sitemap, robots.txt, llms.txt and 404 page; no top-level name is one of Pulse's own paths
// - in a browser, desktop and phone: no failed requests or console errors, no other hosts besides Google Fonts and the
//   film's, every loaded image decodes, nothing left unarrived after a scroll through the page, no sideways scroll at
//   390 px; the words the scripts write (the sound and film buttons, the form's topics) in the page's language; on the
//   Hungarian home page the title, and the English and Spanish pages behind the EN and ES links
// - the brand film (site/films.mjs): each home page names its own language's two cuts and plays them (desktop the
//   wide one, the card and phones the upright one), its structured data points at its wide cut in its language; a
//   cut stored in Pulse's Media Storage is fetched from its address, byte for byte the file in this folder (with
//   seeking), and is not in the site folder; a cut not stored yet is in the folder
import { createRequire } from 'node:module';
import { createHash } from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { FILMS, CUTS, STORED, filmSrc, filmUrl } from '../site/films.mjs';
const { chromium } = createRequire(process.cwd() + '/')('playwright-core');
const BUILD = path.dirname(path.dirname(fileURLToPath(import.meta.url)));   // the build folder, where the cuts' files are
const args = process.argv.slice(2);
if (args.length < 2 || args.length % 2) throw new Error('usage: node lab/sitecheck.mjs <folder> <base> [<folder> <base>]');
// each folder with the address it is served at, and the domain it is for (from its sitemap)
const SITES = [];
for (let i = 0; i < args.length; i += 2) {
  const dir = args[i], base = args[i + 1].replace(/\/?$/, '/');
  const first = fs.readFileSync(path.join(dir, 'sitemap.xml'), 'utf8').match(/<loc>([^<]+)<\/loc>/);
  SITES.push({ dir, base, origin: new URL(first[1]).origin });
}
const HU = 'https://socialstream.hu', ES = 'https://socialstream.es';
const siteOf = u => SITES.find(S => u === S.origin || u.startsWith(S.origin + '/'));
const LOCALE = { hu: 'hu_HU', en: 'en_GB', es: 'es_ES' };
// a page's language from its address: Spanish on socialstream.es, English under socialstream.hu/en/, else Hungarian
const langOf = u => { const x = new URL(u); return x.origin === ES ? 'es' : /^\/en\//.test(x.pathname) ? 'en' : 'hu'; };
// the language home pages and the paths of each kind of page, in every language
const HOME = /^\/(en\/)?$/;
const KIND = {
  service: /\/(szolgaltatasok|services|servicios)\/[^/]+\/$/, faq: /\/(gyik|faq|preguntas-frecuentes)\/$/, about: /\/(rolunk|about|sobre-nosotros)\/$/,
  cases: /\/(esettanulmanyok|case-studies|casos-de-exito)\/$/, caseOne: /\/(esettanulmanyok|case-studies|casos-de-exito)\/[^/]+\/$/,
};
let fails = 0, checks = 0; const ok = (what, cond, info = '') => { checks++; if (!cond) { fails++; console.log('FAIL', what, info); } };
const attr = (html, re) => (html.match(re) || [])[1];
const heads = {}, pages = [];
let nFiles = 0;

for (const S of SITES) {
  const files = S.files = []; const walk = d => { for (const e of fs.readdirSync(d, { withFileTypes: true })) { const p = path.join(d, e.name); if (e.isDirectory()) walk(p); else files.push(path.relative(S.dir, p)); } }; walk(S.dir);
  nFiles += files.length;
  for (const f of files) { const r = await fetch(S.base + f.split(path.sep).map(encodeURIComponent).join('/')); ok(`200 for ${S.origin} ${f}`, r.status === 200, r.status); await r.arrayBuffer(); }
  S.read = f => fs.readFileSync(path.join(S.dir, f), 'utf8');
  // the pages, from the sitemap: each of this domain
  const sitemap = S.read('sitemap.xml');
  const urls = [...sitemap.matchAll(/<url>([\s\S]*?)<\/url>/g)].map(m => ({ loc: m[1].match(/<loc>([^<]+)<\/loc>/)[1], alt: Object.fromEntries([...m[1].matchAll(/hreflang="([^"]+)" href="([^"]+)"/g)].map(a => [a[1], a[2]])) }));
  const fileOf = u => decodeURI(new URL(u).pathname).replace(/^\//, '') + 'index.html';
  const mine = urls.map(u => ({ ...u, S, path: new URL(u.loc).pathname, file: fileOf(u.loc) }));
  ok(S.origin + ' the sitemap lists pages', mine.length >= 2, mine.length);
  ok(S.origin + ' the sitemap lists only this domain', mine.every(pg => pg.loc.startsWith(S.origin + '/')), mine.map(pg => pg.loc).filter(u => !u.startsWith(S.origin + '/')).join(' '));
  ok(S.origin + ' every page in the folder is in the sitemap', files.filter(f => f.endsWith('index.html')).length === mine.length, files.filter(f => f.endsWith('index.html')).length + ' vs ' + mine.length);
  pages.push(...mine);
}

for (const pg of pages) {
  const S = pg.S, read = S.read;
  const r = await fetch(S.base + pg.path.slice(1)); ok('200 at ' + pg.loc, r.status === 200, r.status); await r.arrayBuffer();
  ok('page file for ' + pg.loc, fs.existsSync(path.join(S.dir, pg.file)));
  const html = read(pg.file), lang = attr(html, /<html lang="([^"]+)">/);
  const hd = heads[pg.loc] = {
    lang, title: attr(html, /<title>([^<]*)<\/title>/), desc: attr(html, /<meta name="description" content="([^"]*)">/),
    canon: attr(html, /<link rel="canonical" href="([^"]+)">/),
    alt: Object.fromEntries([...html.matchAll(/<link rel="alternate" hreflang="([^"]+)" href="([^"]+)">/g)].map(m => [m[1], m[2]])),
    ogUrl: attr(html, /<meta property="og:url" content="([^"]+)">/), ogTitle: attr(html, /<meta property="og:title" content="([^"]+)">/),
    ogImg: attr(html, /<meta property="og:image" content="([^"]+)">/), ogLocale: attr(html, /<meta property="og:locale" content="([^"]+)">/),
    h1: (html.match(/<h1[\s>]/g) || []).length, html,
  };
  const at = pg.loc;
  ok(at + ' lang', lang === langOf(pg.loc), lang);
  ok(at + ' one h1', hd.h1 === 1, hd.h1);
  ok(at + ' title', hd.title && hd.title.length >= 20 && hd.title.length <= 70, hd.title);
  ok(at + ' description', hd.desc && hd.desc.length >= 70 && hd.desc.length <= 170, (hd.desc || '').length + ' ' + hd.desc);
  ok(at + ' canonical is its own address', hd.canon === pg.loc, hd.canon);
  const langs = Object.keys(hd.alt).filter(k => k !== 'x-default');
  ok(at + ' alternates hu, en, x-default (and es)', hd.alt.hu && hd.alt.en && hd.alt['x-default'] === hd.alt.hu && hd.alt[lang] === pg.loc && langs.every(l => ['hu', 'en', 'es'].includes(l) && langOf(hd.alt[l]) === l), JSON.stringify(hd.alt));
  ok(at + ' sitemap alternates match the page', JSON.stringify(pg.alt) === JSON.stringify(hd.alt), JSON.stringify(pg.alt));
  ok(at + ' share tags', hd.ogUrl === pg.loc && hd.ogTitle && hd.ogImg === S.origin + '/assets/' + ({ hu: 'og-image.jpg', en: 'og-image-en.jpg', es: 'og-image-es.jpg' })[lang] && hd.ogLocale === LOCALE[lang], JSON.stringify([hd.ogUrl, hd.ogImg, hd.ogLocale]));
  // the switch links every language's page (this one marked current), on its own domain; no other language and no
  // switch buttons are left in the page
  const sw = [...html.matchAll(/<a href="([^"]+)" hreflang="(hu|en|es)" lang="\2"/g)].map(m => [m[2], m[1]]);
  ok(at + ' the language switch goes to the twin pages', sw.length === langs.length && sw.every(([l, h]) => new URL(h, S.origin + '/').href === hd.alt[l] && (h.startsWith('/') === (new URL(hd.alt[l]).origin === S.origin))), JSON.stringify(sw));
  ok(at + ' no words of another language', !/ data-en(-aria|-alt|-ph)?="/.test(html) && !/data-set-lang/.test(html) && !['hu', 'en', 'es'].some(l => l !== lang && html.includes(`data-l="${l}"`)));
  const shown = html.replace(/<!--[\s\S]*?-->/g, '').replace(/<script[\s\S]*?<\/script>/g, '');
  ok(at + ' no em dash', !/—/.test(shown));
  if (lang === 'es') ok(at + ' no forints on a Spanish page', !/\d\s?(M\s?)?Ft\b/.test(shown.replace(/<[^>]+>/g, ' ')));
  // structured data
  let ld = null; try { ld = JSON.parse(attr(html, /<script type="application\/ld\+json">([^<]+)<\/script>/)); } catch (e) {}
  const g = ld && ld['@graph'] || [], node = t => g.find(n => [].concat(n['@type']).includes(t));
  const webpage = g.find(n => n.url === pg.loc && /Page$/.test(n['@type']));
  const site = node('WebSite');
  ok(at + ' structured data parses, with the organisation and the page', !!(ld && node('Organization') && site && webpage && webpage.inLanguage === lang), JSON.stringify(g.map(n => n['@type'])));
  ok(at + ' the website is its domain\'s, the organisation socialstream.hu\'s', site && site.url === S.origin + '/' && webpage && webpage.isPartOf['@id'] === S.origin + '/#website' && node('Organization')['@id'] === HU + '/#org', JSON.stringify(site && [site.url, site.inLanguage]));
  if (!HOME.test(pg.path)) {
    const bc = node('BreadcrumbList');
    ok(at + ' breadcrumb data ends on the page', bc && bc.itemListElement.at(-1).item === pg.loc && bc.itemListElement[0].item === hd.alt[lang].replace(/^(https:\/\/[^/]+\/(en\/)?).*$/, '$1'), JSON.stringify(bc && bc.itemListElement.map(i => i.item)));
    ok(at + ' a visible breadcrumb', /<nav class="pg-crumbs"/.test(html));
  } else {
    const vo = node('VideoObject');
    ok(at + ' the film as a video, its own language\'s cut', vo && vo.inLanguage === lang && vo.contentUrl === filmUrl(lang, 'w') && vo.thumbnailUrl === S.origin + '/assets/hero-poster.jpg', JSON.stringify(vo && [vo.inLanguage, vo.contentUrl, vo.thumbnailUrl]));
    const boxes = [...html.matchAll(/<div class="film [^"]*" data-film[^>]*>/g)].map(m => m[0]);
    ok(at + ' every film names its language\'s two cuts', boxes.length > 0 && boxes.every(t => t.includes(`data-src-w="${filmSrc(lang, 'w')}"`) && t.includes(`data-src-v="${filmSrc(lang, 'v')}"`)), boxes.join(' '));
  }
  if (KIND.service.test(pg.path)) ok(at + ' service data', !!node('Service'));
  if (KIND.faq.test(pg.path)) {
    const shownQ = (html.match(/<details>/g) || []).length, fq = g.find(n => n['@type'] === 'FAQPage');
    ok(at + ' FAQ data has every question shown', fq && fq.mainEntity.length === shownQ && shownQ > 8, (fq && fq.mainEntity.length) + ' vs ' + shownQ);
  }
  if (KIND.about.test(pg.path)) ok(at + ' the team as people', g.filter(n => n['@type'] === 'Person').length === 4);
  // case studies: the hub lists every case as a link; a case sits under the hub and shows its number on its first screen
  if (KIND.cases.test(pg.path)) ok(at + ' the case studies as a collection, each case linked', !!node('CollectionPage') && (html.match(/<a class="mx-card mx-stat pg-case" href="/g) || []).length >= 4);
  if (KIND.caseOne.test(pg.path)) {
    const bc = node('BreadcrumbList');
    ok(at + ' a case under the case studies', bc && bc.itemListElement.length === 3 && KIND.cases.test(bc.itemListElement[1].item), JSON.stringify(bc && bc.itemListElement.map(i => i.item)));
    ok(at + ' the case shows its number on its first screen', /<div class="pg-case-art">\s*<article class="mx-card mx-stat pg-case[^"]*"[^>]*>[\s\S]*?<p class="n num">/.test(html));
  }
  // every link inside the site goes somewhere that exists
  for (const m of html.matchAll(/href="(\/[^"]*)"/g)) {
    const [p, frag] = m[1].split('#'), target = p.endsWith('/') ? p.slice(1) + 'index.html' : p.slice(1);
    ok(`${at} link ${m[1]} exists`, fs.existsSync(path.join(S.dir, decodeURI(target))) && (/\.[a-z0-9]+$/.test(p) || p.endsWith('/')));
    if (frag) ok(`${at} link ${m[1]} has its part`, read(target).includes(`id="${frag}"`));
  }
  for (const m of html.matchAll(/href="#([^"]+)"/g)) ok(`${at} #${m[1]} is on the page`, html.includes(`id="${m[1]}"`));
  // and every link to the other domain goes to a page there (when that folder is checked too)
  for (const m of html.matchAll(/<a [^>]*href="(https:\/\/socialstream\.(?:hu|es)\/[^"]*)"/g)) {
    const T = siteOf(m[1]); if (!T || T === S) { ok(`${at} no full link to its own domain: ${m[1]}`, T !== S); continue; }
    const p = new URL(m[1]).pathname;
    ok(`${at} link ${m[1]} is a page there`, p.endsWith('/') && fs.existsSync(path.join(T.dir, decodeURI(p.slice(1)) + 'index.html')));
  }
}
// the alternates point both ways (across the domains when both are checked), and every title and description is used once
for (const [loc, hd] of Object.entries(heads)) for (const l of Object.keys(hd.alt).filter(k => k !== 'x-default')) {
  if (!siteOf(hd.alt[l])) continue;
  const tw = heads[hd.alt[l]]; ok(`${loc} and its ${l} page point at each other`, tw && JSON.stringify(tw.alt) === JSON.stringify(hd.alt), hd.alt[l]);
}
const dup = k => { const s = Object.values(heads).map(h => h[k]); return s.filter((x, i) => s.indexOf(x) !== i); };
ok('every title is used once', dup('title').length === 0, dup('title').join(' | '));
ok('every description is used once', dup('desc').length === 0, dup('desc').join(' | '));
if (heads[HU + '/']) ok('the home page keeps its title', heads[HU + '/'].title === 'SocialStream · Interest media ügynökség', heads[HU + '/'].title);

// each domain's robots.txt, llms.txt, top level and manifest
const PULSE = ['p', 'form', 'survey', 'survey-assets', 'book', 'a', 'r', 'embed', 'd', 't', 'c', 'o', 'u', 'm', 'chat', 'api', 'fonts', 'page-assets', 'w', 'ct', 'socialstream', 'healthz', '.well-known', 'portal'];
for (const S of SITES) {
  const robots = S.read('robots.txt'), mine = pages.filter(pg => pg.S === S);
  ok(S.origin + ' robots points at its sitemap and lets every crawler in', robots.includes(`Sitemap: ${S.origin}/sitemap.xml`) && /User-agent: \*\nAllow: \//.test(robots) && !/Disallow/.test(robots));
  const llms = fs.existsSync(path.join(S.dir, 'llms.txt')) ? S.read('llms.txt') : '';
  const llmsUrls = [...llms.matchAll(/https:\/\/socialstream\.(?:hu|es)\/[^\s)]*/g)].map(m => m[0]);
  ok(S.origin + ' llms.txt names the pages', llms.startsWith('# SocialStream') && mine.every(pg => llmsUrls.includes(pg.loc)), mine.filter(pg => !llmsUrls.includes(pg.loc)).map(pg => pg.loc).join(' '));
  for (const u of new Set(llmsUrls)) if (siteOf(u)) ok(S.origin + ' llms.txt link is a page: ' + u, !!heads[u]);
  ok(S.origin + ' no top-level name is one of Pulse\'s own paths', !fs.readdirSync(S.dir).some(n => PULSE.includes(n.replace(/\.[^.]+$/, ''))));
  const man = JSON.parse(S.read('site.webmanifest'));
  for (const i of man.icons) ok(S.origin + ' manifest icon in the folder ' + i.src, fs.existsSync(path.join(S.dir, i.src.replace(/^\//, ''))));
}
// STATIC=1: the folders and the served files only, without the browser pass (a quick look, e.g. after an upload)
if (process.env.STATIC) { console.log(`${nFiles} files fetched, ${pages.length} pages, ${checks} checks (no browser); ${fails ? fails + ' FAILED' : 'all static site checks passed'}`); process.exit(fails ? 1 : 0); }

// the words the page scripts write (ss.js, kit.js, site.js), in each language
const RUNTIME = {
  hu: ['Hang be', 'Hang ki', 'Lejátszás', 'Szünet', 'Videó tartalomgyártás', 'Social média jelenlét', 'Fizetett hirdetés', 'Weboldal & landing', 'Automatizáció & e-mail', 'Növekedési stratégia'],
  en: ['Sound on', 'Sound off', 'Play', 'Pause', 'Video content production', 'Social media presence', 'Paid advertising', 'Website & landing pages', 'Automation & email', 'Growth strategy'],
  es: ['Activar sonido', 'Silenciar', 'Reproducir', 'Pausa', 'Producción de vídeo', 'Presencia en redes sociales', 'Publicidad de pago', 'Web y landing pages', 'Automatización y email', 'Estrategia de crecimiento'],
};

// the film's cuts: a stored one answers at its address with the file's own bytes (and a part of it, for seeking),
// and stays out of the folders; one not stored yet travels in its folder
const homeOf = l => pages.find(pg => langOf(pg.loc) === l && HOME.test(pg.path));
for (const l of Object.keys(FILMS).filter(homeOf)) for (const k of CUTS) {
  const c = FILMS[l][k], S = homeOf(l).S, own = fs.readFileSync(path.join(BUILD, c.file)), sha = createHash('sha256').update(own).digest('hex');
  if (!c.url) { ok(`${l} ${k}: the cut not stored yet is in the folder`, S.files.includes(c.file)); continue; }
  ok(`${l} ${k}: a stored cut's address, on its language's domain`, STORED.test(c.url) && c.sha256 === sha && new URL(c.url).origin === new URL(homeOf(l).loc).origin, c.url);
  ok(`${l} ${k}: a stored cut is not in the folder`, !SITES.some(T => T.files.includes(c.file)));
  const r = await fetch(c.url), got = Buffer.from(await r.arrayBuffer());
  ok(`${l} ${k}: ${c.url} answers with ${c.file}, byte for byte`, r.status === 200 && r.headers.get('content-type') === 'video/mp4' && got.length === own.length && createHash('sha256').update(got).digest('hex') === sha, `${r.status} ${r.headers.get('content-type')} ${got.length}`);
  const part = await fetch(c.url, { headers: { Range: 'bytes=1000-1999' } }), pb = Buffer.from(await part.arrayBuffer());
  ok(`${l} ${k}: ${c.url} answers a part of itself (seeking)`, part.status === 206 && pb.equals(own.subarray(1000, 2000)), part.status);
}

// in a browser
const b = await chromium.launch({ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', args: ['--autoplay-policy=no-user-gesture-required'] });
// the sites' own hosts, Google Fonts, and the domains where Media Storage serves the films
const allowed = [...SITES.map(S => new URL(S.base).host), 'fonts.googleapis.com', 'fonts.gstatic.com', ...new Set(Object.values(FILMS).flatMap(f => CUTS.map(k => f[k].url)).filter(Boolean).map(u => new URL(u).host))];
const esSite = SITES.find(S => S.origin === ES);
for (const [dev, opts] of [['desktop', { viewport: { width: 1440, height: 900 } }], ['phone', { viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true, deviceScaleFactor: 2 }]]) {
  const ctx = await b.newContext(opts);
  for (const pg of pages) {
    const S = pg.S, p = await ctx.newPage(), bad = [], errs = [], foreign = new Set();
    p.on('response', r => { if (r.status() >= 400) bad.push(r.status() + ' ' + r.url()); });
    p.on('requestfailed', r => { const t = r.failure()?.errorText || ''; if (!(t.includes('ERR_ABORTED') && /\.mp4/.test(r.url()))) bad.push('failed ' + t + ' ' + r.url()); });
    p.on('request', r => { const h = new URL(r.url()).host; if (h && !allowed.includes(h)) foreign.add(h); });
    p.on('pageerror', e => errs.push(e.message)); p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
    await p.goto(S.base + pg.path.slice(1), { waitUntil: 'load' }); await p.waitForTimeout(HOME.test(pg.path) ? 2500 : 900);
    // through the page, a screen at a time, measuring any sideways scroll on the way
    const H = await p.evaluate(() => document.documentElement.scrollHeight); let wide = 0;
    for (let y = 0; y < H + 900; y += 700) { await p.evaluate(y => scrollTo(0, y), y); await p.waitForTimeout(110); wide = Math.max(wide, await p.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth)); }
    await p.waitForTimeout(900);
    const st = await p.evaluate(() => ({
      unarrived: [...document.querySelectorAll('[data-r]')].filter(e => !e.classList.contains('in')).length,
      broken: [...document.images].filter(i => i.complete && i.currentSrc && !i.naturalWidth).map(i => i.currentSrc),
      lang: document.documentElement.lang, ssL: window.SS && SS.L,
      // what the scripts wrote: the sound and film buttons and the form's topics
      runtime: [...document.querySelectorAll('.ss-sound span, [data-film] .toggle span, .app label span')].map(e => e.textContent.trim()).filter(Boolean),
    }));
    const tag = `${dev} ${pg.loc}`;
    ok(tag + ' no 4xx/5xx or failed requests', bad.length === 0, bad.join(' | '));
    ok(tag + ' no console errors', errs.length === 0, errs.join(' | '));
    ok(tag + ' no other hosts', foreign.size === 0, [...foreign].join(', '));
    ok(tag + ' every loaded image decodes', st.broken.length === 0, st.broken.join(', '));
    ok(tag + ' everything arrived', st.unarrived === 0, st.unarrived);
    ok(tag + ' the page and its scripts in its language', st.lang === heads[pg.loc].lang && st.ssL === st.lang, JSON.stringify(st));
    if (dev === 'phone') ok(tag + ' no sideways scroll at 390 px', wide <= 0, String(wide));
    const other = st.runtime.filter(t => Object.entries(RUNTIME).some(([l, words]) => l !== st.lang && words.includes(t) && !RUNTIME[st.lang].includes(t)));
    ok(tag + ' the scripts\' words in the page\'s language', other.length === 0, other.join(' | '));
    if (HOME.test(pg.path)) {
      // the film in the page's language: the opening plays the wide cut on a computer and the upright one on a phone,
      // the card the upright one; each source is one of the page's own two cuts
      await p.evaluate(() => scrollTo(0, 0)); await p.waitForTimeout(1500);
      const fl = await p.evaluate(() => [...document.querySelectorAll('[data-film]')].map(f => ({ cut: f.dataset.cut, src: f.querySelector('video').currentSrc })).filter(f => f.src));
      const want = { w: new URL(filmSrc(st.lang, 'w'), S.base).href, v: new URL(filmSrc(st.lang, 'v'), S.base).href };
      ok(tag + ' the film in the page\'s language, the right cut for the frame', fl.length > 0 && fl.every(f => f.src === (f.cut === 'v' || dev === 'phone' ? want.v : want.w)), JSON.stringify(fl));
    }
    if (pg.loc === HU + '/') {
      const head = await p.evaluate(() => ({ title: document.title, canon: document.querySelector('link[rel=canonical]')?.href }));
      ok(dev + ' home title', head.title === 'SocialStream · Interest media ügynökség', head.title);
      ok(dev + ' home canonical', head.canon === HU + '/');
      // the EN link opens the English page, with the claim in English
      await p.evaluate(() => scrollTo(0, 0)); await p.waitForTimeout(400);
      await Promise.all([p.waitForURL(/\/en\/$/), p.locator('.lang a[hreflang="en"]').click()]); await p.waitForTimeout(800);
      const en = await p.evaluate(() => [...document.querySelectorAll('#hero-h [data-l="en"]')].some(e => e.textContent.includes('Interest has taken its place')) && document.documentElement.lang === 'en');
      ok(dev + ' the EN link opens the English page', en);
      // the ES link goes to socialstream.es; there (the folder served locally) the claim is in Spanish
      const esHref = await p.locator('.lang a[hreflang="es"]').getAttribute('href');
      ok(dev + ' the ES link goes to socialstream.es', esHref === ES + '/', esHref);
      if (esSite) {
        await p.goto(esSite.base, { waitUntil: 'load' }); await p.waitForTimeout(800);
        const es = await p.evaluate(() => [...document.querySelectorAll('#hero-h [data-l="es"]')].some(e => e.textContent.includes('El interés ha ocupado su lugar')) && document.documentElement.lang === 'es' && SS.L === 'es');
        ok(dev + ' the Spanish home has the claim in Spanish', es);
      }
    }
    await p.close();
  }
  await ctx.close();
}
// each domain's 404 page, in its language, linking its home and the other domain's
const NF = {
  [HU]: { h1: 'Ez az oldal nem létezik.', links: [ES + '/'] },
  [ES]: { h1: 'Esta página no existe.', links: [HU + '/', HU + '/en/'] },
};
for (const S of SITES) {
  const ctx = await b.newContext({ viewport: { width: 390, height: 700 } }), p = await ctx.newPage(), errs = [];
  p.on('pageerror', e => errs.push(e.message)); p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
  await p.goto(S.base + '404.html', { waitUntil: 'load' }); await p.waitForTimeout(400);
  const nf = await p.evaluate(() => ({ h1: document.querySelector('h1')?.textContent, logo: document.querySelector('img')?.naturalWidth, wide: document.documentElement.scrollWidth > innerWidth, home: document.querySelector('a.btn')?.getAttribute('href'), links: [...document.querySelectorAll('a')].map(a => a.getAttribute('href')) }));
  const want = NF[S.origin];
  ok(S.origin + ' 404 heading', want && nf.h1 === want.h1, nf.h1); ok(S.origin + ' 404 logo loads', nf.logo > 0); ok(S.origin + ' 404 no sideways scroll', !nf.wide); ok(S.origin + ' 404 links home', nf.home === '/');
  ok(S.origin + ' 404 links the other domain', want && want.links.every(h => nf.links.includes(h)), JSON.stringify(nf.links)); ok(S.origin + ' 404 no console errors', errs.length === 0, errs.join(' | '));
  if (process.env.SHOTS) await p.screenshot({ path: path.join(process.env.SHOTS, `404-${new URL(S.origin).hostname}-phone.png`) });
  await ctx.close();
}
await b.close();
console.log(`${nFiles} files fetched, ${pages.length} pages, ${checks} checks; ${fails ? fails + ' FAILED' : 'all site checks passed'}`);
// a failure fails the run, as the static pass does (before 2026-11-16 the browser pass always ended with 0)
process.exitCode = fails ? 1 : 0;
