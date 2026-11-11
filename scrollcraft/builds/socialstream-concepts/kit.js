/* What the four concepts share. Each page has its own markup and look; this runs the parts they have in
   common: arrivals and counters, the brand film wherever it sits, the running rows (always moving, faster
   while the page is scrolled), the sentence that lights word by word, things that drift with the scroll,
   the light that follows the cursor, the things that follow or lean toward it, the menu over dark parts, and the
   audit form, which is Daylight's, word for word. */
(function () {
  'use strict';
  var $ = SS.$, $$ = SS.$$, clamp = SS.clamp, reduce = SS.reduce, esc = SS.esc;
  var root = document.documentElement;
  root.classList.add('js');
  if (SS.fine) root.classList.add('fine');
  var L = function (hu, en) { return SS.L === 'en' ? en : hu; };
  var vh = innerHeight, lastY = scrollY, boost = 0;

  /* ---------------- arrivals, once, as each thing comes into view ---------------- */
  var io = 'IntersectionObserver' in window ? new IntersectionObserver(function (es) {
    es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); if (e.target._count) e.target._count(); } });
  }, { threshold: 0.12, rootMargin: '0px 0px -4% 0px' }) : null;
  function arrive(el) { if (io && !reduce) io.observe(el); else { el.classList.add('in'); if (el._count) el._count(); } }

  /* ---------------- numbers count up the first time they are seen ---------------- */
  $$('[data-count]').forEach(function (el) {
    var to = +el.dataset.count, done = false, holder = el.closest('[data-r]') || el;
    function show(n) { el.textContent = SS.fmtN(n); }
    holder._count = function () {
      if (done) return; done = true;
      if (reduce) { show(to); return; }
      var t0 = performance.now(), dur = to > 1000 ? 1900 : 1300;
      (function step(now) { var k = clamp((now - t0) / dur, 0, 1); show(Math.round(to * (1 - Math.pow(1 - k, 3)))); if (k < 1) requestAnimationFrame(step); })(t0);
    };
    if (!reduce && io) show(0); else show(to);
    SS.onLang(function () { if (done || reduce || !io) show(to); });
  });

  /* ---------------- the brand film, wherever a page puts it ---------------- */
  var narrow = matchMedia('(max-width: 760px)');
  var PLAY = '<svg viewBox="0 0 14 14" aria-hidden="true"><path d="M3 1.5l9 5.5-9 5.5z" fill="currentColor"/></svg>';
  var PAUSE = '<svg viewBox="0 0 14 14" aria-hidden="true"><path d="M3 2h3v10H3zM8 2h3v10H8z" fill="currentColor"/></svg>';
  var films = $$('[data-film]').map(function (box) {
    var v = $('video', box), tgl = $('.toggle', box), cut = box.getAttribute('data-cut') || 'auto';
    var f = { paused: reduce || SS.saveData, seen: false, loaded: '', started: false };
    // a vertical cut where the frame stands upright, the full cut where the film is big, the small one elsewhere
    function src() {
      if (cut === 'v' || (cut === 'auto' && narrow.matches)) return 'assets/hero-v-720.mp4';
      if (box.hasAttribute('data-big')) return 'assets/hero-1080.mp4';
      return box.offsetWidth * (window.devicePixelRatio || 1) < 1300 ? 'assets/hero-540.mp4' : 'assets/hero-1080.mp4';
    }
    function load() {
      var s = src(); if (f.loaded === s) return;
      var t = f.loaded ? v.currentTime : 0; f.loaded = s; box.classList.remove('is-playing'); v.src = s; v.load();
      if (t) v.addEventListener('loadedmetadata', function () { try { v.currentTime = t; } catch (e) {} }, { once: true });
    }
    f.state = function () {
      box.classList.toggle('is-paused', f.paused);
      if (!tgl) return;
      tgl.innerHTML = (f.paused ? PLAY : PAUSE) + '<span>' + (f.paused ? L('Lejátszás', 'Play') : L('Szünet', 'Pause')) + '</span>';
      tgl.setAttribute('aria-label', f.paused ? L('Film lejátszása', 'Play the film') : L('Film megállítása', 'Pause the film'));
    };
    f.apply = function () {
      if (!f.started) { f.state(); return; }
      if (f.paused || !f.seen) v.pause();
      else { load(); var p = v.play(); if (p && p.catch) p.catch(function (e) { if (e && e.name === 'NotAllowedError') { f.paused = true; f.state(); } }); }
      f.state();
    };
    f.mq = function () { if (!f.paused) f.apply(); else f.loaded = ''; };
    v.addEventListener('playing', function () { box.classList.add('is-playing'); });
    // a frame may carry a progress line, as a story does; it follows the film
    var bar = $('.progress', box);
    if (bar) v.addEventListener('timeupdate', function () { if (v.duration) bar.style.setProperty('--pr', (v.currentTime / v.duration).toFixed(3)); });
    if (tgl) tgl.addEventListener('click', function () { f.paused = !f.paused; f.started = true; f.apply(); });
    // two changes can arrive in one batch; the last one is current
    if ('IntersectionObserver' in window) new IntersectionObserver(function (es) { f.seen = es[es.length - 1].isIntersecting; f.apply(); }, { threshold: 0.1 }).observe(box);
    else f.seen = true;
    return f;
  });
  SS.onMQ(narrow, function () { films.forEach(function (f) { f.mq(); }); });
  SS.onLang(function () { films.forEach(function (f) { f.state(); }); });
  // a media fetch holds the load event, so the film is fetched only once the page has loaded
  function startFilms() { films.forEach(function (f) { f.started = true; f.apply(); }); }
  if (document.readyState === 'complete') setTimeout(startFilms, 60); else addEventListener('load', function () { setTimeout(startFilms, 60); }, { once: true });

  /* ---------------- running rows: always moving, faster while the page is scrolled ---------------- */
  var rails = $$('[data-rail]').map(function (r) {
    var tr = $('.track', r);
    tr.innerHTML += tr.innerHTML; // doubled, so the row loops without a seam (the row is aria-hidden)
    var o = { r: r, tr: tr, dir: +r.getAttribute('data-rail') || 1, speed: +r.getAttribute('data-speed') || 40, x: 0, w: 0, on: false };
    if ('IntersectionObserver' in window) {
      // pictures in a moving row load a little before the row arrives
      new IntersectionObserver(function (es) { if (es[es.length - 1].isIntersecting) $$('img[loading="lazy"]', r).forEach(function (i) { i.loading = 'eager'; }); }, { rootMargin: '900px 0px' }).observe(r);
      new IntersectionObserver(function (es) { o.on = es[es.length - 1].isIntersecting; if (o.on) run(); }, { threshold: 0 }).observe(r);
    } else o.on = true;
    return o;
  });
  function measureRails() { rails.forEach(function (o) { o.w = o.tr.scrollWidth / 2; }); }
  var running = false, tPrev = 0;
  function run() {
    if (running || reduce || !rails.length) return;
    running = true; tPrev = performance.now();
    requestAnimationFrame(function step(now) {
      var dt = Math.min(0.05, (now - tPrev) / 1000); tPrev = now;
      var any = false;
      boost *= Math.pow(0.04, dt); // a push from the scroll that dies away within a second or so
      rails.forEach(function (o) {
        if (!o.on || !o.w) return; any = true;
        o.x -= o.dir * (o.speed + boost) * dt;
        if (o.x <= -o.w) o.x += o.w; else if (o.x > 0) o.x -= o.w;
        o.tr.style.transform = 'translate3d(' + o.x.toFixed(1) + 'px,0,0)';
      });
      if (any) requestAnimationFrame(step); else running = false;
    });
  }

  /* ---------------- the sentence that lights word by word as it is read ---------------- */
  var lits = $$('[data-lit]');
  lits.forEach(function (lit) {
    $$('[data-l]', lit).forEach(function (l) {
      l.innerHTML = l.textContent.split(/(\s+)/).map(function (t) { return !t || /^\s+$/.test(t) ? t : '<span class="w">' + esc(t) + '</span>'; }).join('');
    });
    if (reduce) $$('.w', lit).forEach(function (w) { w.classList.add('on'); });
  });
  function litTick() {
    lits.forEach(function (lit) {
      var l = $$('[data-l]', lit).filter(function (e) { return getComputedStyle(e).display !== 'none'; })[0], b = lit.getBoundingClientRect();
      if (!l || b.top > vh || b.bottom < 0) return;
      var ws = l._ws || (l._ws = $$('.w', l)), k = Math.round(clamp((vh * 0.88 - b.top) / (b.height + vh * 0.38), 0, 1) * ws.length);
      if (l._k !== k) { l._k = k; ws.forEach(function (w, i) { w.classList.toggle('on', i < k); }); }
    });
  }

  /* ---------------- things that move with the scroll: --p runs 0 to 1 as an element crosses the screen ---------------- */
  var drifts = $$('[data-drift]');
  function driftTick() {
    drifts.forEach(function (d) {
      var r = d.getBoundingClientRect(); if (r.top > vh || r.bottom < 0) return;
      var p = clamp((vh - r.top) / (vh + r.height), 0, 1).toFixed(3);
      if (d._p !== p) { d._p = p; d.style.setProperty('--p', p); }
    });
  }

  /* ---------------- a light that follows the cursor ---------------- */
  if (SS.fine && !reduce) $$('[data-glow]').forEach(function (g) {
    g.addEventListener('pointermove', function (e) { var r = g.getBoundingClientRect(); g.style.setProperty('--mx', (e.clientX - r.left).toFixed(0) + 'px'); g.style.setProperty('--my', (e.clientY - r.top).toFixed(0) + 'px'); g.classList.add('lit'); });
    g.addEventListener('pointerleave', function () { g.classList.remove('lit'); });
  });

  /* ---------------- things that follow the cursor (with a mouse or trackpad, and not with reduced motion) ----------------
     [data-follow]        leans toward the cursor by data-k of the cursor's distance from the middle of the screen
                          (a depth: below zero it moves the other way)
     [data-follow="in"]   follows the cursor inside its parent while the cursor is over the parent. data-anchor is the
                          point of it that sits under the cursor (0,0 is its top left), data-home where it rests (in
                          parts of the parent), data-snap that it starts where the cursor comes in and stays put after
     a.btn                the buttons are pulled a little toward a cursor that comes near
     Each writes --fx and --fy, and the page's CSS says what moves. One listener and one loop, which stops once all
     is still; only what is on screen is worked out. */
  var fol = [], px = 0, py = 0, has = false, folOn = false, fT = 0;
  function kick() { if (!folOn && fol.length) { folOn = true; fT = performance.now(); requestAnimationFrame(folStep); } }
  function folStep(now) {
    var dt = Math.min(0.05, (now - fT) / 1000) || 0.016, a = 1 - Math.pow(0.88, dt * 60), busy = false, W = innerWidth, H = innerHeight;
    fT = now;
    fol.forEach(function (f) {
      if (!f.vis) return;
      var tx = 0, ty = 0, el = f.el;
      if (f.m === 'lean') { if (has) { tx = (px - W / 2) * f.k; ty = (py - H / 2) * f.k; } }
      else if (f.m === 'in') {
        var pr = el.parentElement.getBoundingClientRect(), w = el.offsetWidth, h = el.offsetHeight;
        var inside = has && px >= pr.left && px <= pr.right && py >= pr.top && py <= pr.bottom;
        if (inside) { tx = px - pr.left - w * f.an[0]; ty = py - pr.top - h * f.an[1]; }
        else if (f.snap && f.set) { tx = f.x; ty = f.y; }
        else { tx = pr.width * f.home[0] - w / 2; ty = pr.height * f.home[1] - h / 2; }
        if (!f.set || (inside && !f.on && f.snap)) { f.x = tx; f.y = ty; f.set = true; }
        f.on = inside;
      } else {
        var r = el.getBoundingClientRect(), dx = px - ((r.left + r.right) / 2 - f.x), dy = py - ((r.top + r.bottom) / 2 - f.y);
        if (has && Math.abs(dx) < r.width / 2 + 36 && Math.abs(dy) < r.height / 2 + 36) { tx = clamp(dx * 0.22, -9, 9); ty = clamp(dy * 0.3, -7, 7); }
      }
      f.x += (tx - f.x) * a; f.y += (ty - f.y) * a;
      if (Math.abs(tx - f.x) > 0.15 || Math.abs(ty - f.y) > 0.15) busy = true; else { f.x = tx; f.y = ty; }
      var sx = f.x.toFixed(1), sy = f.y.toFixed(1);
      if (sx !== f.sx || sy !== f.sy) { f.sx = sx; f.sy = sy; el.style.setProperty('--fx', sx + 'px'); el.style.setProperty('--fy', sy + 'px'); }
    });
    if (busy) requestAnimationFrame(folStep); else folOn = false;
  }
  if (SS.fine && !reduce) {
    $$('[data-follow], a.btn').forEach(function (el) {
      var num = function (n, d) { return (el.getAttribute(n) || d).split(',').map(Number); }, kind = el.getAttribute('data-follow');
      fol.push({ el: el, m: kind === 'in' ? 'in' : kind !== null ? 'lean' : 'magnet', k: +(el.getAttribute('data-k') || 0.05), an: num('data-anchor', '0.5,0.5'), home: num('data-home', '0.5,0.5'), snap: el.hasAttribute('data-snap'), x: 0, y: 0, vis: true, set: false, on: false });
    });
    if ('IntersectionObserver' in window) {
      var fio = new IntersectionObserver(function (es) { es.forEach(function (e) { e.target._fs.forEach(function (f) { f.vis = e.isIntersecting; }); }); kick(); }, { rootMargin: '120px 0px' });
      fol.forEach(function (f) { var t = f.m === 'in' ? f.el.parentElement : f.el; f.vis = false; (t._fs = t._fs || []).push(f); fio.observe(t); });
    }
    addEventListener('pointermove', function (e) { if (e.pointerType === 'touch') return; px = e.clientX; py = e.clientY; has = true; kick(); }, { passive: true });
    root.addEventListener('mouseleave', function () { has = false; kick(); });
    addEventListener('blur', function () { has = false; kick(); });
    addEventListener('scroll', kick, { passive: true });
  }

  /* ---------------- the menu: a shadow once scrolled, the dark style over parts marked data-dark ---------------- */
  var nav = $('#nav'), darks = $$('[data-dark]'), was = {};
  function navTick() {
    if (!nav) return;
    var sc = scrollY > 8; if (was.sc !== sc) { was.sc = sc; nav.classList.toggle('is-scrolled', sc); }
    var nb = nav.getBoundingClientRect().bottom - 10, dark = darks.some(function (d) { var r = d.getBoundingClientRect(); return r.top <= nb && r.bottom >= nb; });
    if (was.dark !== dark) { was.dark = dark; nav.classList.toggle('on-dark', dark); }
  }

  var ticking = false;
  function frame() {
    ticking = false; vh = innerHeight;
    var y = scrollY; if (!reduce) boost = Math.min(520, boost + Math.abs(y - lastY) * 2.2); lastY = y;
    litTick(); driftTick(); navTick();
  }
  function onScroll() { if (!ticking) { ticking = true; requestAnimationFrame(frame); } run(); }
  addEventListener('scroll', onScroll, { passive: true });
  addEventListener('resize', function () { measureRails(); frame(); });
  addEventListener('load', function () { measureRails(); run(); });

  /* ---------------- the audit form (Daylight's, unchanged) ---------------- */
  var form = $('#appform'), pick = $('#pick'), sent = $('#sent'), sending = $('#sending'), chosen = [], lastBody = '';
  function renderPick() { pick.innerHTML = SS.TOPICS.map(function (c) { return '<label><input type="checkbox" value="' + c.id + '"' + (chosen.indexOf(c.id) > -1 ? ' checked' : '') + '><span>' + esc(SS.T(c)) + '</span></label>'; }).join(''); }
  pick.addEventListener('change', function (e) { var id = e.target.value, k = chosen.indexOf(id); if (e.target.checked && k < 0) chosen.push(id); else if (!e.target.checked && k > -1) chosen.splice(k, 1); });
  var ERR = {
    name: { hu: 'Írd be a neved, hogy tudjuk, kinek válaszolunk.', en: 'Enter your name so we know who to reply to.' },
    email: { hu: 'Írd be az e-mail címed, ide válaszolunk.', en: 'Enter your email. That’s where we’ll reply.' },
    brand: { hu: 'Írd be a céged vagy a márkád nevét.', en: 'Enter your company or brand name.' },
    mail: { hu: 'Ez nem tűnik e-mail címnek. Például: nev@ceg.hu', en: 'That doesn’t look like an email address. For example: name@company.com' }
  };
  function check(focus) {
    var ok = true;
    ['name', 'email', 'brand'].forEach(function (n) {
      var inp = $('#f-' + n), er = $('#e-' + n), val = inp.value.trim(), m = '';
      if (!val) m = SS.T(ERR[n]); else if (inp.type === 'email' && !SS.isMail(val)) m = SS.T(ERR.mail);
      er.textContent = m; inp.setAttribute('aria-invalid', String(!!m)); if (m && ok) { if (focus) inp.focus(); ok = false; }
    });
    return ok;
  }
  function sentText() {
    return SS.L === 'en'
      ? { b: 'Your email is ready. Just press send.', s: 'If your mail app didn’t open, copy the text and send it to ' + SS.CONTACT + '. Once it reaches us, we’ll reply and set a time for the audit.', c: 'Copy the text' }
      : { b: 'Az e-mailed kész, már csak el kell küldened.', s: 'Ha nem nyílt meg a leveleződ, másold ki a szöveget, és küldd el a ' + SS.CONTACT + ' címre. Amint megkaptuk, válaszolunk, és egyeztetünk egy időpontot az auditra.', c: 'Szöveg másolása' };
  }
  function showSent(body) {
    var s = sentText(); sent.hidden = false;
    sent.innerHTML = '<b>' + s.b + '</b><span>' + esc(s.s) + '</span><button type="button" class="btn" id="copyBody">' + s.c + '</button>';
    var cb = $('#copyBody'); cb.addEventListener('click', function () { SS.copy(body, cb, function () { var m = $('#f-msg'); m.value = body; m.focus(); m.select(); }); });
  }
  var sel = function (id) { var s = $('#' + id); return s.value ? s.options[s.selectedIndex].text : ''; };
  form.addEventListener('submit', function (e) {
    e.preventDefault(); if (!check(true)) return;
    var body = SS.compose({ name: $('#f-name').value.trim(), email: $('#f-email').value.trim(), brand: $('#f-brand').value.trim(), web: $('#f-web').value.trim(), budget: sel('f-budget'), goal: sel('f-goal'), interests: chosen, msg: $('#f-msg').value.trim() });
    lastBody = body; sent.hidden = true; sending.hidden = false; $('#stext').textContent = L('Megnyitjuk a leveleződ…', 'Opening your mail app…');
    sending.style.setProperty('--w', '0%'); void sending.offsetWidth;
    var done = function () { sending.hidden = true; showSent(body); SS.send($('#f-brand').value.trim(), body); };
    requestAnimationFrame(function () { sending.style.setProperty('--w', '100%'); });
    if (reduce) done(); else setTimeout(done, 800);
  });
  ['#copyMail', '#copyMail2'].forEach(function (id) {
    var b = $(id); if (!b) return;
    b.addEventListener('click', function () { SS.copy(SS.CONTACT, b, function () { var r = document.createRange(), s = getSelection(); r.selectNodeContents(b.previousElementSibling); s.removeAllRanges(); s.addRange(r); }); });
  });

  /* ---------------- start ---------------- */
  renderPick();
  SS.onLang(function () { renderPick(); if (lastBody && sending.hidden) showSent(lastBody); if ($$('.app .err').some(function (e) { return e.textContent; })) check(false); measureRails(); });
  SS.start();
  $$('[data-r]').forEach(arrive);
  measureRails(); frame(); run();
})();
