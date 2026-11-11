// node lab/func.mjs   (run from a folder with playwright-core; the build served on :4553, or URL=...)
// What the page does, checked without looking: the film, the counters, the steps, the wall, the team
// photos, the form, English, the questions; then reduced motion and a phone. One line per failed
// check, then a summary line.
import { createRequire } from 'node:module';
const { chromium } = createRequire(process.cwd() + '/')('playwright-core');
const URL = process.env.URL || 'http://localhost:4553/';
const b = await chromium.launch({ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', args: ['--autoplay-policy=no-user-gesture-required'] });
let pass = 0, fail = 0;
const ok = (name, cond, info = '') => { if (cond) pass++; else { fail++; console.log('FAIL', name, info); } };
async function open(opts) {
  const ctx = await b.newContext(opts); const p = await ctx.newPage(); const errs = [];
  p.on('pageerror', e => errs.push('pageerror: ' + e.message)); p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
  await p.goto(URL, { waitUntil: 'load' }); await p.waitForTimeout(1600);
  return { p, errs };
}
const y = (p, top, wait = 700) => p.evaluate(top => scrollTo({ top, behavior: 'instant' }), top).then(() => p.waitForTimeout(wait));
const mid = async (p, sel, at = 0.5, wait = 800) => { await p.evaluate(([sel, at]) => { const r = document.querySelector(sel).getBoundingClientRect(); scrollTo({ top: r.top + scrollY + r.height * at - innerHeight / 2, behavior: 'instant' }); }, [sel, at]); await p.waitForTimeout(wait); };
const nums = (p, sel) => p.evaluate(sel => [...document.querySelectorAll(sel)].map(e => e.textContent.replace(/[\s  ]+/g, ' ').trim()), sel);
const film = p => p.evaluate(() => { const f = document.getElementById('film'), v = f.querySelector('video'); return { src: (v.currentSrc || v.src).split('/').pop(), paused: v.paused, cls: f.className }; });

// 1. desktop
{
  const { p, errs } = await open({ viewport: { width: 1440, height: 900 } });
  ok('script ran', await p.evaluate(() => document.documentElement.classList.contains('js')));
  await p.waitForTimeout(1500);
  let f = await film(p);
  ok('film: a desktop cut plays', /^hero-(1080|540)\.mp4$/.test(f.src) && !f.paused, JSON.stringify(f));
  await p.locator('#film .toggle').click(); await p.waitForTimeout(300); f = await film(p);
  ok('film: the button pauses it', f.paused && /is-paused/.test(f.cls), JSON.stringify(f));
  await p.locator('#film .toggle').click(); await p.waitForTimeout(600); f = await film(p);
  ok('film: and plays it again', !f.paused, JSON.stringify(f));
  await mid(p, '.count', 0.5, 2600);
  ok('count: 300 000 000', (await nums(p, '.count [data-count]'))[0] === '300 000 000', (await nums(p, '.count [data-count]')).join('|'));
  await mid(p, '#eredmenyek', 0.5, 2600);
  ok('results: 81 / 79 / 23 / 105', (await nums(p, '#eredmenyek [data-count]')).join('/') === '81/79/23/105', (await nums(p, '#eredmenyek [data-count]')).join('/'));
  // the steps light over the scroll that carries the list from three quarters down the screen; stop 30% of the way
  await p.evaluate(() => { const s = document.getElementById('steps').getBoundingClientRect(); scrollTo({ top: s.top + scrollY - (innerHeight * 0.75 - s.height * 0.6 * 0.3), behavior: 'instant' }); }); await p.waitForTimeout(600);
  const early = await p.evaluate(() => document.querySelectorAll('#steps .is-on').length);
  await mid(p, '#steps', 1.0, 600); const late = await p.evaluate(() => document.querySelectorAll('#steps .is-on').length);
  ok('steps light one by one', early < 4 && late === 4, early + ' then ' + late);
  ok('six voices on the wall, quoted', (await p.evaluate(() => [...document.querySelectorAll('#wall > li')].filter(li => /„/.test(li.textContent)).length)) === 6);
  await mid(p, '#csapat', 0.5, 900);
  const team = await p.evaluate(() => [...document.querySelectorAll('.person img')].map(i => { const r = i.getBoundingClientRect(); return [Math.round(r.width), Math.round(r.height), i.naturalWidth]; }));
  ok('team: three square photos', team.length === 3 && team.every(([w, h, n]) => Math.abs(w - h) <= 2 && n > 0), JSON.stringify(team));
  await y(p, 1e7, 1200);
  ok('every picture loaded', (await p.evaluate(() => [...document.images].filter(i => i.currentSrc && i.complete && !i.naturalWidth).length)) === 0);
  await p.locator('#kerdesek summary').first().click(); await p.waitForTimeout(250);
  ok('a question opens', await p.evaluate(() => document.querySelector('#kerdesek details').open));
  await mid(p, '#appform', 0.5); await p.locator('#appform button[type=submit]').click(); await p.waitForTimeout(300);
  ok('form: an empty name is refused', (await p.evaluate(() => document.getElementById('e-name').textContent)) === 'Ezt kérjük kitölteni.');
  await p.evaluate(() => { SS.send = (brand, body) => { window.__sent = { brand, body }; }; });
  await p.fill('#f-name', 'Teszt Elek'); await p.fill('#f-email', 'teszt@example.com'); await p.fill('#f-brand', 'Teszt Kft.');
  await p.selectOption('#f-budget', { index: 2 }); await p.selectOption('#f-goal', { index: 1 });
  await p.locator('#pick label').nth(2).click(); await p.locator('#appform button[type=submit]').click(); await p.waitForTimeout(1400);
  const sent = await p.evaluate(() => ({ shown: !document.getElementById('sent').hidden, brand: window.__sent && window.__sent.brand, body: window.__sent ? window.__sent.body : '' }));
  ok('form: the email is composed', sent.shown && sent.brand === 'Teszt Kft.' && /Havi büdzsé: \S/.test(sent.body) && /Ami érdekel: \S/.test(sent.body), JSON.stringify(sent).slice(0, 300));
  await p.locator('[data-set-lang="en"]').click(); await p.waitForTimeout(500);
  const en = await p.evaluate(() => ({ lang: document.documentElement.lang, nav: document.querySelector('.nav .links a').textContent.trim(), hu: [...document.querySelectorAll('[data-l="hu"]')].filter(e => e.offsetParent !== null).length, h1: document.querySelector('#hero-h [data-l="en"]').textContent.replace(/\s+/g, ' ').trim() }));
  ok('English everywhere', en.lang === 'en' && en.nav === 'Results' && en.hu === 0 && /^Videos people watch to the end\. Ads that pay off\.$/.test(en.h1), JSON.stringify(en));
  ok('no errors on desktop', errs.length === 0, errs.slice(0, 2).join(' | '));
  await p.context().close();
}
// 2. reduced motion: everything readable where it stands, the film waits for the visitor
{
  const { p, errs } = await open({ viewport: { width: 1440, height: 900 }, reducedMotion: 'reduce' });
  const r = await p.evaluate(() => ({ count: document.querySelector('.count [data-count]').textContent.replace(/[\s  ]+/g, ' '), late: getComputedStyle(document.querySelector('#kerdesek [data-r]')).opacity, paused: document.querySelector('#film video').paused }));
  ok('reduced motion: numbers and text in place, film paused', r.count === '300 000 000' && r.late === '1' && r.paused, JSON.stringify(r));
  ok('no errors with reduced motion', errs.length === 0, errs.slice(0, 2).join(' | '));
  await p.context().close();
}
// 3. phone
{
  const { p, errs } = await open({ viewport: { width: 393, height: 852 }, isMobile: true, hasTouch: true, deviceScaleFactor: 2 });
  await p.waitForTimeout(1500);
  let f = await film(p);
  ok('phone: the vertical cut', f.src === 'hero-v-720.mp4', JSON.stringify(f));
  await p.locator('#film .toggle').tap(); await p.waitForTimeout(300); f = await film(p);
  ok('phone: tap pauses', f.paused, JSON.stringify(f));
  const fit = await p.evaluate(() => ({ page: document.documentElement.scrollWidth - innerWidth, nav: document.getElementById('nav').scrollWidth - document.getElementById('nav').clientWidth }));
  ok('phone: nothing wider than the screen', fit.page <= 0 && fit.nav <= 0, JSON.stringify(fit));
  await mid(p, '#csapat', 0.5, 900);
  ok('phone: team photos show', (await p.evaluate(() => [...document.querySelectorAll('.person img')].every(i => i.getBoundingClientRect().height >= 140 && i.naturalWidth > 0))));
  ok('no errors on the phone', errs.length === 0, errs.slice(0, 2).join(' | '));
  await p.context().close();
}
console.log(`daylight: ${pass} passed, ${fail} failed`);
await b.close();
