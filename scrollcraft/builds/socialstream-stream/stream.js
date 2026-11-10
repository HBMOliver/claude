/* The stream: 10 000 cards drawn in one WebGL call, on a canvas that sits between the section
   grounds and the text. A "formation" says where every card is: in a figure's own box (a grid,
   a disc, a block of 81), or drifting in the background at its own depth. The page mixes one
   formation into the next from the scroll position; this file only knows how to draw two
   formations and the mix between them, and how to lay the formations out.

   One card is 9:16. A formation is a Float32Array of N * 4: x, y, scale, alpha.
     x, y    0..1 inside the formation's box (the figure's rect, or the viewport for the background)
     scale   times the formation's card size; NEGATIVE marks a background card, which lives in
             the viewport, drifts with the scroll at its own depth and is drawn soft when large
     alpha   0..1, plus 2 for an accent card */
(function () {
  'use strict';
  var N = 10000, ASPECT = 16 / 9;

  function rng(seed) {
    return function () { seed |= 0; seed = seed + 0x6D2B79F5 | 0; var t = Math.imul(seed ^ seed >>> 15, 1 | seed); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; };
  }

  var VERT = `#version 300 es
precision highp float;
layout(location=0) in vec2 aQuad;
layout(location=1) in vec4 aSeed;
layout(location=2) in vec2 aTile;
layout(location=3) in vec4 aA;
layout(location=4) in vec4 aB;
uniform vec2 uRes;
uniform vec4 uView;
uniform vec4 uA0, uA1, uA2, uA3, uB0, uB1, uB2, uB3;
uniform float uMix, uTime, uPhase, uFlow, uFade;
uniform vec4 uStag;
uniform vec3 uPtr;
out vec2 vLocal; out vec2 vHalf; out vec2 vTexHalf; out float vAlpha; out float vRound; out float vTex; out vec2 vUV; out float vAcc; out float vBlur;

void eval(vec4 f, vec4 p0, vec4 p1, vec4 p2, vec4 p3, out vec2 pos, out float w, out float al, out float rot, out float acc, out float bgf) {
  bgf = step(f.z, 0.0);
  float sc = abs(f.z);
  acc = step(1.5, f.w);
  float a = f.w - 2.0 * acc;
  float z = aSeed.w;
  vec2 n = f.xy;
  // a figure card: in the figure's box, optionally flowing through it or wobbling in place
  vec2 fl = p2.xy;
  float flowing = step(0.00001, abs(fl.x) + abs(fl.y));
  vec2 nf = mix(n, fract(n + fl * uFlow * (0.6 + 0.8 * aSeed.x)), flowing);
  float ef = mix(1.0, smoothstep(0.0, 0.06, nf.x) * smoothstep(1.0, 0.94, nf.x) * smoothstep(0.0, 0.06, nf.y) * smoothstep(1.0, 0.94, nf.y), flowing);
  float wm = p2.w;
  if (wm > 0.5 && wm < 1.5) {
    vec2 c = nf - 0.5; float ang = uTime * 0.045 * (1.25 - length(c) * 1.7);
    float cs = cos(ang), sn = sin(ang); nf = 0.5 + vec2(c.x * cs - c.y * sn, c.x * sn + c.y * cs);
  } else if (wm > 1.5) {
    nf += vec2(sin(uTime * (0.5 + aSeed.x) + aSeed.y * 6.2832), cos(uTime * (0.4 + aSeed.y) + aSeed.z * 6.2832)) * 0.014;
  }
  vec2 pf = p0.xy + nf * p0.zw;
  // a background card: in the viewport, moving with the scroll by its depth, with a slow current
  float sp = 0.16 + 0.62 * z;
  vec2 nb = vec2(n.x, fract(n.y - uPhase * sp + uTime * 0.006 * (0.4 + z)));
  nb.x += sin(nb.y * 6.2832 * (0.6 + aSeed.x) + aSeed.y * 6.2832) * 0.011 * (0.4 + z);
  vec2 pb = uView.xy + nb * uView.zw;
  float eb = smoothstep(0.0, 0.05, nb.y) * smoothstep(1.0, 0.95, nb.y);
  pos = mix(pf, pb, bgf);
  w = mix(p1.x, p3.z, bgf) * sc;
  al = mix(p3.x * ef, p3.y * eb, bgf) * a;
  rot = (1.0 - bgf) * p2.z * (aSeed.y - 0.5) * 6.2832;
}

void main() {
  vec2 pa, pb; float wa, wb, aa, ab, ra, rb, ca, cb, ga, gb;
  eval(aA, uA0, uA1, uA2, uA3, pa, wa, aa, ra, ca, ga);
  eval(aB, uB0, uB1, uB2, uB3, pb, wb, ab, rb, cb, gb);
  // each card leaves on its own beat: at random, or keyed to where it sits in A or lands in B
  float key = aSeed.x;
  if (uStag.y > 0.5 && uStag.y < 1.5) key = clamp(1.0 - aA.y, 0.0, 1.0) * 0.8 + aSeed.x * 0.2;
  else if (uStag.y > 1.5 && uStag.y < 2.5) key = clamp(aB.y, 0.0, 1.0) * 0.8 + aSeed.x * 0.2;
  else if (uStag.y > 2.5 && uStag.y < 3.5) key = clamp(length(aB.xy - 0.5) * 1.5, 0.0, 1.0) * 0.8 + aSeed.x * 0.2;
  else if (uStag.y > 3.5) key = clamp(length((aA.xy - 0.5) * vec2(1.0, 0.6)) * 1.9, 0.0, 1.0) * 0.75 + aSeed.x * 0.25;
  float dur = uStag.x;
  float m = clamp((uMix - key * (1.0 - dur)) / dur, 0.0, 1.0);
  float e = m * m * m * (m * (m * 6.0 - 15.0) + 10.0);
  float hop = step(0.5, e);
  vec2 pos = mix(mix(pa, pb, e), mix(pa, pb, hop), uFade);
  float arc = sin(3.14159 * e) * (1.0 - uFade);
  pos += vec2(sin(aSeed.y * 6.2832 + e * 3.0 + uTime * 0.3), cos(aSeed.z * 6.2832 + e * 2.0 + uTime * 0.2)) * arc * uStag.z * (0.35 + aSeed.x);
  pos.y += arc * uStag.w;
  float w = mix(wa, wb, e);
  float ea = ab < aa ? smoothstep(0.0, 0.42, e) : smoothstep(0.3, 1.0, e);
  float al = mix(aa, ab, ea) * mix(1.0, abs(1.0 - 2.0 * e), uFade);
  float rot = mix(ra, rb, e);
  float asp = mix(uA1.y, uB1.y, e);
  float tex = mix(uA1.w, uB1.w, smoothstep(0.35, 1.0, e));
  float over = mix(uA3.w, uB3.w, e);
  float bgm = mix(ga, gb, e);
  // the cursor parts the stream; a card that is a piece of the film stays put
  vec2 d = pos - uPtr.xy; float r2 = dot(d, d);
  pos += d * inversesqrt(r2 + 9.0) * uPtr.z * (1.0 - tex) * mix(0.35, 1.0, bgm) * exp(-r2 / 26000.0);
  float blur = bgm * max(0.0, w - 15.0) * 0.3;
  vec2 th = vec2(w, w * asp) * 0.5;
  vec2 hf = th + over;
  vec2 q = aQuad * 2.0 * (hf + 1.0 + blur * 2.0);
  float cs = cos(rot), sn = sin(rot);
  vec2 p = pos + vec2(q.x * cs - q.y * sn, q.x * sn + q.y * cs);
  gl_Position = al < 0.004 ? vec4(2.0, 2.0, 0.0, 1.0) : vec4(p.x / uRes.x * 2.0 - 1.0, 1.0 - p.y / uRes.y * 2.0, 0.0, 1.0);
  vLocal = q; vHalf = hf; vTexHalf = th;
  vAlpha = al / (1.0 + blur * 0.16);
  vRound = mix(uA1.z, uB1.z, e) * w;
  vTex = tex; vUV = aTile; vAcc = mix(ca, cb, e); vBlur = blur;
}`;

  var FRAG = `#version 300 es
precision highp float;
in vec2 vLocal; in vec2 vHalf; in vec2 vTexHalf; in float vAlpha; in float vRound; in float vTex; in vec2 vUV; in float vAcc; in float vBlur;
uniform sampler2D uVideo;
uniform vec2 uTileUV; uniform float uDpr; uniform vec2 uRes;
uniform vec3 uInk[6]; uniform vec3 uAccC[6]; uniform float uBandTop[6]; uniform int uBandN;
out vec4 o;
void main() {
  float r = min(vRound, min(vHalf.x, vHalf.y));
  vec2 q = abs(vLocal) - (vHalf - r);
  float d = length(max(q, 0.0)) + min(max(q.x, q.y), 0.0) - r;
  float soft = 0.5 / uDpr + vBlur;
  float cov = clamp(0.5 - d / (2.0 * soft), 0.0, 1.0);
  cov = mix(cov, cov * cov * (3.0 - 2.0 * cov), step(0.01, vBlur));
  if (cov < 0.003) discard;
  // the card takes the ink of the field it is over, so it flips exactly on a section's edge
  float y = uRes.y - gl_FragCoord.y / uDpr;
  vec3 ink = uInk[0]; vec3 acc = uAccC[0];
  for (int i = 1; i < 6; i++) { if (i < uBandN && y >= uBandTop[i]) { ink = uInk[i]; acc = uAccC[i]; } }
  vec3 col = mix(ink, acc, vAcc);
  if (vTex > 0.002) {
    vec2 uvl = vLocal / vTexHalf * 0.5 + 0.5;
    col = mix(col, texture(uVideo, clamp(vUV + uvl * uTileUV, 0.0, 1.0)).rgb, vTex);
  }
  float a = vAlpha * cov;
  o = vec4(col * a, a);
}`;

  function create(canvas) {
    var gl = canvas.getContext('webgl2', { alpha: true, antialias: false, premultipliedAlpha: true, depth: false, stencil: false, powerPreference: 'high-performance' });
    if (!gl) return null;
    function shader(type, src) {
      var s = gl.createShader(type); gl.shaderSource(s, src); gl.compileShader(s);
      if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) { console.error('stream shader: ' + gl.getShaderInfoLog(s)); return null; }
      return s;
    }
    var vs = shader(gl.VERTEX_SHADER, VERT), fs = shader(gl.FRAGMENT_SHADER, FRAG);
    if (!vs || !fs) return null;
    var prog = gl.createProgram(); gl.attachShader(prog, vs); gl.attachShader(prog, fs); gl.linkProgram(prog);
    if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) { console.error('stream link: ' + gl.getProgramInfoLog(prog)); return null; }
    gl.useProgram(prog);
    var U = {};
    ['uRes', 'uView', 'uA0', 'uA1', 'uA2', 'uA3', 'uB0', 'uB1', 'uB2', 'uB3', 'uMix', 'uTime', 'uPhase', 'uFlow', 'uFade', 'uStag', 'uPtr', 'uVideo', 'uTileUV', 'uDpr', 'uInk[0]', 'uAccC[0]', 'uBandTop[0]', 'uBandN']
      .forEach(function (n) { U[n] = gl.getUniformLocation(prog, n); });

    // every card's own dice: three randoms and a depth, the same in every formation
    var R = rng(20221), seeds = new Float32Array(N * 4);
    for (var i = 0; i < N * 4; i++) seeds[i] = R();

    function buffer(data, usage) { var b = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, b); gl.bufferData(gl.ARRAY_BUFFER, data, usage || gl.STATIC_DRAW); return b; }
    var vao = gl.createVertexArray(); gl.bindVertexArray(vao);
    function attr(loc, buf, size, div) { gl.bindBuffer(gl.ARRAY_BUFFER, buf); gl.enableVertexAttribArray(loc); gl.vertexAttribPointer(loc, size, gl.FLOAT, false, 0, 0); gl.vertexAttribDivisor(loc, div); }
    attr(0, buffer(new Float32Array([-0.5, -0.5, 0.5, -0.5, -0.5, 0.5, 0.5, 0.5])), 2, 0);
    attr(1, buffer(seeds), 4, 1);
    var tileData = new Float32Array(N * 2), tileBuf = buffer(tileData, gl.DYNAMIC_DRAW); attr(2, tileBuf, 2, 1);
    gl.enableVertexAttribArray(3); gl.vertexAttribDivisor(3, 1);
    gl.enableVertexAttribArray(4); gl.vertexAttribDivisor(4, 1);

    var tex = gl.createTexture();
    gl.activeTexture(gl.TEXTURE0); gl.bindTexture(gl.TEXTURE_2D, tex);
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, 1, 1, 0, gl.RGBA, gl.UNSIGNED_BYTE, new Uint8Array([0, 0, 0, 255]));
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
    gl.uniform1i(U.uVideo, 0);
    gl.disable(gl.DEPTH_TEST); gl.enable(gl.BLEND); gl.blendFunc(gl.ONE, gl.ONE_MINUS_SRC_ALPHA);

    var forms = {}, css = { w: 1, h: 1, dpr: 1 }, lost = false, bInk = new Float32Array(18), bAcc = new Float32Array(18), bTop = new Float32Array(6);
    canvas.addEventListener('webglcontextlost', function (e) { e.preventDefault(); lost = true; canvas.style.visibility = 'hidden'; });

    function setForm(side, p, r) {
      var size = typeof p.size === 'function' ? p.size(r) : (p.size || 4);
      var asp = typeof p.aspect === 'function' ? p.aspect(r) : (p.aspect || ASPECT);
      gl.uniform4f(U['u' + side + '0'], r.x, r.y, r.w, r.h);
      gl.uniform4f(U['u' + side + '1'], size, asp, p.round == null ? 0.2 : p.round, p.tex || 0);
      gl.uniform4f(U['u' + side + '2'], p.flow ? p.flow[0] : 0, p.flow ? p.flow[1] : 0, p.rot || 0, p.warp || 0);
      gl.uniform4f(U['u' + side + '3'], p.alpha == null ? 1 : p.alpha, p.bgAlpha == null ? 1 : p.bgAlpha, p.bgSize || 4.4, typeof p.over === 'function' ? p.over(r) : (p.over || 0));
    }

    return {
      N: N, seeds: seeds, lost: function () { return lost; },
      // register a formation: its card positions and how its figure cards are drawn
      form: function (name, data, params) {
        var f = forms[name];
        if (f) { gl.bindBuffer(gl.ARRAY_BUFFER, f.buf); gl.bufferData(gl.ARRAY_BUFFER, data, gl.STATIC_DRAW); f.p = params || f.p; }
        else forms[name] = { buf: buffer(data), p: params || {} };
      },
      has: function (name) { return !!forms[name]; },
      // which piece of the film each card shows while it is a tile
      tiles: function (cols, rows) {
        for (var i = 0; i < N; i++) { var k = Math.min(i, cols * rows - 1); tileData[i * 2] = (k % cols) / cols; tileData[i * 2 + 1] = Math.floor(k / cols) / rows; }
        gl.bindBuffer(gl.ARRAY_BUFFER, tileBuf); gl.bufferSubData(gl.ARRAY_BUFFER, 0, tileData);
        gl.uniform2f(U.uTileUV, 1 / cols, 1 / rows);
      },
      // the playing frame (or the poster) as the tiles' picture
      source: function (el) {
        try { gl.bindTexture(gl.TEXTURE_2D, tex); gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGB, gl.RGB, gl.UNSIGNED_BYTE, el); return true; } catch (e) { return false; }
      },
      size: function (w, h, dpr) {
        css.w = w; css.h = h; css.dpr = dpr;
        var W = Math.round(w * dpr), H = Math.round(h * dpr);
        if (canvas.width !== W || canvas.height !== H) { canvas.width = W; canvas.height = H; }
      },
      clear: function () { if (lost) return; gl.viewport(0, 0, canvas.width, canvas.height); gl.clearColor(0, 0, 0, 0); gl.clear(gl.COLOR_BUFFER_BIT); },
      // s: { A, B, mix, rectA, rectB, view, time, phase, flow, fade, stag: [dur, mode, transit, sag], ptr: [x, y, k], bands: [{ top, ink: [r,g,b], acc: [r,g,b] }] }
      draw: function (s) {
        if (lost) return;
        var fa = forms[s.A], fb = forms[s.B];
        gl.viewport(0, 0, canvas.width, canvas.height); gl.clearColor(0, 0, 0, 0); gl.clear(gl.COLOR_BUFFER_BIT);
        if (!fa || !fb) return;
        gl.bindVertexArray(vao);
        gl.bindBuffer(gl.ARRAY_BUFFER, fa.buf); gl.vertexAttribPointer(3, 4, gl.FLOAT, false, 0, 0);
        gl.bindBuffer(gl.ARRAY_BUFFER, fb.buf); gl.vertexAttribPointer(4, 4, gl.FLOAT, false, 0, 0);
        setForm('A', fa.p, s.rectA); setForm('B', fb.p, s.rectB);
        gl.uniform2f(U.uRes, css.w, css.h); gl.uniform1f(U.uDpr, css.dpr);
        gl.uniform4f(U.uView, s.view.x, s.view.y, s.view.w, s.view.h);
        gl.uniform1f(U.uMix, s.mix); gl.uniform1f(U.uTime, s.time); gl.uniform1f(U.uPhase, s.phase); gl.uniform1f(U.uFlow, s.flow); gl.uniform1f(U.uFade, s.fade ? 1 : 0);
        gl.uniform4f(U.uStag, s.stag[0], s.stag[1], s.stag[2], s.stag[3]);
        gl.uniform3f(U.uPtr, s.ptr[0], s.ptr[1], s.ptr[2]);
        var n = Math.min(6, s.bands.length), ink = bInk, acc = bAcc, top = bTop;
        for (var i = 0; i < n; i++) { ink.set(s.bands[i].ink, i * 3); acc.set(s.bands[i].acc, i * 3); top[i] = s.bands[i].top; }
        gl.uniform3fv(U['uInk[0]'], ink); gl.uniform3fv(U['uAccC[0]'], acc); gl.uniform1fv(U['uBandTop[0]'], top); gl.uniform1i(U.uBandN, Math.max(1, n));
        gl.drawArraysInstanced(gl.TRIANGLE_STRIP, 0, 4, N);
      }
    };
  }

  /* ---------------- formations ---------------- */
  // a card index order that is the same everywhere, so "the first 81 cards" are always the same 81
  var order = (function () { var o = new Uint16Array(N), r = rng(99), i, j, t; for (i = 0; i < N; i++) o[i] = i; for (i = N - 1; i > 0; i--) { j = Math.floor(r() * (i + 1)); t = o[i]; o[i] = o[j]; o[j] = t; } return o; })();

  // a background card: its depth decides its size class, and it keeps that in every formation
  function back(out, S, i, x, on, amul) {
    var z = S[i * 4 + 3], o = i * 4, sc, al;
    if (z < 0.7) { sc = 0.7 + z * 0.64; al = 0.16 + z * 0.2; }
    else if (z < 0.94) { sc = 1.8 + (z - 0.7) * 9.6; al = 0.34 + (z - 0.7) * 0.9; }
    else { sc = 6.4 + (z - 0.94) * 160; al = 0.3 - (z - 0.94) * 1.6; }
    out[o] = x; out[o + 1] = S[i * 4 + 1]; out[o + 2] = -sc;
    out[o + 3] = on ? al * amul + (S[i * 4 + 2] < 0.12 ? 2 : 0) : 0;
  }

  var make = {
    order: order,
    // the background alone. shape: 'edges' keeps the middle clear, 'river' runs down one side, 'wide' is everywhere
    field: function (S, o) {
      var out = new Float32Array(N * 4), r = rng(o.seed || 5), i, x, a, b;
      for (i = 0; i < N; i++) {
        a = r(); b = r();
        if (o.shape === 'river') x = (o.cx == null ? 0.72 : o.cx) + (a + b - 1) * (o.spread || 0.3) + (a < 0.06 ? (b - 0.5) * 0.9 : 0);
        else if (o.shape === 'edges') x = 0.5 + (a < 0.5 ? -1 : 1) * ((o.gap == null ? 0.2 : o.gap) + Math.pow(b, 0.8) * (0.56 - (o.gap == null ? 0.2 : o.gap)));
        else x = a;
        back(out, S, i, x, S[i * 4] < o.frac, o.alpha == null ? 1 : o.alpha);
      }
      return out;
    },
    // the film: one card per tile of the frame
    tiles: function (S, cols, rows) {
      var out = new Float32Array(N * 4), i, o;
      for (i = 0; i < N; i++) {
        o = i * 4;
        if (i < cols * rows) { out[o] = (i % cols + 0.5) / cols; out[o + 1] = (Math.floor(i / cols) + 0.5) / rows; out[o + 2] = 1; out[o + 3] = 1; }
        else { out[o] = S[i * 4]; out[o + 1] = 1.1; out[o + 2] = 1; out[o + 3] = 0; }
      }
      return out;
    },
    // every card in a grid; lit: a Set of indices drawn bright and larger while the rest go dim
    grid: function (S, cols, rows, o) {
      o = o || {};
      var out = new Float32Array(N * 4), i, k;
      for (i = 0; i < N; i++) {
        k = i * 4; out[k] = (i % cols + 0.5) / cols; out[k + 1] = (Math.floor(i / cols) + 0.5) / rows;
        if (o.lit) { out[k + 2] = o.lit.has(i) ? 2.5 : 1; out[k + 3] = o.lit.has(i) ? 1 : (o.dim == null ? 0.1 : o.dim); }
        else { out[k + 2] = 1; out[k + 3] = o.alpha == null ? 0.6 : o.alpha; }
      }
      return out;
    },
    // forty spread evenly but not regularly over the grid
    pick: function (cols, rows, nx, ny, seed) {
      var s = new Set(), r = rng(seed || 40), ix, iy, c, w;
      for (iy = 0; iy < ny; iy++) for (ix = 0; ix < nx; ix++) {
        c = Math.floor((ix + 0.12 + r() * 0.76) * cols / nx); w = Math.floor((iy + 0.12 + r() * 0.76) * rows / ny);
        s.add(w * cols + c);
      }
      return s;
    },
    // a sunflower disc round a hole in the middle, the inner rings brightest
    disc: function (S, hole) {
      var out = new Float32Array(N * 4), i0 = N * hole * hole / (0.25 - hole * hole), i, k, rr, th;
      for (i = 0; i < N; i++) {
        k = i * 4; rr = 0.5 * Math.sqrt((i + i0) / (N + i0)); th = i * 2.39996323;
        out[k] = 0.5 + rr * Math.cos(th); out[k + 1] = 0.5 + rr * Math.sin(th);
        out[k + 2] = 1; out[k + 3] = 0.95 - 0.6 * (rr - hole) / (0.5 - hole);
      }
      return out;
    },
    // a share of the cards thrown anywhere in the box (drawn tumbling), or set on straight lines
    scatter: function (S, frac, seed) {
      var out = new Float32Array(N * 4), r = rng(seed || 11), i, k, a, b;
      for (i = 0; i < N; i++) { k = i * 4; a = r(); b = r(); out[k] = 0.04 + a * 0.92; out[k + 1] = 0.04 + b * 0.92; out[k + 2] = 0.7 + S[i * 4 + 3] * 1.1; out[k + 3] = S[i * 4] < frac ? 0.8 : 0; }
      return out;
    },
    lines: function (S, frac, count, seed) {
      var out = new Float32Array(N * 4), r = rng(seed || 12), i, k, a, b;
      for (i = 0; i < N; i++) { k = i * 4; a = r(); b = r(); out[k] = a; out[k + 1] = (Math.floor(b * count) + 0.5) / count; out[k + 2] = 0.7 + S[i * 4 + 3] * 1.1; out[k + 3] = S[i * 4] < frac ? 0.85 : 0; }
      return out;
    },
    // blocks of a counted number of cards, the rest of the stream quiet at the page edges.
    // groups: [{ n, cols, x, y, px, py, accent, scale }] with x, y the centre of the first card
    blocks: function (S, groups, bgFrac, bgAlpha) {
      var out = make.field(S, { shape: 'edges', gap: 0.36, frac: bgFrac == null ? 0.1 : bgFrac, alpha: bgAlpha == null ? 0.7 : bgAlpha, seed: 31 }), at = 0;
      groups.forEach(function (g) {
        for (var j = 0; j < g.n; j++, at++) {
          var i = order[at], k = i * 4;
          out[k] = g.x + (j % g.cols) * g.px; out[k + 1] = g.y + Math.floor(j / g.cols) * g.py;
          out[k + 2] = g.scale || 1; out[k + 3] = (g.alpha == null ? 1 : g.alpha) + (g.accent ? 2 : 0);
        }
      });
      return out;
    },
    // points sampled from a drawing (the wordmark): [[x, y, accent], ...]
    points: function (S, pts) {
      var out = new Float32Array(N * 4), i, k, p;
      for (i = 0; i < N; i++) {
        k = order[i] * 4; p = pts[i];
        if (p) { out[k] = p[0]; out[k + 1] = p[1]; out[k + 2] = 1; out[k + 3] = 0.95 + (p[2] ? 2 : 0); }
        else { out[k] = S[k]; out[k + 1] = 1.4; out[k + 2] = 1; out[k + 3] = 0; }
      }
      return out;
    }
  };

  window.Stream = { N: N, create: create, make: make, rng: rng };
})();
