/* Aurora Mix's footer logo builds itself the way the logo kit's animation does (kit/motion/horizontal): the phone
   arrives, the next reel (its S) swipes up into it, it leans in at 15°, its 15° cut opens, and the name streams out
   from behind it, the A's cut opening last. In place, without the video's 3x close-up, so it stays in the footer's
   band, and about 2 s long. The markup itself is the finished logo (the kit's dark master, see tools/logo-anim.mjs),
   which is what shows without script and with reduced motion. Afterwards, while the footer is on screen, the next
   reel swipes in now and then, and at once when a mouse comes over the logo: the S scrolls up out of the phone with
   the next one right under it, the way a feed moves on to the next reel. */
(function () {
  'use strict';
  var box = document.querySelector('[data-logo-anim]');
  if (!box || !('IntersectionObserver' in window) || !window.requestAnimationFrame) return;
  if (window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  function $(id) { return box.querySelector('#fl-' + id); }
  var arrive = $('arrive'), lean = $('lean'), s = $('s'), cutUp = $('cut-up'), cutDn = $('cut-dn'), wipe = $('wipe'),
    social = $('social'), stream = $('stream'), acUp = $('acut-up'), acDn = $('acut-dn'),
    phone = box.querySelector('.fl-phone'), word = box.querySelector('.fl-word');
  if (!arrive || !lean || !s || !cutUp || !cutDn || !wipe || !social || !stream || !acUp || !acDn || !phone || !word) return;
  // GSAP's eases, as the kit's timeline names them
  function expoOut(t) { return t >= 1 ? 1 : 1 - Math.pow(2, -10 * t); }
  function power2Out(t) { return 1 - (1 - t) * (1 - t); }
  function power3Out(t) { return 1 - Math.pow(1 - t, 3); }
  function power3InOut(t) { return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; }
  function backOut(t) { t -= 1; return t * t * (2.4 * t + 1.4) + 1; } // back.out(1.4)
  // the kit composition's values (compositions/logo.html)
  var SY = 225.8107, CUT = 7.8221, ACUT = 42.0348, WIPE = 9314.8163, NAME = 322.8842;
  function set(el, k, v) { el.setAttribute(k, v); }
  function slideS(y) { set(s, 'transform', 'translate(0 ' + y.toFixed(3) + ')'); }
  // [start s, length s, ease, apply(progress 0..1)]
  var build = [
    [0, 0.5, expoOut, function (k) { var c = 0.9 + 0.1 * k; set(arrive, 'opacity', k.toFixed(3)); set(arrive, 'transform', 'translate(128 128) scale(' + c.toFixed(4) + ' ' + c.toFixed(4) + ') translate(-128 -128)'); }],
    [0, 0.45, power2Out, function (k) { phone.style.filter = k < 1 ? 'blur(' + (14 * (1 - k)).toFixed(2) + 'px)' : ''; }],
    [0.25, 0.5, expoOut, function (k) { slideS(SY * (1 - k)); }],
    [0.75, 0.55, backOut, function (k) { set(lean, 'transform', 'rotate(' + (15 * k).toFixed(3) + ' 128 128)'); }],
    [1.15, 0.22, expoOut, function (k) { set(cutUp, 'height', (CUT * (1 - k)).toFixed(4)); set(cutDn, 'y', (222.7552 + CUT * k).toFixed(4)); set(cutDn, 'height', (CUT * (1 - k)).toFixed(4)); }],
    [1.35, 0.65, power3Out, function (k) { set(wipe, 'width', (WIPE * k).toFixed(2)); }],
    [1.35, 0.7, expoOut, function (k) { set(social, 'transform', 'translate(' + (-NAME * (1 - k)).toFixed(3) + ' 0)'); }],
    [1.47, 0.7, expoOut, function (k) { set(stream, 'transform', 'translate(' + (-NAME * (1 - k)).toFixed(3) + ' 0)'); }],
    [1.35, 0.5, power2Out, function (k) { word.style.filter = k < 1 ? 'blur(' + (8 * (1 - k)).toFixed(2) + 'px)' : ''; }],
    [1.77, 0.2, expoOut, function (k) { set(acUp, 'height', (ACUT * (1 - k)).toFixed(4)); set(acDn, 'y', (25.8072 + ACUT * k).toFixed(4)); set(acDn, 'height', (ACUT * (1 - k)).toFixed(4)); }]
  ];
  // the next reel: a copy of the S waits under the screen (clipped like the S, so unseen), and both scroll up
  // together; then the S takes the copy's place and the copy goes back under, which looks the same
  var s2 = s.cloneNode(true);
  s2.removeAttribute('id');
  s2.setAttribute('transform', 'translate(0 ' + SY + ')');
  s.parentNode.appendChild(s2);
  var swipe = [
    [0, 0.6, power3InOut, function (k) { slideS(-SY * k); set(s2, 'transform', 'translate(0 ' + (SY * (1 - k)).toFixed(3) + ')'); }]
  ];
  function swiped() { slideS(0); set(s2, 'transform', 'translate(0 ' + SY + ')'); rest(); }
  var raf = 0;
  function run(tl, done) {
    cancelAnimationFrame(raf);
    var t0 = 0, end = 0;
    tl.forEach(function (r) { end = Math.max(end, r[0] + r[1]); });
    raf = requestAnimationFrame(function step(now) {
      if (!t0) t0 = now;
      var t = (now - t0) / 1000;
      tl.forEach(function (r) { if (t >= r[0]) r[3](r[2](Math.min(1, (t - r[0]) / r[1]))); });
      if (t < end) raf = requestAnimationFrame(step); else { raf = 0; if (done) done(); }
    });
  }
  // hidden until it builds (the markup is the finished logo); the footer is off screen when the page opens
  build.forEach(function (r) { r[3](0); });
  var built = false, inView = false, timer = 0;
  function rest() {
    clearTimeout(timer);
    if (inView) timer = setTimeout(function () { if (inView && !raf) run(swipe, swiped); else rest(); }, 7000);
  }
  new IntersectionObserver(function (es) {
    inView = es[es.length - 1].isIntersecting;
    if (inView && !built) { built = true; run(build, rest); } else if (inView) rest(); else clearTimeout(timer);
  }, { threshold: 0.4 }).observe(box);
  box.addEventListener('pointerenter', function (e) { if (e.pointerType === 'mouse' && built && !raf) run(swipe, swiped); });
})();
