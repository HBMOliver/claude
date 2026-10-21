/* Shared by the Edit, Feed and Exhibit designs: language, small helpers, and the
   audit hand-off (a mailto carrying every field, with copy fallbacks, because a
   mail app may not open). Each page keeps its own structure and interactions. */
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

  SS.start = function () {
    htmlEls = SS.$$('[data-en]').filter(function (el) { return el.children.length > 0; });
    htmlHu = htmlEls.map(function (el) { return el.innerHTML; });
    SS.$$('[data-set-lang]').forEach(function (b) { b.addEventListener('click', function () { SS.setLang(b.dataset.setLang, true); }); });
    var initial = store.get('ss-lang');
    SS.setLang(initial === 'en' ? 'en' : 'hu', false);
  };
})();
