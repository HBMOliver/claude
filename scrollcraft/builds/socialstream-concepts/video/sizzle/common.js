    // Shared by every scene (build.py puts it at the top of each scene's script): the film's clock, the frame and
    // the stream's camera. Every time is in seconds of the whole film; AT(t) turns one into this scene's own time.
    const TM = %TM%;
    const START = %START%, AT = (t) => t - START;
    const W = %W%, H = %H%, TALL = H > W, CX = W / 2, CY = H / 2;
    const clamp01 = (v) => (v < 0 ? 0 : v > 1 ? 1 : v);
    const lerp = (a, b, p) => a + (b - a) * p;
    const EZ = {};
    const ez = (name, p) => (EZ[name] || (EZ[name] = gsap.parseEase(name)))(clamp01(p));
    // the stream's camera: from TM.s0 it flies TM.travel px forward and brakes (power2.out) until TM.land
    const camZ = (t) => TM.travel * ez("power2.out", (t - TM.s0) / (TM.land - TM.s0));
    // a card standing at world (X, Y, Z) seen at time t: its centre on screen, its scale and its depth
    const project = (X, Y, Z, t) => {
      const D = Z - camZ(t), s = TM.f / D;
      return { x: CX + X * s, y: CY + Y * s, s, D };
    };
    // the scale that makes a bw x bh box cover a rw x rh window (object-fit: cover)
    const cover = (bw, bh, rw, rh) => Math.max(rw / bw, rh / bh);
    // footage covering a rect R: its focus (fx, fy, 0-1) as near the rect's centre as the cover allows; dy moves it
    // down by that much (a swipe). Returns the top-left corner and the scale
    const coverAt = (bw, bh, R, fx, fy, dy) => {
      const z = cover(bw, bh, R.w, R.h), sw = bw * z, sh = bh * z, x0 = R.cx - R.w / 2, y0 = R.cy - R.h / 2;
      const x = Math.min(x0, Math.max(x0 + R.w - sw, R.cx - sw * fx));
      const y = Math.min(y0, Math.max(y0 + R.h - sh, R.cy - sh * fy));
      return { x, y: y + dy, z };
    };
    // a rect {cx, cy, w, h, r} part of the way to another
    const mixRect = (a, b, p) => ({ cx: lerp(a.cx, b.cx, p), cy: lerp(a.cy, b.cy, p), w: lerp(a.w, b.w, p),
      h: lerp(a.h, b.h, p), r: lerp(a.r, b.r, p) });
    const insetOf = (R) => `inset(${(R.cy - R.h / 2).toFixed(2)}px ${(W - R.cx - R.w / 2).toFixed(2)}px ` +
      `${(H - R.cy - R.h / 2).toFixed(2)}px ${(R.cx - R.w / 2).toFixed(2)}px round ${Math.max(0, R.r).toFixed(2)}px)`;
    // Turns a drawing that is a function of time into ordinary tweens, which the player seeks like every other
    // animation (it re-renders nested timelines its own way, and code run from onUpdate or modifiers does not reliably
    // run again on each frame). draw(t, put) is called once for every frame of [from, to] while the scene is set up,
    // and reports with put(el, prop, value) what it would set. Each element's property then becomes a chain of
    // tweens, one per run of frames where it moves at a steady rate (a held value needs none), so every frame gets
    // exactly the value drawn for it. Text values (visibility, display) become sets where they change.
    const FPS = %FPS%;
    const bake = (tl, from, to, draw) => {
      const n = Math.round((to - from) * FPS), tracks = new Map();
      for (let i = 0; i <= n; i++) {
        draw(from + i / FPS, (el, prop, v) => {
          let m = tracks.get(el);
          if (!m) tracks.set(el, (m = new Map()));
          let a = m.get(prop);
          if (!a) m.set(prop, (a = new Array(n + 1)));
          a[i] = v;
        });
      }
      const at = (i) => AT(from) + i / FPS;
      tracks.forEach((m, el) => m.forEach((a, prop) => {
        for (let i = 1; i <= n; i++) if (a[i] === undefined) a[i] = a[i - 1];
        if (a[0] === undefined) a[0] = a.find((v) => v !== undefined);
        tl.set(el, { [prop]: a[0] }, at(0));
        if (typeof a[0] !== "number") {          // a text value: set it where it changes
          // a quarter frame early, so a seek that lands a hair before the frame's time still gets it
          for (let i = 1; i <= n; i++) if (a[i] !== a[i - 1]) tl.set(el, { [prop]: a[i] }, at(i) - 0.25 / FPS);
          return;
        }
        let i0 = 0;
        while (i0 < n) {
          // the longest run from i0 along which the value moves at a steady rate
          let i1 = i0 + 1;
          const lin = (j, k) => { for (let q = i0 + 1; q < k; q++) { const e = a[i0] + (a[k] - a[i0]) * (q - i0) / (k - i0); if (Math.abs(a[q] - e) > 0.02) return false; } return true; };
          while (i1 + 1 <= n && lin(i0, i1 + 1)) i1++;
          if (a[i1] !== a[i0]) tl.fromTo(el, { [prop]: a[i0] }, { [prop]: a[i1], duration: (i1 - i0) / FPS, ease: "none", immediateRender: false }, at(i0));
          i0 = i1;
        }
      }));
    };
