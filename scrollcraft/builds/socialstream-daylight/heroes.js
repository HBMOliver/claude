/* Daylight's first screen, three options: the parts that move. daylight.js already runs the film
   (which cut, play and pause, the button); this adds what each option needs on top of it: the menu
   turning dark over a dark first screen, Cinema's slower film, Glow's light and opening frame,
   Capsule's film growing out of the headline, and, after the first screen of Cinema and Capsule,
   the number sliding in, the long sentence lighting word by word and the objects floating. */
(function () {
  'use strict';
  var $ = SS.$, $$ = SS.$$, clamp = SS.clamp, reduce = SS.reduce;
  var hero = $('#top'), nav = $('#nav'), screen = $('#film');
  if (!hero || !nav || !screen) return;
  var kind = hero.classList.contains('hf') ? 'cinema' : hero.classList.contains('hd') ? 'glow' : hero.classList.contains('ht') ? 'capsule' : '';
  if (!kind) return;
  var video = $('video', screen), narrow = matchMedia('(max-width: 760px)'), was = {}, vh = innerHeight;
  function ease(t) { return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; }
  function easeOut(t) { return 1 - Math.pow(1 - t, 3); }
  function set(el, k, v) { if (el['_' + k] !== v) { el['_' + k] = v; el.style.setProperty(k, v); } }

  /* ---------- Glow: the film's light spills on the stage around it ---------- */
  var amb = kind === 'glow' ? $('.hd-amb', hero) : null, actx = amb && amb.getContext('2d'), seen = true, looping = false, n = 0;
  function loop() {
    if (looping || !actx) return;
    looping = true;
    (function step() {
      if (!seen) { looping = false; return; }
      if (!video.paused && video.readyState >= 2 && n++ % 5 === 0) { try { actx.drawImage(video, 0, 0, amb.width, amb.height); } catch (e) {} }
      requestAnimationFrame(step);
    })();
  }
  if (actx) {
    var poster = $('.poster img', screen);
    var paint = function () { try { actx.drawImage(poster, 0, 0, amb.width, amb.height); } catch (e) {} };
    if (poster.complete) paint(); else poster.addEventListener('load', paint, { once: true });
    if ('IntersectionObserver' in window) new IntersectionObserver(function (es) { seen = es[es.length - 1].isIntersecting; if (seen) loop(); }, { threshold: 0 }).observe(hero);
    else loop();
  }

  /* ---------- Capsule: the film grows from the capsule in the headline to the whole screen ---------- */
  var cap = kind === 'capsule' ? hero : null, stage = cap && $('.ht-stage', cap), copy = cap && $('.ht-copy', cap);
  var live = false, base = null, sw = 0, sh = 0, p = 0;
  // layout position, not the drawn one: the headline may still be arriving (a transform) when this runs
  function offsetIn(el, anc) { var x = 0, y = 0; while (el && el !== anc) { x += el.offsetLeft; y += el.offsetTop; el = el.offsetParent; } return { x: x, y: y }; }
  function measure() {
    if (!cap) return;
    if (reduce) { cap.classList.remove('is-live'); live = false; return; }
    // the scene needs the whole of the type on one screen; on a screen too short the film simply sits under it
    cap.classList.add('is-live');
    sw = stage.clientWidth; sh = stage.clientHeight;
    // the button row is pushed to the bottom of the screen; when the type is too tall it is pushed past it
    var foot = $('.ht-foot', cap), padB = parseFloat(getComputedStyle(copy).paddingBottom) || 0;
    live = foot.offsetTop + foot.offsetHeight <= copy.clientHeight - padB + 1;
    cap.classList.toggle('is-live', live);
    if (!live) {
      ['--fx', '--fy', '--fw', '--fh', '--fr'].forEach(function (k) { screen.style.removeProperty(k); screen['_' + k] = null; });
      cap.classList.remove('is-grown'); was.grown = null;
      return;
    }
    set(cap, '--stage-h', sh + 'px');
    var pill = $$('.ht-pill', cap).filter(function (e) { return e.offsetParent !== null; })[0];
    var o = offsetIn(pill, stage);
    base = { x: o.x, y: o.y, w: pill.offsetWidth, h: pill.offsetHeight };
  }
  function capsule() {
    if (!live) return;
    p = clamp(-cap.getBoundingClientRect().top / (sh * 0.95), 0, 1);
    var e = ease(p), cy = -p * 110;
    set(screen, '--fx', (base.x * (1 - e)).toFixed(1) + 'px');
    set(screen, '--fy', ((base.y + cy) * (1 - e)).toFixed(1) + 'px');
    set(screen, '--fw', (base.w + (sw - base.w) * e).toFixed(1) + 'px');
    set(screen, '--fh', (base.h + (sh - base.h) * e).toFixed(1) + 'px');
    set(screen, '--fr', ((base.h / 2) * (1 - e)).toFixed(1) + 'px');
    set(cap, '--co', (1 - clamp((p - 0.02) * 3.4, 0, 1)).toFixed(3));
    set(cap, '--cy', cy.toFixed(1) + 'px');
    // the pause button is a small round one while the film is a capsule, the usual one once it has grown
    var grown = p > 0.82;
    if (was.grown !== grown) { was.grown = grown; cap.classList.toggle('is-grown', grown); }
  }

  /* ---------- after the first screen (Cinema and Capsule): one moving thing per section ---------- */
  var slide = $('[data-slide]'), lit = $('[data-lit]'), float = $('[data-float]');
  if (lit) {
    // every word in its own span, once for each language; the language on show is the one that lights
    $$('[data-l]', lit).forEach(function (l) {
      l.innerHTML = l.textContent.split(/(\s+)/).map(function (t) { return !t || /^\s+$/.test(t) ? t : '<span class="w">' + SS.esc(t) + '</span>'; }).join('');
    });
    if (reduce) $$('.w', lit).forEach(function (w) { w.classList.add('on'); });
  }
  function after() {
    if (reduce) return;
    // the number slides in from the right and is in place by the time it is a little above the middle
    if (slide) {
      var s = slide.getBoundingClientRect();
      if (s.top < vh * 1.2 && s.bottom > -vh * 0.2) set(slide, '--nx', ((1 - easeOut(clamp((vh - s.top) / (vh * 0.62), 0, 1))) * 24).toFixed(2) + 'vw');
    }
    // the sentence lights from when it enters the lower part of the screen until its end passes the middle
    if (lit) {
      var l = $$('[data-l]', lit).filter(function (e) { return getComputedStyle(e).display !== 'none'; })[0], b = lit.getBoundingClientRect();
      if (l && b.top < vh && b.bottom > 0) {
        var ws = l._ws || (l._ws = $$('.w', l)), k = Math.round(clamp((vh * 0.85 - b.top) / (b.height + vh * 0.35), 0, 1) * ws.length);
        if (l._k !== k) { l._k = k; ws.forEach(function (w, i) { w.classList.toggle('on', i < k); }); }
      }
    }
    // the objects drift from +1 to -1 of their own amount across the row's pass through the screen
    if (float) {
      var f = float.getBoundingClientRect();
      if (f.top < vh && f.bottom > 0) set(float, '--wf', ((0.5 - clamp((vh - f.top) / (vh + f.height), 0, 1)) * 2).toFixed(3));
    }
  }

  /* ---------- every frame: the menu, Cinema's slower film, Glow's opening frame, Capsule, the sections after ---------- */
  var ticking = false;
  function frame() {
    ticking = false;
    vh = innerHeight;
    after();
    if (kind === 'cinema' && !reduce && hero.getBoundingClientRect().bottom > 0) set(hero, '--sy', clamp(scrollY / vh, 0, 1).toFixed(3));
    if (kind === 'glow' && !reduce) {
      var r = screen.getBoundingClientRect();
      if (r.top < vh * 1.2 && r.bottom > 0) {
        // fully inset while the film's top is in the lower part of the screen, fully open near the top
        var q = ease(clamp((vh * 0.72 - r.top) / (vh * 0.57), 0, 1));
        set(screen, '--in', ((1 - q) * (narrow.matches ? 6 : 7)).toFixed(2) + 'vw');
        set(screen, '--rr', ((1 - q) * (narrow.matches ? 22 : 26)).toFixed(1) + 'px');
      }
    }
    if (cap) capsule();
    var nb = nav.getBoundingClientRect().bottom, dark;
    if (cap) dark = live && p > 0.9 && cap.getBoundingClientRect().bottom > nb;
    else dark = hero.getBoundingClientRect().bottom - (kind === 'glow' ? 34 : 0) > nb - 8;
    if (was.dark !== dark) {
      was.dark = dark;
      nav.classList.toggle('on-dark', dark);
      // on Cinema and Capsule the dark first screen is the film: the logo shows the kit's corner mark for video
      // there (daylight.css); Glow's dark stage takes the dark lockup
      nav.classList.toggle('on-film', dark && kind !== 'glow');
      SS.themeColor(dark ? (kind === 'glow' ? '#120c14' : '#0c0b0d') : '#ffffff');
    }
  }
  function onScroll() { if (!ticking) { ticking = true; requestAnimationFrame(frame); } }
  function refit() { measure(); frame(); }
  addEventListener('scroll', onScroll, { passive: true });
  addEventListener('resize', refit);
  addEventListener('load', refit);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(refit);
  // the headline has a capsule in each language; the shown one is measured again
  SS.onLang(refit);
  refit();
})();
