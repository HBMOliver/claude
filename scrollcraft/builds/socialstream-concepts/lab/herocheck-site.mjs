// herocheck for the multi-page site build: the home page is / in Hungarian and /en/ in English, each its own page, so
// nothing here calls SS.setLang. Checks the right cut per frame and language, the card taking the opening's clock,
// the loop from 3.2 s, the counted figures, and that a language stored by v10 ("ss-lang") does not turn either page
// into the other language. Usage (from a folder with playwright-core): node lab/herocheck-site.mjs <base> [out] [build]
// (out: where its screenshots go, default a new temporary folder; build: the build folder, default this file's)
// Since v18 (2026-11-18): each language plays its own cuts, the ones its page names (site/films.mjs in the build
// folder: Pulse's Media Storage addresses, or /assets/ files until stored), Spanish included.
import { createRequire } from 'node:module';
import path from 'node:path';
import fs from 'node:fs';
import os from 'node:os';
import { pathToFileURL, fileURLToPath } from 'node:url';
const { chromium } = createRequire(process.cwd() + '/')('playwright-core');
const [base, out = fs.mkdtempSync(path.join(os.tmpdir(), 'herocheck-')), build = path.dirname(path.dirname(fileURLToPath(import.meta.url)))] = process.argv.slice(2);
const { filmSrc } = await import(pathToFileURL(path.resolve(build, 'site/films.mjs')).href);
const cutUrl = (l, k) => new URL(filmSrc(l, k), base).href;
const b = await chromium.launch({ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', args: ['--autoplay-policy=no-user-gesture-required'] });
const res = []; const ok = (n, pass, info = '') => res.push(`${pass ? 'ok  ' : 'FAIL'} ${n}${info ? ' (' + info + ')' : ''}`);
const vids = p => p.evaluate(() => [...document.querySelectorAll('#top [data-film] video')].map(v => ({ src: v.currentSrc || '', t: +v.currentTime.toFixed(2), paused: v.paused, dur: +(v.duration || 0).toFixed(2), loop: v.loop })));
const seek = (p, i, t) => p.evaluate(([i, t]) => new Promise(r => { const v = document.querySelectorAll('#top [data-film] video')[i]; v.addEventListener('seeked', () => setTimeout(r, 350), { once: true }); v.currentTime = t; }), [i, t]);
const wait = (p, ms) => p.waitForTimeout(ms);
const errs = [];
const PAGE = { hu: '', en: 'en/', es: 'es/' };
// Hungarian counts four figures; English three, because €0.29 is not a whole number and is not counted
const FIGS = { hu: ['81×ROAS', '79MFt', '23×ROAS', '105Ft'], en: ['81×ROAS', '€216K', '23×ROAS'], es: ['81×ROAS', '216K€', '23×ROAS'] };
const TEXT = { hu: ['105 Ft', '300M+ Ft'], en: ['€0.29', '€820K+'], es: ['0,29 €', '820K+ €'] };
for (const lang of ['hu', 'en', 'es']) {
  const p = await b.newPage({ viewport: { width: 1440, height: 900 } });
  p.on('pageerror', e => errs.push(lang + ' desktop: ' + e.message));
  await p.addInitScript(() => { try { localStorage.clear(); } catch (e) {} });
  await p.goto(base + PAGE[lang] + '?hc=' + Date.now(), { waitUntil: 'load' });
  await wait(p, 4000);
  let v = await vids(p);
  ok(`desktop ${lang}: the opening plays the wide cut`, v[0].src === cutUrl(lang, 'w') && !v[0].paused && v[0].t > 2, JSON.stringify(v[0]));
  ok(`desktop ${lang}: the film is 59.4 s and loops by script`, v[0].dur === 59.4 && v[0].loop === false, `${v[0].dur} s, loop ${v[0].loop}`);
  const st = await p.evaluate(() => { const s = document.querySelector('#top'); return { top: s.getBoundingClientRect().top + scrollY, span: s.offsetHeight - innerHeight }; });
  for (const q of [0.3, 0.5, 0.56, 0.62, 1.0]) {
    await p.evaluate(y => scrollTo({ top: y, behavior: 'instant' }), st.top + q * st.span); await wait(p, 900);
    if (q === 1.0) await p.screenshot({ path: `${out}/desk-${lang}-q1.0.jpg`, quality: 75 });
  }
  await wait(p, 1500);
  v = await vids(p);
  ok(`desktop ${lang}: the card plays the upright cut`, v[1].src === cutUrl(lang, 'v') && !v[1].paused, JSON.stringify(v[1]));
  ok(`desktop ${lang}: the card took the opening's clock`, v[1].t > 4, `card ${v[1].t} s, opening ${v[0].t} s (paused ${v[0].paused})`);
  await seek(p, 1, 58.6); await wait(p, 1600);
  v = await vids(p);
  ok(`desktop ${lang}: after the end the card loops from 3.2 s`, v[1].t >= 3.2 && v[1].t < 5.2 && !v[1].paused, JSON.stringify(v[1]));
  const figs = await p.evaluate(async () => {
    const got = [];
    for (const e of document.querySelectorAll('[data-count]')) {
      e.scrollIntoView({ block: 'center', behavior: 'instant' });
      await new Promise(r => setTimeout(r, 2600));
      got.push((e.closest('.n') || e).innerText.replace(/\s+/g, ''));
    }
    return got;
  });
  ok(`desktop ${lang}: the counters reach their figures`, JSON.stringify(figs) === JSON.stringify(FIGS[lang]), JSON.stringify(figs));
  const body = await p.evaluate(() => document.body.innerText);
  ok(`desktop ${lang}: the page shows ${TEXT[lang].join(' and ')}`, TEXT[lang].every(t => body.includes(t)));
  ok(`desktop ${lang}: no figure in the other currency`, lang !== 'hu' ? !/\d\s?(M\s)?Ft\b/.test(body) : !/€/.test(body), lang !== 'hu' ? (body.match(/.{20}\d\s?(M\s)?Ft\b.{0,20}/) || [''])[0] : (body.match(/.{20}€.{20}/) || [''])[0]);
  await p.close();
}
for (const lang of ['hu', 'en', 'es']) {
  const p = await b.newPage({ viewport: { width: 390, height: 664 }, deviceScaleFactor: 1, isMobile: true, hasTouch: true });
  p.on('pageerror', e => errs.push(lang + ' phone: ' + e.message));
  await p.addInitScript(() => { try { localStorage.clear(); } catch (e) {} });
  await p.goto(base + PAGE[lang] + '?hc=' + Date.now(), { waitUntil: 'load' });
  await wait(p, 4000);
  const v = await vids(p);
  ok(`phone ${lang}: the opening plays the upright cut`, v[0].src === cutUrl(lang, 'v') && !v[0].paused, JSON.stringify(v[0]));
  await p.close();
}
for (const [lang, stale] of [['hu', 'en'], ['en', 'hu'], ['es', 'en'], ['es', 'hu']]) {
  const seen = {};
  for (const stored of [null, stale]) {
    const p = await b.newPage({ viewport: { width: 1440, height: 900 } });
    p.on('pageerror', e => errs.push(lang + ' stale ' + stored + ': ' + e.message));
    await p.addInitScript(s => { try { localStorage.clear(); if (s) localStorage.setItem('ss-lang', s); } catch (e) {} }, stored);
    await p.goto(base + PAGE[lang] + '?hc=' + Date.now(), { waitUntil: 'load' });
    await wait(p, 3000);
    seen[stored || 'clean'] = await p.evaluate(() => ({
      lang: document.documentElement.lang,
      shown: [...document.querySelectorAll('[data-l]')].filter(e => e.getClientRects().length > 0).map(e => e.getAttribute('data-l')).join(''),
      h1: (document.querySelector('h1') || {}).innerText?.replace(/\s+/g, ' ').slice(0, 60),
      film: ((document.querySelector('#top [data-film] video') || {}).currentSrc || '').split('/').pop(),
    }));
    await p.close();
  }
  const a = seen.clean, s = seen[stale];
  ok(`${PAGE[lang] || '/'} stays ${lang} with a stored "${stale}" from v10`, s.lang === lang && s.shown === a.shown && s.h1 === a.h1 && s.film === a.film, JSON.stringify(s));
}
ok('no script errors', errs.length === 0, errs.join(' / '));
await b.close();
console.log(res.join('\n')); if (res.some(r => r.startsWith('FAIL'))) process.exitCode = 1;
