'use strict';
// Reusable scene templates for Profenzo videos. Canvas scenes register in SCENES, DOM scenes in DOMS.
// Every scene gets (ctx, localTime, duration, sceneParams, globalTime).

// ---------------------------------------------------------------- shared backgrounds
function bgFill(c, s, t) {
  const kind = (s && s.bg) || 'studio';
  if (kind === 'studio') { drawStudio(c, t, s.warm || .4, 14, .32); return; }
  if (kind === 'studioClear') { drawStudio(c, t, s.warm || .3, 0, 0); return; }
  const G = { night: ['#060c22', '#0d1a40'], warm: ['#2a1a0c', '#120a05'], cool: ['#0a1c2e', '#04101c'], lab: ['#e9f1f7', '#c9d8e6'], day: ['#ffe3b3', '#f6b97a'], paper: ['#f6efe3', '#e6dccb'], mint: ['#103a33', '#071c19'], citrus: ['#ffe9a8', '#ffb547'] }[kind] || ['#060c22', '#0d1a40'];
  const g = c.createLinearGradient(0, 0, 0, H); g.addColorStop(0, G[0]); g.addColorStop(1, G[1]); c.fillStyle = g; c.fillRect(0, 0, W, H);
  const r = c.createRadialGradient(540, 520, 30, 540, 520, 800); const light = ['lab', 'day', 'paper', 'citrus'].includes(kind);
  r.addColorStop(0, light ? 'rgba(255,255,255,.55)' : 'rgba(255,190,110,.16)'); r.addColorStop(1, 'rgba(0,0,0,0)'); c.fillStyle = r; c.fillRect(0, 0, W, H);
}
const isLightBg = s => ['lab', 'day', 'paper', 'citrus'].includes(s && s.bg);

// ---------------------------------------------------------------- DOM template helpers
const sceneDom = document.getElementById('sceneDom');
const DOMS = {};
function el(tag, css, html) { const e = document.createElement(tag); if (css) e.style.cssText = css; if (html !== undefined) e.innerHTML = html; return e; }
const colorOf = (c, light) => c === 'amber' ? (light ? '#b45309' : 'var(--amber)') : c === 'green' ? (light ? '#047857' : 'var(--green)') : c === 'red' ? 'var(--alarm)' : c === 'dark' ? '#14203f' : (light ? '#14203f' : '#fff');
function popIn(node, k, from = .6) { const s = k < 0 ? 0 : k < .12 ? lerp(from, 1.08, k / .12) : k < .22 ? lerp(1.08, 1, (k - .12) / .1) : 1; node.style.opacity = clamp(k / .08, 0, 1); return s; }

