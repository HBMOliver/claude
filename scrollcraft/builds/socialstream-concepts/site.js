/* socialstream.hu only: the site's pages load it after kit.js, the concept pages do not. What it adds:
   - "Hang be / Hang ki": the brand film keeps playing in the background, and a button on it turns its sound on and
     off in place (the founder, 2026-11-18: no window, no timeline; it is part of the design). Every cut carries the
     soundtrack (tools/hero.sh); the films start muted, as browsers require.
   And two effects after Magic UI (magicui.design, MIT licence), rewritten in plain JS and CSS (site.css):
   - a light that keeps travelling round the audit form's edge (after Border Beam);
   - lines of light between the objects on the services page's first screen, from the video to the ads to the
     measurement (after Animated Beam). */
(function () {
  'use strict';
  var $ = SS.$, $$ = SS.$$, reduce = SS.reduce;
  var en = document.documentElement.lang === 'en';
  var L = function (hu, e) { return en ? e : hu; };

  /* ---------------- the brand film's sound, on and off in place ----------------
     kit.js plays and pauses the films (it keeps them muted); this only decides whether the one that is playing is
     heard. A film is unmuted only while it plays and muted again whenever it stops, so kit.js's own play() never has
     to start a film with sound (browsers refuse that without a click). On a computer the opening hands over to the
     card at the same moment of the film, and the sound goes with it. If a browser still refuses the sound, the film
     keeps playing silently and the buttons go back to "Hang be". */
  var ON = '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M2 6h3l4-3v10l-4-3H2z" fill="currentColor"/><path d="M11.4 5.3a3.9 3.9 0 0 1 0 5.4M13.3 3.5a6.5 6.5 0 0 1 0 9" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>';
  var OFF = '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M2 6h3l4-3v10l-4-3H2z" fill="currentColor"/><path d="M11 6l4 4M15 6l-4 4" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>';
  var films = $$('[data-film]'), vids = films.map(function (box) { return $('video', box); }).filter(Boolean), sound = false, btns = [];
  var show = function () {
    btns.forEach(function (b) {
      b.innerHTML = (sound ? ON : OFF) + '<span>' + (sound ? L('Hang ki', 'Sound off') : L('Hang be', 'Sound on')) + '</span>';
      b.setAttribute('aria-pressed', String(sound));
    });
  };
  var hear = function (v) { if (sound && !v.paused) v.muted = false; };
  vids.forEach(function (v) {
    v.addEventListener('playing', function () {
      // a film that only plays for a moment inside the click (see below) stays muted
      if (!sound || v.dataset.ssHeld === '1') return;
      v.muted = false;
      // a browser that will not play this film with sound pauses it; then the film goes on silently
      setTimeout(function () { if (sound && v.paused && !v.ended && v.muted === false && v.dataset.ssHeld !== '1') { sound = false; v.muted = true; show(); var p = v.play(); if (p && p.catch) p.catch(function () {}); } }, 300);
    });
    v.addEventListener('pause', function () { v.muted = true; });
  });
  films.forEach(function (box) {
    var b = document.createElement('button');
    b.type = 'button';
    b.className = 'ss-sound';
    b.setAttribute('aria-label', L('A film hangja', 'The film’s sound'));
    b.addEventListener('click', function () {
      sound = !sound;
      // inside the click every film may take its sound: the one playing is heard at once, the others when they play
      vids.forEach(function (v) {
        if (!sound) { v.muted = true; return; }
        if (!v.paused) { hear(v); return; }
        // a film that is not playing yet (the card before the opening hands over) is allowed sound by this click;
        // one that kit.js has not loaded (the card on a phone, which never shows) is left alone
        if (!v.currentSrc) return;
        v.dataset.ssHeld = '1';
        var p = v.play();
        if (p && p.then) p.then(function () { v.pause(); v.dataset.ssHeld = ''; }, function () { v.dataset.ssHeld = ''; });
        else { v.pause(); v.dataset.ssHeld = ''; }
      });
      show();
    });
    btns.push(b);
    box.appendChild(b);
  });
  show();

  /* ---------------- a light round the audit form's edge (its look is in site.css) ---------------- */
  $$('.mx-form .app').forEach(function (app) {
    var s = document.createElement('span');
    s.className = 'ss-beam';
    s.setAttribute('aria-hidden', 'true');
    s.innerHTML = '<i></i>';
    app.appendChild(s);
  });

  /* ---------------- lines of light between floating objects (data-beams) ----------------
     Each path names the objects it joins (data-from, data-to: their order among the box's images). The line runs
     from edge to edge of the two objects and bends a little (data-bend); while the box is on screen it is drawn
     again every frame, so it stays joined to the objects as they float and lean toward the cursor. */
  $$('[data-beams]').forEach(function (box) {
    var imgs = $$('img', box), svg = $('svg', box), paths = $$('path[data-from]', box);
    if (!svg || !paths.length) return;
    var at = function (el, b) { var r = el.getBoundingClientRect(); return { x: r.left - b.left + r.width / 2, y: r.top - b.top + r.height / 2, r: r.width * 0.3 }; };
    var draw = function () {
      var b = box.getBoundingClientRect();
      svg.setAttribute('viewBox', '0 0 ' + b.width.toFixed(1) + ' ' + b.height.toFixed(1));
      paths.forEach(function (p) {
        var A = at(imgs[+p.getAttribute('data-from')], b), B = at(imgs[+p.getAttribute('data-to')], b);
        var dx = B.x - A.x, dy = B.y - A.y, len = Math.hypot(dx, dy) || 1, ux = dx / len, uy = dy / len;
        var x1 = A.x + ux * A.r, y1 = A.y + uy * A.r, x2 = B.x - ux * B.r, y2 = B.y - uy * B.r;
        var k = +(p.getAttribute('data-bend') || 0.18) * len, mx = (x1 + x2) / 2 - uy * k, my = (y1 + y2) / 2 + ux * k;
        p.setAttribute('d', 'M' + x1.toFixed(1) + ',' + y1.toFixed(1) + ' Q' + mx.toFixed(1) + ',' + my.toFixed(1) + ' ' + x2.toFixed(1) + ',' + y2.toFixed(1));
      });
    };
    draw();
    addEventListener('resize', draw);
    addEventListener('load', draw);
    if (reduce || !('IntersectionObserver' in window)) return;
    var on = false, raf = 0;
    var loop = function () { draw(); raf = on ? requestAnimationFrame(loop) : 0; };
    new IntersectionObserver(function (es) { on = es[0].isIntersecting; if (on && !raf) raf = requestAnimationFrame(loop); }).observe(box);
  });
})();
