// node tools/site.mjs   (from this build's folder, after node build.mjs; the share image comes from tools/og.mjs)
// Packages Aurora Mix as the live site for https://socialstream.hu, hosted by Pulse CRM. Pulse serves an uploaded
// folder's files exactly as they are, at the domain root (the hosting session's notes, pulse-hosting-bundle.md), so
// this writes dist/site/ (cleared first):
//   index.html            mix.html as the domain's page: the real title, the canonical address, share tags and image,
//                         and the organisation's details for search engines; everything else exactly as in mix.html
//   base.css mix.css ss.js kit.js   the page's own files, linked relatively, as mix.html links them
//   assets/               only the files the page uses: named in its markup, styles or scripts, plus the three cuts
//                         of the brand film that kit.js picks between at runtime
//   favicon.ico favicon.svg apple-touch-icon.png site.webmanifest and the icons the manifest names
//                         the logo kit's web files, at the root, where the page's head and the manifest ask for them
//   404.html robots.txt sitemap.xml
// Real files only, no symlinks. It stops if anything the page names is missing, or if the folder breaks Pulse's
// limits (60 MB, 1,500 files).
import fs from 'node:fs';
import path from 'node:path';

const ORIGIN = 'https://socialstream.hu', OUT = 'dist/site';
const TITLE = 'SocialStream · Interest media ügynökség';
const OG = 'assets/og-image.jpg';
const OG_ALT = 'A SocialStream logója és a mondat: A social media meghalt. Az érdeklődés vette át a helyét.';
const FILM = ['assets/hero-540.mp4', 'assets/hero-1080.mp4', 'assets/hero-v-720.mp4'];
const LIMIT_MB = 60, LIMIT_FILES = 1500;

const read = f => fs.readFileSync(f, 'utf8');
const text = s => s.replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;');
let html = read('mix.html');
if (!/^<!doctype html>\s*<html lang="hu">/i.test(html)) throw new Error('mix.html is not a complete Hungarian page');
for (const need of ['<meta charset="utf-8">', '<meta name="viewport"', '<link rel="icon"', '<link rel="manifest"'])
  if (!html.includes(need)) throw new Error('mix.html has no ' + need);
