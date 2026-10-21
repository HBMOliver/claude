/* SocialStream shared site script: language, the stream film and its synced
   lines, entry counters, the audit form. Page-specific behaviour lives in
   each page; it talks to this file through window.SS. */
(function () {
  'use strict';
  var root = document.documentElement;
  root.classList.add('js');
  var CONTACT = 'hello@socialstream.hu';
  var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var esc = function (s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); };
  var store = {
    get: function (k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set: function (k, v) { try { localStorage.setItem(k, v); } catch (e) {} }
  };

  var TOPICS = [
    { id: 'video', hu: 'Videó tartalomgyártás', en: 'Video content production' },
    { id: 'social', hu: 'Social média jelenlét', en: 'Social media presence' },
    { id: 'ads', hu: 'Fizetett hirdetés', en: 'Paid advertising' },
    { id: 'web', hu: 'Weboldal & landing', en: 'Website & landing pages' },
    { id: 'auto', hu: 'Automatizáció & e-mail', en: 'Automation & email' },
    { id: 'strategy', hu: 'Növekedési stratégia', en: 'Growth strategy' }
  ];
  var SS = window.SS = { L: 'hu', reduce: reduce, topics: TOPICS, chosen: [], listeners: [], esc: esc, $: $, $$: $$ };
  SS.T = function (o) { return o[SS.L] || o.hu; };
  SS.onLang = function (fn) { SS.listeners.push(fn); };

  /* ---------------- language ---------------- */
  var swaps = [['[data-en]', 'text', 'en', 'hu'], ['[data-en-alt]', 'alt', 'enAlt', 'huAlt'], ['[data-en-aria]', 'aria-label', 'enAria', 'huAria'], ['[data-en-ph]', 'placeholder', 'enPh', 'huPh']];
  swaps.forEach(function (s) { $$(s[0]).forEach(function (el) { el.dataset[s[3]] = s[1] === 'text' ? el.textContent : (el.getAttribute(s[1]) || ''); }); });
  SS.setLang = function (l, save) {
    if (l !== 'hu' && l !== 'en') return;
    SS.L = l; root.lang = l;
    swaps.forEach(function (s) {
      $$(s[0]).forEach(function (el) {
        var v = el.dataset[l === 'en' ? s[2] : s[3]];
        if (s[1] === 'text') el.textContent = v; else el.setAttribute(s[1], v);
      });
    });
    $$('[data-set-lang]').forEach(function (b) { b.setAttribute('aria-pressed', String(b.dataset.setLang === l)); });
    $$('.js-mail').forEach(function (a) { a.href = 'mailto:' + CONTACT + '?subject=' + encodeURIComponent(l === 'en' ? 'Free audit' : 'Ingyenes audit'); });
    SS.listeners.forEach(function (fn) { fn(); });
    if (save) store.set('ss-lang', l);
  };
  $$('[data-set-lang]').forEach(function (b) { b.addEventListener('click', function () { SS.setLang(b.dataset.setLang, true); }); });

  /* ---------------- the stream film ----------------
     The film is silent and text-free; its manifesto lines are live text,
     switched on the film's own clock so they stay in both languages. The clip
     only starts after the page has loaded: a media fetch holds the load event,
     and the poster is the film's first frame. */
  function film(v) {
    var wide = matchMedia('(min-width: ' + (v.dataset.breakpoint || '820') + 'px)').matches;
    var src = wide ? v.dataset.src : (v.dataset.srcM || v.dataset.src);
    var poster = wide ? v.dataset.poster : (v.dataset.posterM || v.dataset.poster);
    var box = v.closest('[data-film-box]') || v.parentElement;
    var lines = $$('[data-beat]', box.closest('[data-film-scope]') || document);
    var scrim = $('[data-film-scrim]', box.closest('[data-film-scope]') || box);
    var beats = JSON.parse(v.dataset.beats || '[]');
    var btn = $('[data-film-toggle]', box.closest('[data-film-scope]') || box);
    if (poster) { v.poster = poster; var pi = $('img.film-poster', box); if (pi) pi.src = poster; }
    var ready = document.readyState === 'complete', loaded = false, paused = reduce, onScreen = true, cur = -2;
    function load() { if (loaded || !ready) return; loaded = true; v.src = src; v.load(); }
    function beatAt(t) {
      for (var i = 0; i < beats.length; i++) {
        var a = beats[i][0], b = beats[i][1];
        if (a <= b ? (t >= a && t < b) : (t >= a || t < b)) return i;
      }
      return -1;
    }
    function show(i) {
      if (i === cur) return; cur = i;
      lines.forEach(function (el) { el.classList.toggle('is-on', +el.dataset.beat === i); });
      if (scrim) scrim.classList.toggle('is-on', i > -1);
      mark();
    }
    /* The beat is reported to the scroll-craft harness only while the film is on
       screen; left on after the hero has gone, it makes every later flow section
       look like a stage that never changes. The film runs on its own clock, not
       on scroll, so it is declared a hold: two scroll samples on the same beat
       are the film playing, not dead scroll. */
    function mark() {
      if (onScreen) { box.setAttribute('data-sc-verify-state', 'beat' + cur); box.setAttribute('data-sc-verify-hold', 'true'); }
      else { box.removeAttribute('data-sc-verify-state'); box.removeAttribute('data-sc-verify-hold'); }
    }
    function apply() {
      if (paused || !onScreen) v.pause();
      else { load(); if (loaded) { var p = v.play(); if (p && p.catch) p.catch(function () {}); } }
      if (btn) {
        btn.setAttribute('aria-pressed', String(paused));
        btn.setAttribute('aria-label', paused ? (SS.L === 'en' ? 'Play film' : 'Film lejátszása') : (SS.L === 'en' ? 'Pause film' : 'Film megállítása'));
        btn.innerHTML = paused ? '<svg viewBox="0 0 14 14" aria-hidden="true"><path d="M3 1.5l9 5.5-9 5.5z" fill="currentColor"/></svg>' : '<svg viewBox="0 0 14 14" aria-hidden="true"><path d="M3 2h3v10H3zM8 2h3v10H8z" fill="currentColor"/></svg>';
      }
    }
    if (!ready) addEventListener('load', function () { setTimeout(function () { ready = true; apply(); }, 60); }, { once: true });
    v.addEventListener('playing', function () { box.classList.add('is-playing'); });
    if (btn) btn.addEventListener('click', function () { paused = !paused; apply(); });
    if ('IntersectionObserver' in window) new IntersectionObserver(function (es) { onScreen = es[0].isIntersecting; mark(); apply(); }, { threshold: 0.04 }).observe(box);
    SS.onLang(apply);
    show(0);
    (function tick() { if (loaded && !v.paused) show(beatAt(v.currentTime)); requestAnimationFrame(tick); })();
    apply();
  }

  /* ---------------- counters, once on entry ---------------- */
  function counters() {
    var els = $$('[data-count]');
    if (!('IntersectionObserver' in window) || reduce) return;
    els.forEach(function (c) { c.textContent = '0'; });
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (!e.isIntersecting) return;
        io.unobserve(e.target);
        var el = e.target, to = +el.dataset.count, t0 = performance.now();
        (function f(now) { var k = Math.min(1, (now - t0) / 1500); el.textContent = String(Math.round(to * (1 - Math.pow(1 - k, 3)))); if (k < 1) requestAnimationFrame(f); })(t0);
      });
    }, { threshold: 0.6 });
    els.forEach(function (c) { io.observe(c); });
  }

  /* ---------------- the audit form ---------------- */
  function form() {
    var f = $('#appform'); if (!f) return;
    var msg = $('#f-msg'), sent = $('#sent'), chips = $('#formChips'), note = $('#carryNote'), lastBody = '';
    function renderChips() {
      if (!chips) return;
      chips.innerHTML = TOPICS.map(function (t) {
        return '<label class="chip"><input type="checkbox" name="int" value="' + t.id + '"' + (SS.chosen.indexOf(t.id) > -1 ? ' checked' : '') + '><span>' + esc(SS.T(t)) + '</span></label>';
      }).join('');
    }
    var noteFrom = null;
    function renderNote() { if (note) { note.hidden = !noteFrom; note.textContent = noteFrom ? SS.T(noteFrom) : ''; } }
    SS.setInterests = function (ids, from) {
      SS.chosen = ids.slice(); noteFrom = from || null; renderChips(); renderNote();
    };
    if (chips) chips.addEventListener('change', function (e) {
      var id = e.target.value, k = SS.chosen.indexOf(id);
      if (e.target.checked && k < 0) SS.chosen.push(id); else if (!e.target.checked && k > -1) SS.chosen.splice(k, 1);
      if (SS.onChosen) SS.onChosen();
    });
    SS.onLang(function () { renderChips(); renderNote(); });
    var ERR = { req: { hu: 'Ezt kérjük kitölteni.', en: 'Please fill this in.' }, mail: { hu: 'Ez nem tűnik e-mail címnek.', en: 'That doesn\'t look like an email address.' } };
    function check() {
      var ok = true;
      [['f-name', 'e-name'], ['f-email', 'e-email'], ['f-brand', 'e-brand']].forEach(function (p) {
        var el = $('#' + p[0]), er = $('#' + p[1]), v = el.value.trim(), m = '';
        if (!v) m = SS.T(ERR.req); else if (el.type === 'email' && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v)) m = SS.T(ERR.mail);
        er.textContent = m; el.setAttribute('aria-invalid', String(!!m));
        if (m && ok) { el.focus(); ok = false; }
      });
      return ok;
    }
    function copyText(text, btn) {
      var done = function () { btn.textContent = SS.L === 'en' ? 'Copied' : 'Kimásolva'; };
      var fallback = function () { msg.value = text; msg.focus(); msg.select(); };
      try { if (navigator.clipboard) navigator.clipboard.writeText(text).then(done, fallback); else fallback(); } catch (e) { fallback(); }
    }
    var ca = $('#copyAddr'); if (ca) ca.addEventListener('click', function () { copyText(CONTACT, ca); });
    function showSent(body) {
      sent.hidden = false;
      sent.innerHTML = '<b>' + (SS.L === 'en' ? 'Your email is ready.' : 'Az e-mailed elkészült.') + '</b><span>' +
        (SS.L === 'en' ? 'If your mail app opened, just press send there. If it didn\'t, copy the text and send it to ' : 'Ha megnyílt a leveleződ, ott már csak küldened kell. Ha nem, másold ki a szöveget, és küldd el ide: ') +
        '<a href="mailto:' + CONTACT + '">' + CONTACT + '</a>.</span><button type="button" class="btn btn--ghost" id="copyBody">' + (SS.L === 'en' ? 'Copy the text' : 'Szöveg másolása') + '</button>';
      $('#copyBody').addEventListener('click', function () { copyText(body, this); });
    }
    SS.onLang(function () { if (lastBody) showSent(lastBody); });
    f.addEventListener('submit', function (e) {
      e.preventDefault();
      if (!check()) return;
      var v = function (id) { var el = $('#' + id); return el.tagName === 'SELECT' ? (el.value ? el.options[el.selectedIndex].text : '') : el.value.trim(); };
      var ints = SS.chosen.map(function (id) { return SS.T(TOPICS.filter(function (t) { return t.id === id; })[0]); }).join(', ');
      var extra = SS.formExtra ? SS.formExtra() : '';
      var lines = SS.L === 'en'
        ? ['Name: ' + v('f-name'), 'Email: ' + v('f-email'), 'Company: ' + v('f-brand'), 'Web / Instagram: ' + v('f-web'), 'Monthly budget: ' + v('f-budget'), 'Main goal: ' + v('f-goal'), 'Interested in: ' + ints]
        : ['Név: ' + v('f-name'), 'E-mail: ' + v('f-email'), 'Cég: ' + v('f-brand'), 'Web / Instagram: ' + v('f-web'), 'Havi büdzsé: ' + v('f-budget'), 'Fő cél: ' + v('f-goal'), 'Ami érdekel: ' + ints];
      if (extra) lines.push(extra);
      lines.push('', v('f-msg'));
      var body = lines.join('\n');
      lastBody = body; showSent(body);
      location.href = 'mailto:' + CONTACT + '?subject=' + encodeURIComponent((SS.L === 'en' ? 'Audit request: ' : 'Audit kérés: ') + v('f-brand')) + '&body=' + encodeURIComponent(body);
    });
    renderChips();
  }

  /* ---------------- start ---------------- */
  SS.start = function () {
    $$('video[data-film]').forEach(film);
    counters();
    form();
    var initial = new URLSearchParams(location.search).get('lang') || store.get('ss-lang');
    SS.setLang(initial === 'en' ? 'en' : 'hu', false);
  };
})();
