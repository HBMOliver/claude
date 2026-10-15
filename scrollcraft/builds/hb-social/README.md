# HB Marketing, /social

Luxury social media landing page for hbmarketing.hu/social. Static: `index.html`,
`scrollcraft.css`, `scrollcraft.js` and `assets/`. Upload the folder as-is to
the `/social` path. No build step.

- Languages: Hungarian (default) and English, switched in the top-right corner,
  remembered per visitor, or forced with `?lang=en`.
- Contact address: one constant, `CONTACT`, at the top of the page script.
  Also update the two `mailto:` fallbacks in the close section.
- Satin background: regenerate with `python3 lab/satin.py 21 out.jpg`.
- Preview locally: `node ../../../.claude/skills/scroll-craft/scripts/serve.mjs --root . --port 4500`.

See `BRIEF.md` for the creative brief, grammar and feeling curve.
