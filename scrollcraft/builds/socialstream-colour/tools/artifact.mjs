// node tools/artifact.mjs [riviera|dusk|paper|ember|lagoon|velvet ...]   (no argument: all six)
// Package the site as claude.ai Artifact pages, one per colour world: the host wraps the page in
// its own <html>/<head>/<body>, so strip those, inline the stylesheet and every local script (no
// other script hosts are allowed), fix the look, and keep assets/ as published files next to the
// page. Each look is written to dist/<look>/index.html.
import fs from 'node:fs';
const LOOKS = { riviera: 'SocialStream Riviera', dusk: 'SocialStream Dusk', paper: 'SocialStream Paper', ember: 'SocialStream Ember', lagoon: 'SocialStream Lagoon', velvet: 'SocialStream Velvet' };
const src = fs.readFileSync('index.html', 'utf8');
// Function replacements, so a "$&" or "$'" inside the inlined code is never read as a pattern.
function swap(s, from, to) { if (!s.includes(from)) throw new Error('not found in index.html: ' + from); return s.replace(from, () => to); }
const want = process.argv.slice(2).length ? process.argv.slice(2) : Object.keys(LOOKS);
for (const look of want) {
  if (!LOOKS[look]) throw new Error('unknown look: ' + look);
  let head = src.slice(src.indexOf('<head>') + 6, src.indexOf('</head>'));
  let body = src.slice(src.indexOf('<body>') + 6, src.lastIndexOf('</body>'));
  head = head.replace(/<meta charset[^>]*>\s*/, '').replace(/<meta name="viewport"[^>]*>\s*/, '');
  head = swap(head, '<title>SocialStream</title>', '<title>' + LOOKS[look] + '</title>\n<meta name="claude:viewport-fit-sides" content="cover">');
  head = swap(head, '<script>/* which colour world', '<script>window.__LOOK = "' + look + '";</script>\n<script>/* which colour world');
  head = swap(head, '<link rel="stylesheet" href="scrollcraft.css">', '<style>\n' + fs.readFileSync('scrollcraft.css', 'utf8') + '\n</style>');
  body = body.replace(/<script src="([a-z0-9-]+\.js)"><\/script>/g, (m, f) => '<script>\n' + fs.readFileSync(f, 'utf8').replace(/<\/script/gi, '<\\/script') + '\n</script>');
  if (/<script src=/.test(body)) throw new Error('a script was left un-inlined');
  fs.mkdirSync('dist/' + look, { recursive: true });
  fs.writeFileSync('dist/' + look + '/index.html', head.trim() + '\n' + body.trim() + '\n');
  console.log('dist/' + look + '/index.html', fs.statSync('dist/' + look + '/index.html').size, 'bytes');
}
