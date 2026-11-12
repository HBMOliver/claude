// node lab/check.mjs [names]   (run from a folder with playwright-core; served on :4560, or BASE=...)
// What each concept page does, checked without looking: the claim and the audit button on the first screen,
// the line through "social media", the film playing and pausing, the running rows moving when nothing is
// scrolled, the counters, the audit form (errors, the email it writes, the sent note), English, questions,
// reduced motion and no sideways scroll; the six business problems, each linked to its service card before the
// services; things on the first screen following a mouse, and nothing following on a phone or with reduced motion;
// no sideways scroll with a mouse at the screen's edges anywhere down the page, at 1440 and 1100 wide.
// One line per failed check, then a summary line per page.
import { createRequire } from 'node:module';
const { chromium } = createRequire(process.cwd() + '/')('playwright-core');
const BASE = process.env.BASE || 'http://localhost:4560/';
const names = process.argv[2] ? process.argv[2].split(',') : ['pulse', 'premiere', 'aurora', 'studio', 'mix'];
const b = await chromium.launch({ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', args: ['--autoplay-policy=no-user-gesture-required'] });
const CLAIM_HU = 'A social media meghalt. Az érdeklődés vette át a helyét.', CLAIM_EN = 'Social media is dead. Interest has taken its place.';
const DESK = { viewport: { width: 1440, height: 900 } }, PHONE = { viewport: { width: 390, height: 664 }, isMobile: true, hasTouch: true, deviceScaleFactor: 2 };
let total = 0, failed = 0;

for (const name of names) {
  let pass = 0, fail = 0;
  const ok = (what, cond, info = '') => { if (cond) pass++; else { fail++; console.log(`FAIL ${name}: ${what}`, info); } };
  const open = async opts => {
    const ctx = await b.newContext(opts), p = await ctx.newPage(), errs = [];
    p.on('pageerror', e => errs.push(e.message)); p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
    await p.goto(BASE + name + '.html', { waitUntil: 'load' }); await p.waitForTimeout(1800);
    return { p, ctx, errs };
  };
  const to = (p, sel, k = 0.3, wait = 900) => p.evaluate(([s, k]) => { const e = document.querySelector(s), r = e.getBoundingClientRect(); scrollTo({ top: scrollY + r.top - innerHeight * k, behavior: 'instant' }); }, [sel, k]).then(() => p.waitForTimeout(wait));
  const onScreen = (p, sel) => p.evaluate(sel => [...document.querySelectorAll(sel)].some(e => { const r = e.getBoundingClientRect(); return e.offsetParent !== null && r.width > 0 && r.top >= 0 && r.bottom <= innerHeight; }), sel);
  const strike = p => p.evaluate(() => {
    const s = [...document.querySelectorAll('.claim .strike')].find(e => e.offsetParent !== null); if (!s) return null;
    const a = getComputedStyle(s, '::after'), c = document.createElement('canvas').getContext('2d'); c.font = getComputedStyle(s).font; const t = c.measureText('x');
    const fs = parseFloat(getComputedStyle(s).fontSize), mid = t.fontBoundingBoxAscent - t.actualBoundingBoxAscent / 2, line = parseFloat(a.top) + parseFloat(a.height) / 2;
    return { drawn: new DOMMatrix(a.transform === 'none' ? undefined : a.transform).a > 0.99, off: +Math.abs((line - mid) / fs).toFixed(3) };
  });
  const film = p => p.evaluate(() => { const f = document.querySelector('[data-film]'), v = f.querySelector('video'); return { src: (v.currentSrc || '').split('/').pop(), paused: v.paused, t: v.currentTime }; });

  for (const [dev, opts] of [['desktop', DESK], ['phone', PHONE]]) {
    const { p, ctx, errs } = await open(opts);
    // the first screen: the claim and the button
    const h1 = await p.evaluate(() => document.querySelector('#hero-h [data-l="hu"]').textContent.replace(/\s+/g, ' ').trim());
    ok(`${dev}: the claim is the headline`, h1 === CLAIM_HU, h1);
    // a page that opens on its film alone (#top[data-seq]): the film fills the first screen and plays; at the end of the
    // opening the claim and the audit button are on screen and fully shown, the line is drawn, and the light follows
    const seq = await p.evaluate(() => !!document.querySelector('#top[data-seq]'));
    const toSeqEnd = () => p.evaluate(() => { const s = document.getElementById('top'), r = s.getBoundingClientRect(); const span = s.classList.contains('is-morph') ? s.offsetHeight - innerHeight : innerHeight; scrollTo({ top: scrollY + r.top + Math.max(0, span), behavior: 'instant' }); }).then(() => p.waitForTimeout(900));
    if (!seq) {
      ok(`${dev}: the claim and the audit button on the first screen`, await onScreen(p, '.claim') && await onScreen(p, '#top a.btn[href="#audit"]'));
      const st = await strike(p);
      ok(`${dev}: "social media" is struck through the middle`, st && st.drawn && st.off < 0.06, JSON.stringify(st));
    } else {
      const cover = await p.evaluate(() => { const f = document.querySelector('#top [data-seq-open] [data-film]'), r = f.getBoundingClientRect(), v = f.querySelector('video'); return { area: +((Math.min(r.right, innerWidth) - Math.max(r.left, 0)) * (Math.min(r.bottom, innerHeight) - Math.max(r.top, 0)) / (innerWidth * innerHeight)).toFixed(2), playing: !v.paused && v.currentTime > 0, src: (v.currentSrc || '').split('/').pop() }; });
      ok(`${dev}: the film alone fills the first screen and plays`, cover.area > 0.9 && cover.playing, JSON.stringify(cover));
      await toSeqEnd();
      const vis = await p.evaluate(() => { const op = e => { let o = 1; for (; e && e !== document.body; e = e.parentElement) o *= +getComputedStyle(e).opacity; return o; }; const on = e => { const r = e.getBoundingClientRect(); return r.width > 0 && r.top >= 0 && r.bottom <= innerHeight; }; const c = document.querySelector('#top .claim'), b = document.querySelector('#top a.btn[href="#audit"]'); return { claim: on(c), claimShown: +op(c).toFixed(2), button: on(b), buttonShown: +op(b).toFixed(2) }; });
      ok(`${dev}: after the opening, the claim and the audit button are on screen and fully shown`, vis.claim && vis.button && vis.claimShown > 0.98 && vis.buttonShown > 0.98, JSON.stringify(vis));
      const st = await strike(p);
      ok(`${dev}: after the opening, "social media" is struck through the middle`, st && st.drawn && st.off < 0.06, JSON.stringify(st));
    }
    ok(`${dev}: no Tenerife or Budapest on the first screen`, await p.evaluate(() => !/Tenerif|Budapest/i.test(document.getElementById('top').innerText)));
    // the business problems: six, each pointing at its own service card, all of them before the services
    const pains = await p.evaluate(() => {
      const ls = [...document.querySelectorAll('a[href^="#svc-"]')], svc = document.getElementById('szolgaltatasok');
      return { n: ls.length, uniq: new Set(ls.map(a => a.getAttribute('href'))).size, hit: ls.every(a => { const t = document.querySelector(a.getAttribute('href')); return !!t && svc.contains(t); }), before: ls.every(a => !!(a.compareDocumentPosition(svc) & Node.DOCUMENT_POSITION_FOLLOWING)) };
    });
    ok(`${dev}: six problems, each linked to its service, before the services`, pains.n === 6 && pains.uniq === 6 && pains.hit && pains.before, JSON.stringify(pains));
    // the first screen follows a mouse; on a phone nothing follows
    if (seq) await toSeqEnd();
    const fxy = () => p.evaluate(() => [...document.querySelectorAll('#top [data-follow]')].map(e => [parseFloat(e.style.getPropertyValue('--fx')) || 0, parseFloat(e.style.getPropertyValue('--fy')) || 0]));
    const vw = opts.viewport.width, vhh = opts.viewport.height;
    await p.mouse.move(70, 120, { steps: 4 }); await p.waitForTimeout(1300); const f0 = await fxy();
    await p.mouse.move(vw - 70, vhh - 70, { steps: 8 }); await p.waitForTimeout(1300); const f1 = await fxy();
    const moved = f0.length ? Math.max(...f0.map((v, i) => Math.hypot(f1[i][0] - v[0], f1[i][1] - v[1]))) : 0;
    if (dev === 'desktop') ok('desktop: the first screen follows the cursor', f0.length > 0 && moved >= 10, `${f0.length} followers, moved ${moved.toFixed(1)}px`);
    else ok('phone: nothing follows a cursor', f1.every(v => v[0] === 0 && v[1] === 0), JSON.stringify(f1));
    await p.mouse.move(2, 2);
    if (seq) { await p.evaluate(() => scrollTo({ top: 0, behavior: 'instant' })); await p.waitForTimeout(900); }
    // the film plays where it is seen, and its button pauses it
    await to(p, '[data-film]', 0.15, 1800);
    let f = await film(p);
    ok(`${dev}: the film plays`, f.src && !f.paused && f.t > 0, JSON.stringify(f));
    if (dev === 'phone') ok('phone: an upright film plays the vertical cut', await p.evaluate(() => { const f = document.querySelector('[data-film]'); const v = f.querySelector('video'); return f.dataset.cut === 'h' || /hero-v-720/.test(v.currentSrc); }));
    await p.locator('[data-film] .toggle').first().click({ force: true }); await p.waitForTimeout(300); f = await film(p);
    ok(`${dev}: the film's button pauses it`, f.paused, JSON.stringify(f));
    // the running rows move without any scrolling
    // (the first row outside an opening: one inside it only runs once the opening has brought it in)
    const rails = await p.evaluate(() => { const r = [...document.querySelectorAll('[data-rail]')].find(e => !e.closest('#top[data-seq]')); if (r) r.setAttribute('data-test-rail', ''); return !!r; });
    if (rails) {
      await to(p, '[data-test-rail]', 0.4, 600);
      const x0 = await p.evaluate(() => document.querySelector('[data-test-rail] .track').style.transform); await p.waitForTimeout(1000);
      const x1 = await p.evaluate(() => document.querySelector('[data-test-rail] .track').style.transform);
      ok(`${dev}: a running row moves at rest`, x0 !== x1, x0 + ' -> ' + x1);
    }
    // counters reach the real numbers
    const counts = await p.evaluate(() => [...document.querySelectorAll('#eredmenyek [data-count], .au-stats [data-count]')].length);
    if (counts) {
      await to(p, '[data-count]', 0.4, 2400);
      const ns = await p.evaluate(() => [...new Set([...document.querySelectorAll('[data-count]')].map(e => e.closest('[data-r]') || e))].length);
      await p.evaluate(() => [...document.querySelectorAll('[data-count]')].forEach(e => e.scrollIntoView({ block: 'center' })));
      await p.waitForTimeout(2600);
      const got = await p.evaluate(() => [...document.querySelectorAll('[data-count]')].map(e => e.textContent.replace(/[\s  ]/g, '') === e.dataset.count.replace(/\B(?=(\d{3})+(?!\d))/g, '')).every(Boolean));
      ok(`${dev}: every counter ends on its real number`, got && ns > 0);
    }
    // the audit form
    await to(p, '#appform', 0.1, 600);
    await p.evaluate(() => { window.__mail = null; SS.send = (brand, body) => { window.__mail = body; }; });
    await p.locator('#appform button[type="submit"]').click(); await p.waitForTimeout(300);
    const errs1 = await p.evaluate(() => ['name', 'email', 'brand'].map(n => document.getElementById('e-' + n).textContent));
    ok(`${dev}: each empty field says what to do`, errs1[0] === 'Írd be a neved, hogy tudjuk, kinek válaszolunk.' && errs1[1] === 'Írd be az e-mail címed, ide válaszolunk.' && errs1[2] === 'Írd be a céged vagy a márkád nevét.', JSON.stringify(errs1));
    await p.fill('#f-name', 'Teszt Elek'); await p.fill('#f-email', 'teszt@'); await p.fill('#f-brand', 'Próba Kft');
    await p.locator('#appform button[type="submit"]').click(); await p.waitForTimeout(300);
    ok(`${dev}: a wrong address gets an example`, (await p.textContent('#e-email')) === 'Ez nem tűnik e-mail címnek. Például: nev@ceg.hu');
    await p.fill('#f-email', 'teszt@pelda.hu'); await p.selectOption('#f-budget', '300-1m');
    await p.locator('#appform button[type="submit"]').click(); await p.waitForTimeout(250);
    ok(`${dev}: while it works it says so`, (await p.textContent('#stext')) === 'Megnyitjuk a leveleződ…');
    await p.waitForTimeout(1100);
    const mail = await p.evaluate(() => window.__mail || '');
    ok(`${dev}: the email carries the fields`, /Teszt Elek/.test(mail) && /teszt@pelda\.hu/.test(mail) && /Havi büdzsé: 300 ezer – 1 millió Ft/.test(mail), mail.slice(0, 160));
    ok(`${dev}: the sent note`, /Az e-mailed kész, már csak el kell küldened\./.test(await p.textContent('#sent')) && await p.evaluate(() => !document.getElementById('sent').hidden));
    // English
    await p.locator('[data-set-lang="en"]').first().click(); await p.waitForTimeout(400);
    const en = await p.evaluate(() => ({ h1: document.querySelector('#hero-h [data-l="en"]').textContent.replace(/\s+/g, ' ').trim(), nav: document.querySelector('.nav .links a').textContent.trim(), cta: document.querySelector('#top a.btn[href="#audit"]').textContent.trim(), hu: [...document.querySelectorAll('[data-l="hu"]')].filter(e => e.offsetParent !== null).length }));
    ok(`${dev}: English`, en.h1 === CLAIM_EN && en.nav === 'Results' && en.cta === 'Get my free audit' && en.hu === 0, JSON.stringify(en));
    await p.locator('[data-set-lang="hu"]').first().click(); await p.waitForTimeout(300);
    ok(`${dev}: eight questions`, (await p.evaluate(() => document.querySelectorAll('.faq-list details').length)) === 8);
    ok(`${dev}: no page errors`, !errs.length, errs.join(' | '));
    await ctx.close();
  }
  // reduced motion: everything in its end state, nothing running
  {
    const { p, ctx } = await open({ ...DESK, reducedMotion: 'reduce' });
    await p.mouse.move(80, 120, { steps: 3 }); await p.mouse.move(1300, 800, { steps: 6 }); await p.waitForTimeout(800);
    const still = await p.evaluate(() => [...document.querySelectorAll('[data-follow], a.btn')].every(e => !e.style.getPropertyValue('--fx')));
    ok('reduced motion: nothing follows the cursor', still);
    const r = await p.evaluate(() => ({ hidden: [...document.querySelectorAll('[data-r]')].filter(e => getComputedStyle(e).opacity !== '1').length, tracks: [...document.querySelectorAll('[data-rail] .track')].filter(t => t.style.transform).length, paused: [...document.querySelectorAll('[data-film] video')].every(v => v.paused) }));
    const st = await strike(p);
    ok('reduced motion: all in place, rows still, film waiting', r.hidden === 0 && r.tracks === 0 && r.paused && st && st.drawn, JSON.stringify({ r, st }));
    await ctx.close();
  }
  // no sideways scroll on narrow phones
  for (const w of [320, 390]) {
    const { p, ctx } = await open({ ...PHONE, viewport: { width: w, height: 680 } });
    const H = await p.evaluate(() => document.documentElement.scrollHeight); let worst = 0;
    for (let y = 0; y < H; y += 900) { await p.evaluate(y => scrollTo({ top: y, behavior: 'instant' }), y); await p.waitForTimeout(120); worst = Math.max(worst, await p.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth)); }
    ok(`${w}px: no sideways scroll`, worst <= 0, String(worst));
    await ctx.close();
  }
  // with a mouse at the screen's edges, nothing that follows the cursor widens the page, anywhere down it
  for (const w of [1440, 1100]) {
    const { p, ctx } = await open({ viewport: { width: w, height: 900 } });
    const H = await p.evaluate(() => document.documentElement.scrollHeight); let worst = 0;
    for (let y = 0; y < H; y += 900) {
      await p.evaluate(y => scrollTo({ top: y, behavior: 'instant' }), y);
      for (const [x, yy] of [[w - 6, 894], [6, 6]]) { await p.mouse.move(x, yy, { steps: 3 }); await p.waitForTimeout(450); worst = Math.max(worst, await p.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth)); }
    }
    ok(`${w}px, a mouse at the edges: no sideways scroll`, worst <= 0, String(worst));
    await ctx.close();
  }
  console.log(`${name}: ${pass} passed, ${fail} failed`);
  total += pass; failed += fail;
}
console.log(`concepts: ${total} passed, ${failed} failed`);
await b.close();
