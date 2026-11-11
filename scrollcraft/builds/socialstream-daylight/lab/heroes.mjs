// node lab/heroes.mjs   (run from a folder with playwright-core; the build served on :4553, or BASE=...)
// The three first-screen options (hero-cinema.html, hero-glow.html, hero-capsule.html), checked without
// looking: the promise and the button on the first screen, the film's size, the menu over the dark parts,
// Glow's frame opening to the full width, Capsule's film growing from the capsule to the whole screen and
// falling back to a plain layout on short screens and with reduced motion, English, and no sideways scroll.
import { createRequire } from 'node:module';
const { chromium } = createRequire(process.cwd() + '/')('playwright-core');
const BASE = process.env.BASE || 'http://localhost:4553/';
const b = await chromium.launch({ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', args: ['--autoplay-policy=no-user-gesture-required'] });
let pass = 0, fail = 0;
const ok = (name, cond, info = '') => { if (cond) pass++; else { fail++; console.log('FAIL', name, info); } };
const DESK = { viewport: { width: 1440, height: 900 } };
const PHONE = { viewport: { width: 393, height: 852 }, isMobile: true, hasTouch: true, deviceScaleFactor: 2 };
async function open(name, opts) {
  const ctx = await b.newContext(opts); const p = await ctx.newPage(); const errs = [];
  p.on('pageerror', e => errs.push(e.message)); p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
  await p.goto(BASE + 'hero-' + name + '.html', { waitUntil: 'load' }); await p.waitForTimeout(2200);
  return { p, errs, ctx };
}
const to = (p, top, wait = 500) => p.evaluate(top => scrollTo({ top, behavior: 'instant' }), top).then(() => p.waitForTimeout(wait));
const rect = (p, sel) => p.evaluate(sel => { const e = [...document.querySelectorAll(sel)].find(e => e.offsetParent !== null || getComputedStyle(e).position === 'fixed'); if (!e) return null; const r = e.getBoundingClientRect(); return { x: r.x, y: r.y, w: r.width, h: r.height, b: r.bottom, r: r.right }; }, sel);
const onScreen = (p, sel) => p.evaluate(sel => { const e = document.querySelector(sel), r = e.getBoundingClientRect(); return r.top >= 0 && r.bottom <= innerHeight && r.width > 0 && getComputedStyle(e).visibility !== 'hidden'; }, sel);
const dark = p => p.evaluate(() => document.getElementById('nav').classList.contains('on-dark'));
const wide = p => p.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
const near = (a, b, d = 2) => Math.abs(a - b) <= d;

for (const [dev, opts] of [['desktop', DESK], ['phone', PHONE]]) {
  // Cinema: the film is the first screen, with the promise and the button on the strip under it
  {
    const { p, errs, ctx } = await open('cinema', opts);
    const vh = opts.viewport.height, f = await rect(p, '.hf-film');
    ok(`cinema ${dev}: the film fills most of the first screen`, f.y === 0 && f.h >= vh * 0.6, JSON.stringify(f));
    ok(`cinema ${dev}: headline and button on the first screen`, await onScreen(p, '#hero-h') && await onScreen(p, '.hf-act .btn'));
    ok(`cinema ${dev}: the menu is dark over the film`, await dark(p));
    await to(p, vh * 1.2); ok(`cinema ${dev}: and light again after it`, !(await dark(p)));
    ok(`cinema ${dev}: no page errors`, !errs.length, errs.join(' | '));
    await ctx.close();
  }
  // Glow: a dark stage; the film opens out to the full width as it comes up
  {
    const { p, errs, ctx } = await open('glow', opts);
    const vh = opts.viewport.height, vw = opts.viewport.width;
    ok(`glow ${dev}: headline and button on the first screen`, await onScreen(p, '#hero-h') && await onScreen(p, '.hd .cta-row .btn'));
    ok(`glow ${dev}: the menu is dark over the stage`, await dark(p));
    const inset0 = await p.evaluate(() => getComputedStyle(document.getElementById('film')).getPropertyValue('--in'));
    await p.evaluate(() => { const r = document.getElementById('film').getBoundingClientRect(); scrollTo({ top: scrollY + r.top - innerHeight * 0.12, behavior: 'instant' }); }); await p.waitForTimeout(500);
    const inset1 = await p.evaluate(() => getComputedStyle(document.getElementById('film')).getPropertyValue('--in'));
    ok(`glow ${dev}: the frame starts inset and opens to the full width`, parseFloat(inset0) > 4 && parseFloat(inset1) < 0.05, inset0 + ' -> ' + inset1);
    await p.evaluate(() => { const r = document.querySelector('.count').getBoundingClientRect(); scrollTo({ top: scrollY + r.top - 40, behavior: 'instant' }); }); await p.waitForTimeout(500);
    ok(`glow ${dev}: the menu is light over the page`, !(await dark(p)));
    ok(`glow ${dev}: no page errors`, !errs.length, errs.join(' | '));
    await ctx.close();
  }
  // Capsule: the film grows from the capsule in the headline to the whole screen
  {
    const { p, errs, ctx } = await open('capsule', opts);
    ok(`capsule ${dev}: the scroll scene is on`, await p.evaluate(() => document.querySelector('.ht').classList.contains('is-live')));
    ok(`capsule ${dev}: headline and button on the first screen`, await onScreen(p, '#hero-h') && await onScreen(p, '.ht-act .btn'));
    let f = await rect(p, '#film'), c = await rect(p, '.ht-pill');
    ok(`capsule ${dev}: the film sits on the capsule`, near(f.x, c.x) && near(f.y, c.y) && near(f.w, c.w) && near(f.h, c.h), JSON.stringify({ f, c }));
    const t = await rect(p, '#film .toggle');
    ok(`capsule ${dev}: a pause button inside the capsule`, t && t.w >= 24 && t.x >= f.x && t.r <= f.r + 1 && t.y >= f.y - 1 && t.b <= f.b + 1, JSON.stringify({ t, f }));
    ok(`capsule ${dev}: the menu is light over the type`, !(await dark(p)));
    const sh = await p.evaluate(() => document.querySelector('.ht-stage').clientHeight);
    await to(p, Math.ceil(sh * 0.95) + 4, 700);
    f = await rect(p, '#film');
    ok(`capsule ${dev}: grown, the film fills the screen`, near(f.x, 0) && near(f.y, 0) && near(f.w, opts.viewport.width) && near(f.h, sh), JSON.stringify(f));
    ok(`capsule ${dev}: grown, the menu is dark and the button is the usual one`, await dark(p) && await p.evaluate(() => { const s = document.querySelector('#film .toggle span'); return !!s && s.offsetWidth > 0; }));
    await p.evaluate(() => { const r = document.querySelector('.count').getBoundingClientRect(); scrollTo({ top: scrollY + r.top - 40, behavior: 'instant' }); }); await p.waitForTimeout(500);
    ok(`capsule ${dev}: the menu is light over the page`, !(await dark(p)));
    // English: the other capsule is the one measured
    await to(p, 0, 400); await p.locator('[data-set-lang="en"]').first().click(); await p.waitForTimeout(700);
    f = await rect(p, '#film'); c = await rect(p, '.ht-pill');
    const h1 = await p.evaluate(() => document.querySelector('#hero-h [data-l="en"]').textContent.replace(/\s+/g, ' ').trim());
    ok(`capsule ${dev}: English, and the film on the English capsule`, h1 === 'Videos people watch to the end. Ads that pay off.' && near(f.x, c.x) && near(f.y, c.y), JSON.stringify({ h1, f, c }));
    ok(`capsule ${dev}: no page errors`, !errs.length, errs.join(' | '));
    await ctx.close();
  }
}
// Capsule on a short screen and with reduced motion: no scene, the film simply under the type, the button still there
// the scene runs in a 13-inch laptop's browser window and on a phone with its browser bars showing
for (const [label, opts] of [['laptop window', { viewport: { width: 1280, height: 650 } }], ['phone with bars', { ...PHONE, viewport: { width: 390, height: 664 } }], ['small phone with bars', { ...PHONE, viewport: { width: 375, height: 548 } }]]) {
  const { p, ctx } = await open('capsule', opts);
  ok(`capsule ${label}: the scroll scene is on`, await p.evaluate(() => document.querySelector('.ht').classList.contains('is-live')));
  ok(`capsule ${label}: headline and button on the first screen`, await onScreen(p, '#hero-h') && await onScreen(p, '.ht-act .btn'));
  await ctx.close();
}
for (const [label, opts] of [['short laptop', { viewport: { width: 1280, height: 480 } }], ['short phone', { ...PHONE, viewport: { width: 375, height: 480 } }], ['reduced motion', { ...DESK, reducedMotion: 'reduce' }]]) {
  const { p, ctx } = await open('capsule', opts);
  const live = await p.evaluate(() => document.querySelector('.ht').classList.contains('is-live'));
  const f = await rect(p, '#film'), h = await rect(p, '#hero-h');
  ok(`capsule ${label}: plain layout, the film under the type`, !live && f.y > h.b, JSON.stringify({ live, f, h }));
  await p.evaluate(() => document.querySelector('.ht-act .btn').scrollIntoView({ block: 'center' })); await p.waitForTimeout(300);
  ok(`capsule ${label}: the button is reachable`, await onScreen(p, '.ht-act .btn'));
  await ctx.close();
}
// no sideways scroll on narrow phones, at the top, in the middle of the first screen and past it
for (const name of ['cinema', 'glow', 'capsule']) {
  for (const w of [320, 393]) {
    const { p, ctx } = await open(name, { ...PHONE, viewport: { width: w, height: w === 320 ? 640 : 852 } });
    let worst = 0;
    for (const k of [0, 0.5, 1, 1.6, 2.4]) { await to(p, (w === 320 ? 640 : 852) * k, 350); worst = Math.max(worst, await wide(p)); }
    ok(`${name} ${w}px: no sideways scroll`, worst <= 0, String(worst));
    await ctx.close();
  }
}
console.log(`heroes: ${pass} passed, ${fail} failed`);
await b.close();
