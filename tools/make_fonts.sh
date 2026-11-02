#!/bin/sh
# Builds Noir's fonts (Latin + Cyrillic) from the macOS SF Mono / SF Pro Rounded system fonts.
# Requires: brew install freetype pkgconf
set -e
HERE=$(cd "$(dirname "$0")" && pwd)
RB="$HERE/../.rockbox"
WORK="$HERE/.build"
mkdir -p "$WORK" "$RB/fonts"
cd "$WORK"

[ -f convttf.c ] || curl -sSL -o convttf.c https://raw.githubusercontent.com/Rockbox/rockbox/master/tools/convttf.c
[ -x convttf ]   || cc -O2 -o convttf convttf.c $(pkg-config --cflags --libs freetype2)

# -s 32 .. -l 0x2122: Latin, Cyrillic (incl. Ukrainian), dashes/quotes, ™
# SF Mono (ui-monospace) from macOS: status bar + file info. Apple font, personal use only.
MONO=/System/Library/Fonts/SFNSMono.ttf
# Variable font: default instance is Light. -t (N<<16) picks named instance N:
# 1 Light, 2 Regular, 3 Medium, 4 Semibold, 5 Bold, 6 Heavy.
WEIGHT=$((5 << 16))  # Bold
./convttf -s 32 -l 8482 -p 15 -t $WEIGHT -o "$RB/fonts/15-Noir-Mono.fnt" "$MONO" >/dev/null
./convttf -s 32 -l 8482 -p 14 -t $WEIGHT -o "$RB/fonts/14-Noir-Mono.fnt" "$MONO" >/dev/null

# SF Pro Rounded Semibold (named instance 7), like reFresh: title 22, menu 20, artist/album 16, genre 14.
ROUNDED=/System/Library/Fonts/SFNSRounded.ttf
for size in 22 20 16 14; do
    ./convttf -s 32 -l 8482 -p $size -t $((7 << 16)) -o "$RB/fonts/$size-SF-Pro-Rounded-Semibold.fnt" "$ROUNDED" >/dev/null
done

echo "Fonts built."