const desc = (html.match(/<meta name="description" content="([^"]+)">/) || [])[1];
const email = (html.match(/mailto:([^"?]+)/) || [])[1];
if (!desc || !email) throw new Error('mix.html has no description or no contact address');
if (!fs.existsSync(OG)) throw new Error(OG + ' is missing: run tools/og.mjs');

// the domain's head: these go right after the description; the title is replaced
const org = { '@context': 'https://schema.org', '@type': 'Organization', name: 'SocialStream', url: ORIGIN + '/',
  logo: ORIGIN + '/icon-512.png', email, description: desc };
const head = [
  `<link rel="canonical" href="${ORIGIN}/">`,
  '<meta property="og:type" content="website">',
  '<meta property="og:site_name" content="SocialStream">',
  '<meta property="og:locale" content="hu_HU">',
  '<meta property="og:locale:alternate" content="en_GB">',
  `<meta property="og:url" content="${ORIGIN}/">`,
  `<meta property="og:title" content="${text(TITLE)}">`,
  `<meta property="og:description" content="${desc}">`,
  `<meta property="og:image" content="${ORIGIN}/${OG}">`,
  '<meta property="og:image:width" content="1200">',
  '<meta property="og:image:height" content="630">',
  `<meta property="og:image:alt" content="${text(OG_ALT)}">`,
  '<meta name="twitter:card" content="summary_large_image">',
  `<script type="application/ld+json">${JSON.stringify(org).replace(/</g, '\\u003c')}</script>`,
].join('\n');
html = html.replace(/<title>[^<]*<\/title>/, () => `<title>${text(TITLE)}</title>`)
  .replace(/(<meta name="description"[^>]*>)/, m => m + '\n' + head);
if (!html.includes('og:image') || !html.includes(`<title>${text(TITLE)}</title>`)) throw new Error('the head was not rewritten');

// what the page needs
const local = [...html.matchAll(/<link rel="stylesheet" href="([a-z0-9-]+\.css)">/g), ...html.matchAll(/<script src="([a-z0-9-]+\.js)"><\/script>/g)].map(m => m[1]);
const named = t => [...t.matchAll(/assets\/[A-Za-z0-9._-]+\.(?:webp|jpg|jpeg|png|svg|gif|mp4|webm|woff2?|vtt)/g)].map(m => m[0]);
const assets = [...new Set([html, ...local.map(read)].flatMap(named).concat(FILM))].sort();
const root = [...html.matchAll(/<link rel="(?:icon|apple-touch-icon|manifest)"[^>]*href="\/([^"]+)"/g)].map(m => m[1]);
for (const i of JSON.parse(read('site.webmanifest')).icons || []) root.push(i.src.replace(/^\//, ''));
const files = [...new Set([...local, ...assets, ...root])];
const missing = files.filter(f => !fs.existsSync(f));
if (missing.length) throw new Error('missing: ' + missing.join(', '));

// write the folder: real copies (realpath, so a linked source still lands as a file)
fs.rmSync(OUT, { recursive: true, force: true });
fs.mkdirSync(OUT + '/assets', { recursive: true });
for (const f of files) fs.copyFileSync(fs.realpathSync(f), path.join(OUT, f));
fs.writeFileSync(OUT + '/index.html', html);
fs.writeFileSync(OUT + '/robots.txt', `User-agent: *\nAllow: /\n\nSitemap: ${ORIGIN}/sitemap.xml\n`);
fs.writeFileSync(OUT + '/sitemap.xml', `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n  <url><loc>${ORIGIN}/</loc><lastmod>${new Date().toISOString().slice(0, 10)}</lastmod></url>\n</urlset>\n`);
// shown for an unknown address at any depth, so everything it links is from the root
fs.writeFileSync(OUT + '/404.html', `<!doctype html>
<html lang="hu">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Nincs ilyen oldal · SocialStream</title>
<meta name="robots" content="noindex">
<meta name="theme-color" content="#05070f">
<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<style>
  :root { color-scheme: dark; }
  html, body { height: 100%; margin: 0; }
  body { display: grid; place-items: center; padding: 24px; box-sizing: border-box; color: #eef1f8; font: 17px/1.6 system-ui, -apple-system, "Segoe UI", sans-serif;
    background: radial-gradient(60% 70% at 8% 110%, rgba(255, 92, 138, 0.32), transparent 60%), radial-gradient(50% 60% at 96% -10%, rgba(47, 214, 195, 0.16), transparent 60%), #05070f; }
  main { display: grid; gap: 18px; justify-items: start; max-width: 34rem; }
  img { width: 220px; height: auto; }
  h1 { margin: 10px 0 0; font-size: clamp(1.8rem, 6vw, 2.6rem); line-height: 1.1; letter-spacing: -0.02em; }
  p { margin: 0; color: #b9c1d6; }
  a { color: #ffd1df; }
  a.btn { display: inline-block; margin-top: 6px; padding: 14px 22px; border-radius: 999px; background: #d6336a; color: #fff; font-weight: 700; text-decoration: none; }
  a:focus-visible { outline: 2px solid #ffd1df; outline-offset: 3px; }
  .en { font-size: 14px; color: #8a94ad; }
</style>
</head>
<body>
<main>
  <img src="/assets/socialstream-logo-horizontal-small-dark.svg" alt="SocialStream">
  <h1>Ez az oldal nem létezik.</h1>
  <p>Lehet, hogy elírás van a címben, vagy ez az oldal már nem él.</p>
  <a class="btn" href="/">Vissza a főoldalra</a>
  <p class="en">This page doesn't exist. <a href="/">Go to the home page</a>.</p>
</main>
</body>
</html>
`);
if (!fs.existsSync(path.join(OUT, 'assets/socialstream-logo-horizontal-small-dark.svg'))) throw new Error('404.html names a logo the site does not carry');

// check the result the way Pulse will take it
const all = [];
const walk = d => { for (const e of fs.readdirSync(d, { withFileTypes: true })) { const p = path.join(d, e.name); if (e.isSymbolicLink()) throw new Error('symlink in the site: ' + p); if (e.isDirectory()) walk(p); else all.push(p); } };
walk(OUT);
const bytes = all.reduce((t, f) => t + fs.statSync(f).size, 0);
if (all.length > LIMIT_FILES || bytes > LIMIT_MB * 1048576) throw new Error(`too big for Pulse: ${all.length} files, ${(bytes / 1048576).toFixed(1)} MB`);
console.log(`${OUT}: ${all.length} files, ${(bytes / 1048576).toFixed(1)} MB (${assets.length} assets, ${root.length} root icons; contact ${email})`);
