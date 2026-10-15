# SocialStream hero sizzle

Motion-graphics sizzle for the website hero, cut from SocialStream's own client
footage. `render.html` draws any moment of the 30 s timeline (1920x1080, 25 fps);
`render.mjs` screenshots every frame with headless Chromium; ffmpeg encodes.

    node render.mjs <dir> 0 30          # frames to <dir>/out
    ffmpeg -framerate 25 -i out/%05d.jpg -c:v libx264 -crf 23 -pix_fmt yuv420p -an hero.mp4

Frames are extracted from the source clips into `frames/<clip>-s` (216x384 tiles)
and `frames/<clip>-l` (608x1080), with `manifest.json` listing frame counts.

## Delivered files (Higgsfield storage, public)

- 1080p, 30 s, silent, 8.0 MB: https://d2ol7oe51mr4n9.cloudfront.net/user_3Hzci0f7dFf3ca1p4x3SQpjBiuR/8a14c8e0-2e67-4255-93e6-6b3cc5a7c1d5.mp4
- 720p, 3.3 MB (phones): https://d2ol7oe51mr4n9.cloudfront.net/user_3Hzci0f7dFf3ca1p4x3SQpjBiuR/b8a81f85-5009-49d9-b8d9-d8c620e28a9b.mp4
- Poster frame: https://d2ol7oe51mr4n9.cloudfront.net/user_3Hzci0f7dFf3ca1p4x3SQpjBiuR/e4157f44-b968-4e84-a961-9462a9a1b60c.jpg

Rendered in the Higgsfield sandbox from the five clips in the client's Drive folder
(no generation credits used). For production, download these and serve them from
your own host next to the page.