// cards: list / grid / vs ----------------------------------------------------------
DOMS.cards = {
  bg: bgFill,
  build(s) {
    const root = el('div', 'position:absolute;left:0;top:0;width:1080px;height:1920px;');
    const light = isLightBg(s);
    if (s.title) root.appendChild(el('div', `position:absolute;left:60px;right:60px;top:252px;text-align:center;font:800 48px MontserratVF;letter-spacing:-.5px;text-transform:uppercase;color:${light ? '#14203f' : '#fff'};opacity:0;`, s.title)).className = 'ttl';
    const glass = light ? 'background:rgba(255,255,255,.75);border:2px solid rgba(20,32,63,.12);color:#14203f;box-shadow:0 18px 40px rgba(20,32,63,.18);'
                        : 'background:rgba(14,22,52,.62);border:1.5px solid rgba(255,255,255,.18);color:#fff;box-shadow:0 18px 40px rgba(0,0,0,.35);backdrop-filter:blur(10px);';
    const items = s.items || [];
    if (s.layout === 'grid') {
      items.forEach((it, i) => { const x = 90 + (i % 2) * 460, y = (s.title ? 330 : 270) + Math.floor(i / 2) * 248;
        const n = el('div', `position:absolute;left:${x}px;top:${y}px;width:440px;height:228px;border-radius:36px;${glass}display:flex;flex-direction:column;align-items:center;justify-content:center;gap:10px;opacity:0;text-align:center;`,
          `<div style="font:86px 'Noto Color Emoji'">${it.e || ''}</div><div style="font:800 36px MontserratVF;text-transform:uppercase;color:${colorOf(it.c || (light ? 'dark' : 'white'), light)};padding:0 16px;line-height:1.1">${it.t}</div>`);
        n.className = 'it'; root.appendChild(n); });
    } else if (s.layout === 'vs') {
      items.slice(0, 2).forEach((it, i) => { const x = 60 + i * 520;
        const bul = (it.list || []).map(b => `<div class="b" style="opacity:0;margin-top:14px;font:600 30px Inter;line-height:1.25;display:flex;gap:10px;"><span style="color:${colorOf(it.c || 'amber', light)}">●</span><span>${b}</span></div>`).join('');
        const n = el('div', `position:absolute;left:${x}px;top:${s.title ? 330 : 270}px;width:440px;min-height:460px;border-radius:40px;${glass}padding:30px 28px;box-sizing:border-box;opacity:0;`,
          `<div style="text-align:center;font:118px 'Noto Color Emoji'">${it.e || ''}</div><div style="text-align:center;font:800 42px MontserratVF;text-transform:uppercase;margin-top:8px;color:${colorOf(it.c || 'amber', light)}">${it.t}</div>${bul}`);
        n.className = 'it'; root.appendChild(n); });
      const vs = el('div', `position:absolute;left:490px;top:${(s.title ? 330 : 270) + 200}px;width:100px;height:100px;border-radius:50%;background:var(--amber);color:#1a1305;font:900 40px MontserratVF;display:flex;align-items:center;justify-content:center;box-shadow:0 10px 30px rgba(0,0,0,.4);opacity:0;`, 'VS');
      vs.className = 'vs'; root.appendChild(vs);
    } else { // list
      items.forEach((it, i) => { const y = (s.title ? 330 : 270) + i * 124;
        const n = el('div', `position:absolute;left:80px;top:${y}px;width:920px;height:108px;border-radius:30px;${glass}display:flex;align-items:center;gap:22px;padding:0 30px;box-sizing:border-box;opacity:0;`,
          `<div style="font:60px 'Noto Color Emoji';width:76px;text-align:center">${it.e || '✓'}</div><div style="font:700 37px MontserratVF;line-height:1.12;color:${colorOf(it.c || (light ? 'dark' : 'white'), light)}">${it.t}</div>`);
        n.className = 'it'; root.appendChild(n); });
    }
    return root;
  },
  update(root, tl, dur, s) {
    const ttl = root.querySelector('.ttl'); if (ttl) { const k = tl; const sc = popIn(ttl, k, .8); ttl.style.transform = `scale(${sc})`; }
    const st = s.stagger || Math.min(.55, (dur * .6) / Math.max(1, (s.items || []).length));
    // itemsAt: per-item entry times (scene-relative, from "@word" anchors in timeline.json); else an even stagger
    root.querySelectorAll('.it').forEach((n, i) => { const k = tl - (s.itemsAt && s.itemsAt[i] !== undefined ? s.itemsAt[i] : (s.title ? .25 : .1) + i * st); const sc = popIn(n, k);
      n.style.transform = s.layout === 'list' ? `translateX(${(1 - clamp(k / .2, 0, 1)) * -60}px) scale(${sc})` : `scale(${sc})`;
      n.querySelectorAll('.b').forEach((b, j) => { b.style.opacity = clamp((k - .3 - j * (s.bulletStagger || .25)) / .15, 0, 1); }); });
    const vs = root.querySelector('.vs'); if (vs) { const k = tl - .5 - st; vs.style.transform = `scale(${popIn(vs, k)}) rotate(${(1 - clamp(k / .3, 0, 1)) * -40}deg)`; }
    const sh = s.dim ? clamp(tl / .3, 0, 1) * s.dim : 0; root.style.filter = sh ? `brightness(${1 - sh})` : '';
  }
};

// bigtext: kinetic typography --------------------------------------------------------
DOMS.bigtext = {
  bg: bgFill,
  build(s) {
    const root = el('div', `position:absolute;left:50px;width:980px;top:${s.y || 300}px;display:flex;flex-direction:column;align-items:center;gap:8px;`);
    (s.lines || []).forEach(([txt, c, size]) => { const n = el('div', `position:relative;font:900 ${size || 118}px MontserratVF;letter-spacing:-2px;text-transform:uppercase;line-height:1;white-space:nowrap;opacity:0;text-align:center;`,
      `<span style="position:absolute;left:0;top:0;width:100%;color:transparent;-webkit-text-stroke:18px rgba(6,8,22,.9)">${txt}</span><span style="position:relative;color:${colorOf(c)};text-shadow:0 10px 30px rgba(0,0,0,.5)">${txt}</span>`);
      n.className = 'ln'; root.appendChild(n); });
    return root;
  },
  update(root, tl, dur, s) {
    root.querySelectorAll('.ln').forEach((n, i) => { const k = tl - i * (s.stagger || .28); const sc = popIn(n, k, .3);
      const shake = s.shake && k > 0 && k < .35 ? Math.sin(k * 90) * 10 * (1 - k / .35) : 0;
      let w = n.scrollWidth; const f = w > 980 ? 980 / w : 1; n.style.transform = `translateX(${shake}px) scale(${sc * f})`; });
  }
};

