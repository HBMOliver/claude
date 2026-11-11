// node tools/artifact.mjs [orbit|screen|bento ...]   (no argument: all three)
// Package each template as a claude.ai Artifact page: the host wraps the page in its own
// <html>/<head>/<body>, so strip those (the body's classes, the palette among them, move to the
// root element), inline the shared stylesheets, the template's look and every local script
// (no other script hosts are allowed), and keep assets/ as published files next to the page.
// Each template is written to dist/<name>/index.html.
import fs from 'node:fs';
const TITLES = { orbit: 'SocialStream Orbit', screen: 'SocialStream Screen', bento: 'SocialStream Bento' };
// Function replacements, so a "$&" or "$'" inside the inlined code is never read as a pattern.
function swap(s, from, to) { if (!s.includes(from)) throw new Error('not found: ' + from); return s.replace(from, () => to); }
const want = process.argv.slice(2).length ? process.argv.slice(2) : Object.keys(TITLES);
for (const name of want) {
  if (!TITLES[name]) throw new Error('unknown template: ' + name);
  const src = fs.readFileSync(name + '.html', 'utf8');
  let head = src.slice(src.indexOf('<head>') + 6, src.indexOf('</head>'));
  const open = src.match(/<body class="([^"]*)">/);
  if (!open) throw new Error(name + ': no <body class>');
  let body = src.slice(src.indexOf(open[0]) + open[0].length, src.lastIndexOf('</body>'));
  head = head.replace(/<meta charset[^>]*>\s*/, '').replace(/<meta name="viewport"[^>]*>\s*/, '');
  head = swap(head, '<title>SocialStream</title>', '<title>' + TITLES[name] + '</title>\n<meta name="claude:viewport-fit-sides" content="cover">');
  head = swap(head, '<link rel="stylesheet" href="scrollcraft.css">', '<style>\n' + fs.readFileSync('scrollcraft.css', 'utf8') + '\n</style>');
  head = swap(head, '<link rel="stylesheet" href="base.css">', '<style>\n' + fs.readFileSync('base.css', 'utf8') + '\n</style>');
  // each template's own look
  head = swap(head, '<link rel="stylesheet" href="look-' + name + '.css">', '<style>\n' + fs.readFileSync('look-' + name + '.css', 'utf8') + '\n</style>');
  // the palette class sits on <body> in the page; the host owns <body>, so a first script puts it on the root element,
  // which is there whether or not the host has opened <body> yet
  body = '<script>document.documentElement.classList.add(' + open[1].split(/\s+/).filter(Boolean).map(c => JSON.stringify(c)).join(', ') + ');</script>\n' + body.trim();
  body = body.replace(/<script src="([a-z0-9-]+\.js)"><\/script>/g, (m, f) => '<script>\n' + fs.readFileSync(f, 'utf8').replace(/<\/script/gi, '<\\/script') + '\n</script>');
  if (/<script src=/.test(body) || /<link rel="stylesheet" href="(?!https:)/.test(head)) throw new Error(name + ': something local was left un-inlined');
  fs.mkdirSync('dist/' + name, { recursive: true });
  fs.writeFileSync('dist/' + name + '/index.html', head.trim() + '\n' + body + '\n');
  console.log('dist/' + name + '/index.html', fs.statSync('dist/' + name + '/index.html').size, 'bytes');
}
