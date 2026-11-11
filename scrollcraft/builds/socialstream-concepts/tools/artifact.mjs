// node tools/artifact.mjs [names]   (default: all four; run node build.mjs first)
// Package each concept as a claude.ai Artifact page. The host wraps the page in its own <html>/<head>/<body>,
// so those are stripped; the stylesheets and the local scripts are inlined (no other script hosts are allowed);
// assets/ stays as published files next to the page. For each concept it writes:
//   dist/<name>/index.html   the page to publish
//   dist/<name>/files.json   the assets it uses, as the publish files map: from its markup and styles, plus the
//                            three cuts of the brand film, which kit.js picks between (they are not in the markup)
//   dist/<name>.html         the same page wrapped the way the host wraps it, to test locally
//                            (BASE=http://localhost:4560/dist/ node lab/check.mjs); dist/assets points at assets/
import fs from 'node:fs';
const all = ['pulse', 'premiere', 'aurora', 'studio'];
const names = process.argv[2] ? process.argv[2].split(',') : all;
const FILM = ['assets/hero-540.mp4', 'assets/hero-1080.mp4', 'assets/hero-v-720.mp4'];
fs.mkdirSync('dist', { recursive: true });
if (!fs.existsSync('dist/assets')) fs.symlinkSync('../assets', 'dist/assets');
for (const n of names) {
  const src = fs.readFileSync(n + '.html', 'utf8');
  let head = src.slice(src.indexOf('<head>') + 6, src.indexOf('</head>'));
  let body = src.slice(src.indexOf('<body>') + 6, src.lastIndexOf('</body>'));
  head = head.replace(/<meta charset[^>]*>\s*/, '').replace(/<meta name="viewport"[^>]*>\s*/, '');
  if (!/<title>[^<]+<\/title>/.test(head)) throw new Error(n + ': no title');
  head = head.replace(/(<title>[^<]+<\/title>)/, m => m + '\n<meta name="claude:viewport-fit-sides" content="cover">');
  // function replacements, so a "$&" or "$'" inside the inlined code is never read as a pattern
  head = head.replace(/<link rel="stylesheet" href="([a-z0-9-]+\.css)">/g, (m, f) => '<style>\n' + fs.readFileSync(f, 'utf8') + '\n</style>');
  body = body.replace(/<script src="([a-z0-9-]+\.js)"><\/script>/g, (m, f) => '<script>\n' + fs.readFileSync(f, 'utf8').replace(/<\/script/gi, '<\\/script') + '\n</script>');
  if (/<script src=/.test(body) || /<link rel="stylesheet" href="(?!https:)/.test(head)) throw new Error(n + ': something local was left un-inlined');
  const page = head.trim() + '\n' + body.trim() + '\n';
  // the page's own icon ends up in the body, where the browser ignores it and asks for /favicon.ico; the host sets
  // its own icon, so only the local wrapper needs it in its head
  const icon = (src.match(/<link rel="icon"[^>]*>/) || [''])[0];
  const used = [...new Set([...page.matchAll(/assets\/[A-Za-z0-9._-]+\.(?:webp|jpg|jpeg|png|svg|mp4|webm)/g)].map(m => m[0]).concat(FILM))].sort();
  const missing = used.filter(f => !fs.existsSync(f));
  if (missing.length) throw new Error(n + ': missing ' + missing.join(', '));
  fs.mkdirSync('dist/' + n, { recursive: true });
  fs.writeFileSync('dist/' + n + '/index.html', page);
  fs.writeFileSync('dist/' + n + '/files.json', JSON.stringify(Object.fromEntries(used.map(f => [f, f])), null, 1) + '\n');
  fs.writeFileSync('dist/' + n + '.html', '<!doctype html>\n<html>\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n' + icon + '\n</head>\n<body>\n' + page + '</body>\n</html>\n');
  const bytes = used.reduce((t, f) => t + fs.statSync(f).size, 0);
  console.log(`dist/${n}/index.html ${page.length} bytes, ${used.length} assets (${(bytes / 1048576).toFixed(1)} MB)`);
}
