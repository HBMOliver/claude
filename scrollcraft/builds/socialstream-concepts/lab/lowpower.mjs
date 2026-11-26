// Low Power Mode, as near as Chrome can play it. An iPhone in Low Power Mode (and a Mac saving its battery) refuses
// video.play() unless it is called inside a touch, click or key that the browser counts, and a video that has been let
// play inside one may play later by itself. The stub below does the same in Chrome; here a touchstart, pointerdown,
// mousedown or pointerup does not count, so the page must keep listening after a refused try. The checks follow the
// site's films (kit.js) and reels (reels.js) through it: the still and no Play button before a touch, everything
// starting at the first one, the sound button as the very first touch, a computer, a page of reels, reduced motion as
// before, and an ordinary phone as before. It is a model of WebKit's rule, not an iPhone: the real check is a phone.
// The films are served from this folder's files instead of Pulse's Media Storage (site/films.mjs).
// usage, from a folder with playwright-core: node lab/lowpower.mjs <base> [folder for screenshots]
import { createRequire } from 'module';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
const { chromium } = createRequire(process.cwd() + '/')('playwright-core');
const ROOT = path.join(path.dirname(fileURLToPath(import.meta.url)), '..');
const { FILMS } = await import(path.join(ROOT, 'site/films.mjs'));
const BASE = (process.argv[2] || 'http://localhost:4566').replace(/\/$/, ''), OUT = process.argv[3] || '';
// the Spanish site (socialstream.es since 2026-11-26) at its own address: ES_BASE; before the split it was <base>/es/
const ES_BASE = (process.env.ES_BASE || BASE + '/es/').replace(/\/?$/, '/');

const LOCAL = {}, BYTES = {};
for (const l of Object.keys(FILMS)) for (const k of Object.keys(FILMS[l])) if (FILMS[l][k].url) LOCAL[FILMS[l][k].url] = path.join(ROOT, FILMS[l][k].file);
async function serveFilm(route) {
  const file = LOCAL[route.request().url().split('?')[0]];
  if (!file || !fs.existsSync(file)) return route.continue();
  const b = BYTES[file] || (BYTES[file] = fs.readFileSync(file)), m = /bytes=(\d+)-(\d*)/.exec(route.request().headers().range || '');
  if (!m) return route.fulfill({ status: 200, contentType: 'video/mp4', headers: { 'accept-ranges': 'bytes' }, body: b });
  const a = +m[1], z = m[2] ? Math.min(+m[2], b.length - 1) : b.length - 1;
  return route.fulfill({ status: 206, contentType: 'video/mp4', headers: { 'accept-ranges': 'bytes', 'content-range': `bytes ${a}-${z}/${b.length}` }, body: b.subarray(a, z + 1) });
}

// WebKit's rule: play() is refused outside a counted touch, click or key; a video let play once stays let
function STUB() {
  const play = HTMLMediaElement.prototype.play, let_ = new WeakSet();
  let inside = false;
  for (const t of ['touchend', 'click', 'keydown']) addEventListener(t, e => { if (e.isTrusted) { inside = true; setTimeout(() => { inside = false; }, 0); } }, true);
  window.__refused = 0;
  HTMLMediaElement.prototype.play = function () {
    if (inside) { let_.add(this); this.dataset.lpmLet = '1'; }
    if (!let_.has(this)) { window.__refused++; return Promise.reject(new DOMException('The request is not allowed by the user agent or the platform in the current context, possibly because the user denied permission.', 'NotAllowedError')); }
    return play.call(this);
  };
}

