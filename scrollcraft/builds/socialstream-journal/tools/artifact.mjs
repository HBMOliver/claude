// Package the site as a claude.ai Artifact page: the host wraps the page in its own
// <html>/<head>/<body>, so strip those, inline the engine and the site script (no
// other script hosts are allowed) and keep assets/ as published files next to the page.
import fs from 'node:fs';
const TITLE = 'SocialStream Journal';
const src = fs.readFileSync('index.html', 'utf8');
const inline = (f) => '<script>\n' + fs.readFileSync(f, 'utf8').replace(/<\/script/gi, '<\\/script') + '\n</script>';
// Function replacements, so a "$&" or "$'" inside the inlined code is never read as a pattern.
function swap(s, from, to) { if (!s.includes(from)) throw new Error('not found in index.html: ' + from); return s.replace(from, () => to); }
let head = src.slice(src.indexOf('<head>') + 6, src.indexOf('</head>'));
let body = src.slice(src.indexOf('<body>') + 6, src.lastIndexOf('</body>'));
head = head.replace(/<meta charset[^>]*>\s*/, '').replace(/<meta name="viewport"[^>]*>\s*/, '');
head = swap(head, '<title>SocialStream</title>', '<title>' + TITLE + '</title>');
head = swap(head, '<link rel="stylesheet" href="scrollcraft.css">', '<style>\n' + fs.readFileSync('scrollcraft.css', 'utf8') + '\n</style>');
body = swap(body, '<script src="scrollcraft.js"></script>', inline('scrollcraft.js'));
if (fs.existsSync('site.js')) body = swap(body, '<script src="site.js"></script>', inline('site.js'));
fs.mkdirSync('dist', { recursive: true });
fs.writeFileSync('dist/index.html', head.trim() + '\n' + body.trim() + '\n');
console.log('dist/index.html', fs.statSync('dist/index.html').size, 'bytes');
