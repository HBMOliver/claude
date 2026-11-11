// node tools/artifact.mjs
// Package the page as a claude.ai Artifact page: the host wraps it in its own <html>/<head>/<body>,
// so strip those, inline the stylesheet and both local scripts (no other script hosts are allowed),
// and keep assets/ as published files next to the page. Written to dist/daylight/index.html.
import fs from 'node:fs';
// Function replacements, so a "$&" or "$'" inside the inlined code is never read as a pattern.
function swap(s, from, to) { if (!s.includes(from)) throw new Error('not found: ' + from); return s.replace(from, () => to); }
const src = fs.readFileSync('index.html', 'utf8');
let head = src.slice(src.indexOf('<head>') + 6, src.indexOf('</head>'));
let body = src.slice(src.indexOf('<body>') + 6, src.lastIndexOf('</body>'));
head = head.replace(/<meta charset[^>]*>\s*/, '').replace(/<meta name="viewport"[^>]*>\s*/, '');
head = swap(head, '<title>SocialStream</title>', '<title>SocialStream Daylight</title>\n<meta name="claude:viewport-fit-sides" content="cover">');
head = swap(head, '<link rel="stylesheet" href="daylight.css">', '<style>\n' + fs.readFileSync('daylight.css', 'utf8') + '\n</style>');
body = body.replace(/<script src="([a-z0-9-]+\.js)"><\/script>/g, (m, f) => '<script>\n' + fs.readFileSync(f, 'utf8').replace(/<\/script/gi, '<\\/script') + '\n</script>');
if (/<script src=/.test(body) || /<link rel="stylesheet" href="(?!https:)/.test(head)) throw new Error('something local was left un-inlined');
fs.mkdirSync('dist/daylight', { recursive: true });
fs.writeFileSync('dist/daylight/index.html', head.trim() + '\n' + body.trim() + '\n');
console.log('dist/daylight/index.html', fs.statSync('dist/daylight/index.html').size, 'bytes');