// label: product label close-up with a magnified keyword -----------------------------
DOMS.label = {
  bg: bgFill,
  build(s) {
    const root = el('div', 'position:absolute;left:0;top:0;width:1080px;height:1920px;');
    const card = el('div', `position:absolute;left:150px;top:262px;width:780px;height:560px;border-radius:26px;background:linear-gradient(170deg,#fffdf6,#f1e9d8);box-shadow:0 40px 90px rgba(0,0,0,.45);padding:44px 52px;box-sizing:border-box;transform:rotate(-3deg);opacity:0;overflow:hidden;`);
    const bar = w => `<div style="height:16px;width:${w}%;border-radius:8px;background:rgba(20,32,63,.13);margin:12px 0;"></div>`;
    let html = `<div style="display:flex;align-items:center;gap:16px;"><div style="font:54px 'Noto Color Emoji'">${s.icon || '🌿'}</div><div><div style="font:800 40px MontserratVF;color:#14203f;letter-spacing:-.5px">${s.product || 'Termékcímke'}</div><div style="font:600 22px Inter;color:#6b7690;letter-spacing:2px">${s.kicker || 'TERMÉKINFORMÁCIÓ'}</div></div></div><div style="height:2px;background:rgba(20,32,63,.12);margin:26px 0 18px"></div>`;
    (s.sections || ['Felhasználás', 'Figyelmeztetés']).forEach((sec, i) => { const hi = (s.highlight || []).includes(i);
      html += `<div class="sec" data-hi="${hi ? 1 : 0}" style="position:relative;margin-top:16px;padding:8px 14px;border-radius:12px;"><div style="font:800 27px MontserratVF;color:${hi ? '#b45309' : '#14203f'};text-transform:uppercase;letter-spacing:.5px">${sec}</div>${bar(92)}${bar(78)}</div>`; });
    card.innerHTML = html; card.className = 'card'; root.appendChild(card);
    const lens = el('div', 'position:absolute;width:300px;height:300px;border-radius:50%;border:12px solid #2a2f3a;box-shadow:0 20px 50px rgba(0,0,0,.45), inset 0 0 0 3px rgba(255,255,255,.6);background:radial-gradient(circle at 35% 30%,rgba(255,255,255,.35),rgba(255,255,255,.05) 60%);opacity:0;pointer-events:none;');
    lens.className = 'lens'; root.appendChild(lens);
    const handle = el('div', 'position:absolute;width:40px;height:150px;border-radius:20px;background:#2a2f3a;opacity:0;transform-origin:50% 0;');
    handle.className = 'handle'; root.appendChild(handle);
    return root;
  },
  update(root, tl, dur, s) {
    const card = root.querySelector('.card'); const k = tl; card.style.opacity = clamp(k / .15, 0, 1);
    card.style.transform = `rotate(-3deg) translateY(${(1 - easeOut(k / .35)) * 80}px) scale(${1 + .05 * (tl / dur)})`;
    const his = [...root.querySelectorAll('.sec')].filter(n => n.dataset.hi === '1');
    his.forEach((n, i) => { const a = clamp((tl - .5 - i * .4) / .25, 0, 1); n.style.background = `rgba(255,181,71,${.38 * a})`; n.style.boxShadow = a ? `0 0 0 3px rgba(255,181,71,${.7 * a})` : 'none'; });
    const lens = root.querySelector('.lens'), hd = root.querySelector('.handle');
    if (his.length) { const tgt = his[0].getBoundingClientRect(), st = document.getElementById('stage').getBoundingClientRect();
      const cx = tgt.left - st.left + tgt.width * .62, cy = tgt.top - st.top + tgt.height * .5, a = clamp((tl - .45) / .3, 0, 1);
      lens.style.opacity = a; hd.style.opacity = a; const bob = 6 * Math.sin(tl * 3);
      lens.style.left = (cx - 150) + 'px'; lens.style.top = (cy - 150 + bob) + 'px'; lens.style.transform = `scale(${.7 + .3 * easeOut(a)})`;
      hd.style.left = (cx + 88) + 'px'; hd.style.top = (cy + 100 + bob) + 'px'; hd.style.transform = 'rotate(-40deg)'; }
  }
};

// kbsearch: profenzo.com knowledge base search UI ------------------------------------
DOMS.kbsearch = {
  bg: bgFill,
  build(s) {
    const root = el('div', 'position:absolute;left:0;top:0;width:1080px;height:1920px;');
    const win = el('div', 'position:absolute;left:70px;top:258px;width:940px;height:600px;border-radius:34px;overflow:hidden;background:#0f1836;border:1.5px solid rgba(255,255,255,.16);box-shadow:0 40px 90px rgba(0,0,0,.5);opacity:0;');
    win.className = 'win';
    win.innerHTML = `<div style="height:64px;background:rgba(255,255,255,.06);display:flex;align-items:center;gap:12px;padding:0 24px;"><span style="width:16px;height:16px;border-radius:50%;background:#ff5f57"></span><span style="width:16px;height:16px;border-radius:50%;background:#febc2e"></span><span style="width:16px;height:16px;border-radius:50%;background:#28c840"></span>
      <div style="margin-left:18px;flex:1;height:38px;border-radius:19px;background:rgba(255,255,255,.08);color:#cfe0ff;font:600 22px Inter;display:flex;align-items:center;padding-left:18px">🔒 profenzo.com/hu/knowledge</div></div>
      <div style="padding:30px 36px;"><div style="font:800 40px MontserratVF;color:#fff">Prof. Enzo <span style="color:var(--green)">Tudástár</span></div>
      <div style="margin-top:20px;height:78px;border-radius:39px;background:#fff;display:flex;align-items:center;padding:0 28px;gap:14px;"><span style="font:32px 'Noto Color Emoji'">🔎</span><span class="q" style="font:700 30px Inter;color:#14203f"></span><span class="car" style="width:3px;height:36px;background:#2b5cff"></span></div>
      <div class="res" style="margin-top:22px;display:flex;flex-direction:column;gap:14px;"></div></div>`;
    const res = win.querySelector('.res');
    (s.results || []).forEach(([e, t, tag]) => { const r = el('div', 'display:flex;align-items:center;gap:18px;padding:16px 22px;border-radius:22px;background:rgba(255,255,255,.07);opacity:0;',
      `<span style="font:44px 'Noto Color Emoji'">${e}</span><span style="flex:1;font:700 28px Inter;color:#fff;line-height:1.2">${t}</span>${tag ? `<span style="font:800 20px MontserratVF;color:#0B1530;background:var(--green);padding:8px 14px;border-radius:14px">${tag}</span>` : ''}`);
      r.className = 'r'; res.appendChild(r); });
    root.appendChild(win); return root;
  },
  update(root, tl, dur, s) {
    const win = root.querySelector('.win'); win.style.opacity = clamp(tl / .15, 0, 1); win.style.transform = `translateY(${(1 - easeOut(tl / .35)) * 60}px)`;
    const q = s.query || '', n = Math.min(q.length, Math.floor(Math.max(0, tl - .3) / .045)); root.querySelector('.q').textContent = q.slice(0, n);
    root.querySelector('.car').style.opacity = Math.floor(tl * 2.4) % 2 ? .2 : 1;
    const t0 = .35 + q.length * .045 + .2;
    root.querySelectorAll('.r').forEach((r, i) => { const k = tl - t0 - i * .3; r.style.opacity = clamp(k / .15, 0, 1); r.style.transform = `translateY(${(1 - easeOut(k / .25)) * 20}px)`; });
  }
};

