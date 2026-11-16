// node lab/sitecheck.mjs dist/site http://localhost:4565/   (after tools/site.mjs, with dist/site served as the root;
// or against the live domain: node lab/sitecheck.mjs dist/site https://socialstream.hu/)
// The live-site checks for socialstream.hu, every page from the folder's sitemap:
// - every file answers 200, and every page answers 200 at its own address (with the trailing slash)
// - each page's head: its language, one h1, a title and a description used by no other page, the canonical address
//   (its own), the three language alternates (hu, en, x-default) pointing both ways, the share tags, and structured
//   data that parses, names the page, and has what the kind of page needs (breadcrumb, service, FAQ, team)
// - no words of the other language and no switch buttons left in a page, no em dash in what a page shows
// - every link inside the site goes to a page or file that exists (an address ends in "/"), every #part to a part
// - the sitemap, robots.txt, llms.txt and the 404 page; no top-level name is one of Pulse's own paths
// - in a browser, desktop and phone: no failed requests or console errors, no other hosts besides Google Fonts,
//   every loaded image decodes, nothing left unarrived after a scroll through the page, no sideways scroll at
//   390 px; on the home page the title, the share image and the English page behind the EN link
import { createRequire } from 'node:module';
import fs from 'node:fs';
import path from 'node:path';
const { chromium } = createRequire(process.cwd() + '/')('playwright-core');
const [dir, base] = process.argv.slice(2);
const ORIGIN = 'https://socialstream.hu';
let fails = 0, checks = 0; const ok = (what, cond, info = '') => { checks++; if (!cond) { fails++; console.log('FAIL', what, info); } };
const files = []; const walk = d => { for (const e of fs.readdirSync(d, { withFileTypes: true })) { const p = path.join(d, e.name); if (e.isDirectory()) walk(p); else files.push(path.relative(dir, p)); } }; walk(dir);
for (const f of files) { const r = await fetch(base + f.split(path.sep).map(encodeURIComponent).join('/')); ok('200 for ' + f, r.status === 200, r.status); await r.arrayBuffer(); }

