#!/bin/sh
# Packs the installable theme (.rockbox/ only) into dist/Noir.zip.
# Fonts are not in git: run tools/make_fonts.sh first.
set -e
ROOT=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT"
for f in 14-Noir-Mono 15-Noir-Mono 14-SF-Pro-Rounded-Semibold 16-SF-Pro-Rounded-Semibold \
         20-SF-Pro-Rounded-Semibold 22-SF-Pro-Rounded-Semibold; do
    [ -f ".rockbox/fonts/$f.fnt" ] || { echo "missing .rockbox/fonts/$f.fnt — run tools/make_fonts.sh" >&2; exit 1; }
done
mkdir -p dist
rm -f dist/Noir.zip
zip -rq -X dist/Noir.zip .rockbox -x '*.DS_Store'
echo "dist/Noir.zip: $(unzip -l dist/Noir.zip | tail -1 | awk '{print $2}') files"