// ---------------------------------------------------------------- canvas templates
function bottle(c, x, y, s, a, glowOn, labelCol) {
  c.save(); c.translate(x, y); c.scale(s, s); c.globalAlpha = a;
  if (glowOn) { glow(c, 'rgba(255,190,90,.9)', 40); }
  let g = c.createLinearGradient(-40, 0, 40, 0); g.addColorStop(0, '#5a2c0c'); g.addColorStop(.5, '#a85a1c'); g.addColorStop(1, '#4a2208');
  c.fillStyle = g; rr(c, -40, -150, 80, 150, 16); c.fill(); noGlow(c);
  c.fillStyle = '#f4f1ea'; rr(c, -26, -196, 52, 46, 8); c.fill(); c.fillStyle = '#d9d4c8'; c.fillRect(-26, -160, 52, 6);
  c.fillStyle = labelCol || '#f6efe3'; rr(c, -32, -118, 64, 70, 8); c.fill();
  c.fillStyle = 'rgba(40,60,40,.55)'; c.beginPath(); c.ellipse(0, -92, 9, 14, .5, 0, 7); c.fill(); c.fillRect(-18, -70, 36, 5); c.fillRect(-14, -60, 28, 4);
  c.fillStyle = 'rgba(255,255,255,.22)'; rr(c, -30, -146, 10, 120, 5); c.fill();
  c.restore();
}
SCENES.shelf = function (c, tl, dur, s, t) {
  bgFill(c, { bg: 'studio', warm: .6 }, t);
  const n = s.count || 7, mode = s.mode || 'count', active = s.active || [1, 4];
  c.fillStyle = 'rgba(0,0,0,.35)'; c.fillRect(0, 0, W, H);
  c.fillStyle = '#3b2616'; rr(c, 70, 700, 940, 34, 10); c.fill(); c.fillStyle = 'rgba(0,0,0,.35)'; c.fillRect(70, 734, 940, 20);
  const xs = i => 140 + i * (800 / Math.max(1, n - 1));
  for (let i = 0; i < n; i++) {
    let a = 1, sc = 1, dy = 0, gl = false;
    if (mode === 'count') { const k = tl - i * (Math.min(.22, dur * .7 / n)); a = clamp(k / .1, 0, 1); sc = popScale(k); }
    if (mode === 'museum' || mode === 'two') { const on = active.includes(i); a = on ? 1 : .38; if (on) { gl = true; dy = mode === 'two' ? -Math.abs(Math.sin((tl + i) * 5)) * 26 : 0; } }
    if (a > 0) bottle(c, xs(i), 700 + dy, 1.05 * sc, a, gl);
  }
  if (mode === 'count' && s.counter) { const vals = s.counter, idx = Math.min(vals.length - 1, Math.floor(tl / (dur / vals.length)));
    c.save(); c.font = '900 170px MontserratVF'; c.textAlign = 'center'; c.fillStyle = AMBER; glow(c, AMBER, 30); c.fillText(String(vals[idx]), 540, 380); noGlow(c); c.restore(); }
  if (mode === 'museum') { // velvet rope + plaque + spotlights
    for (const i of active) { const x = xs(i); const g = c.createLinearGradient(x, 180, x, 700); g.addColorStop(0, 'rgba(255,230,170,.0)'); g.addColorStop(1, 'rgba(255,230,170,.28)'); c.fillStyle = g; c.beginPath(); c.moveTo(x - 30, 180); c.lineTo(x + 30, 180); c.lineTo(x + 110, 720); c.lineTo(x - 110, 720); c.closePath(); c.fill(); }
    c.strokeStyle = '#8b1a2b'; c.lineWidth = 12; c.beginPath(); c.moveTo(90, 800); c.quadraticCurveTo(540, 880, 990, 800); c.stroke();
    c.fillStyle = '#c9a34e'; for (const x of [90, 990]) { rr(c, x - 10, 780, 20, 140, 8); c.fill(); }
    c.save(); c.fillStyle = '#c9a34e'; rr(c, 380, 300, 320, 74, 14); c.fill(); c.fillStyle = '#2a1a08'; c.font = '800 34px MontserratVF'; c.textAlign = 'center'; c.fillText('KIÁLLÍTÁS', 540, 350); c.restore();
  }
};
function popScale(k) { return k < 0 ? 0 : k < .1 ? lerp(.5, 1.12, k / .1) : k < .2 ? lerp(1.12, 1, (k - .1) / .1) : 1; }