// the pages, from the sitemap
const read = f => fs.readFileSync(path.join(dir, f), 'utf8');
const sitemap = read('sitemap.xml');
const urls = [...sitemap.matchAll(/<url>([\s\S]*?)<\/url>/g)].map(m => ({ loc: m[1].match(/<loc>([^<]+)<\/loc>/)[1], alt: Object.fromEntries([...m[1].matchAll(/hreflang="([^"]+)" href="([^"]+)"/g)].map(a => [a[1], a[2]])) }));
const fileOf = u => decodeURI(new URL(u).pathname).replace(/^\//, '') + 'index.html';
const pages = urls.map(u => ({ ...u, path: new URL(u.loc).pathname, file: fileOf(u.loc) }));
ok('the sitemap lists pages', pages.length >= 2, pages.length);
ok('every page in the folder is in the sitemap', files.filter(f => f.endsWith('index.html')).length === pages.length, files.filter(f => f.endsWith('index.html')).length + ' vs ' + pages.length);
const attr = (html, re) => (html.match(re) || [])[1];
const heads = {};
for (const pg of pages) {
  const r = await fetch(base + pg.path.slice(1)); ok('200 at ' + pg.path, r.status === 200, r.status); await r.arrayBuffer();
  ok('page file for ' + pg.path, fs.existsSync(path.join(dir, pg.file)));
  const html = read(pg.file), lang = attr(html, /<html lang="([^"]+)">/);
  const hd = heads[pg.loc] = {
    lang, title: attr(html, /<title>([^<]*)<\/title>/), desc: attr(html, /<meta name="description" content="([^"]*)">/),
    canon: attr(html, /<link rel="canonical" href="([^"]+)">/),
    alt: Object.fromEntries([...html.matchAll(/<link rel="alternate" hreflang="([^"]+)" href="([^"]+)">/g)].map(m => [m[1], m[2]])),
    ogUrl: attr(html, /<meta property="og:url" content="([^"]+)">/), ogTitle: attr(html, /<meta property="og:title" content="([^"]+)">/),
    ogImg: attr(html, /<meta property="og:image" content="([^"]+)">/), ogLocale: attr(html, /<meta property="og:locale" content="([^"]+)">/),
    h1: (html.match(/<h1[\s>]/g) || []).length, html,
  };
  ok(pg.path + ' lang', lang === (pg.path.startsWith('/en/') ? 'en' : 'hu'), lang);
  ok(pg.path + ' one h1', hd.h1 === 1, hd.h1);
  ok(pg.path + ' title', hd.title && hd.title.length >= 20 && hd.title.length <= 70, hd.title);
  ok(pg.path + ' description', hd.desc && hd.desc.length >= 70 && hd.desc.length <= 170, (hd.desc || '').length + ' ' + hd.desc);
  ok(pg.path + ' canonical is its own address', hd.canon === pg.loc, hd.canon);
  ok(pg.path + ' alternates hu, en, x-default', hd.alt.hu && hd.alt.en && hd.alt['x-default'] === hd.alt.hu && hd.alt[lang] === pg.loc, JSON.stringify(hd.alt));
  ok(pg.path + ' sitemap alternates match the page', JSON.stringify(pg.alt) === JSON.stringify({ hu: hd.alt.hu, en: hd.alt.en, 'x-default': hd.alt['x-default'] }), JSON.stringify(pg.alt));
  ok(pg.path + ' share tags', hd.ogUrl === pg.loc && hd.ogTitle && hd.ogImg === ORIGIN + '/assets/og-image.jpg' && hd.ogLocale === (lang === 'en' ? 'en_GB' : 'hu_HU'), JSON.stringify([hd.ogUrl, hd.ogImg, hd.ogLocale]));
  // the switch is a link to the twin page; no other language and no switch buttons are left in the page
  const sw = [...html.matchAll(/<a href="([^"]+)" hreflang="(hu|en)" lang="\2"/g)].map(m => [m[2], m[1]]);
  ok(pg.path + ' the HU / EN switch goes to the twin pages', sw.length === 2 && sw.every(([l, h]) => ORIGIN + h === hd.alt[l]), JSON.stringify(sw));
  ok(pg.path + ' no words of the other language', !/ data-en(-aria|-alt|-ph)?="/.test(html) && !/data-set-lang/.test(html) && !html.includes(`data-l="${lang === 'hu' ? 'en' : 'hu'}"`));
  const shown = html.replace(/<!--[\s\S]*?-->/g, '').replace(/<script[\s\S]*?<\/script>/g, '');
  ok(pg.path + ' no em dash', !/—/.test(shown));
  // structured data
  let ld = null; try { ld = JSON.parse(attr(html, /<script type="application\/ld\+json">([^<]+)<\/script>/)); } catch (e) {}
  const g = ld && ld['@graph'] || [], node = t => g.find(n => [].concat(n['@type']).includes(t));
  const webpage = g.find(n => n.url === pg.loc && /Page$/.test(n['@type']));
  ok(pg.path + ' structured data parses, with the organisation and the page', !!(ld && node('Organization') && node('WebSite') && webpage && webpage.inLanguage === lang), JSON.stringify(g.map(n => n['@type'])));
  if (pg.path !== '/' && pg.path !== '/en/') {
    const bc = node('BreadcrumbList');
    ok(pg.path + ' breadcrumb data ends on the page', bc && bc.itemListElement.at(-1).item === pg.loc && bc.itemListElement[0].item === hd.alt[lang].replace(/^(https:\/\/[^/]+\/(en\/)?).*$/, '$1'), JSON.stringify(bc && bc.itemListElement.map(i => i.item)));
    ok(pg.path + ' a visible breadcrumb', /<nav class="pg-crumbs"/.test(html));
  } else ok(pg.path + ' the film as a video', !!node('VideoObject'));
  if (/\/(szolgaltatasok|services)\/[^/]+\/$/.test(pg.path)) ok(pg.path + ' service data', !!node('Service'));
  if (/\/(gyik|faq)\/$/.test(pg.path)) {
    const shownQ = (html.match(/<details>/g) || []).length, fq = g.find(n => n['@type'] === 'FAQPage');
    ok(pg.path + ' FAQ data has every question shown', fq && fq.mainEntity.length === shownQ && shownQ > 8, (fq && fq.mainEntity.length) + ' vs ' + shownQ);
  }
  if (/\/(rolunk|about)\/$/.test(pg.path)) ok(pg.path + ' the team as people', g.filter(n => n['@type'] === 'Person').length === 4);
  // case studies: the hub lists every case as a link; a case sits under the hub and shows its number on its first screen
  if (/\/(esettanulmanyok|case-studies)\/$/.test(pg.path)) ok(pg.path + ' the case studies as a collection, each case linked', !!node('CollectionPage') && (html.match(/<a class="mx-card mx-stat pg-case" href="/g) || []).length >= 4);
  if (/\/(esettanulmanyok|case-studies)\/[^/]+\/$/.test(pg.path)) {
    const bc = node('BreadcrumbList');
    ok(pg.path + ' a case under the case studies', bc && bc.itemListElement.length === 3 && /\/(esettanulmanyok|case-studies)\/$/.test(bc.itemListElement[1].item), JSON.stringify(bc && bc.itemListElement.map(i => i.item)));
    ok(pg.path + ' the case shows its number on its first screen', /<div class="pg-case-art">\s*<article class="mx-card mx-stat pg-case[^"]*"[^>]*>[\s\S]*?<p class="n num">/.test(html));
  }
  // every link inside the site goes somewhere that exists
  for (const m of html.matchAll(/href="(\/[^"]*)"/g)) {
    const [p, frag] = m[1].split('#'), target = p.endsWith('/') ? p.slice(1) + 'index.html' : p.slice(1);
    ok(`${pg.path} link ${m[1]} exists`, fs.existsSync(path.join(dir, decodeURI(target))) && (/\.[a-z0-9]+$/.test(p) || p.endsWith('/')));
    if (frag) ok(`${pg.path} link ${m[1]} has its part`, read(target).includes(`id="${frag}"`));
  }
  for (const m of html.matchAll(/href="#([^"]+)"/g)) ok(`${pg.path} #${m[1]} is on the page`, html.includes(`id="${m[1]}"`));
}
// the alternates point both ways, and every title and description is used once
for (const [loc, hd] of Object.entries(heads)) for (const l of ['hu', 'en']) { const tw = heads[hd.alt[l]]; ok(`${loc} and its ${l} page point at each other`, tw && tw.alt.hu === hd.alt.hu && tw.alt.en === hd.alt.en, hd.alt[l]); }
const dup = k => { const s = Object.values(heads).map(h => h[k]); return s.filter((x, i) => s.indexOf(x) !== i); };
ok('every title is used once', dup('title').length === 0, dup('title').join(' | '));
ok('every description is used once', dup('desc').length === 0, dup('desc').join(' | '));
ok('the home page keeps its title', heads[ORIGIN + '/'].title === 'SocialStream · Interest media ügynökség', heads[ORIGIN + '/'].title);

// robots.txt, llms.txt, the folder's top level
const robots = read('robots.txt');
ok('robots points at the sitemap and lets every crawler in', robots.includes(`Sitemap: ${ORIGIN}/sitemap.xml`) && /User-agent: \*\nAllow: \//.test(robots) && !/Disallow/.test(robots));
const llms = fs.existsSync(path.join(dir, 'llms.txt')) ? read('llms.txt') : '';
const llmsUrls = [...llms.matchAll(/https:\/\/socialstream\.hu\/[^\s)]*/g)].map(m => m[0]);
ok('llms.txt names the pages', llms.startsWith('# SocialStream') && llmsUrls.length >= pages.length, llmsUrls.length);
for (const u of new Set(llmsUrls)) ok('llms.txt link is a page: ' + u, !!heads[u]);
const PULSE = ['p', 'form', 'survey', 'survey-assets', 'book', 'a', 'r', 'embed', 'd', 't', 'c', 'o', 'u', 'm', 'chat', 'api', 'fonts', 'page-assets', 'w', 'ct', 'socialstream'];
ok('no top-level name is one of Pulse\'s own paths', !fs.readdirSync(dir).some(n => PULSE.includes(n.replace(/\.[^.]+$/, ''))));
const man = JSON.parse(read('site.webmanifest'));
for (const i of man.icons) ok('manifest icon in the folder ' + i.src, fs.existsSync(path.join(dir, i.src.replace(/^\//, ''))));
// STATIC=1: the folder and the served files only, without the browser pass (a quick look, e.g. after an upload)
if (process.env.STATIC) { console.log(`${files.length} files fetched, ${pages.length} pages, ${checks} checks (no browser); ${fails ? fails + ' FAILED' : 'all static site checks passed'}`); process.exit(fails ? 1 : 0); }

// in a browser
const b = await chromium.launch({ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', args: ['--autoplay-policy=no-user-gesture-required'] });
const allowed = [new URL(base).host, 'fonts.googleapis.com', 'fonts.gstatic.com'];
for (const [dev, opts] of [['desktop', { viewport: { width: 1440, height: 900 } }], ['phone', { viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true, deviceScaleFactor: 2 }]]) {
  const ctx = await b.newContext(opts);
  for (const pg of pages) {
    const p = await ctx.newPage(), bad = [], errs = [], foreign = new Set();
    p.on('response', r => { if (r.status() >= 400) bad.push(r.status() + ' ' + r.url()); });
    p.on('requestfailed', r => { const t = r.failure()?.errorText || ''; if (!(t.includes('ERR_ABORTED') && /\.mp4/.test(r.url()))) bad.push('failed ' + t + ' ' + r.url()); });
    p.on('request', r => { const h = new URL(r.url()).host; if (h && !allowed.includes(h)) foreign.add(h); });
    p.on('pageerror', e => errs.push(e.message)); p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
    await p.goto(base + pg.path.slice(1), { waitUntil: 'load' }); await p.waitForTimeout(home(pg) ? 2500 : 900);
    // through the page, a screen at a time, measuring any sideways scroll on the way
    const H = await p.evaluate(() => document.documentElement.scrollHeight); let wide = 0;
    for (let y = 0; y < H + 900; y += 700) { await p.evaluate(y => scrollTo(0, y), y); await p.waitForTimeout(110); wide = Math.max(wide, await p.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth)); }
    await p.waitForTimeout(900);
    const st = await p.evaluate(() => ({
      unarrived: [...document.querySelectorAll('[data-r]')].filter(e => !e.classList.contains('in')).length,
      broken: [...document.images].filter(i => i.complete && i.currentSrc && !i.naturalWidth).map(i => i.currentSrc),
      lang: document.documentElement.lang, ssL: window.SS && SS.L,
    }));
    const tag = `${dev} ${pg.path}`;
    ok(tag + ' no 4xx/5xx or failed requests', bad.length === 0, bad.join(' | '));
    ok(tag + ' no console errors', errs.length === 0, errs.join(' | '));
    ok(tag + ' no other hosts', foreign.size === 0, [...foreign].join(', '));
    ok(tag + ' every loaded image decodes', st.broken.length === 0, st.broken.join(', '));
    ok(tag + ' everything arrived', st.unarrived === 0, st.unarrived);
    ok(tag + ' the page and its scripts in its language', st.lang === heads[pg.loc].lang && st.ssL === st.lang, JSON.stringify(st));
    if (dev === 'phone') ok(tag + ' no sideways scroll at 390 px', wide <= 0, String(wide));
    if (home(pg) && pg.path === '/') {
      const head = await p.evaluate(() => ({ title: document.title, canon: document.querySelector('link[rel=canonical]')?.href, og: document.querySelector('meta[property="og:image"]')?.content }));
      ok(dev + ' home title', head.title === 'SocialStream · Interest media ügynökség', head.title);
      ok(dev + ' home canonical', head.canon === ORIGIN + '/');
      // the EN link opens the English page, with the claim in English
      await p.evaluate(() => scrollTo(0, 0)); await p.waitForTimeout(400);
      await Promise.all([p.waitForURL(/\/en\/$/), p.locator('.lang a[hreflang="en"]').click()]); await p.waitForTimeout(800);
      const en = await p.evaluate(() => [...document.querySelectorAll('#hero-h [data-l="en"]')].some(e => e.textContent.includes('Interest has taken its place')) && document.documentElement.lang === 'en');
      ok(dev + ' the EN link opens the English page', en);
    }
    await p.close();
  }
  await ctx.close();
}
function home(pg) { return pg.path === '/' || pg.path === '/en/'; }
// the 404 page
const ctx = await b.newContext({ viewport: { width: 390, height: 700 } }), p = await ctx.newPage(), errs = [];
p.on('pageerror', e => errs.push(e.message)); p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
await p.goto(base + '404.html', { waitUntil: 'load' }); await p.waitForTimeout(400);
const nf = await p.evaluate(() => ({ h1: document.querySelector('h1')?.textContent, logo: document.querySelector('img')?.naturalWidth, wide: document.documentElement.scrollWidth > innerWidth, home: document.querySelector('a.btn')?.getAttribute('href') }));
ok('404 heading', nf.h1 === 'Ez az oldal nem létezik.'); ok('404 logo loads', nf.logo > 0); ok('404 no sideways scroll', !nf.wide); ok('404 links home', nf.home === '/'); ok('404 no console errors', errs.length === 0, errs.join(' | '));
if (process.env.SHOTS) await p.screenshot({ path: path.join(process.env.SHOTS, '404-phone.png') });
await b.close();
console.log(`${files.length} files fetched, ${pages.length} pages, ${checks} checks; ${fails ? fails + ' FAILED' : 'all site checks passed'}`);
// a failure fails the run, as the static pass does (before 2026-11-16 the browser pass always ended with 0)
process.exitCode = fails ? 1 : 0;