const b = await chromium.launch({ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', args: ['--autoplay-policy=no-user-gesture-required'] });
const PHONE = { viewport: { width: 390, height: 844 }, deviceScaleFactor: 3, isMobile: true, hasTouch: true };
const DESK = { viewport: { width: 1440, height: 900 }, deviceScaleFactor: 2 };
let passed = 0; const failed = [];
const check = (cond, what) => { if (cond) passed++; else { failed.push(what); console.log('FAIL ' + what); } };
async function open(opts, url, lpm) {
  const ctx = await b.newContext(opts);
  await ctx.route(/^https:\/\/socialstream\.(hu|es)\/m\/med_[\w-]+\.mp4/, serveFilm);
  if (lpm) await ctx.addInitScript(STUB);
  const p = await ctx.newPage(), errors = [];
  p.on('pageerror', e => errors.push(String(e)));
  await p.goto(/^https?:/.test(url) ? url : BASE + url, { waitUntil: 'load' });
  await p.waitForTimeout(2500);
  return { ctx, p, errors };
}
const films = p => p.evaluate(() => [...document.querySelectorAll('[data-film]')].map(box => {
  const v = box.querySelector('video'), t = box.querySelector('.toggle'), img = box.querySelector('.poster img'), s = box.querySelector('.ss-sound');
  return { cls: box.className, waiting: box.classList.contains('is-waiting'), playing: box.classList.contains('is-playing'), pausedCls: box.classList.contains('is-paused'),
    paused: v.paused, t: v.currentTime, muted: v.muted, let: v.dataset.lpmLet === '1', vOpacity: getComputedStyle(v).opacity, toggle: t && getComputedStyle(t).visibility,
    toggleText: t && t.textContent, poster: getComputedStyle(box.querySelector('.poster')).opacity, img: img && img.currentSrc.split('/').pop(), imgW: img && img.naturalWidth,
    sound: s && getComputedStyle(s).visibility, pressed: s && s.getAttribute('aria-pressed') };
}));
// seen: at least 60% on screen (reels.js plays from 10%, so these have had time); far: 100 px or more off screen
// (reels.js loads from 80 px)
const reels = p => p.evaluate(() => [...document.querySelectorAll('.rv video')].map(v => {
  const r = v.getBoundingClientRect(), w = Math.max(0, Math.min(r.right, innerWidth) - Math.max(r.left, 0)), h = Math.max(0, Math.min(r.bottom, innerHeight) - Math.max(r.top, 0));
  return { on: v.classList.contains('on'), paused: v.paused, t: v.currentTime, src: !!v.getAttribute('src'), let: v.dataset.lpmLet === '1',
    seen: r.width > 0 && w * h >= 0.6 * r.width * r.height,
    far: r.width === 0 || r.top > innerHeight + 100 || r.bottom < -100 || r.left > innerWidth + 100 || r.right < -100 };
}));
// a point on the page that is not a link, a button or a field, inside sel (or the screen)
const safePoint = (p, sel) => p.evaluate(sel => {
  const r = (sel && document.querySelector(sel) || document.body).getBoundingClientRect(), top = Math.max(0, r.top), h = Math.min(r.bottom, innerHeight) - top;
  for (const fy of [0.35, 0.5, 0.25, 0.6, 0.45, 0.7, 0.15]) for (const fx of [0.5, 0.3, 0.7, 0.2, 0.8]) {
    const x = Math.round(r.left + r.width * fx), y = Math.round(top + h * fy), el = document.elementFromPoint(x, y);
    if (el && !el.closest('a, button, input, select, textarea, label, summary, [role="button"], [tabindex]')) return { x, y };
  }
  return null;
}, sel);
const shot = async (p, name) => { if (OUT) await p.screenshot({ path: path.join(OUT, name + '.png') }); };
const refused = p => p.evaluate(() => window.__refused || 0);
const toY = (p, sel, off = 0.25) => p.evaluate(([sel, off]) => { const e = document.querySelector(sel); if (e) scrollTo(0, e.getBoundingClientRect().top + scrollY - innerHeight * off); return !!e; }, [sel, off]);

// 1. a phone in Low Power Mode, the home page in each language: the still, then everything at the first tap
for (const url of ['/', '/en/', ES_BASE]) {
  const { ctx, p, errors } = await open(PHONE, url, true), at = 'phone ' + url;
  let [o] = await films(p);
  check(o.waiting && o.paused && !o.playing, `${at}: the opening waits, not started (${o.cls})`);
  check(!o.pausedCls && o.toggle === 'hidden', `${at}: no Play button while it waits (is-paused ${o.pausedCls}, toggle ${o.toggle})`);
  check(o.vOpacity === '0' && o.poster === '1', `${at}: only the still shows (video ${o.vOpacity}, still ${o.poster})`);
  check(o.img === 'hero-v-poster-1080.jpg' && o.imgW > 0, `${at}: the still is the sharp 1080 one, loaded (${o.img}, ${o.imgW})`);
  check(o.sound === 'visible', `${at}: the sound button stays (${o.sound})`);
  check(await refused(p) > 0, `${at}: the stub refused the film`);
  if (url === '/') await shot(p, 'phone-waiting');
  const before = await refused(p), pt = await safePoint(p, '.mx-openfilm');
  check(!!pt, `${at}: a free point on the opening to tap`);
  if (pt) await p.touchscreen.tap(pt.x, pt.y);
  await p.waitForTimeout(1800);
  [o] = await films(p);
  check(await refused(p) > before, `${at}: the touchstart was refused first and the page tried again`);
  check(!o.paused && o.t > 0.3 && o.playing && !o.waiting, `${at}: the film starts at the first tap (paused ${o.paused}, t ${o.t.toFixed(2)}, ${o.cls})`);
  check(o.vOpacity === '1' && o.toggle === 'visible' && o.muted, `${at}: the film shows, Pause is back, still silent (video ${o.vOpacity}, toggle ${o.toggle}, muted ${o.muted})`);
  if (url === '/') await shot(p, 'phone-after-tap');
  // no more touches from here: the reels and the card were let play inside the tap
  const rs0 = await reels(p);
  check(rs0.length > 0 && rs0.every(r => r.let), `${at}: every reel was let play inside the tap (${rs0.filter(r => r.let).length}/${rs0.length})`);
  check(rs0.filter(r => r.far).every(r => !r.src), `${at}: the reels out of view did not load`);
  await toY(p, '.rv'); await p.waitForTimeout(1800);
  const rs = (await reels(p)).filter(r => r.seen);
  check(rs.length > 0 && rs.every(r => !r.paused && r.on), `${at}: the reels on screen play after scrolling, with no touch (${rs.filter(r => !r.paused).length}/${rs.length})`);
  await toY(p, '.mx-film', 0.1); await p.waitForTimeout(2200);
  const card = (await films(p))[1];
  check(card && !card.paused && card.t > 0.2 && !card.waiting, `${at}: the card's film plays when it comes into view, with no touch (paused ${card && card.paused}, t ${card && card.t.toFixed(2)})`);
  check(!errors.length, `${at}: no script errors (${errors.join(' | ')})`);
  await ctx.close();
}

// 2. the sound button as the very first touch: the film starts and is heard
{
  const { ctx, p, errors } = await open(PHONE, '/', true), at = 'phone /, sound first';
  const r = await p.locator('.mx-openfilm .ss-sound').boundingBox();
  await p.touchscreen.tap(r.x + r.width / 2, r.y + r.height / 2);
  await p.waitForTimeout(1800);
  const [o] = await films(p);
  check(!o.paused && o.t > 0.3 && !o.muted && o.pressed === 'true', `${at}: plays with sound (paused ${o.paused}, t ${o.t.toFixed(2)}, muted ${o.muted}, pressed ${o.pressed})`);
  check(!errors.length, `${at}: no script errors (${errors.join(' | ')})`);
  await ctx.close();
}

// 3. a computer saving its battery: the first click starts the film; the card's film takes over later by itself
{
  const { ctx, p, errors } = await open(DESK, '/', true), at = 'computer /';
  let [o] = await films(p);
  check(o.waiting && o.paused && o.toggle === 'hidden' && o.img === 'hero-poster-1920.jpg', `${at}: the opening waits on the sharp still (${o.cls}, ${o.img})`);
  await shot(p, 'computer-waiting');
  const pt = await safePoint(p, '.mx-openfilm');
  if (pt) await p.mouse.click(pt.x, pt.y);
  await p.waitForTimeout(1800);
  [o] = await films(p);
  check(!o.paused && o.t > 0.3 && !o.waiting, `${at}: the film starts at the first click (paused ${o.paused}, t ${o.t.toFixed(2)})`);
  const card0 = (await films(p))[1];
  check(card0.let, `${at}: the card's film was let play inside the click`);
  // to the end of the opening, where the card's film takes over
  await p.evaluate(() => { const st = document.querySelector('[data-seq]'); scrollTo(0, st.getBoundingClientRect().top + scrollY + st.offsetHeight - innerHeight); });
  await p.waitForTimeout(2500);
  const card = (await films(p))[1];
  check(!card.paused && card.t > 0.3, `${at}: the card's film plays after the opening hands over, with no click (paused ${card.paused}, t ${card.t.toFixed(2)})`);
  check(!errors.length, `${at}: no script errors (${errors.join(' | ')})`);
  await ctx.close();
}

// 4. a page of reels: posters, then the reels at the first tap
{
  const { ctx, p, errors } = await open(PHONE, '/esettanulmanyok/prof-enzo/', true), at = 'phone prof-enzo';
  await toY(p, '.rv'); await p.waitForTimeout(1800);
  let rs = (await reels(p)).filter(r => r.seen);
  check(rs.length > 0 && rs.every(r => r.paused && !r.on), `${at}: the reels on screen wait on their posters (${rs.length})`);
  check(await refused(p) > 0, `${at}: the stub refused the reels`);
  const pt = await safePoint(p);
  if (pt) await p.touchscreen.tap(pt.x, pt.y);
  await p.waitForTimeout(1800);
  rs = (await reels(p)).filter(r => r.seen);
  check(rs.length > 0 && rs.every(r => !r.paused && r.on), `${at}: they play from the first tap (${rs.filter(r => !r.paused).length}/${rs.length})`);
  check(!errors.length, `${at}: no script errors (${errors.join(' | ')})`);
  await ctx.close();
}

// 5. reduced motion, as before: the still and the Play button, nothing starts
{
  const { ctx, p, errors } = await open({ ...PHONE, reducedMotion: 'reduce' }, '/', true), at = 'phone /, reduced motion';
  const [o] = await films(p), rs = await reels(p);
  check(o.paused && o.pausedCls && !o.waiting && o.toggle === 'visible' && /Lejátszás/.test(o.toggleText), `${at}: the still and the Play button as before (${o.cls}, ${o.toggleText})`);
  check(rs.every(r => !r.src), `${at}: no reel loads`);
  check(!errors.length, `${at}: no script errors (${errors.join(' | ')})`);
  await ctx.close();
}

// 6. no Low Power Mode, as before: the film starts by itself and never waits
for (const [opts, at] of [[PHONE, 'phone / (no Low Power Mode)'], [DESK, 'computer / (no Low Power Mode)']]) {
  const { ctx, p, errors } = await open(opts, '/', false);
  const [o] = await films(p);
  check(!o.paused && o.t > 0.2 && o.playing && !o.waiting && o.vOpacity === '1', `${at}: plays by itself (paused ${o.paused}, t ${o.t.toFixed(2)}, ${o.cls})`);
  check(!errors.length, `${at}: no script errors (${errors.join(' | ')})`);
  await ctx.close();
}

await b.close();
console.log(`lowpower: ${passed} passed, ${failed.length} failed`);
process.exit(failed.length ? 1 : 0);
