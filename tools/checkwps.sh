#!/bin/sh
# Validates Noir's skins with Rockbox's own checkwps for the iPod Video (same parser as the player).
# Usage: tools/checkwps.sh [git-ref]   e.g. v4.0-final, or master (default) for daily/dev builds
set -e
REF=${1:-master}
HERE=$(cd "$(dirname "$0")" && pwd)
WORK="$HERE/.build/rockbox-$REF"
if [ ! -d "$WORK" ]; then
    git clone -q --depth 1 --branch "$REF" https://github.com/Rockbox/rockbox.git "$WORK"
fi
# Rockbox's configure swaps Apple clang for Homebrew gcc-14 on macOS; clang is fine for checkwps.
sed -i '' 's/if $CC --version | grep -q "clang"; then/if false; then/' "$WORK/tools/configure"
mkdir -p "$WORK/build-checkwps"
cd "$WORK/build-checkwps"
[ -f Makefile ] || ../tools/configure --target=ipodvideo --type=C >/dev/null
# macOS SDK turns strlcpy/strlcat into fortify macros that clash with Rockbox's own prototypes
grep -q 'FORTIFY_SOURCE' Makefile || sed -i '' 's/^export GCCOPTS=/export GCCOPTS= -U_FORTIFY_SOURCE -D_FORTIFY_SOURCE=0 -w/' Makefile
# ...and there is no gcc-ar on macOS, plain ar does the job
sed -i '' 's/^export AR=.*gcc-ar.*/export AR=ar/' Makefile
make -j4 >/dev/null 2>&1 || make
CHECK=$(ls checkwps* | head -1)
cd "$HERE/../.rockbox"
for f in wps/Noir.wps wps/Noir.sbs; do
    echo "=== $f"
    "$WORK/build-checkwps/$CHECK" -v "$f" 2>&1 | tail -15
done
