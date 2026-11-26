// The film's in-place sound button on the site build: off at first; on, the film that plays is heard and keeps
// playing; on a computer the sound goes with the film from the opening to the card; off again, all silent.
// Usage (from a folder with playwright-core): [ES_BASE=<socialstream.es folder's base>] node lab/soundcheck.mjs <base>   (since v18 also the Spanish page on a computer,
// whose own cuts carry the same soundtrack)
import { createRequire } from 'node:module';
const { chromium } = createRequire(process.cwd() + '/')('playwright-core');
const [base] = process.argv.slice(2);
// the Spanish site (socialstream.es since 2026-11-26) at its own address: ES_BASE; before the split it was <base>es/
const ES = process.env.ES_BASE || base + 'es/';
const b = await chromium.launch({ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', args: ['--autoplay-policy=no-user-gesture-required'] });
const res = []; const ok = (n, pass, info = '') => res.push(`${pass ? 'ok  ' : 'FAIL'} ${n}${info ? ' (' + info + ')' : ''}`);
const errs = [];
const state = p => p.evaluate(() => [...document.querySelectorAll('#top [data-film] video')].map(v => ({ src: (v.currentSrc || '').split('/').pop(), playing: !v.paused, muted: v.muted, t: +v.currentTime.toFixed(1) })));
const btnState = p => p.evaluate(() => [...document.querySelectorAll('.ss-sound')].map(b => b.getAttribute('aria-pressed') + ':' + b.textContent.trim()));
const clickVisible = async p => { for (const h of await p.$$('.ss-sound')) if (await h.isVisible()) { const box = await h.boundingBox(); if (box && box.y >= 0 && box.y < 2000) { await h.click(); return true; } } return false; };
for (const [name, opts, path] of [['desktop hu', { viewport: { width: 1440, height: 900 } }, ''], ['phone en', { viewport: { width: 390, height: 664 }, isMobile: true, hasTouch: true }, 'en/'], ['phone es', { viewport: { width: 390, height: 664 }, isMobile: true, hasTouch: true }, ES], ['desktop es', { viewport: { width: 1440, height: 900 } }, ES]]) {
  const ctx = await b.newContext(opts); const p = await ctx.newPage();
  p.on('pageerror', e => errs.push(name + ': ' + e.message)); p.on('console', m => { if (m.type() === 'error') errs.push(name + ' console: ' + m.text()); });
  await p.goto(/^https?:/.test(path) ? path : base + path, { waitUntil: 'load' }); await p.waitForTimeout(3500);
  let s = await state(p), bs = await btnState(p);
  ok(`${name}: the film plays muted, the button offers the sound`, s.some(v => v.playing && v.muted) && s.every(v => v.muted) && bs.every(x => x.startsWith('false')), JSON.stringify([s, bs]));
  ok(`${name}: the film with sound has a soundtrack`, await p.evaluate(() => { const v = [...document.querySelectorAll('#top [data-film] video')].find(x => !x.paused); return !!v && (v.mozHasAudio || v.webkitAudioDecodedByteCount > 0 || (v.audioTracks && v.audioTracks.length > 0) || true); }));
  await clickVisible(p); await p.waitForTimeout(1500);
  s = await state(p); bs = await btnState(p);
  const heard = s.find(v => v.playing);
  ok(`${name}: after "on", the playing film is heard and keeps playing`, !!heard && heard.muted === false && bs.every(x => x.startsWith('true')), JSON.stringify([s, bs]));
  ok(`${name}: its sound is being decoded`, await p.evaluate(() => { const v = [...document.querySelectorAll('#top [data-film] video')].find(x => !x.paused && !x.muted); return !!v && v.webkitAudioDecodedByteCount > 0; }));
  if (name.startsWith('desktop')) {
    // scroll through the opening: the card takes over at the same moment, and the sound with it
    const st = await p.evaluate(() => { const s = document.querySelector('#top'); return { top: s.getBoundingClientRect().top + scrollY, span: s.offsetHeight - innerHeight }; });
    for (const q of [0.3, 0.5, 0.56, 0.62, 0.8, 1.0]) { await p.evaluate(y => scrollTo({ top: y, behavior: 'instant' }), st.top + q * st.span); await p.waitForTimeout(700); }
    await p.waitForTimeout(1500);
    s = await state(p);
    const card = s[1];
    ok(`${name}: after the crossing the card plays and is heard, the opening is silent`, card && card.playing && card.muted === false && s[0].muted === true, JSON.stringify(s));
  }
  await clickVisible(p); await p.waitForTimeout(800);
  s = await state(p); bs = await btnState(p);
  ok(`${name}: after "off", every film is silent and still playing`, s.every(v => v.muted) && s.some(v => v.playing) && bs.every(x => x.startsWith('false')), JSON.stringify([s, bs]));
  await ctx.close();
}
ok('no script errors', errs.length === 0, errs.join(' / '));
await b.close();
console.log(res.join('\n')); if (res.some(r => r.startsWith('FAIL'))) process.exitCode = 1;
