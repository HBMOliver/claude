// node phones.mjs <url> <outdir> <tiny|se|a360|i15|max|land|ipad|ipadl|desk> [perf]   (run from a folder with playwright-core)
// Walks the page top to bottom in half-screen steps and, at each stop, records text cut off at
// the screen edge, text rendered under 11.5px, tap targets under 44px or covered by something else,
// and inputs under 16px (iOS zooms the page when one is focused). Screenshots every stop and
// writes a contact sheet. "perf" instead loads on a throttled phone (4x CPU, slow 4G) and
// measures LCP, CLS, long tasks, the film's first frame and frame times during touch scrolling.
import { createRequire } from 'node:module';
import fs from 'node:fs';
const { chromium } = createRequire(process.cwd() + '/')('playwright-core');
const [url, out, prof, mode] = process.argv.slice(2);
const IOS = 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.5 Mobile/15E148 Safari/604.1';
const AND = 'Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Mobile Safari/537.36';
const m = (w, h, d, ua) => ({ viewport: { width: w, height: h }, deviceScaleFactor: d, isMobile: true, hasTouch: true, userAgent: ua });
// heights are what Safari / Chrome leave for the page with their bars showing
const P = {
  tiny: m(320, 568, 2, AND), se: m(375, 547, 2, IOS), a360: m(360, 740, 3, AND), i15: m(393, 659, 3, IOS),
  max: m(430, 739, 3, IOS), land: m(750, 340, 3, IOS),
  ipad: { viewport: { width: 820, height: 1106 }, deviceScaleFactor: 2, hasTouch: true },
  ipadl: { viewport: { width: 1180, height: 746 }, deviceScaleFactor: 2, hasTouch: true },
  desk: { viewport: { width: 1440, height: 900 } },
};
fs.mkdirSync(out, { recursive: true });
const b = await chromium.launch({ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' });
const ctx = await b.newContext(P[prof]);
const page = await ctx.newPage();
const errs = [], failed = [];
page.on('pageerror', e => errs.push('pageerror: ' + e.message));
page.on('console', c => { if (c.type() === 'error') errs.push(c.text()); });
page.on('requestfailed', r => failed.push(r.url().split('/').pop() + ' ' + (r.failure() || {}).errorText));
await page.addInitScript(() => {
  window.__m = { lcp: 0, lcpEl: '', cls: 0, lt: [], playing: 0 };
  const po = (type, f) => { try { new PerformanceObserver(l => l.getEntries().forEach(f)).observe({ type, buffered: true }); } catch (e) {} };
  po('largest-contentful-paint', e => { __m.lcp = Math.round(e.startTime); __m.lcpEl = e.element ? e.element.tagName + (e.element.id ? '#' + e.element.id : '') + ' ' + (e.url || '').split('/').pop() : ''; });
  po('layout-shift', e => { if (!e.hadRecentInput) __m.cls += e.value; });
  po('longtask', e => __m.lt.push([Math.round(e.startTime), Math.round(e.duration)]));
  document.addEventListener('playing', e => { if (!__m.playing) __m.playing = Math.round(performance.now()); }, true);
});

if (mode === 'perf') {
  const cdp = await ctx.newCDPSession(page);
  await cdp.send('Emulation.setCPUThrottlingRate', { rate: 4 });
  await cdp.send('Network.enable');
  await cdp.send('Network.emulateNetworkConditions', { offline: false, latency: 150, downloadThroughput: 1.6 * 1024 * 1024 / 8, uploadThroughput: 750 * 1024 / 8 });
  const t0 = Date.now();
  await page.goto(url, { waitUntil: 'load', timeout: 120000 });
  const loadMs = Date.now() - t0;
  await page.waitForTimeout(6000);
  const load = await page.evaluate(() => {
    const res = performance.getEntriesByType('resource'); const by = {};
    res.forEach(r => { const k = r.initiatorType; by[k] = (by[k] || 0) + (r.transferSize || r.encodedBodySize || 0); });
    Object.keys(by).forEach(k => by[k] = Math.round(by[k] / 1024) + 'KB');
    return { lcp: __m.lcp, lcpEl: __m.lcpEl, cls: +__m.cls.toFixed(3), playing: __m.playing, longTasks: __m.lt.length, longMs: __m.lt.reduce((s, x) => s + x[1], 0), worst: Math.max(0, ...__m.lt.map(x => x[1])), bytes: by };
  });
  await cdp.send('Network.emulateNetworkConditions', { offline: false, latency: 0, downloadThroughput: -1, uploadThroughput: -1 });
  const { width: W, height: H } = P[prof].viewport;
  await page.evaluate(() => { window.__fr = []; window.__on = true; window.__m.lt = []; let last = performance.now(); const f = t => { __fr.push(t - last); last = t; if (__on) requestAnimationFrame(f); }; requestAnimationFrame(f); });
  const touch = !!P[prof].hasTouch;
  const total = await page.evaluate(() => document.documentElement.scrollHeight - innerHeight);
  const reps = Math.min(40, Math.ceil(total / (H * 0.7)));
  await cdp.send('Input.synthesizeScrollGesture', { x: Math.round(W / 2), y: Math.round(H * 0.75), yDistance: -Math.round(H * 0.7), speed: 1400, gestureSourceType: touch ? 'touch' : 'mouse', repeatCount: reps, repeatDelayMs: 120 });
  const fr = await page.evaluate(() => { __on = false; return { fr: __fr.slice(2), lt: __m.lt }; });
  const s = fr.fr.slice().sort((a, b) => a - b), q = p => +(s[Math.floor(p * (s.length - 1))] || 0).toFixed(1);
  const scroll = { frames: s.length, median: q(0.5), p95: q(0.95), over33: +(100 * s.filter(x => x > 33.4).length / s.length).toFixed(1) + '%', over50: s.filter(x => x > 50).length, longTasks: fr.lt.length, longMs: fr.lt.reduce((a, x) => a + x[1], 0), reached: await page.evaluate(() => Math.round(100 * scrollY / (document.documentElement.scrollHeight - innerHeight)) + '%') };
  const r = { prof, loadMs, load, scroll, errs, failed };
  fs.writeFileSync(`${out}/perf-${prof}.json`, JSON.stringify(r, null, 1));
  console.log(JSON.stringify(r));
  await b.close(); process.exit(0);
}

await page.goto(url, { waitUntil: 'load' });
await page.waitForTimeout(2500);

function inspect() {
  const W = innerWidth, H = innerHeight;
  const o = { cut: [], tiny: [], taps: [], inputs: [], doc: document.documentElement.scrollWidth - W };
  const vis = el => el.checkVisibility ? el.checkVisibility({ opacityProperty: true, visibilityProperty: true }) : true;
  const inView = r => r.width > 0 && r.height > 0 && r.bottom > 0 && r.top < H && r.right > 0 && r.left < W;
  const d = el => { let s = el.tagName.toLowerCase(); if (el.id) s += '#' + el.id; const c = [...el.classList].slice(0, 2).join('.'); if (c) s += '.' + c; const t = (el.getAttribute('aria-label') || el.textContent || '').trim().replace(/\s+/g, ' ').slice(0, 28); return s + (t ? ' "' + t + '"' : ''); };
  const op = el => { let v = 1; for (let a = el; a && a.nodeType === 1; a = a.parentElement) { v *= +getComputedStyle(a).opacity; if (v < 0.05) return 0; } return v; };
  const clipped = el => { for (let a = el.parentElement; a && a !== document.body; a = a.parentElement) { if (getComputedStyle(a).overflowX !== 'visible') { const r = a.getBoundingClientRect(); if (r.left >= -1 && r.right <= W + 1) return true; } } return false; };
  const scale = el => { const r = el.getBoundingClientRect(); return el.offsetWidth ? r.width / el.offsetWidth : 1; };
  const tw = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT); let n; const sT = new Set(), sC = new Set();
  while ((n = tw.nextNode())) {
    if (!n.nodeValue.trim()) continue;
    const el = n.parentElement; if (!el || !vis(el) || el.closest('script,style,noscript')) continue;
    const eb = el.getBoundingClientRect(); if (eb.width <= 2 || eb.height <= 2) continue; // screen-reader-only text
    const rg = document.createRange(); rg.selectNodeContents(n);
    const rs = [...rg.getClientRects()].filter(inView); if (!rs.length || op(el) < 0.3) continue;
    const k = d(el), px = parseFloat(getComputedStyle(el).fontSize) * scale(el);
    if (px < 11.5 && !sT.has(k)) { sT.add(k); o.tiny.push([k, +px.toFixed(1)]); }
    if (rs.some(r => r.right > W + 1 || r.left < -1) && !clipped(el) && !sC.has(k)) { sC.add(k); o.cut.push([k, Math.round(Math.min(...rs.map(r => r.left))), Math.round(Math.max(...rs.map(r => r.right)))]); }
  }
  for (const el of document.querySelectorAll('a[href],button,input,select,textarea,label,[role=button],[role=tab],[role=slider],[role=checkbox],[role=radio],[tabindex]:not([tabindex="-1"]),summary')) {
    if (!vis(el) || el.disabled) continue;
    if (el.tagName === 'INPUT' && /checkbox|radio/.test(el.type) && el.closest('label')) continue; // the label is the target
    if (el.tagName === 'LABEL' && !el.querySelector('input[type=checkbox],input[type=radio]')) continue;
    const eb = el.getBoundingClientRect(); if (eb.width <= 2 || eb.height <= 2) continue;
    const s = getComputedStyle(el); if (s.pointerEvents === 'none') continue;
    const r = el.getBoundingClientRect(); if (!inView(r) || op(el) < 0.3) continue;
    const x = Math.min(W - 1, Math.max(0, r.left + r.width / 2)), y = Math.min(H - 1, Math.max(0, r.top + r.height / 2));
    const top = document.elementFromPoint(x, y);
    const cov = top && !(el === top || el.contains(top) || top.contains(el) || (el.tagName === 'INPUT' && top.tagName === 'LABEL' && top.contains(el)));
    if (r.width < 44 || r.height < 44 || cov) o.taps.push([d(el), Math.round(r.width), Math.round(r.height), s.display === 'inline' ? 'inline' : '', cov ? 'under ' + d(top) : '']);
    if (/^(INPUT|TEXTAREA|SELECT)$/.test(el.tagName) && parseFloat(s.fontSize) < 16) o.inputs.push([d(el), s.fontSize]);
  }
  return o;
}

const total = await page.evaluate(() => document.documentElement.scrollHeight - innerHeight);
const H = P[prof].viewport.height;
const stops = []; for (let y = 0; y < total; y += Math.round(H * 0.5)) stops.push(y); stops.push(total);
const agg = { cut: {}, tiny: {}, taps: {}, inputs: {} }; let docMax = 0; const shots = []; let last = -1;
for (const y of stops) {
  await page.evaluate(y => scrollTo({ top: y, behavior: 'instant' }), y);
  await page.waitForTimeout(750);
  const at = await page.evaluate(() => Math.round(scrollY));
  if (at === last) continue; last = at;
  const r = await page.evaluate(inspect);
  docMax = Math.max(docMax, r.doc);
  for (const k of ['cut', 'tiny', 'taps', 'inputs']) for (const row of r[k]) { const key = row.slice(0, k === 'taps' ? 5 : 1).join(' | '); (agg[k][key] = agg[k][key] || { row, at: [] }).at.push(Math.round(100 * at / Math.max(1, total))); }
  const f = `${out}/${String(shots.length).padStart(2, '0')}.jpg`;
  await page.screenshot({ path: f, type: 'jpeg', quality: 55 }); shots.push([f, Math.round(100 * at / Math.max(1, total))]);
}
const flat = k => Object.values(agg[k]).map(v => [...v.row, '@' + v.at.slice(0, 4).join(',') + (v.at.length > 4 ? '…' : '') + '%']);
const res = { prof, screens: (total / H + 1).toFixed(1), docOverflow: docMax, cut: flat('cut'), tiny: flat('tiny'), taps: flat('taps'), inputs: flat('inputs'), errs, failed };
fs.writeFileSync(`${out}/audit-${prof}.json`, JSON.stringify(res, null, 1));
// contact sheet
const { width: W } = P[prof].viewport; const tw = Math.min(200, Math.round(W / 2)), th = Math.round(tw * H / W);
const cols = Math.max(4, Math.floor(1400 / (tw + 8)));
const html = `<body style="margin:0;background:#222;font:11px sans-serif;color:#ccc;display:grid;grid-template-columns:repeat(${cols},${tw}px);gap:8px;padding:8px">` +
  shots.map(([f, p]) => `<figure style="margin:0"><img src="data:image/jpeg;base64,${fs.readFileSync(f).toString('base64')}" style="width:${tw}px;height:${th}px;display:block"><figcaption>${p}%</figcaption></figure>`).join('') + '</body>';
const sp = await (await b.newContext({ viewport: { width: cols * (tw + 8) + 8, height: 400 } })).newPage();
await sp.setContent(html); await sp.waitForTimeout(300);
await sp.screenshot({ path: `${out}/sheet-${prof}.jpg`, type: 'jpeg', quality: 70, fullPage: true });
console.log(JSON.stringify(res));
await b.close();
