# Review: SocialStream logo animation, vertical (2026-11-13)

Covers the square version too (`../square/`): same build, same checks, same results.

## Creative calls

- The founder approved the horizontal's motion, so the phone's beats and the clock are unchanged.
- The stacked lockup, the kit's form for tall and square frames. Its name sits under the phone, so it drops out
  from under the phone instead of streaming out sideways: SOCIAL first, then STREAM from under SOCIAL, in
  reading order.
- The phone's size during its beats is 38 % of the frame height in the vertical (as in the horizontal) and 45 %
  in the square, so the square's move into the lockup is smaller (2.1× instead of 3.2×).

## Measured

- `npx hyperframes check`: passes for both, no errors or warnings (one note: no sound).
- Last frame against the kit's stacked dark master, both rendered through the HyperFrames pipeline: identical
  apart from 186 (vertical) and 187 (square) edge pixels that differ by one or two anti-aliasing samples (mean
  difference 0.006 and 0.01 levels), most of them along STREAM's baseline. The kit file stores coordinates to
  0.01 of its 256 px tall drawing, which at this size moves an edge by up to 0.014 px.
- The delivery MP4s against the lossless last frames: mean difference 2 levels, largest 13. Inside flat areas
  the median Cream, Stream Blue and Night are within 4 levels of the true colours (single pixels up to 8).
  H.264, BT.709 tags, 138 frames each.

## Looked at, not measured

- 10 fps filmstrips of the first 3 s of both, full-resolution frames of the name drop, the review sheet and the
  phone-width sheet.
- Not checked: playback on a phone, how Instagram and TikTok recompress it, and their buttons and captions over
  it. The logo sits between 35 % and 65 % of the height and 20 % and 80 % of the width, clear of where those
  usually go.

## Weakest shot

SOCIAL appears from a level edge that runs past the phone on both sides, so outside the phone's width it reads as
a mask more than in the horizontal, where the edge is the phone's own side. The A's cut is about 8 px wide here.

## Kept on purpose

The first frame is empty Night (use the last frame as the cover) and there is no sound, as in the horizontal.