SCENES.stop = function (c, tl, dur, s, t) {
  bgFill(c, { bg: s.bg || 'citrus' }, t);
  const k = tl, sc = popScale(k) * (1 + .02 * Math.sin(tl * 8)), shake = k < .4 ? Math.sin(k * 80) * 14 * (1 - k / .4) : 0;
  c.save(); c.translate(540 + shake, 520); c.scale(sc, sc); c.rotate(-.05);
  c.fillStyle = 'rgba(0,0,0,.25)'; poly(c, 8, 300, 14, 20); c.fill();
  c.fillStyle = '#e23b3b'; poly(c, 8, 300, 0, 0); c.fill(); c.strokeStyle = '#fff'; c.lineWidth = 22; poly(c, 8, 268, 0, 0); c.stroke();
  c.fillStyle = '#fff'; c.font = '900 150px MontserratVF'; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText(s.text || 'ÁLLJ!', 0, 8); c.restore(); c.textBaseline = 'alphabetic';
};
function poly(c, n, r, ox, oy) { c.beginPath(); for (let i = 0; i < n; i++) { const a = Math.PI / n + i * 2 * Math.PI / n; const x = ox + r * Math.cos(a), y = oy + r * Math.sin(a); i ? c.lineTo(x, y) : c.moveTo(x, y); } c.closePath(); }

SCENES.sun = function (c, tl, dur, s, t) {
  let g = c.createLinearGradient(0, 0, 0, H); g.addColorStop(0, '#5ec8ff'); g.addColorStop(.42, '#bfe9ff'); g.addColorStop(.43, '#2a8fd6'); g.addColorStop(.55, '#1f6fb0'); g.addColorStop(.56, '#f3d9a4'); g.addColorStop(1, '#e8c286'); c.fillStyle = g; c.fillRect(0, 0, W, H);
  const sx = 760, sy = 330; c.save(); c.translate(sx, sy); c.rotate(tl * .25);
  for (let i = 0; i < 16; i++) { c.rotate(Math.PI / 8); c.fillStyle = 'rgba(255,214,90,.55)'; c.beginPath(); c.moveTo(130, -14); c.lineTo(250 + 20 * Math.sin(tl * 4 + i), 0); c.lineTo(130, 14); c.closePath(); c.fill(); }
  c.restore(); g = c.createRadialGradient(sx, sy, 10, sx, sy, 140); g.addColorStop(0, '#fff7c2'); g.addColorStop(1, '#ffc23d'); c.fillStyle = g; glow(c, '#ffd23d', 60); c.beginPath(); c.arc(sx, sy, 115, 0, 7); c.fill(); noGlow(c);
  if (s.mode === 'uv') { const a = clamp(tl / .4, 0, 1); c.strokeStyle = `rgba(150,80,255,${.85 * a})`; c.lineWidth = 7; c.setLineDash([22, 16]); c.lineDashOffset = -tl * 120;
    for (let i = 0; i < 5; i++) { c.beginPath(); c.moveTo(sx - 60 - i * 20, sy + 80 + i * 10); c.lineTo(260 + i * 70, 760); c.stroke(); } c.setLineDash([]);
    c.fillStyle = '#e7b48f'; rr(c, 120, 720, 560, 120, 60); c.fill(); c.fillStyle = 'rgba(255,255,255,.25)'; rr(c, 140, 735, 520, 30, 15); c.fill();
    c.save(); c.globalAlpha = a; c.font = "800 38px MontserratVF"; c.fillStyle = '#5b21b6'; c.textAlign = 'center'; c.fillText('UV', 300, 600); c.restore(); }
  else { c.font = '150px "Noto Color Emoji"'; c.textAlign = 'center'; const b = Math.sin(tl * 3) * 10; c.fillText('😎', 330, 600 + b); c.font = '110px "Noto Color Emoji"'; c.fillText('🍋', 820, 720 - b); c.fillText('⛱️', 180, 820); }
};

