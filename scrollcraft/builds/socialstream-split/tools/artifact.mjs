// Package the site as a claude.ai Artifact page: the host wraps the page in its own
// <html>/<head>/<body>, so strip those, inline the engine (no other script hosts are
// allowed) and keep assets/ as published files next to the page.
import fs from 'node:fs';
const src = fs.readFileSync('index.html', 'utf8');
const css = fs.readFileSync('scrollcraft.css', 'utf8');
const js = fs.readFileSync('scrollcraft.js', 'utf8');
let head = src.slice(src.indexOf('<head>') + 6, src.indexOf('</head>'));
let body = src.slice(src.indexOf('<body>') + 6, src.lastIndexOf('</body>'));
head = head
  .replace(/<meta charset[^>]*>\s*/, '')
  .replace(/<meta name="viewport"[^>]*>\s*/, '')
  .replace('<title>SocialStream</title>', '<title>SocialStream Split Stage</title>')
  .replace('<link rel="stylesheet" href="scrollcraft.css">', '<style>\n' + css + '\n</style>');
body = body.replace('<script src="scrollcraft.js"></script>', '<script>\n' + js.replace(/<\/script/gi, '<\\/script') + '\n</script>');
fs.mkdirSync('dist', { recursive: true });
fs.writeFileSync('dist/index.html', head.trim() + '\n' + body.trim() + '\n');
console.log('dist/index.html', fs.statSync('dist/index.html').size, 'bytes');
