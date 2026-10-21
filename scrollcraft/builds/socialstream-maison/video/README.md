# Stream film recipe

The hero film for Maison, Journal and Noir. Vertical cards of the FlyX Tenerife
footage flow like a feed being scrolled; the feed stops, one card blooms to full
frame and plays, then folds back into the stream. Four blooms per 24 s loop. The
loop starts inside the first bloom, so the seam is hidden and the first frame
(the poster) is already full-bleed footage.

`stream.swift` renders an edit file into a silent H.264 MP4 with AVFoundation
(no ffmpeg needed): HDR HLG is tone-mapped to Rec.709 by the reader, then one
warm, soft filmic grade. The ground behind the cards is a parameter, so the same
edit renders on cream (Maison, Journal) or on warm black (Noir). Paths in the
edit files point at the local copies of the Drive footage under
`~/Movies/CapCut/funny assets/drive*`.

    swiftc -swift-version 5 -O stream.swift -o stream
    CREAM=0.937,0.914,0.874
    INK=0.075,0.071,0.066
    ./stream film-wide.json 1920 1080 3400000 ../assets/film-wide-1080.mp4 $CREAM stills-wide
    ./stream film-tall.json 1080 1920 3200000 ../../socialstream-journal/assets/film-tall-1080.mp4 $CREAM stills-tall
    ./stream film-tall.json 720 1280 1500000 ../assets/film-tall-720.mp4 $CREAM
    ./stream film-tall.json 1080 1920 3200000 ../../socialstream-split-noir/assets/film-ink-1080.mp4 $INK stills-ink
    ./stream film-tall.json 720 1280 1500000 ../../socialstream-split-noir/assets/film-ink-720.mp4 $INK

`film-wide.json` (16:9, desktop Maison) and `film-tall.json` (9:16, phones and
the Journal cover) share 26 feed cards and differ in two blooms: the wide edit
blooms 23_IMG_0871, b148_IMG_0474, b216_IMG_6214 and 37_IMG_1193; the tall one
swaps in b242_IMG_6987 and 21_IMG_0842, which hold their subject in a vertical
frame. The page reads the bloom windows from the video's `data-beats`
(`[start, end]` in seconds, wrapping at the loop point) and switches its four
manifesto lines on the film's own clock, so the film carries no text and works
in both languages.

## Loops and stills

The thumb-stop cards, the Journal plates and the photograph band are cut with
`../../socialstream-split/video/cut.swift` and its `GRADE=warm` switch (the
same warm grade as the film, without the vignette). One edit file per piece in
`loops/`:

    GRADE=warm ./cut loops/pirate.json 540 960 1100000 loop-pirate.mp4 st-pirate
    GRADE=warm ./cut loops/ed-cinema.json 1200 1500 4000000 x-ed-cinema.mp4 st-ed-cinema
    GRADE=warm ./cut loops/band.json 2400 1030 6000000 x-band.mp4 st-band

The stills directory gets the first frame as `poster.jpg`, which becomes the
card poster (`assets/loop-*.jpg`). Plates and the band are those stills cropped
and resized with `../../socialstream-split/video/img.swift`, for example
`img st-band/s00.jpg ../assets/band-screen.jpg 2400 1030 0.5 0.5 1 0.8`.
