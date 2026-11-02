#!/usr/bin/env python3
"""Imports icons from the reFresh theme (CC-BY-SA 3.0, Ciprian Dragu) onto Noir's black background.
reFresh icons are white artwork baked over its teal backdrop; we un-composite them using the
backdrop pixels at the position each icon is drawn in reFresh, then re-composite onto black."""
import os, struct, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_bitmaps import write_bmp  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "..", "reFresh", "wps", "iPod-reFresh-three")
DST = os.path.join(HERE, "assets", "refresh")  # committed: Noir builds without reFresh next to it
MAGENTA = (255, 0, 255)

def read(path):
    d = open(path, "rb").read()
    off, = struct.unpack_from("<I", d, 10)
    w, h = struct.unpack_from("<ii", d, 18)
    bpb = struct.unpack_from("<H", d, 28)[0] // 8
    stride = (w * bpb + 3) & ~3
    rows = [[(d[off + y * stride + x * bpb + 2], d[off + y * stride + x * bpb + 1],
              d[off + y * stride + x * bpb]) for x in range(w)] for y in range(abs(h))]
    return rows[::-1] if h > 0 else rows

BACKDROP = None

def available():
    return os.path.isdir(SRC)

def lum(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]

def uncomposite(img, ox, oy, frame_h=None):
    """White-over-backdrop -> white-over-black. Animated strips reuse the same origin per frame."""
    fh = frame_h or len(img)
    out = []
    for y, row in enumerate(img):
        new = []
        for x, c in enumerate(row):
            if c == MAGENTA:
                new.append((0, 0, 0))
                continue
            b = BACKDROP[oy + y % fh][ox + x]
            if lum(b) > 100:  # artwork baked into the backdrop (e.g. the speaker): use row edge colour
                b = BACKDROP[oy + y % fh][ox]
            a = (lum(c) - lum(b)) / max(1.0, 255 - lum(b))
            v = round(255 * min(1.0, max(0.0, a)))
            new.append((v, v, v))
        out.append(new)
    return out

def levels(img, floor):
    """Drop a residual flat plate (the badge's own tinted box) by remapping [floor..255] -> [0..255]."""
    return [[tuple(round(max(0, v - floor) * 255 / (255 - floor)) for v in c) for c in row] for row in img]

# (file, x, y, frame height) as positioned in iPod-reFresh-three.wps
ICONS = [("lossless.bmp", 162, 126, None), ("shuffle.bmp", 191, 207, None),
         ("repeat.bmp", 144, 207, 20), ("volume.bmp", 96, 199, 36)]

def main():
    global BACKDROP
    BACKDROP = read(os.path.join(SRC, "backdrop-wps.bmp"))
    os.makedirs(DST, exist_ok=True)
    for name, x, y, fh in ICONS:
        img = uncomposite(read(os.path.join(SRC, name)), x, y, fh)
        if name == "lossless.bmp":
            img = levels(img, 48)
        write_bmp(os.path.join(DST, name), img)
        print("imported", name)

if __name__ == "__main__":
    main()
