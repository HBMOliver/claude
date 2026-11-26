#!/bin/zsh
# Puts the SocialStream film in the place of the "Tahoe Day" moving wallpaper on this Mac (macOS 26), after
# keeping Apple's own file. Works from the project folder (it then copies the wallpaper files into Pictures
# first) and from the Pictures folder itself (to put the film back after an update of macOS).
# Unofficial: macOS has no setting for one's own lock-screen film. To undo: restore-lock-screen.sh
set -e
HERE="${0:A:h}"
SLOT="$HOME/Library/Application Support/com.apple.wallpaper/aerials/videos/4C108785-A7BA-422E-9C79-B0129F1D5550.mov"
KEEP="$HOME/Pictures/SocialStream wallpaper"
FILM="$KEEP/SocialStream-lock-screen.mov"
[[ -f "$SLOT" ]] || { echo "The Tahoe Day film is not on this Mac. Choose Tahoe Day once in System Settings > Wallpaper, wait for its download, then run this again."; exit 1; }
# the film is too large for the repo: a fresh checkout has the stills only
if [[ ! -f "$HERE/final/SocialStream-lock-screen.mov" && ! -f "$FILM" ]]; then
  echo "The lock-screen film is not here. Make it with film.sh (see README.md), or copy SocialStream-lock-screen.mov from a Mac that has it into: $KEEP"
  exit 1
fi
mkdir -p "$KEEP/Apple original"
if [[ -d "$HERE/final" ]]; then                # run from the project folder: bring the files to Pictures
  for f in "$HERE"/final/SocialStream-*(N); do cp "$f" "$KEEP/"; done    # (N): no error when a kind is missing
  cp "$HERE/restore-lock-screen.sh" "$HERE/install-lock-screen.sh" "$KEEP/"
fi
[[ -f "$FILM" ]] || { echo "Missing: $FILM"; exit 1; }
if cmp -s "$SLOT" "$FILM"; then
  echo "The SocialStream film is already in place: only restarting the wallpaper."
else
  if [[ ! -f "$KEEP/Apple original/Tahoe Day.mov" ]]; then
    cp -p "$SLOT" "$KEEP/Apple original/Tahoe Day.mov"
    echo "Kept Apple's film in: $KEEP/Apple original/Tahoe Day.mov"
  fi
  cp "$FILM" "$SLOT.new"
  mv "$SLOT.new" "$SLOT"
fi
# the two programs that show the wallpaper; macOS starts them again by itself. Run this script again whenever the
# desktop picture has gone black or the lock screen has stopped moving: restarting them is the cure.
killall WallpaperAerialsExtension 2>/dev/null || true
killall WallpaperAgent 2>/dev/null || true
echo "Done. Lock the screen (Control-Command-Q) to see it."
