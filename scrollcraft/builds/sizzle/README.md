# SocialStream hero sizzle

Motion-graphics sizzle for the website hero, cut from SocialStream's own client
footage. `render.html` draws any moment of the 30 s timeline (1920x1080, 25 fps);
`render.mjs` screenshots every frame with headless Chromium; ffmpeg encodes.

    node render.mjs <dir> 0 30          # frames to <dir>/out
    ffmpeg -framerate 25 -i out/%05d.jpg -c:v libx264 -crf 23 -pix_fmt yuv420p -an hero.mp4

Frames are extracted from the source clips into `frames/<clip>-s` (216x384 tiles)
and `frames/<clip>-l` (608x1080), with `manifest.json` listing frame counts.