SCENES.house = function (c, tl, dur, s, t) {
  bgFill(c, { bg: s.bg || 'night' }, t);
  const layers = s.layers || ['TÁPLÁLKOZÁS', 'MOZGÁS', 'PIHENÉS', 'STRESSZKEZELÉS', 'TUDATOS OTTHON', 'ÖNGONDOSKODÁS'];
  const cols = ['#2e7d5b', '#3a8f6a', '#4a9c7a', '#d38b2c', '#e2a243', '#f0c060', '#9BE7B4'];
  const inv = s.mode === 'upside'; const wob = inv ? Math.sin(tl * 4) * .06 : 0;
  c.save(); c.translate(540, 790); c.rotate(wob);
  c.fillStyle = 'rgba(255,255,255,.18)'; c.fillRect(-470, 2, 940, 6);
  const n = layers.length, h = 82, per = (dur * (s.buildFrac || .75)) / n;
  for (let i = 0; i < n; i++) {
    const k = tl - (s.layerAt ? s.layerAt[i] : i * per); if (k < 0 && !inv) continue;
    const drop = inv ? 0 : (1 - easeOut(clamp(k / .3, 0, 1))) * -380;
    const w = 900 - i * (inv ? -0 : 110) * (s.pyramid === false ? 0 : 1);
    const idx = inv ? n - 1 - i : i; const ww = inv ? 900 - idx * 110 : w;
    const y = inv ? -(i + 1) * h : -(i + 1) * h + drop;
    c.globalAlpha = inv ? 1 : clamp(k / .1, 0, 1);
    c.fillStyle = cols[idx % cols.length]; rr(c, -ww / 2, y, ww, h - 8, 16); c.fill();
    c.fillStyle = 'rgba(255,255,255,.18)'; rr(c, -ww / 2 + 8, y + 6, ww - 16, 16, 8); c.fill();
    c.fillStyle = '#fff'; c.font = '800 34px MontserratVF'; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText(layers[idx], 0, y + (h - 8) / 2 + 2);
  }
  c.globalAlpha = 1; c.textBaseline = 'alphabetic';
  if (s.roof) { const k = tl - (s.roofAt !== undefined ? s.roofAt : n * per); if (k > 0) { const a = clamp(k / .3, 0, 1), y = -(n + 1) * h - 20; c.globalAlpha = a; c.fillStyle = '#9BE7B4'; c.beginPath(); c.moveTo(-170, y + 90); c.lineTo(0, y - 40); c.lineTo(170, y + 90); c.closePath(); c.fill();
      c.fillStyle = '#0B1530'; c.font = '800 26px MontserratVF'; c.textAlign = 'center'; c.fillText(s.roof, 0, y + 70); c.globalAlpha = 1; } }
  if (s.products) { const a = clamp((tl - (s.productsAt ?? .3)) / .3, 0, 1); c.globalAlpha = a; c.font = '84px "Noto Color Emoji"'; c.textAlign = 'center';
    c.font = '72px "Noto Color Emoji"';
    if (inv) ['🧴', '💊', '🌿'].forEach((e, i) => c.fillText(e, -150 + i * 130, 40 + Math.sin(tl * 3 + i) * 8));
    else {   // beside the narrow top of the pyramid (left), so they never cover a layer or the header: part of the routine, not the foundation
      const cx = -355, by = -(n - 1) * h - 18;
      ['🧴', '💊', '🌿'].forEach((e, i) => c.fillText(e, cx + (i - 1) * 88, by + Math.sin(tl * 3 + i) * 6));
      if (s.productsNote) { c.fillStyle = '#fff'; c.font = '700 30px Inter';
        const parts = s.productsNote.split(/\s+(?=[–-]\s)/);   // "rutin része – nem az alap" -> two lines
        parts.forEach((p, i) => c.fillText(p.trim(), cx, by + 48 + i * 36)); } }
    c.globalAlpha = 1; }
  if (s.side) { const a = clamp((tl - (s.sideAt ?? dur * .6)) / .3, 0, 1); c.globalAlpha = a; c.fillStyle = '#7FD3FF'; rr(c, 380, -n * h, 70, n * h - 8, 14); c.fill();
    c.save(); c.translate(415, -n * h / 2); c.rotate(-Math.PI / 2); c.fillStyle = '#0B1530'; c.font = '800 26px MontserratVF'; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText(s.side, 0, 0); c.restore(); c.globalAlpha = 1; }
  c.restore();
};

