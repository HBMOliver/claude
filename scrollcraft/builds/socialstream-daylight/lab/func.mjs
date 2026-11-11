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
  ok('"not for you" said once', (await p.evaluate(() => (document.body.textContent.match(/Nem neked való/g) || []).length)) === 1);
  const qs = await p.evaluate(() => [...document.querySelectorAll('#kerdesek summary')].map(s => s.textContent.trim()));
  ok('questions: what happens after sending', qs.length === 8 && qs[2] === 'Mi történik, miután elküldöm?', qs.join('|'));
  ok('footer: copy button says what it copies', (await p.evaluate(() => document.getElementById('copyMail2').textContent)) === 'Cím másolása');
  await mid(p, '#appform', 0.5);
  const fm = await p.evaluate(() => { const b = document.querySelector('#appform button[type=submit]'); return { btn: b.textContent.trim(), desc: b.getAttribute('aria-describedby'), hint: document.getElementById('f-hint').textContent, opt: [...document.querySelectorAll('#appform .opt')].map(o => o.textContent), ph: document.getElementById('f-msg').placeholder, budget: [...document.querySelectorAll('#f-budget option')].map(o => o.textContent).join('|') }; });
  ok('form: the button and the line under it say the mail app opens', fm.btn === 'Jelentkezem e-mailben' && fm.desc === 'f-hint' && /^A gomb megnyitja a leveleződ/.test(fm.hint), JSON.stringify(fm));
  ok('form: five fields marked optional, an example in the message box', fm.opt.length === 5 && fm.opt.every(t => t === '(nem kötelező)') && /^Pl\. webshopunk/.test(fm.ph), JSON.stringify(fm));
  ok('form: budget ranges in words', fm.budget === 'Válassz sávot|300 ezer Ft alatt|300 ezer – 1 millió Ft|1–3 millió Ft|3 millió Ft felett', fm.budget);
  await p.locator('#appform button[type=submit]').click(); await p.waitForTimeout(300);
  const e0 = await p.evaluate(() => ['name', 'email', 'brand'].map(n => document.getElementById('e-' + n).textContent));
  ok('form: each empty field says what to enter', e0.join('|') === 'Írd be a neved, hogy tudjuk, kinek válaszolunk.|Írd be az e-mail címed, ide válaszolunk.|Írd be a céged vagy a márkád nevét.', e0.join('|'));
  await p.fill('#f-email', 'teszt@'); await p.locator('#appform button[type=submit]').click(); await p.waitForTimeout(250);
  ok('form: a wrong address gets an example', (await p.evaluate(() => document.getElementById('e-email').textContent)) === 'Ez nem tűnik e-mail címnek. Például: nev@ceg.hu');
  await p.evaluate(() => { SS.send = (brand, body) => { window.__sent = { brand, body }; }; });
  await p.fill('#f-name', 'Teszt Elek'); await p.fill('#f-email', 'teszt@example.com'); await p.fill('#f-brand', 'Teszt Kft.');
  await p.selectOption('#f-budget', { index: 2 }); await p.selectOption('#f-goal', { index: 1 });
  await p.locator('#pick label').nth(2).click(); await p.locator('#appform button[type=submit]').click(); await p.waitForTimeout(300);
  const mid1 = await p.evaluate(() => ({ sending: !document.getElementById('sending').hidden, t: document.getElementById('stext').textContent }));
  ok('form: while it works, it says the mail app is opening', mid1.sending && mid1.t === 'Megnyitjuk a leveleződ…', JSON.stringify(mid1));
  await p.waitForTimeout(1100);
  const sent = await p.evaluate(() => ({ shown: !document.getElementById('sent').hidden, brand: window.__sent && window.__sent.brand, body: window.__sent ? window.__sent.body : '' }));
  ok('form: the email is composed', sent.shown && sent.brand === 'Teszt Kft.' && /Havi büdzsé: 300 ezer – 1 millió Ft/.test(sent.body) && /Ami érdekel: \S/.test(sent.body), JSON.stringify(sent).slice(0, 300));
  const after = await p.evaluate(() => ({ sending: document.getElementById('sending').hidden, b: document.querySelector('#sent b').textContent, s: document.querySelector('#sent span').textContent, pct: /100%/.test(document.getElementById('appform').textContent) }));
  ok('form: after sending, what is left and what comes next', after.sending && !after.pct && after.b === 'Az e-mailed kész, már csak el kell küldened.' && /hello@socialstream\.hu címre\. Amint megkaptuk, válaszolunk/.test(after.s), JSON.stringify(after).slice(0, 300));
  await p.locator('[data-set-lang="en"]').click(); await p.waitForTimeout(500);
  const en = await p.evaluate(() => ({ lang: document.documentElement.lang, nav: document.querySelector('.nav .links a').textContent.trim(), hu: [...document.querySelectorAll('[data-l="hu"]')].filter(e => e.offsetParent !== null).length, h1: document.querySelector('#hero-h [data-l="en"]').textContent.replace(/\s+/g, ' ').trim() }));
  ok('English everywhere', en.lang === 'en' && en.nav === 'Results' && en.hu === 0 && /^Videos people watch to the end\. Ads that pay off\.$/.test(en.h1), JSON.stringify(en));
  const enf = await p.evaluate(() => ({ btn: document.querySelector('#appform button[type=submit]').textContent.trim(), hint: document.getElementById('f-hint').textContent, opt: [...document.querySelectorAll('#appform .opt')].every(o => o.textContent === '(optional)'), ph: document.getElementById('f-msg').placeholder, b: document.querySelector('#sent b').textContent, foot: document.getElementById('copyMail2').textContent }));
  ok('English form copy', enf.btn === 'Apply by email' && /^This opens your mail app/.test(enf.hint) && enf.opt && /^E\.g\. /.test(enf.ph) && enf.b === 'Your email is ready. Just press send.' && enf.foot === 'Copy address', JSON.stringify(enf));
  await p.fill('#f-name', ''); await p.locator('#appform button[type=submit]').click(); await p.waitForTimeout(250);
  const enErr = await p.evaluate(() => document.getElementById('e-name').textContent);
  await p.locator('[data-set-lang="hu"]').click(); await p.waitForTimeout(400);
  const huErr = await p.evaluate(() => document.getElementById('e-name').textContent);
  ok('errors follow the language', enErr === 'Enter your name so we know who to reply to.' && huErr === 'Írd be a neved, hogy tudjuk, kinek válaszolunk.', enErr + ' | ' + huErr);
  await p.locator('[data-set-lang="en"]').click(); await p.waitForTimeout(300);
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
