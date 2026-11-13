# Review: SocialStream logo animation, horizontal (2026-11-13)

## Creative calls

- One storyline, the logo's own construction (phone, S, lean, cut, name), because the mark's idea is that
  construction. Not built: an opening on a wall of reels (the brand film already opens that way), a version
  with sound, a version where the phone stays large.
- Restraint: one move at a time; the only overlap is the name starting 0.2 s before the phone lands, so it
  comes out from behind the phone rather than from empty space.
- The S stays a filled Night shape while it moves (on Night it looks like the see-through S). In a transparent
  export it would show as a Night S, which matches the kit's corner mark for video.

## Measured

- `npx hyperframes check`: passes, no errors or warnings (one note: no sound).
- Last frame against the kit master, both rendered through the HyperFrames pipeline: identical apart from 32
  isolated edge pixels that differ by one anti-aliasing sample (mean difference 0.002 levels).
- The delivery MP4 against the lossless last frame: mean difference 1 level, largest 12; Night, Cream and
  Stream Blue within 2 levels in flat areas. H.264, BT.709 tags, 138 frames.

## Looked at, not measured

- Snapshots at every beat, zooms on the phone's edge before the cut, on the cut opening and on the A's cut, a
  10 fps filmstrip of the first 3 s, and the phone-width sheet (360 px).
- Not checked: playback on a real phone, and how Instagram, TikTok or YouTube recompress it. Nobody listened,
  because there is no sound.

## Weakest shot

The A's cut (2.32 s) is about 3 px wide at 1080p, so it reads as a detail, not a beat. With more time: a sound
hit on the phone's cut and an echo on the A's, or a slower A cut.

## Kept on purpose

- The first frame is empty Night: a sting starts from its ground. Use the last frame as the cover image.
- No sound: it is a 4.6 s sting; a sound version is an option.
- The lean's ~1° overshoot: it is the phone leaning in, not a bouncing UI element.
- At phone width (360 px) the lockup is 216 px wide, below the kit's 250 px minimum for the primary drawing, and
  the phone's slice gets thin there. Phone feeds should get the vertical and square versions (not made yet).