SCENES.field = function (c, tl, dur, s, t) {
  const lemon = s.mode === 'lemon';
  let g = c.createLinearGradient(0, 0, 0, 760); g.addColorStop(0, lemon ? '#8fd3ff' : '#ff9b6a'); g.addColorStop(1, lemon ? '#e8f7ff' : '#ffd9a0'); c.fillStyle = g; c.fillRect(0, 0, W, 760);
  c.fillStyle = lemon ? 'rgba(255,255,255,.9)' : 'rgba(255,240,200,.95)'; glow(c, '#fff3c0', 60); c.beginPath(); c.arc(lemon ? 820 : 540, lemon ? 200 : 600, lemon ? 80 : 120, 0, 7); c.fill(); noGlow(c);
  g = c.createLinearGradient(0, 600, 0, H); g.addColorStop(0, lemon ? '#5c9a3a' : '#6b4a8f'); g.addColorStop(1, lemon ? '#2f5a1e' : '#2d1b45'); c.fillStyle = g; c.fillRect(0, 600, W, H);
  const R = rng(lemon ? 31 : 29), z = 1 + .05 * (tl / dur);
  c.save(); c.translate(540, 640); c.scale(z, z); c.translate(-540, -640);
  if (!lemon) { for (let r = 0; r < 16; r++) { const k = r / 16, y = 610 + Math.pow(k, 1.8) * 1300; for (let i = -12; i <= 12; i++) { const x = 540 + i * (30 + k * 260) + Math.sin(tl * 1.5 + r) * 6 * k;
          const rad = 3 + k * 26; c.fillStyle = `hsl(${268 + R() * 18},${45 + R() * 20}%,${45 + R() * 20}%)`; c.beginPath(); c.ellipse(x, y, rad * .8, rad * 1.6, 0, 0, 7); c.fill(); } } }
  else { for (let i = 0; i < 9; i++) { const x = 60 + i * 120 + R() * 40, y = 620 + R() * 60, r = 70 + R() * 40; c.fillStyle = `hsl(${100 + R() * 25},45%,${28 + R() * 10}%)`; c.beginPath(); c.arc(x, y, r, 0, 7); c.fill();
      for (let j = 0; j < 6; j++) { c.fillStyle = '#ffd93b'; c.beginPath(); c.ellipse(x + (R() - .5) * r * 1.4, y + (R() - .5) * r * 1.2, 12, 16, R(), 0, 7); c.fill(); } } }
  c.restore();
};

SCENES.chroma = function (c, tl, dur, s, t) {
  let g = c.createLinearGradient(0, 0, 0, H); g.addColorStop(0, '#061428'); g.addColorStop(1, '#0b2440'); c.fillStyle = g; c.fillRect(0, 0, W, H);
  c.strokeStyle = 'rgba(127,211,255,.08)'; c.lineWidth = 1.5; for (let x = 80; x <= 1000; x += 46) { c.beginPath(); c.moveTo(x, 220); c.lineTo(x, 760); c.stroke(); } for (let y = 220; y <= 760; y += 46) { c.beginPath(); c.moveTo(80, y); c.lineTo(1000, y); c.stroke(); }
  const peaks = [[.08, .3], [.15, .55], [.22, .2], [.31, .9], [.38, .4], [.47, .65], [.55, .25], [.63, .8], [.72, .35], [.8, .5], [.88, .22]];
  const p = clamp(tl / (dur * .8), 0, 1), f = x => peaks.reduce((a, [px, ph]) => a + ph * Math.exp(-((x - px) ** 2) / .00018), 0);
  c.beginPath(); for (let i = 0; i <= 600 * p; i++) { const x = i / 600, X = 90 + x * 900, Y = 740 - f(x) * 460; i ? c.lineTo(X, Y) : c.moveTo(X, Y); }
  c.strokeStyle = CYAN; c.lineWidth = 5; glow(c, CYAN, 20); c.stroke(); noGlow(c);
  c.font = '700 26px Inter'; c.fillStyle = 'rgba(255,255,255,.65)'; c.textAlign = 'left'; c.fillText(s.caption || 'GC-MS · összetétel-vizsgálat', 90, 205);
  c.font = '90px "Noto Color Emoji"'; c.textAlign = 'center'; c.fillText('🧪', 900, 200 + Math.sin(tl * 2) * 6);
};

SCENES.diffuser = function (c, tl, dur, s, t) {
  drawStudio(c, t, .9, 8, .2);
  const mode = s.mode || 'normal', x = 540, y = 760;
  if (mode === 'field') { const a = clamp(tl / (dur * .7), 0, 1); c.fillStyle = `rgba(150,110,220,${.45 * a})`; c.fillRect(0, 0, W, H);
    const R = rng(41); c.font = '70px "Noto Color Emoji"'; c.textAlign = 'center'; for (let i = 0; i < 40 * a; i++) c.fillText('💜', R() * W, 200 + R() * 800); }
  if (mode === 'window') { const a = easeOut(clamp(tl / .6, 0, 1)); c.fillStyle = '#9ad7ff'; rr(c, 90, 220, 300, 460, 20); c.fill(); c.fillStyle = '#e8f6ff'; rr(c, 90 + 150 * a, 220, 150 * (1 - a) + 6, 460, 10); c.fill();
    c.strokeStyle = 'rgba(255,255,255,.85)'; c.lineWidth = 6; for (let i = 0; i < 5; i++) { const yy = 300 + i * 80, off = (tl * 300 + i * 90) % 700; c.beginPath(); c.moveTo(390 + off * .2, yy); c.bezierCurveTo(500 + off * .3, yy - 30, 600 + off * .3, yy + 30, 700 + off * .4, yy); c.stroke(); } }
  // vapor
  const R = rng(43); for (let i = 0; i < 26; i++) { const ph = R(), q = (tl * (.25 + R() * .2) + ph) % 1; const yy = y - 120 - q * 520, xx = x + Math.sin(q * 6 + ph * 9) * 60 * q, r = 30 + q * 110;
    const g = c.createRadialGradient(xx, yy, 0, xx, yy, r); g.addColorStop(0, `rgba(235,240,255,${.22 * (1 - q)})`); g.addColorStop(1, 'rgba(235,240,255,0)'); c.fillStyle = g; c.beginPath(); c.arc(xx, yy, r, 0, 7); c.fill(); }
  // device
  let g = c.createLinearGradient(x - 120, 0, x + 120, 0); g.addColorStop(0, '#6b4426'); g.addColorStop(.5, '#a0703f'); g.addColorStop(1, '#5a361c'); c.fillStyle = g; c.beginPath(); c.ellipse(x, y, 130, 40, 0, 0, 7); c.fill(); rr(c, x - 130, y - 70, 260, 70, 30); c.fill();
  g = c.createLinearGradient(x - 110, 0, x + 110, 0); g.addColorStop(0, '#e9e6df'); g.addColorStop(.5, '#ffffff'); g.addColorStop(1, '#d8d3c8'); c.fillStyle = g; c.beginPath(); c.moveTo(x - 115, y - 70); c.quadraticCurveTo(x - 90, y - 190, x, y - 200); c.quadraticCurveTo(x + 90, y - 190, x + 115, y - 70); c.closePath(); c.fill();
  c.fillStyle = '#2a2f3a'; c.beginPath(); c.ellipse(x, y - 196, 18, 7, 0, 0, 7); c.fill();
  c.fillStyle = `rgba(255,190,90,${.6 + .3 * Math.sin(tl * 3)})`; glow(c, '#ffb547', 30); c.beginPath(); c.ellipse(x, y - 30, 40, 8, 0, 0, 7); c.fill(); noGlow(c);
};

