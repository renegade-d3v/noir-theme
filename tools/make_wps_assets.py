#!/usr/bin/env python3
"""Noir WPS bitmaps: rounded progress bar, rounded-md album art corners, codec badge frame,
and dimmed 'off' frames for the imported reFresh shuffle/repeat icons."""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_bitmaps import write_bmp  # noqa: E402
from make_statusbar import rrect, render, polygon, WHITE  # noqa: E402
from make_bitmaps import read_bmp  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".rockbox", "wps", "Noir")
MAGENTA = (255, 0, 255)
BG = (0x1E, 0x1C, 0x1A)  # theme background ("terracotta black", Paidago dark --background)
ACCENT = (0x39, 0xFF, 0x88)  # neon green: progress bar, volume slider bar, title (icons stay white)
PB_W, PB_H = 296, 5
ART, RADIUS = 136, 6  # Tailwind rounded-md = 6px

def progress():
    bar = rrect(0, 0, PB_W, PB_H, PB_H / 2)
    write_bmp(os.path.join(OUT, "pb_fill.bmp"), render(PB_W, PB_H, [(bar, ACCENT, 1.0)]))
    write_bmp(os.path.join(OUT, "pb_back.bmp"), render(PB_W, PB_H, [(bar, WHITE, 0.22)]))

def corners(r=RADIUS, suffix="", which=("TL", "TR", "BL", "BR")):
    """Black outside a quarter circle, magenta (transparent) inside; one image per corner."""
    def corner(cx, cy):
        rows = []
        for y in range(r):
            row = []
            for x in range(r):
                hits = sum((x + (i + .5) / 4 - cx) ** 2 + (y + (j + .5) / 4 - cy) ** 2 > r * r
                           for i in range(4) for j in range(4))
                row.append((0, 0, 0) if hits >= 8 else MAGENTA)
            rows.append(row)
        return rows
    for name, cx, cy in (("TL", r, r), ("TR", 0, r), ("BL", r, 0), ("BR", 0, 0)):
        if name not in which:
            continue
        write_bmp(os.path.join(OUT, f"corner{name}{suffix}.bmp"), corner(cx, cy))

def tint(img, col=ACCENT):
    """White-on-black artwork -> accent-on-black."""
    return [[tuple(round(c[0] / 255 * v) for v in col) for c in row] for row in img]

def dim(img, k=0.32):
    return [[tuple(round(v * k) for v in c) for c in row] for row in img]

def toggles():
    """Shuffle/repeat: bright white when on, a dark grey 'off' frame (high contrast) so the row stays put."""
    shuffle = read_bmp(os.path.join(OUT, "shuffle.bmp"))[:20]
    write_bmp(os.path.join(OUT, "shuffle.bmp"), shuffle + dim(shuffle, 0.22))
    repeat = read_bmp(os.path.join(OUT, "repeat.bmp"))[:80]
    write_bmp(os.path.join(OUT, "repeat.bmp"), dim(repeat[:20], 0.22) + repeat)

FRAME = ART + 4  # 2px accent border around the 136px art
def art_frame():
    """140x140 overlay drawn on top of the album art: transparent (magenta) inside the art's
    rounded-md shape, a 2px accent ring around it, black outside. Outer edge anti-aliased onto black."""
    outer = rrect(0, 0, FRAME, FRAME, RADIUS + 2)
    inner = rrect(2, 2, FRAME - 2, FRAME - 2, RADIUS)
    rows = []
    for y in range(FRAME):
        row = []
        for x in range(FRAME):
            n_out = n_in = 0
            for j in range(4):
                for i in range(4):
                    px, py = x + (i + .5) / 4, y + (j + .5) / 4
                    n_out += outer(px, py)
                    n_in += inner(px, py)
            if n_in >= 8:
                row.append(MAGENTA)
            else:
                a = n_out / 16
                row.append(tuple(round(v * a) for v in ACCENT))
        rows.append(row)
    write_bmp(os.path.join(OUT, "art_frame.bmp"), rows)

CODEC_W = 26
def codec_icon():
    """Sound-wave bars, shown before the codec name for lossy files."""
    heights = (4, 8, 13, 9, 16, 11, 14, 7, 3)
    bars = [rrect(i * 3, 8.5 - h / 2, i * 3 + 2, 8.5 + h / 2, 1.0) for i, h in enumerate(heights)]
    write_bmp(os.path.join(OUT, "codec.bmp"), render(CODEC_W, 17, [(b, WHITE, 1.0) for b in bars]))

