#!/bin/zsh
# Puts Apple's "Tahoe Day" film back where install-lock-screen.sh replaced it.
set -e
SLOT="$HOME/Library/Application Support/com.apple.wallpaper/aerials/videos/4C108785-A7BA-422E-9C79-B0129F1D5550.mov"
ORIG="$HOME/Pictures/SocialStream wallpaper/Apple original/Tahoe Day.mov"
[[ -f "$ORIG" ]] || { echo "Apple's film was not kept at: $ORIG. Choose another wallpaper in System Settings > Wallpaper instead."; exit 1; }
cp -p "$ORIG" "$SLOT.new"
mv "$SLOT.new" "$SLOT"
killall WallpaperAerialsExtension 2>/dev/null || true
killall WallpaperAgent 2>/dev/null || true
echo "Apple's Tahoe Day film is back."
