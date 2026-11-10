// node lab/func.mjs <outdir>   (run from a folder with playwright-core)
// What the page does, checked without looking: the scroll states of every scene, the English
// switch, the services list, the audit form, reduced motion, and the page with no WebGL at all.
import { createRequire } from 'node:module';
import fs from 'node:fs';
const { chromium } = createRequire(process.cwd() + '/')('playwright-core');
const out = process.argv[2]; fs.mkdirSync(out, { recursive: true });
const URL = process.env.URL || 'http://localhost:4550/';
const b = await chromium.launch({ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', args: ['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist'] });
const res = {};
async function open(opts, init) {
  const ctx = await b.newContext(opts); const p = await ctx.newPage(); const errs = [];
  p.on('pageerror', e => errs.push('pageerror: ' + e.message)); p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
  if (init) await p.addInitScript(init);
  await p.goto(URL, { waitUntil: 'load' }); await p.waitForTimeout(1800);
  return { p, errs, ctx };
}
const to = async (p, sel, at = 0.5, wait = 900) => { await p.evaluate(([sel, at]) => { const r = document.querySelector(sel).getBoundingClientRect(); scrollTo({ top: r.top + scrollY + r.height * at - innerHeight / 2, behavior: 'instant' }); }, [sel, at]); await p.waitForTimeout(wait); };
const txt = (p, sel) => p.evaluate(sel => document.querySelector(sel).textContent.trim(), sel);

// 1. desktop: the states of every scene
{
  const { p, errs } = await open({ viewport: { width: 1440, height: 900 } });
  res.film = await p.evaluate(() => { const v = document.querySelector('#reel video'); return { src: v.currentSrc.split('/').pop(), paused: v.paused, tiled: document.getElementById('reel').classList.contains('is-tiled'), bar: document.querySelector('.bar').dataset.on }; });
  await p.evaluate(() => scrollTo({ top: innerHeight * 0.4, behavior: 'instant' })); await p.waitForTimeout(700);
  res.tiled = await p.evaluate(() => document.getElementById('reel').classList.contains('is-tiled'));
  await to(p, '.law1', 0.3); res.count = await txt(p, '#cnt');
  await to(p, '.law1', 0.95, 1300); res.law1 = await p.evaluate(() => ({ count: document.getElementById('cnt').textContent, likes: document.getElementById('likes').textContent, cls: document.querySelector('.law1').className.replace(/sec |f-dark |sc-\S+ ?/g, '') }));
  await to(p, '.law2', 0.62, 1200); res.watch = await txt(p, '#wpct');
  await to(p, '.law3', 0.72, 1300); res.rules = await p.evaluate(() => [...document.querySelectorAll('.law3 .rules li')].map(li => li.className || '-').join(' '));
  await to(p, '#fig-r81', 0.5, 1300); res.r81 = await p.evaluate(() => ({ n: document.querySelector('[data-r="r81"] .v').textContent, on: document.querySelector('[data-r="r81"]').classList.contains('is-on') }));
  await to(p, '#fig-r5700', 0.5, 1300); res.r5700 = await txt(p, '[data-r="r5700"] .v');
  await to(p, '.services', 0.4); const row = p.locator('#svcList li').nth(3); await row.hover(); await p.waitForTimeout(300);
  res.svcHover = await p.evaluate(() => ({ row: [...document.querySelectorAll('#svcList li')].findIndex(li => li.classList.contains('is-on')), drawing: [...document.querySelectorAll('#viewer .dv')].findIndex(d => d.classList.contains('is-on')) }));
  await p.evaluate(() => scrollTo({ top: document.documentElement.scrollHeight, behavior: 'instant' })); await p.waitForTimeout(1500);
  res.end = await p.evaluate(() => ({ bar: document.querySelector('.bar').dataset.on, theme: document.querySelector('meta[name="theme-color"]').content }));
  await p.screenshot({ path: `${out}/end.jpg`, type: 'jpeg', quality: 70 });
  // the form
  await to(p, '#appform', 0.5); await p.locator('#appform button[type=submit]').click(); await p.waitForTimeout(300);
  res.formErr = await txt(p, '#e-name');
  await p.evaluate(() => { SS.send = (brand, body) => { window.__sent = { brand, body }; }; });
  await p.fill('#f-name', 'Teszt Elek'); await p.fill('#f-email', 'teszt@example.com'); await p.fill('#f-brand', 'Teszt Kft.'); await p.selectOption('#f-budget', '1-3m');
  await p.locator('#chips label').nth(2).click(); await p.locator('#appform button[type=submit]').click(); await p.waitForTimeout(1300);
  res.sent = await p.evaluate(() => ({ shown: !document.getElementById('sent').hidden, brand: window.__sent && window.__sent.brand, lines: window.__sent && window.__sent.body.split('\n').slice(0, 7) }));
  // English
  await p.locator('[data-set-lang="en"]').click(); await p.waitForTimeout(500);
  res.en = { h1: (await txt(p, '.m2')).replace(/\s+/g, ' ').slice(-40), nav: await txt(p, '.bar .links a'), svc: await txt(p, '#svcList h3'), lang: await p.evaluate(() => document.documentElement.lang) };
  res.enVisible = await p.evaluate(() => [...document.querySelectorAll('[data-l="hu"]')].filter(e => e.offsetParent !== null).length);
  await to(p, '.law2', 0.5, 1200); await p.screenshot({ path: `${out}/en-law2.jpg`, type: 'jpeg', quality: 70 });
  res.errs = errs; await p.context().close();
}
// 2. reduced motion
{
  const { p, errs } = await open({ viewport: { width: 1440, height: 900 }, reducedMotion: 'reduce' });
  await to(p, '.manifesto', 0.5); await p.screenshot({ path: `${out}/reduced-claim.jpg`, type: 'jpeg', quality: 70 });
  await to(p, '.law1', 0.95, 1000); await p.screenshot({ path: `${out}/reduced-law1.jpg`, type: 'jpeg', quality: 70 });
  res.reduced = { count: await txt(p, '#cnt'), lit: await p.evaluate(() => document.querySelectorAll('.lit .w:not(.on)').length), errs };
  await p.context().close();
}
// 3. no WebGL: the page is still whole
{
  const { p, errs } = await open({ viewport: { width: 1440, height: 900 } }, () => { const g = HTMLCanvasElement.prototype.getContext; HTMLCanvasElement.prototype.getContext = function (t) { return /webgl/.test(t) ? null : g.apply(this, arguments); }; });
  await to(p, '.law1', 0.95, 1000);
  res.noGL = { cls: await p.evaluate(() => document.documentElement.classList.contains('no-stream')), count: await txt(p, '#cnt'), figs: await p.evaluate(() => [...document.querySelectorAll('.figure')].filter(f => f.offsetParent !== null).map(f => f.id).join(',')), errs };
  await p.evaluate(() => scrollTo({ top: document.documentElement.scrollHeight, behavior: 'instant' })); await p.waitForTimeout(800);
  await p.screenshot({ path: `${out}/nogl-end.jpg`, type: 'jpeg', quality: 70 });
  await p.context().close();
}
// 4. a phone
{
  const { p, errs } = await open({ viewport: { width: 393, height: 700 }, isMobile: true, hasTouch: true, deviceScaleFactor: 2 });
  res.phone = await p.evaluate(() => ({ src: document.querySelector('#reel video').currentSrc.split('/').pop(), vertical: document.getElementById('reel').classList.contains('is-vertical') }));
  await p.tap('#reel', { position: { x: 196, y: 300 } }); await p.waitForTimeout(300);
  res.phone.tapPaused = await p.evaluate(() => document.querySelector('#reel video').paused);
  await p.tap('#reel', { position: { x: 196, y: 300 } });
  res.phone.overflow = await p.evaluate(() => document.documentElement.scrollWidth - innerWidth); res.phone.errs = errs;
  await p.context().close();
}
console.log(JSON.stringify(res, null, 1));
await b.close();