def speaker(waves):
    body = polygon([(0.8, 4.6), (3.6, 4.6), (7.4, 1.2), (7.4, 11.8), (3.6, 8.4), (0.8, 8.4)])
    def arc(r0, r1):
        return lambda x, y: (r0 ** 2 <= (x - 6.0) ** 2 + (y - 6.5) ** 2 <= r1 ** 2
                             and x > 6.0 and abs(y - 6.5) < 0.9 * (x - 6.0))
    layers = [(body, WHITE, 1.0)] + [(arc(r, r + 1.3), WHITE, 1.0) for r in (3.4, 6.2)[:waves]]
    return render(16, 13, layers)

VB_W = 248
def volume_slider():
    bar = rrect(0, 0, VB_W, 5, 2.5)
    write_bmp(os.path.join(OUT, "vol_fill.bmp"), render(VB_W, 5, [(bar, ACCENT, 1.0)]))
    write_bmp(os.path.join(OUT, "vol_back.bmp"), render(VB_W, 5, [(bar, WHITE, 0.22)]))
    write_bmp(os.path.join(OUT, "spk_low.bmp"), speaker(1))
    write_bmp(os.path.join(OUT, "spk_high.bmp"), speaker(2))

FADE = (35, 70)  # % brightness steps when the icon row fades back in
def fades():
    for name in ("volume", "repeat", "shuffle"):
        img = read_bmp(os.path.join(OUT, f"{name}.bmp"))
        for pct in FADE:
            write_bmp(os.path.join(OUT, f"{name}_{pct}.bmp"), dim(img, pct / 100))

MENU_PAD, MENU_H = 9, 21
def menu_caps():
    """Right-edge caps for the skinned menu list; images draw over text, so these act as right padding.
    Selected: neon green with the two right corners rounded (6px). Others: plain black."""
    g = (0x39, 0xFF, 0x88)
    def inside(x, y):
        cx = MENU_PAD - RADIUS
        cy = min(max(y, RADIUS), MENU_H - RADIUS)
        return x < cx or (x - cx) ** 2 + (y - cy) ** 2 <= RADIUS ** 2
    sel = []
    for y in range(MENU_H):
        row = []
        for x in range(MENU_PAD):
            hits = sum(inside(x + (i + .5) / 4, y + (j + .5) / 4) for i in range(4) for j in range(4))
            row.append(g if hits >= 8 else (0, 0, 0))
        sel.append(row)
    write_bmp(os.path.join(OUT, "menu_cap_sel.bmp"), sel)
    write_bmp(os.path.join(OUT, "menu_cap.bmp"), [[(0, 0, 0)] * MENU_PAD for _ in range(MENU_H)])

def onto_bg():
    """Everything above was drawn as white/accent over black (alpha = brightest channel, since white
    and the accent both peak at 255). Re-composite onto BG; magenta stays transparent.
    battery.bmp / lock.bmp live in the black status bar and are left alone."""
    for name in sorted(os.listdir(OUT)):
        if not name.endswith(".bmp") or name in ("battery.bmp", "lock.bmp"):
            continue
        path = os.path.join(OUT, name)
        img = read_bmp(path)
        out = [[c if c == MAGENTA else
                tuple(round(c[i] + BG[i] * (1 - max(c) / 255)) for i in range(3))
                for c in row] for row in img]
        write_bmp(path, out)

def refresh_icons():
    """Start every run from the clean white reFresh icons, so frames/tints never stack up.
    They are re-imported from ../../reFresh when it is present, else taken from tools/assets/refresh."""
    import shutil, import_refresh
    if import_refresh.available():
        import_refresh.main()
    for name in ("lossless.bmp", "shuffle.bmp", "repeat.bmp", "volume.bmp"):
        shutil.copy(os.path.join(import_refresh.DST, name), os.path.join(OUT, name))

if __name__ == "__main__":
    refresh_icons()
    progress(); corners(which=("TL", "BL")); corners(4, "_s"); toggles(); art_frame(); codec_icon(); volume_slider(); fades(); menu_caps(); onto_bg()
    print("pb, corners, shuffle(2), repeat(5), codec, volume slider, fades", FADE)
