// node tools/artifact.mjs [page]
// Package a page as a claude.ai Artifact page: the host wraps it in its own <html>/<head>/<body>,
// so strip those, inline the stylesheets and the local scripts (no other script hosts are allowed),
// and keep assets/ as published files next to the page.
//   index (the default)  -> dist/daylight/index.html
//   hero-cinema          -> dist/cinema/index.html    (run tools/heroes.mjs first)
//   hero-glow            -> dist/glow/index.html
//   hero-capsule         -> dist/capsule/index.html
import fs from 'node:fs';
const PAGES = {
  index: ['daylight', 'SocialStream Daylight'],
  'hero-cinema': ['cinema', 'Daylight Cinema'],
  'hero-glow': ['glow', 'Daylight Glow'],
  'hero-capsule': ['capsule', 'Daylight Capsule'],
};
const page = process.argv[2] || 'index';
if (!PAGES[page]) throw new Error('unknown page: ' + page + ' (one of ' + Object.keys(PAGES).join(', ') + ')');
const [dir, title] = PAGES[page];
// Function replacements, so a "$&" or "$'" inside the inlined code is never read as a pattern.
function swap(s, from, to) { if (!s.includes(from)) throw new Error('not found: ' + from); return s.replace(from, () => to); }
const src = fs.readFileSync(page + '.html', 'utf8');
let head = src.slice(src.indexOf('<head>') + 6, src.indexOf('</head>'));
let body = src.slice(src.indexOf('<body>') + 6, src.lastIndexOf('</body>'));
head = head.replace(/<meta charset[^>]*>\s*/, '').replace(/<meta name="viewport"[^>]*>\s*/, '');
head = swap(head, '<title>SocialStream</title>', '<title>' + title + '</title>\n<meta name="claude:viewport-fit-sides" content="cover">');
head = head.replace(/<link rel="stylesheet" href="([a-z0-9-]+\.css)">/g, (m, f) => '<style>\n' + fs.readFileSync(f, 'utf8') + '\n</style>');
body = body.replace(/<script src="([a-z0-9-]+\.js)"><\/script>/g, (m, f) => '<script>\n' + fs.readFileSync(f, 'utf8').replace(/<\/script/gi, '<\\/script') + '\n</script>');
if (/<script src=/.test(body) || /<link rel="stylesheet" href="(?!https:)/.test(head)) throw new Error('something local was left un-inlined');
fs.mkdirSync('dist/' + dir, { recursive: true });
fs.writeFileSync('dist/' + dir + '/index.html', head.trim() + '\n' + body.trim() + '\n');
console.log('dist/' + dir + '/index.html', fs.statSync('dist/' + dir + '/index.html').size, 'bytes');
