/* Aurora Mix's reels play as short silent loops. Each clip loads only when its card comes near the screen, plays
   while the card is on screen, and pauses when it leaves or the tab is hidden; the poster under it shows until the
   first frame plays. The bar along the card's foot follows the clip. With reduced motion, a data saver, or no
   IntersectionObserver, nothing loads and the posters stay. The moving rail is doubled by kit.js before this runs,
   so its copies are found here too (the same files, from the cache). */
(function () {
  'use strict';
  var vids = [].slice.call(document.querySelectorAll('.rv video[data-src]'));
  if (!vids.length || !('IntersectionObserver' in window)) return;
  if (window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  if (navigator.connection && navigator.connection.saveData) return;
  var live = [], raf = 0;
  function play(v) {
    if (!v.getAttribute('src')) { v.muted = true; v.src = v.getAttribute('data-src'); }
    var p = v.play();
    if (p && p.catch) p.catch(function () {});
  }
  function bars() {
    raf = 0;
    live.forEach(function (v) { if (v.duration) v.parentNode.style.setProperty('--t', (v.currentTime / v.duration).toFixed(3)); });
    if (live.length && !document.hidden) raf = requestAnimationFrame(bars);
  }
  var io = new IntersectionObserver(function (es) {
    es.forEach(function (e) {
      var v = e.target, i = live.indexOf(v);
      if (e.isIntersecting) { if (i < 0) live.push(v); if (!document.hidden) play(v); }
      else { if (i > -1) live.splice(i, 1); v.pause(); }
    });
    if (live.length && !raf) raf = requestAnimationFrame(bars);
  }, { rootMargin: '80px 0px', threshold: 0.1 });
  vids.forEach(function (v) {
    v.addEventListener('playing', function () { v.classList.add('on'); }, { once: true });
    io.observe(v);
  });
  document.addEventListener('visibilitychange', function () {
    live.forEach(function (v) { if (document.hidden) v.pause(); else play(v); });
    if (!document.hidden && live.length && !raf) raf = requestAnimationFrame(bars);
  });
})();
