# Hero video recipe

`cut.swift` renders `edl.json` (41 shots, 30 fps, every in-point and crop) into a
graded, silent H.264 MP4 with AVFoundation, no ffmpeg needed. Paths in the edit
list point at the local copies of the Drive folders ("Internal Promo Material"
clips under `~/Movies/CapCut/funny assets/drive*`, "interveiw 6.0 j.mp4",
"6. rész.mp4").

    swiftc -swift-version 5 -O cut.swift -o cut
    ./cut edl.json 1080 1920 3300000 ../assets/hero-1080.mp4 stills/
    ./cut edl.json 720 1280 1600000 ../assets/hero-720.mp4

The grade is one 33-point LUT built in `makeLUT` (filmic contrast, petrol
shadows, amber highlights, violet screens pulled to teal, greens toward teal).
`GRADE=warm ./cut ...` swaps in `makeWarmLUT` (soft filmic contrast, 20% less
saturation, warm shadows and highlights, no vignette), the grade used for the
Maison, Journal and Noir loops and stills; see `../../socialstream-maison/video/`.
`sheet.swift` makes timestamped contact sheets for picking shots; `img.swift`
cuts the stream tiles and portraits.
