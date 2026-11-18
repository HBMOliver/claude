// Renders the composition page frame by frame and pipes JPEG frames into ffmpeg.
// usage: node render.js <cfg.json> <out.mp4> [fromFrame] [toFrame]
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

(async () => {
  const [cfgPath, outPath, fromArg, toArg] = process.argv.slice(2);
  const cfg = JSON.parse(fs.readFileSync(cfgPath, 'utf8'));
  const N = Math.round(cfg.duration * cfg.fps);
  const from = fromArg ? parseInt(fromArg, 10) : 0;
  const to = toArg ? Math.min(parseInt(toArg, 10), N) : N;
  const browser = await chromium.launch({ args: ['--font-render-hinting=none', '--disable-lcd-text'] });
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  page.on('console', m => { if (m.type() === 'error') console.error('[page]', m.text()); });
  page.on('pageerror', e => console.error('[pageerror]', e.message));
  await page.goto('file://' + path.join(__dirname, 'render.html'));
  await page.evaluate(c => window.init(c), cfg);
  if (outPath.endsWith('.jpg') || outPath.endsWith('.png')) {           // still mode: render one frame
    await page.evaluate(t => window.renderAt(t), from / cfg.fps);
    await page.screenshot({ path: outPath, type: outPath.endsWith('.png') ? 'png' : 'jpeg', quality: outPath.endsWith('.png') ? undefined : 92 });
    await browser.close(); return;
  }
  const ff = spawn('ffmpeg', ['-y', '-v', 'error', '-f', 'image2pipe', '-framerate', String(cfg.fps), '-c:v', 'mjpeg', '-i', '-',
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '16', '-pix_fmt', 'yuv420p', '-r', String(cfg.fps), outPath], { stdio: ['pipe', 'inherit', 'inherit'] });
  const t0 = Date.now();
  for (let i = from; i < to; i++) {
    await page.evaluate(t => window.renderAt(t), i / cfg.fps);
    const buf = await page.screenshot({ type: 'jpeg', quality: 94 });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if ((i - from) % 90 === 0) console.log(`frame ${i}/${to} (${((Date.now() - t0) / 1000).toFixed(1)}s)`);
  }
  ff.stdin.end();
  await new Promise(r => ff.on('close', r));
  await browser.close();
  console.log('done', outPath, ((Date.now() - t0) / 1000).toFixed(1) + 's');
})().catch(e => { console.error(e); process.exit(1); });
