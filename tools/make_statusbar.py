#!/usr/bin/env python3
"""Generates macOS-style status bar bitmaps for Noir (battery strip, lock). Pure Python.
Shapes are rasterised with 8x8 supersampling and pre-blended onto black (theme background)."""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_bitmaps import write_bmp  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".rockbox", "wps", "Noir")
SS = 8
WHITE = (255, 255, 255)
RED = (0xFF, 0x45, 0x3A)
GREEN = (0x30, 0xD1, 0x58)

def rrect(x0, y0, x1, y1, r):
    """Inside-test for a rounded rect with corners at (x0,y0)-(x1,y1)."""
    def inside(x, y):
        if not (x0 <= x <= x1 and y0 <= y <= y1):
            return False
        cx = min(max(x, x0 + r), x1 - r)
        cy = min(max(y, y0 + r), y1 - r)
        return (x - cx) ** 2 + (y - cy) ** 2 <= r * r
    return inside

def polygon(pts):
    def inside(x, y):
        c = False
        j = len(pts) - 1
        for i in range(len(pts)):
            xi, yi = pts[i]
            xj, yj = pts[j]
            if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
                c = not c
            j = i
        return c
    return inside

def render(w, h, layers):
    """layers: list of (inside_fn, colour, opacity); later layers paint over earlier ones."""
    img = []
    for py in range(h):
        row = []
        for px in range(w):
            acc = [0.0, 0.0, 0.0]
            for sy in range(SS):
                for sx in range(SS):
                    x, y = px + (sx + 0.5) / SS, py + (sy + 0.5) / SS
                    c = (0.0, 0.0, 0.0)
                    for fn, col, op in layers:
                        if fn(x, y):
                            c = tuple(c[i] + (col[i] - c[i]) * op for i in range(3))
                    for i in range(3):
                        acc[i] += c[i]
            row.append(tuple(round(v / (SS * SS)) for v in acc))
        img.append(row)
    return img

# Battery: 25x12 body + 2px nub, like the macOS menu bar glyph.
BW, BH = 28, 13
def battery(level, charging):
    body_out = rrect(0.5, 0.5, 25.0, 12.5, 3.6)
    body_in = rrect(1.5, 1.5, 24.0, 11.5, 2.6)
    ring = lambda x, y: body_out(x, y) and not body_in(x, y)
    nub = rrect(25.8, 4.3, 27.6, 8.7, 0.9)
    fill_w = 19.5 * level / 100
    fill = rrect(3.0, 3.0, 3.0 + max(fill_w, 0.01), 10.0, 1.6)
    if charging:
        col = GREEN
    elif level <= 12:
        col = RED
    else:
        col = WHITE
    layers = [(ring, WHITE, 0.45), (nub, WHITE, 0.45)]
    if level > 0:
        layers.append((fill, col, 1.0))
    if charging:
        bolt = polygon([(14.6, 1.6), (9.2, 7.3), (12.9, 7.3), (11.6, 11.4),
                        (17.0, 5.7), (13.3, 5.7)])
        outline = polygon([(15.4, 0.4), (7.6, 8.3), (11.8, 8.3), (10.4, 12.8),
                           (18.6, 4.7), (14.4, 4.7)])
        layers += [(outline, (0, 0, 0), 1.0), (bolt, WHITE, 1.0)]
    return render(BW, BH, layers)

def lock():
    # SF Symbols "lock.fill": shackle arc over a rounded body.
    body = rrect(0.5, 5.5, 9.5, 12.5, 1.6)
    outer = rrect(1.9, 0.6, 8.1, 9.0, 3.1)
    inner = rrect(3.3, 2.0, 6.7, 9.0, 1.7)
    shackle = lambda x, y: outer(x, y) and not inner(x, y)
    return render(10, 13, [(shackle, WHITE, 1.0), (body, WHITE, 1.0)])

def main():
    levels = [6, 12, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    frames = [battery(l, False) for l in levels] + [battery(l, True) for l in levels]
    write_bmp(os.path.join(OUT, "battery.bmp"), [row for f in frames for row in f])
    write_bmp(os.path.join(OUT, "lock.bmp"), lock())
    print(f"battery.bmp: {len(frames)} frames of {BW}x{BH}; lock.bmp: 10x13")

if __name__ == "__main__":
    main()
