/* Shared by the Edit, Feed and Exhibit designs: language, small helpers, the reel
   all three open on, and the audit hand-off (a mailto carrying every field, with
   copy fallbacks, because a mail app may not open). Each page keeps its own
   structure and interactions. */
(function () {
  var SS = window.SS = {};
  SS.reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  SS.fine = matchMedia('(hover: hover) and (pointer: fine)').matches;
  SS.$ = function (s, r) { return (r || document).querySelector(s); };
  SS.$$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  SS.lerp = function (a, b, k) { return a + (b - a) * k; };
  SS.clamp = function (x, a, b) { return Math.min(b, Math.max(a, x)); };
  SS.esc = function (s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); };
  var store = { get: function (k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
                set: function (k, v) { try { localStorage.setItem(k, v); } catch (e) {} } };

  /* ---------------- language ---------------- */
  SS.L = 'hu';
  var onLang = [];
  SS.onLang = function (f) { onLang.push(f); };
  SS.T = function (o) { return SS.L === 'en' ? o.en : o.hu; };
  SS.fmtN = function (n) { return String(n).replace(/\B(?=(\d{3})+(?!\d))/g, SS.L === 'en' ? ',' : ' '); };
  var htmlEls = [], htmlHu = [];
  function swap(el, attr, prop) {
    var key = 'hu' + attr;
    if (!(key in el.dataset)) el.dataset[key] = prop === 'text' ? el.textContent : el.getAttribute(prop) || '';
    var val = SS.L === 'en' ? el.dataset['en' + attr] : el.dataset[key];
    if (prop === 'text') el.textContent = val; else el.setAttribute(prop, val);
  }
  SS.setLang = function (l, save) {
    SS.L = l === 'en' ? 'en' : 'hu'; document.documentElement.lang = SS.L;
    SS.$$('[data-en]').forEach(function (el) { if (!el.children.length && htmlEls.indexOf(el) < 0) swap(el, '', 'text'); });
    htmlEls.forEach(function (el, i) { if (SS.L === 'en') el.textContent = el.dataset.en; else el.innerHTML = htmlHu[i]; });
    SS.$$('[data-en-alt]').forEach(function (el) { swap(el, 'Alt', 'alt'); });
    SS.$$('[data-en-aria]').forEach(function (el) { swap(el, 'Aria', 'aria-label'); });
    SS.$$('[data-en-ph]').forEach(function (el) { swap(el, 'Ph', 'placeholder'); });
    SS.$$('[data-set-lang]').forEach(function (b) { b.setAttribute('aria-pressed', String(b.dataset.setLang === SS.L)); });
    if (save) store.set('ss-lang', SS.L);
    onLang.forEach(function (f) { f(); });
  };

  /* ---------------- the audit hand-off ---------------- */
  SS.CONTACT = 'hello@socialstream.hu';
  SS.TOPICS = [
    { id: 'video', hu: 'Videó tartalomgyártás', en: 'Video content production' },
    { id: 'social', hu: 'Social média jelenlét', en: 'Social media presence' },
    { id: 'ads', hu: 'Fizetett hirdetés', en: 'Paid advertising' },
    { id: 'web', hu: 'Weboldal & landing', en: 'Website & landing pages' },
    { id: 'auto', hu: 'Automatizáció & e-mail', en: 'Automation & email' },
    { id: 'strategy', hu: 'Növekedési stratégia', en: 'Growth strategy' }
  ];
  SS.topic = function (id) { return SS.T(SS.TOPICS.filter(function (t) { return t.id === id; })[0]); };
  SS.ERR = { req: { hu: 'Ezt kérjük kitölteni.', en: 'Please fill this in.' }, mail: { hu: 'Ez nem tűnik e-mail címnek.', en: 'That doesn’t look like an email address.' } };
  SS.isMail = function (v) { return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v); };
  // f: { name, email, brand, web, budget, goal, interests: [ids], msg }
  SS.compose = function (f) {
    var ints = (f.interests || []).map(SS.topic).join(', ');
    var lines = SS.L === 'en'
      ? ['Name: ' + f.name, 'Email: ' + f.email, 'Company: ' + f.brand, 'Web / Instagram: ' + (f.web || ''), 'Monthly budget: ' + (f.budget || ''), 'Main goal: ' + (f.goal || ''), 'Interested in: ' + ints]
      : ['Név: ' + f.name, 'E-mail: ' + f.email, 'Cég: ' + f.brand, 'Web / Instagram: ' + (f.web || ''), 'Havi büdzsé: ' + (f.budget || ''), 'Fő cél: ' + (f.goal || ''), 'Ami érdekel: ' + ints];
    lines.push('', f.msg || '');
    return lines.join('\n');
  };
  SS.send = function (brand, body) {
    location.href = 'mailto:' + SS.CONTACT + '?subject=' + encodeURIComponent((SS.L === 'en' ? 'Audit request: ' : 'Audit kérés: ') + brand) + '&body=' + encodeURIComponent(body);
  };
  // copy inside the click; if the clipboard is refused, the caller's fallback selects the text instead
  SS.copy = function (text, btn, fallback) {
    var done = function () { btn.textContent = SS.L === 'en' ? 'Copied' : 'Kimásolva'; };
    try { if (navigator.clipboard) navigator.clipboard.writeText(text).then(done, fallback); else fallback(); } catch (e) { fallback(); }
  };
  SS.sentText = function () {
    return SS.L === 'en'
      ? { b: 'Your email is ready.', s: 'If your mail app opened, just press send there. If it didn’t, copy the text and send it to ' + SS.CONTACT + '.', c: 'Copy the text' }
      : { b: 'Az e-mailed elkészült.', s: 'Ha megnyílt a leveleződ, ott már csak küldened kell. Ha nem, másold ki a szöveget, és küldd el ide: ' + SS.CONTACT + '.', c: 'Szöveg másolása' };
  };

  /* ---------------- the reel: full screen, first ---------------- */
  // The film all three designs open on: their client work, with live HU/EN lines and the real
  // numbers on the film's clock. sec holds a video (data-src/-m, data-poster/-m), .rcue[data-t]
  // lines and an optional .toggle; disc is the cursor's play/pause disc. The cut follows the
  // screen's shape (16:9 landscape, 9:16 portrait) and is decided again at load time.
  var PLAY = '<svg viewBox="0 0 14 14" aria-hidden="true"><path d="M3 1.5l9 5.5-9 5.5z" fill="currentColor"/></svg>';
  var PAUSE = '<svg viewBox="0 0 14 14" aria-hidden="true"><path d="M3 2h3v10H3zM8 2h3v10H8z" fill="currentColor"/></svg>';
  SS.reel = function (sec, disc) {
    var v = SS.$('video', sec), toggle = SS.$('.toggle', sec), label = disc && SS.$('span', disc);
    var landscape = function () { return matchMedia('(orientation: landscape)').matches; };
    var loaded = false, on = true, paused = SS.reduce;
    var cues = SS.$$('.rcue', sec).map(function (el) { var t = el.dataset.t.split(' ').map(Number); return { el: el, a: t[0], b: t[1], dim: el.hasAttribute('data-dim'), n: SS.$('[data-to]', el) }; });
    function load() {
      if (loaded) return; loaded = true;
      var wide = landscape();
      v.poster = wide ? v.dataset.poster : v.dataset.posterM; v.src = wide ? v.dataset.src : v.dataset.srcM; v.load();
    }
    function word() { return paused ? (SS.L === 'en' ? 'Play' : 'Lejátszás') : (SS.L === 'en' ? 'Pause' : 'Szünet'); }
    function apply() {
      if (paused || !on) v.pause(); else { load(); var p = v.play(); if (p && p.catch) p.catch(function () {}); }
      if (toggle) {
        toggle.setAttribute('aria-label', paused ? (SS.L === 'en' ? 'Play the reel' : 'Reel lejátszása') : (SS.L === 'en' ? 'Pause the reel' : 'Reel megállítása'));
        toggle.innerHTML = paused ? PLAY : PAUSE;
      }
    }
    function flip() { paused = !paused; apply(); }
    if (toggle) toggle.addEventListener('click', flip);
    v.addEventListener('playing', function () { sec.classList.add('is-playing'); });
    if ('IntersectionObserver' in window) new IntersectionObserver(function (es) { on = es[0].isIntersecting; apply(); }, { threshold: 0.05 }).observe(sec);
    // a media fetch holds the load event, so the film is fetched only once the page has loaded
    if (document.readyState === 'complete') apply(); else addEventListener('load', function () { setTimeout(apply, 60); }, { once: true });
    SS.onLang(apply);
    // over the film the cursor is a play/pause disc
    var dx = -200, dy = -200, tx = -200, ty = -200, ds = 0, dts = 0;
    if (SS.fine && disc) {
      sec.addEventListener('pointermove', function (e) { tx = e.clientX; ty = e.clientY; dts = e.target.closest('.ui, a, button') ? 0 : 1; });
      sec.addEventListener('pointerleave', function () { dts = 0; });
      sec.addEventListener('click', function (e) { if (!e.target.closest('.ui, a, button')) flip(); });
    }
    var lastT = -1;
    function tick() {
      var t = loaded ? v.currentTime : 0;
      if (t !== lastT) {
        lastT = t; var dim = false;
        cues.forEach(function (c) {
          var hit = t >= c.a && t < c.b;
          if (hit !== c.el.classList.contains('is-on')) c.el.classList.toggle('is-on', hit);
          if (hit && c.dim) dim = true;
          if (hit && c.n) { var k = Math.min(1, (t - c.a) / 0.7); c.n.textContent = String(Math.round(+c.n.dataset.to * (1 - Math.pow(1 - k, 3)))); }
        });
        sec.classList.toggle('is-dim', dim);
      }
      if (SS.fine && disc) {
        dx = SS.lerp(dx, tx, 0.22); dy = SS.lerp(dy, ty, 0.22); ds = SS.lerp(ds, dts, 0.18);
        disc.style.setProperty('--x', dx.toFixed(1) + 'px'); disc.style.setProperty('--y', dy.toFixed(1) + 'px'); disc.style.setProperty('--s', ds.toFixed(3));
        if (label.textContent !== word()) label.textContent = word();
      }
    }
    return { video: v, tick: tick, flip: flip, on: function () { return on; }, paused: function () { return paused; }, time: function () { return loaded ? v.currentTime : 0; } };
  };

  SS.start = function () {
    htmlEls = SS.$$('[data-en]').filter(function (el) { return el.children.length > 0; });
    htmlHu = htmlEls.map(function (el) { return el.innerHTML; });
    SS.$$('[data-set-lang]').forEach(function (b) { b.addEventListener('click', function () { SS.setLang(b.dataset.setLang, true); }); });
    var initial = store.get('ss-lang');
    SS.setLang(initial === 'en' ? 'en' : 'hu', false);
  };
})();
