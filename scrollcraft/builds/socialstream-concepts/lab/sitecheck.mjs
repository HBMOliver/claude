// node lab/sitecheck.mjs dist/site http://localhost:4565/   (after tools/site.mjs, with dist/site served as the root)
// The live-site extras for socialstream.hu: every file answers 200, the page's head, no failed or foreign requests,
// English, and the 404 page.
import { createRequire } from 'node:module';
import fs from 'node:fs';
import path from 'node:path';
const { chromium } = createRequire(process.cwd() + '/')('playwright-core');
const [dir, base] = process.argv.slice(2);
let fails = 0; const ok = (what, cond, info = '') => { if (!cond) { fails++; console.log('FAIL', what, info); } };
const files = []; const walk = d => { for (const e of fs.readdirSync(d, { withFileTypes: true })) { const p = path.join(d, e.name); if (e.isDirectory()) walk(p); else files.push(path.relative(dir, p)); } }; walk(dir);
for (const f of files) { const r = await fetch(base + f.split(path.sep).map(encodeURIComponent).join('/')); ok('200 for ' + f, r.status === 200, r.status); await r.arrayBuffer(); }
const html = fs.readFileSync(path.join(dir, 'index.html'), 'utf8');
const ld = html.match(/<script type="application\/ld\+json">([^<]+)<\/script>/);
ok('organisation data parses', ld && JSON.parse(ld[1]).url === 'https://socialstream.hu/');
ok('sitemap names the domain', fs.readFileSync(path.join(dir, 'sitemap.xml'), 'utf8').includes('<loc>https://socialstream.hu/</loc>'));
ok('robots points at the sitemap', fs.readFileSync(path.join(dir, 'robots.txt'), 'utf8').includes('Sitemap: https://socialstream.hu/sitemap.xml'));
const man = JSON.parse(fs.readFileSync(path.join(dir, 'site.webmanifest'), 'utf8'));
for (const i of man.icons) ok('manifest icon in the folder ' + i.src, fs.existsSync(path.join(dir, i.src.replace(/^\//, ''))));
const b = await chromium.launch({ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', args: ['--autoplay-policy=no-user-gesture-required'] });
const allowed = [new URL(base).host, 'fonts.googleapis.com', 'fonts.gstatic.com'];
for (const [dev, opts] of [['desktop', { viewport: { width: 1440, height: 900 } }], ['phone', { viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true, deviceScaleFactor: 2 }]]) {
  const ctx = await b.newContext(opts), p = await ctx.newPage(), bad = [], errs = [], foreign = new Set();
  p.on('response', r => { if (r.status() >= 400) bad.push(r.status() + ' ' + r.url()); });
  p.on('requestfailed', r => { const t = r.failure()?.errorText || ''; if (!(t.includes('ERR_ABORTED') && /\.mp4/.test(r.url()))) bad.push('failed ' + t + ' ' + r.url()); });
  p.on('request', r => { const h = new URL(r.url()).host; if (h && !allowed.includes(h)) foreign.add(h); });
  p.on('pageerror', e => errs.push(e.message)); p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
  await p.goto(base + 'index.html', { waitUntil: 'load' }); await p.waitForTimeout(2500);
  for (let y = 0; y < 30; y++) { await p.mouse.wheel(0, 900); await p.waitForTimeout(120); }
  await p.waitForTimeout(800);
  const head = await p.evaluate(() => ({ title: document.title, lang: document.documentElement.lang, canon: document.querySelector('link[rel=canonical]')?.href, og: document.querySelector('meta[property="og:image"]')?.content, icon: [...document.querySelectorAll('link[rel=icon]')].map(l => l.href) }));
  ok(dev + ' title', head.title === 'SocialStream · Interest media ügynökség', head.title);
  ok(dev + ' lang hu', head.lang === 'hu');
  ok(dev + ' canonical', head.canon === 'https://socialstream.hu/');
  ok(dev + ' share image', head.og === 'https://socialstream.hu/assets/og-image.jpg');
  ok(dev + ' no 4xx/5xx or failed requests', bad.length === 0, bad.join(' | '));
  ok(dev + ' no console errors', errs.length === 0, errs.join(' | '));
  ok(dev + ' no other hosts', foreign.size === 0, [...foreign].join(', '));
  const broken = await p.evaluate(() => [...document.images].filter(i => i.complete && i.currentSrc && !i.naturalWidth).map(i => i.currentSrc));
  ok(dev + ' every loaded image decodes', broken.length === 0, broken.join(', '));
  await p.evaluate(() => scrollTo(0, 0)); await p.waitForTimeout(500);
  await p.locator('[data-set-lang="en"]').first().click(); await p.waitForTimeout(500);
  const en = await p.evaluate(() => [...document.querySelectorAll('#hero-h [data-l="en"]')].some(e => e.offsetParent !== null && e.textContent.includes('Interest has taken its place')));
  ok(dev + ' English shows', en);
  await ctx.close();
}
const ctx = await b.newContext({ viewport: { width: 390, height: 700 } }), p = await ctx.newPage(), errs = [];
p.on('pageerror', e => errs.push(e.message)); p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
await p.goto(base + '404.html', { waitUntil: 'load' }); await p.waitForTimeout(400);
const nf = await p.evaluate(() => ({ h1: document.querySelector('h1')?.textContent, logo: document.querySelector('img')?.naturalWidth, wide: document.documentElement.scrollWidth > innerWidth, home: document.querySelector('a.btn')?.getAttribute('href') }));
ok('404 heading', nf.h1 === 'Ez az oldal nem létezik.'); ok('404 logo loads', nf.logo > 0); ok('404 no sideways scroll', !nf.wide); ok('404 links home', nf.home === '/'); ok('404 no console errors', errs.length === 0, errs.join(' | '));
if (process.env.SHOTS) await p.screenshot({ path: path.join(process.env.SHOTS, '404-phone.png') });
await b.close();
console.log(`${files.length} files fetched; ${fails ? fails + ' FAILED' : 'all site checks passed'}`);
