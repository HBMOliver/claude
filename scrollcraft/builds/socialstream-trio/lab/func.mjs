// node lab/func.mjs [orbit|screen|bento ...]   (run from a folder with playwright-core; the build served on :4552)
// What each template does, checked without looking: its own scroll states, then what all three
// share (services, results, voices, the form, English), reduced motion, and a phone (the film's
// vertical cut, tap to pause, nothing wider than the screen). Prints one line per check that fails
// and a summary line per template.
import { createRequire } from 'node:module';
const { chromium } = createRequire(process.cwd() + '/')('playwright-core');
const BASE = process.env.URL || 'http://localhost:4552/';
const which = process.argv.slice(2).length ? process.argv.slice(2) : ['orbit', 'screen', 'bento'];
const b = await chromium.launch({ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' });
async function open(t, opts) {
  const ctx = await b.newContext(opts); const p = await ctx.newPage(); const errs = [];
  p.on('pageerror', e => errs.push('pageerror: ' + e.message)); p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
  await p.goto(BASE + t + '.html', { waitUntil: 'load' }); await p.waitForTimeout(1600);
  return { p, errs };
}
const y = (p, top, wait = 700) => p.evaluate(top => scrollTo({ top, behavior: 'instant' }), top).then(() => p.waitForTimeout(wait));
// scroll so that a point `at` of the way down an element is in the middle of the screen
const mid = async (p, sel, at = 0.5, wait = 800) => { await p.evaluate(([sel, at]) => { const r = document.querySelector(sel).getBoundingClientRect(); scrollTo({ top: r.top + scrollY + r.height * at - innerHeight / 2, behavior: 'instant' }); }, [sel, at]); await p.waitForTimeout(wait); };
// scroll a held section (one taller than the screen with a sticky stage) to progress k
const held = async (p, sel, k, wait = 900) => { await p.evaluate(([sel, k]) => { const r = document.querySelector(sel).getBoundingClientRect(); scrollTo({ top: r.top + scrollY + (r.height - innerHeight) * k, behavior: 'instant' }); }, [sel, k]); await p.waitForTimeout(wait); };
const has = (p, sel, cls) => p.evaluate(([sel, cls]) => document.querySelector(sel).classList.contains(cls), [sel, cls]);
const txt = (p, sel) => p.evaluate(sel => document.querySelector(sel).textContent.replace(/ /g, ' ').trim(), sel);

const OWN = {
  async orbit(p, ok) {
    await held(p, '.claim', 0.2); ok('claim: first sentence, old feed', !(await has(p, '.claim', 'is-b')) && !(await has(p, '#shot', 'is-fy')));
    await held(p, '.claim', 0.97); ok('claim: second sentence, new feed, notes', (await has(p, '.claim', 'is-b')) && (await has(p, '#shot', 'is-fy')) && (await has(p, '.claim', 'is-notes')));
    await held(p, '.law1', 0.2); const mid1 = await txt(p, '#cnt'); ok('law I: the count is running', mid1 !== '0' && mid1 !== '10 000', mid1);
    await held(p, '.law1', 0.97); ok('law I: 10 000, 40, the law', (await txt(p, '#cnt')) === '10 000' && (await txt(p, '#likes')) === '40' && (await has(p, '.law1', 'is-law')));
    await mid(p, '#ring', 0.5); ok('law II: the ring is full when centred', (await txt(p, '#ring .pct b')) === '100%', await txt(p, '#ring .pct b'));
    await mid(p, '#rulesFig', 0.5); ok('law III: two struck, three in', (await p.evaluate(() => document.querySelectorAll('#rules .is-x').length + '/' + document.querySelectorAll('#rules .is-in').length)) === '2/3');
    await mid(p, '#fan', 0.5); ok('the fan is open', (await p.evaluate(() => document.getElementById('fan').style.getPropertyValue('--k'))) === '1.000');
    await mid(p, '#quotes', 0.5); await p.locator('.qnav .next').click(); await p.waitForTimeout(300); ok('voices: next', (await txt(p, '#qn')) === '2 / 6' && (await p.evaluate(() => document.querySelectorAll('#quotes li.is-on').length)) === 1);
  },
  async screen(p, ok) {
    const map = [0, 0, 0, 1, 2, 3];
    for (let i = 0; i < 6; i++) {
      // the caption a little past the middle of the screen, so its own animation has run
      await p.evaluate(i => { const r = document.querySelectorAll('.cap')[i].getBoundingClientRect(); scrollTo({ top: r.top + scrollY - innerHeight / 2 + r.height * 0.8, behavior: 'instant' }); }, i); await p.waitForTimeout(900);
      const s = await p.evaluate(() => ({ ch: +document.getElementById('story').dataset.ch, on: [...document.querySelectorAll('.s')].findIndex(e => e.classList.contains('is-on')), fy: document.getElementById('pwrap').classList.contains('is-fy'), tag: document.querySelectorAll('.tag.is-on').length }));
      ok('chapter ' + i + ' shows screen ' + map[i], s.ch === i && s.on === map[i] && s.fy === (i > 0), JSON.stringify(s));
      if (i === 3) ok('law I in the phone: 10 000 and 40', (await txt(p, '#pcnt')) === '10 000' && (await txt(p, '#plikes')) === '40' && (await has(p, '#sprof', 'is-like')));
      if (i === 4) ok('law II in the phone: watched to the end', (await txt(p, '#wpct')) === '100%');
      if (i === 5) ok('law III in the phone: two struck, three in', (await p.evaluate(() => document.querySelectorAll('#rules .is-x').length + '/' + document.querySelectorAll('#rules .is-in').length)) === '2/3');
    }
  },
  async bento(p, ok) {
    await held(p, '#board', 0.02); const a = await p.evaluate(() => ({ k: +document.querySelector('.b-claim').style.getPropertyValue('--k'), m1: +document.getElementById('board').style.getPropertyValue('--m1') }));
    ok('board: the first sentence alone', a.k < 0.05 && a.m1 === 1, JSON.stringify(a));
    await held(p, '#board', 0.95); const z = await p.evaluate(() => ({ ks: [...document.querySelectorAll('#board .tile')].map(t => +t.style.getPropertyValue('--k')), m1: +document.getElementById('board').style.getPropertyValue('--m1'), set: document.getElementById('board').classList.contains('is-set'), fits: document.getElementById('bento').getBoundingClientRect().bottom <= innerHeight + 1 }));
    ok('board: every tile in place, on one screen', z.ks.every(k => k === 1) && z.m1 === 0 && z.set && z.fits, JSON.stringify(z));
    // each law card after it has held its place for a while
    const dwell = (i, k) => p.evaluate(([i, k]) => { const c = document.querySelectorAll('.scard')[i], m = document.querySelectorAll('.mk')[i]; scrollTo({ top: m.getBoundingClientRect().top + scrollY - parseFloat(getComputedStyle(c).top) + innerHeight * k, behavior: 'instant' }); }, [i, k]).then(() => p.waitForTimeout(900));
    await dwell(0, 0.45); ok('law I: 10 000 cells, 40 lit', (await txt(p, '#cnt')) === '10 000' && (await txt(p, '#likes')) === '40' && (await has(p, '#gridfig', 'is-lit')));
    await dwell(1, 0.45); ok('law II: the ring is full', (await txt(p, '#ring .pct b')) === '100%', await txt(p, '#ring .pct b'));
    ok('law II lies on law I', (await p.evaluate(() => +document.querySelectorAll('.scard')[0].style.getPropertyValue('--t'))) > 0.9);
    await dwell(2, 0.02); ok('law III: two struck, three in', (await p.evaluate(() => document.querySelectorAll('#rules .is-x').length + '/' + document.querySelectorAll('#rules .is-in').length)) === '2/3');
    // the services are a board of photographs: walk past it so every one has loaded
    for (const k of [0.15, 0.5, 0.85]) await mid(p, '#svc', k, 600);
    ok('services: six photographs, all loaded', (await p.evaluate(() => [...document.querySelectorAll('#svc .ph img')].filter(i => i.complete && i.naturalWidth > 0).length)) === 6);
  }
};

for (const t of which) {
  const fails = []; let n = 0;
  const ok = (name, pass, got) => { n++; if (!pass) { fails.push(name); console.log('  FAIL ' + t + ': ' + name + (got ? ' (' + got + ')' : '')); } };
  // 1. desktop
  {
    const { p, errs } = await open(t, { viewport: { width: 1440, height: 900 } });
    const film = await p.evaluate(() => { const v = document.querySelector('#reel video'); return { src: v.currentSrc.split('/').pop(), paused: v.paused, bar: document.querySelector('.bar').dataset.on }; });
    ok('film plays, bar clear over it', film.src === 'hero-1080.mp4' && !film.paused && film.bar === 'film', JSON.stringify(film));
    await OWN[t](p, ok);
    ok('six services, each with its scene', (await p.evaluate(() => document.querySelectorAll('#svc > li').length + '/' + document.querySelectorAll('.dv').length)) === '6/6');
    // each template its own picture of a service, and its own ground: circles and the old cream belong to none but orbit
    const look = await p.evaluate(() => ({ orbit: document.querySelectorAll('#svc .gv img').length, screen: document.querySelectorAll('#viewer .ap-iso .iso img').length, bento: document.querySelectorAll('#svc .ph img').length,
      shapes: document.querySelectorAll('.rings, .glowb, .sphere, .torus, .pill').length, cream: document.querySelectorAll('.f-cream, [data-field="cream"]').length, mock: document.querySelectorAll('.ap-video, .ap-ads, .ap-web').length }));
    ok('its own service pictures', look[t] === 6 && look.mock === 0, JSON.stringify(look));
    ok('no cream; shapes only in orbit', look.cream === 0 && (t === 'orbit' ? look.shapes > 0 : look.shapes === 0), JSON.stringify(look));
    await mid(p, '#res', 0.5, 1900); ok('results counted', (await p.evaluate(() => [...document.querySelectorAll('#res [data-count]')].map(e => e.textContent).join(','))) === '81,79,23,105');
    const drawn = await p.evaluate(() => { const o = document.querySelector('#res .res-obj'); const e = [...o.querySelectorAll('svg *')].find(x => !x.closest('defs')); return { d: getComputedStyle(o).display, fill: e ? getComputedStyle(e).fill : '' }; });
    ok('results drawn in the template\'s own way', t === 'bento' ? drawn.d === 'none' : t === 'screen' ? drawn.d !== 'none' && drawn.fill === 'none' : drawn.d !== 'none' && drawn.fill !== 'none', JSON.stringify(drawn));
    ok('four drawn objects, no still lifes', (await p.evaluate(() => document.querySelectorAll('#res svg.obj').length + '/' + document.querySelectorAll('img[src*="case-"], img[data-src*="case-"]').length)) === '4/0');
    ok('six voices, three people', (await p.evaluate(() => document.querySelectorAll('#quotes > li').length + '/' + document.querySelectorAll('.crew > li').length)) === '6/3');
    ok('every picture loaded', (await p.evaluate(() => [...document.images].filter(i => i.currentSrc && i.complete && !i.naturalWidth).length)) === 0);
    await y(p, 1e7, 1200);
    const end = await p.evaluate(() => { const big = document.querySelector('.foot .big'); return { bar: document.querySelector('.bar').dataset.on, fits: big.firstElementChild.getBoundingClientRect().width <= big.clientWidth + 1 }; });
    ok('the name fits the last screen', end.bar === 'on' && end.fits, JSON.stringify(end));
    await mid(p, '#appform', 0.5); await p.locator('#appform button[type=submit]').click(); await p.waitForTimeout(300);
    ok('form: an empty name is refused', (await txt(p, '#e-name')) === 'Ezt kérjük kitölteni.');
    await p.evaluate(() => { SS.send = (brand, body) => { window.__sent = { brand, body }; }; });
    await p.fill('#f-name', 'Teszt Elek'); await p.fill('#f-email', 'teszt@example.com'); await p.fill('#f-brand', 'Teszt Kft.'); await p.selectOption('#f-budget', '1-3m');
    await p.locator('#chips label').nth(2).click(); await p.locator('#appform button[type=submit]').click(); await p.waitForTimeout(1300);
    const sent = await p.evaluate(() => ({ shown: !document.getElementById('sent').hidden, brand: window.__sent && window.__sent.brand, body: window.__sent ? window.__sent.body : '' }));
    ok('form: the email is composed', sent.shown && sent.brand === 'Teszt Kft.' && /Havi büdzsé: 1M–3M Ft/.test(sent.body) && /Ami érdekel: Fizetett hirdetés/.test(sent.body));
    await p.locator('[data-set-lang="en"]').click(); await p.waitForTimeout(500);
    const en = await p.evaluate(() => ({ lang: document.documentElement.lang, nav: document.querySelector('.bar .links a').textContent, hu: [...document.querySelectorAll('[data-l="hu"]')].filter(e => e.offsetParent !== null).length, svc: document.querySelector('#svc h3').textContent, who: document.querySelector('#res .who').textContent }));
    ok('English everywhere', en.lang === 'en' && en.nav === 'Laws' && en.hu === 0 && en.svc === 'Video content production' && /^Door webshop/.test(en.who), JSON.stringify(en));
    ok('no errors on desktop', errs.length === 0, errs.slice(0, 2).join(' | '));
    await p.context().close();
  }
  // 2. reduced motion: everything readable where it stands
  {
    const { p, errs } = await open(t, { viewport: { width: 1440, height: 900 }, reducedMotion: 'reduce' });
    await y(p, 950, 900);
    const still = await p.evaluate(t => t === 'orbit' ? getComputedStyle(document.querySelector('.claim-h .m2')).opacity === '1' : t === 'bento' ? [...document.querySelectorAll('#board .tile')].every(e => +e.style.getPropertyValue('--k') === 1) : document.querySelectorAll('.lit .w:not(.on)').length === 0, t);
    ok('reduced motion: the opening is whole', still && errs.length === 0, errs.slice(0, 2).join(' | '));
    await p.context().close();
  }
  // 3. a phone
  {
    const { p, errs } = await open(t, { viewport: { width: 393, height: 700 }, isMobile: true, hasTouch: true, deviceScaleFactor: 2 });
    const film = await p.evaluate(() => ({ src: document.querySelector('#reel video').currentSrc.split('/').pop(), vertical: document.getElementById('reel').classList.contains('is-vertical') }));
    await p.tap('#reel', { position: { x: 196, y: 300 } }); await p.waitForTimeout(300);
    const paused = await p.evaluate(() => document.querySelector('#reel video').paused);
    ok('phone: the vertical film, tap pauses', film.src === 'hero-v-720.mp4' && film.vertical && paused, JSON.stringify(film));
    let wide = 0; const total = await p.evaluate(() => document.documentElement.scrollHeight);
    for (let at = 0; at < total; at += 600) { await y(p, at, 220); wide = Math.max(wide, await p.evaluate(() => Math.max(innerWidth, document.documentElement.scrollWidth) - 393)); }
    ok('phone: nothing wider than the screen', wide === 0, String(wide));
    ok('no errors on a phone', errs.length === 0, errs.slice(0, 2).join(' | '));
    await p.context().close();
  }
  console.log(t + ': ' + (n - fails.length) + ' of ' + n + ' checks pass');
}
await b.close();
