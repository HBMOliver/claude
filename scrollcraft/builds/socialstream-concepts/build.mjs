// node build.mjs [names]: writes pulse.html, premiere.html, aurora.html, studio.html and mix.html next to this file,
// each from content.mjs (the words), parts.mjs (shared markup) and concepts/<name>.mjs (its own page).
import fs from 'node:fs';
const all = ['pulse', 'premiere', 'aurora', 'studio', 'mix'];
const names = process.argv[2] ? process.argv[2].split(',') : all;
for (const n of names) {
  if (!fs.existsSync(`concepts/${n}.mjs`)) { console.log(`${n}: not written yet`); continue; }
  const mod = await import(`./concepts/${n}.mjs?${Date.now()}`);
  const html = mod.page();
  if (/—/.test(html.replace(/<!--[\s\S]*?-->/g, ''))) throw new Error(`${n}: an em dash in the visible copy`);
  fs.writeFileSync(`${n}.html`, html);
  console.log(`${n}.html`, html.length, 'bytes');
}
