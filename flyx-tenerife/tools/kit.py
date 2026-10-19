"""Build FlyX-GHL-Kit.zip: paste-in code, images, image-link helper, guide, and a standalone copy.
Run after tools/build.py: python3 flyx-tenerife/tools/kit.py"""
import json, pathlib, re, shutil, zipfile
root = pathlib.Path(__file__).resolve().parent.parent
out = root / 'dist' / 'FlyX-GHL-Kit'
if out.exists(): shutil.rmtree(out)
(out / 'images').mkdir(parents=True)
embed = (root / 'ghl-embed.html').read_text()
base = re.search(r'https://cdn\.jsdelivr\.net/gh/[^"\s]+?/flyx-tenerife/assets/', embed).group(0)
images = sorted(set(re.findall(re.escape(base) + r'([a-z]+\.(?:jpg|png))', embed)))
for name in images: shutil.copy(root / 'assets' / name, out / 'images' / name)
(out / '1-paste-into-GHL.html').write_text(embed)

# Image-link helper: paste Media Library links, get updated code
fields = "\n".join(f'<label><span>{n}</span><input id="f-{n}" placeholder="{base}{n}"></label>' for n in images)
helper = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>FlyX image link helper</title>
<style>
body {{ margin: 0; font: 15px/1.5 system-ui, sans-serif; background: #f4f6f6; color: #0d2b31; }}
main {{ max-width: 860px; margin: 0 auto; padding: 32px 20px 60px; display: grid; gap: 18px; }}
h1 {{ font-weight: 500; margin: 0; }} p {{ margin: 0; color: #55676b; }}
.box {{ background: #fff; border-radius: 14px; padding: 20px; display: grid; gap: 12px; box-shadow: 0 1px 0 rgba(0,0,0,.06); }}
label {{ display: grid; grid-template-columns: 120px 1fr; gap: 12px; align-items: center; }}
label span {{ font: 600 13px/1 system-ui; }}
input {{ font: 13px/1.4 ui-monospace, monospace; padding: 9px 10px; border: 1px solid #cfd8d9; border-radius: 8px; min-width: 0; }}
button {{ justify-self: start; font: 600 14px/1 system-ui; padding: 12px 18px; border: 0; border-radius: 999px; background: #b07d27; color: #1c1305; cursor: pointer; }}
textarea {{ width: 100%; height: 220px; box-sizing: border-box; font: 12px/1.4 ui-monospace, monospace; border: 1px solid #cfd8d9; border-radius: 8px; padding: 10px; }}
#msg {{ font-weight: 600; color: #0e5866; min-height: 1.2em; }}
@media (max-width: 560px) {{ label {{ grid-template-columns: 1fr; gap: 4px; }} }}
</style></head><body><main>
<h1>FlyX image link helper</h1>
<p>Upload the files from the <b>images</b> folder to your GoHighLevel Media Library. Copy each file's link and paste it next to its name. Leave a field empty to keep the current link. Then press <b>Build code</b> and paste the result into the Custom JS/HTML element.</p>
<div class="box">{fields}<button type="button" id="build">Build code</button></div>
<div class="box"><textarea id="out" readonly aria-label="Updated code"></textarea><button type="button" id="copy">Copy code</button><span id="msg"></span></div>
</main>
<script>
const CODE = {json.dumps(embed).replace('</', '<\\/')};
const BASE = {json.dumps(base)};
const NAMES = {json.dumps(images)};
const out = document.getElementById('out'), msg = document.getElementById('msg');
function build() {{
  let code = CODE, n = 0;
  NAMES.forEach(name => {{
    const v = document.getElementById('f-' + name).value.trim();
    if (v) {{ code = code.split(BASE + name).join(v); n++; }}
  }});
  out.value = code;
  msg.textContent = n ? 'Code built with ' + n + ' of ' + NAMES.length + ' Media Library links.' : 'Code built with the current links.';
}}
document.getElementById('build').addEventListener('click', build);
document.getElementById('copy').addEventListener('click', async () => {{
  if (!out.value) build();
  try {{ await navigator.clipboard.writeText(out.value); msg.textContent = 'Copied. Paste it into the Custom JS/HTML element.'; }}
  catch {{ out.select(); msg.textContent = 'Selected. Press Ctrl+C (Cmd+C on Mac) to copy.'; }}
}});
build();
</script></body></html>"""
(out / '2-image-link-helper.html').write_text(helper)

# Standalone copy for regular hosting (fallback)
sa = out / 'standalone-site'
(sa / 'assets' / 'js').mkdir(parents=True)
shutil.copy(root / 'index.html', sa / 'index.html')
for name in images: shutil.copy(root / 'assets' / name, sa / 'assets' / name)
for js in (root / 'assets' / 'js').glob('*.js'): shutil.copy(js, sa / 'assets' / 'js' / js.name)
shutil.copy(root / 'GHL-SETUP.md', out / 'README.md')

z = root / 'dist' / 'FlyX-GHL-Kit.zip'
with zipfile.ZipFile(z, 'w', zipfile.ZIP_DEFLATED) as zf:
    for f in sorted(out.rglob('*')):
        if f.is_file(): zf.write(f, f.relative_to(out.parent))
print('images:', images); print('kit:', z, z.stat().st_size // 1024, 'KB')
