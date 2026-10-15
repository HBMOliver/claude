# Social Stream landing page

Luxury scroll-driven rebuild of socialstream.hu (formerly HB Marketing /social).
Static: `index.html`, `scrollcraft.css`, `scrollcraft.js`, `assets/`. No build step.

- Copy, results, testimonials, team and chapter structure come verbatim from the
  supplied `socialstream-erdeklodes-kora.html`; English translations ride in
  `data-en` attributes and switch with the HU/EN control (remembered per visitor,
  or forced with `?lang=en`).
- Contact: `CONTACT` constant at the top of the page script (hello@socialstream.hu).
- Case-study cards link to `case-*.html`, as on the live site. Team photos for
  David and Lidi, and one workshop photo, load from the live site's CDN; if they
  fail the page falls back to an initial or a local photo.
- Hero cutout made with rembg (isnet-general-use) from Olivér's studio portrait.

Preview: `node ../../../.claude/skills/scroll-craft/scripts/serve.mjs --root . --port 4501`
