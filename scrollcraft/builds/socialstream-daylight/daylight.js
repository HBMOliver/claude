/* SocialStream Daylight: the page's behaviour. Language and the mail hand-off come from ss.js;
   everything else is here: the film in its frame, arrivals, counters, the scroll-linked lift of
   the first screen and the method line, the review wall and the audit form. */
(function () {
  'use strict';
  var $ = SS.$, $$ = SS.$$, clamp = SS.clamp, reduce = SS.reduce, esc = SS.esc;
  var root = document.documentElement;
  root.classList.add('js');
  var L = function (hu, en) { return SS.L === 'en' ? en : hu; };

  /* ---------------- their words, verbatim ---------------- */
  var QS = [
    { hu: '„Egyszer már leállítottuk a Facebook hirdetéseinket, mert egyszerűen nem érte meg. Miután megismertük Olivért, adtunk egy újabb esélyt. Már az induláskor is volt vásárlás – olyan számokat produkált, amit eddig nem is láttunk.”', en: '“We had already switched off our Facebook ads once because they simply weren’t worth it. After meeting Olivér we gave it another chance. There were purchases from launch day, and he produced numbers we had never seen before.”', who: 'Péter · Hoofbútor', whoEn: 'Péter · Hoofbútor' },
    { hu: '„Azt hittük, a Facebook a fiataloknak és a webshopoknak való – mi csarnokot építünk. Aztán egy hét alatt annyi ajánlatkérésünk lett, mint korábban fél év alatt összesen.”', en: '“We thought Facebook was for young people and webshops; we build industrial halls. Then in one week we got as many quote requests as we used to get in half a year.”', who: 'Csarnoképítő ügyfél · B2B', whoEn: 'Hall-building client · B2B' },
    { hu: '„Minden decemberben rettegtünk a hirdetési áraktól. Idén először éreztük úgy, hogy az ünnepi szezon nekünk dolgozik – nem ellenünk.”', en: '“Every December we dreaded ad prices. This year, for the first time, the holiday season felt like it was working for us, not against us.”', who: 'Karóra webshop', whoEn: 'Watch webshop' },
    { hu: '„Pár száz jelentkezőre számítottunk a webinárra. Amikor a számláló majdnem 5700-nál állt meg, alig hittük el, hogy ez ugyanabból a büdzséből jött ki.”', en: '“We expected a few hundred registrants for the webinar. When the counter stopped at almost 5,700, we could hardly believe it came from the same budget.”', who: 'Egészségügyi szolgáltató', whoEn: 'Healthcare provider' },
    { hu: '„Profi csapatot szerettem volna az indulás után. Mind Facebook/Instagram, mind weboldal és hirdetés területén profi kampányokat készítenek. Rövid időn belül jöttek az eredmények – nekem semmi dolgom nem volt velük.”', en: '“I wanted a professional team after launch. They build professional campaigns across Facebook/Instagram, the website and ads. Results came quickly, and I had nothing to do.”', who: 'Rita · Rita’s Beauty Corner', whoEn: 'Rita · Rita’s Beauty Corner' },
    { hu: '„A Social Stream profi módon készítette el a weboldalam. Mindenkinek tetszett az igényes és könnyen áttekinthető tartalom! Csak ajánlani tudom őket.”', en: '“Social Stream built my website professionally. Everyone loved the polished, easy-to-follow content! I can only recommend them.”', who: 'János · EJ Massage Therapies', whoEn: 'János · EJ Massage Therapies' }
  ];
  var wall = $('#wall');
  function renderWall() {
    var en = SS.L === 'en';
    wall.innerHTML = QS.map(function (q, i) {
      return '<li data-r class="in" style="--d:' + (i % 3) + '"><blockquote>' + esc(en ? q.en : q.hu) + '</blockquote><span class="by"><i aria-hidden="true">' + esc(q.who.charAt(0)) + '</i>' + esc(en ? q.whoEn : q.who) + '</span></li>';
    }).join('');
  }

  /* ---------------- arrivals: once, as each thing comes into view ---------------- */
  var io = 'IntersectionObserver' in window ? new IntersectionObserver(function (es) {
    es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); if (e.target._count) e.target._count(); } });
  }, { threshold: 0.14, rootMargin: '0px 0px -6% 0px' }) : null;
  function arrive(el) { if (io && !reduce) io.observe(el); else { el.classList.add('in'); if (el._count) el._count(); } }

  /* ---------------- numbers count up the first time they are seen ---------------- */
  $$('[data-count]').forEach(function (el) {
    var to = +el.dataset.count, done = false, holder = el.closest('[data-r]') || el;
    function show(n) { el.textContent = SS.fmtN(n); }
    el._show = function () { show(done ? to : 0); };
    holder._count = function () {
      if (done) return; done = true;
      if (reduce) { show(to); return; }
      var t0 = performance.now(), dur = to > 1000 ? 1900 : 1300;
      (function step(now) { var k = clamp((now - t0) / dur, 0, 1); show(Math.round(to * (1 - Math.pow(1 - k, 3)))); if (k < 1) requestAnimationFrame(step); })(t0);
    };
    if (!reduce && io) show(0); else show(to);
    SS.onLang(function () { if (done || reduce || !io) show(to); });
  });

  /* ---------------- the film in its frame ---------------- */
  var frame = $('#film'), v = $('video', frame), tgl = $('.toggle', frame), narrow = matchMedia('(max-width: 760px)');
  var PLAY = '<svg viewBox="0 0 14 14" aria-hidden="true"><path d="M3 1.5l9 5.5-9 5.5z" fill="currentColor"/></svg>';
  var PAUSE = '<svg viewBox="0 0 14 14" aria-hidden="true"><path d="M3 2h3v10H3zM8 2h3v10H8z" fill="currentColor"/></svg>';
  var paused = reduce || SS.saveData, inView = true, loaded = '', started = false;
  // a phone holds the frame upright and gets the vertical cut; elsewhere the small cut plays where the frame is small,
  // unless the frame is marked data-big (a first screen where the film grows to the full width)
  function srcFor() { if (narrow.matches) return 'assets/hero-v-720.mp4'; if (frame.hasAttribute('data-big')) return 'assets/hero-1080.mp4'; return frame.offsetWidth * (window.devicePixelRatio || 1) < 1300 ? 'assets/hero-540.mp4' : 'assets/hero-1080.mp4'; }
  function load() {
    var s = srcFor(); if (loaded === s) return;
    var t = loaded ? v.currentTime : 0; loaded = s; frame.classList.remove('is-playing'); v.src = s; v.load();
    if (t) v.addEventListener('loadedmetadata', function () { try { v.currentTime = t; } catch (e) {} }, { once: true });
  }
  function state() {
    frame.classList.toggle('is-paused', paused);
    tgl.innerHTML = (paused ? PLAY : PAUSE) + '<span>' + (paused ? L('Lejátszás', 'Play') : L('Szünet', 'Pause')) + '</span>';
    tgl.setAttribute('aria-label', paused ? L('Film lejátszása', 'Play the film') : L('Film megállítása', 'Pause the film'));
  }
  function apply() {
    if (!started) { state(); return; }
    if (paused || !inView) v.pause();
    else { load(); var p = v.play(); if (p && p.catch) p.catch(function (e) { if (e && e.name === 'NotAllowedError') { paused = true; state(); } }); }
    state();
  }
  v.addEventListener('playing', function () { frame.classList.add('is-playing'); });
  tgl.addEventListener('click', function () { paused = !paused; started = true; apply(); });
  // two changes can arrive in one batch (a first screen that rearranges itself while loading): the last one is current
  if ('IntersectionObserver' in window) new IntersectionObserver(function (es) { inView = es[es.length - 1].isIntersecting; apply(); }, { threshold: 0.1 }).observe(frame);
  SS.onMQ(narrow, function () { if (!paused) apply(); else loaded = ''; });
  SS.onLang(state);
  // the film is fetched after the page has loaded, so it never holds up the first screen
  function go() { started = true; apply(); }
  if (document.readyState === 'complete') setTimeout(go, 60); else addEventListener('load', function () { setTimeout(go, 60); }, { once: true });

  /* ---------------- the audit form ---------------- */
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
    var b = $(id); b.addEventListener('click', function () { SS.copy(SS.CONTACT, b, function () { var r = document.createRange(), s = getSelection(); r.selectNodeContents(b.previousElementSibling); s.removeAllRanges(); s.addRange(r); }); });
  });

  /* ---------------- scroll: the menu's shadow, the first screen's lift, the method line ---------------- */
  var nav = $('#nav'), stage = $('#stage'), steps = $('#steps'), stepEls = $$('.step', steps), ticking = false, was = {};
  function frameTick() {
    ticking = false;
    var vh = innerHeight, y = scrollY;
    var sc = y > 8; if (was.sc !== sc) { was.sc = sc; nav.classList.toggle('is-scrolled', sc); }
    if (!reduce) {
      var r = stage.getBoundingClientRect();
      if (r.bottom > -100 && r.top < vh + 100) { var hp = clamp((vh - r.top) / (vh * 0.9), 0, 1).toFixed(3); if (was.hp !== hp) { was.hp = hp; stage.style.setProperty('--hp', hp); } }
    }
    var s = steps.getBoundingClientRect();
    if (s.bottom > -100 && s.top < vh + 100) {
      var sp = reduce ? 1 : clamp((vh * 0.75 - s.top) / Math.max(1, s.height * 0.6), 0, 1), sps = sp.toFixed(3);
      if (was.sp !== sps) { was.sp = sps; steps.style.setProperty('--sp', sps); stepEls.forEach(function (el, i) { el.classList.toggle('is-on', sp >= (i / Math.max(1, stepEls.length - 1)) * 0.98 - 0.001); }); }
    }
  }
  function onScroll() { if (!ticking) { ticking = true; requestAnimationFrame(frameTick); } }
  addEventListener('scroll', onScroll, { passive: true });
  addEventListener('resize', onScroll);

  /* ---------------- start ---------------- */
  renderWall(); renderPick();
  SS.onLang(function () { renderWall(); renderPick(); if (lastBody && sending.hidden) showSent(lastBody); if ($$('.app .err').some(function (e) { return e.textContent; })) check(false); });
  SS.start();
  $$('[data-r]').forEach(arrive);
  frameTick();
})();