SCENES.carrier = function (c, tl, dur, s, t) {
  bgFill(c, { bg: 'warm' }, t);
  // big carrier bottle (left), small essential oil bottle (right), bowl centre
  let g = c.createLinearGradient(170, 0, 330, 0); g.addColorStop(0, 'rgba(255,255,255,.25)'); g.addColorStop(.5, 'rgba(255,255,255,.5)'); g.addColorStop(1, 'rgba(255,255,255,.2)');
  const tilt = easeOut(clamp((tl - .3) / .4, 0, 1)) * .55;
  c.save(); c.translate(250, 640); c.rotate(tilt); c.fillStyle = 'rgba(255,214,120,.65)'; rr(c, -70, -300, 140, 300, 30); c.fill(); c.fillStyle = g; rr(c, -70, -300, 140, 300, 30); c.fill(); c.fillStyle = '#e9e1cf'; rr(c, -26, -360, 52, 64, 10); c.fill();
  c.fillStyle = '#fff7e6'; rr(c, -56, -220, 112, 90, 10); c.fill(); c.fillStyle = '#14203f'; c.font = '800 18px MontserratVF'; c.textAlign = 'center'; c.fillText('HORDOZÓ-', 0, -180); c.fillText('OLAJ', 0, -156); c.restore();
  if (tilt > .45) { const q = clamp((tl - .75) / .4, 0, 1); c.strokeStyle = 'rgba(255,214,120,.85)'; c.lineWidth = 12; c.beginPath(); c.moveTo(430, 470); c.quadraticCurveTo(500, 520, 520, 520 + 160 * q); c.stroke(); }
  bottle(c, 800, 600, 1.15, 1, true);
  const dk = (tl - 1.1) % 1.4; if (tl > 1.1 && dk < .7) { const yy = 600 - 220 + 40 + dk / .7 * 260; c.fillStyle = '#ffd38a'; glow(c, '#ffb547', 18); c.beginPath(); c.ellipse(700 - dk * 150, yy, 10, 15, 0, 0, 7); c.fill(); noGlow(c); }
  c.fillStyle = 'rgba(255,255,255,.18)'; c.beginPath(); c.ellipse(540, 760, 190, 50, 0, 0, 7); c.fill(); g = c.createLinearGradient(0, 720, 0, 800); g.addColorStop(0, 'rgba(255,214,120,.75)'); g.addColorStop(1, 'rgba(200,140,40,.55)'); c.fillStyle = g; c.beginPath(); c.ellipse(540, 756, 160, 36, 0, 0, 7); c.fill();
  label(c, s.label || 'HÍGÍTÁS', 540, 300, GREEN, clamp((tl - .5) / .3, 0, 1));
};

SCENES.concentrate = function (c, tl, dur, s, t) { // many plants -> one drop
  bgFill(c, { bg: 'mint' }, t);
  const R = rng(51), p = easeIn(clamp(tl / (dur * .7), 0, 1));
  c.font = '70px "Noto Color Emoji"'; c.textAlign = 'center';
  for (let i = 0; i < 60; i++) { const x0 = 80 + R() * 920, y0 = 180 + R() * 620, x = lerp(x0, 540, p), y = lerp(y0, 520, p); c.globalAlpha = 1 - p * .9; c.fillText(['🌿', '🍃', '🌸', '🍋'][i % 4], x, y); }
  c.globalAlpha = 1; const a = clamp((p - .7) / .3, 0, 1); c.fillStyle = `rgba(255,211,138,${a})`; glow(c, '#ffb547', 40 * a); c.beginPath(); c.ellipse(540, 520, 46 * a, 70 * a, 0, 0, 7); c.fill(); noGlow(c);
  label(c, s.label || 'KONCENTRÁLT', 540, 300, AMBER, a);
};
