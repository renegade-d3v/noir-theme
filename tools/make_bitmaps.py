#!/usr/bin/env python3
"""Shared BMP helpers for Noir's asset scripts (pure Python, no deps)."""
import struct, os

ROOT = os.path.join(os.path.dirname(__file__), "..", ".rockbox")
ACCENT = (0xFF, 0x6B, 0x4A)
LIGHT = (0xD8, 0xD8, 0xD8)
DIM = (0x6A, 0x6A, 0x6A)
MAGENTA = (0xFF, 0x00, 0xFF)  # Rockbox transparency colour

def write_bmp(path, pixels):
    h, w = len(pixels), len(pixels[0])
    pad = (4 - (w * 3) % 4) % 4
    data = b"".join(
        b"".join(bytes((b, g, r)) for r, g, b in row) + b"\0" * pad
        for row in reversed(pixels))
    hdr = b"BM" + struct.pack("<IHHI", 54 + len(data), 0, 0, 54)
    info = struct.pack("<IiiHHIIiiII", 40, w, h, 1, 24, 0, len(data), 2835, 2835, 0, 0)
    with open(path, "wb") as f:
        f.write(hdr + info + data)

def solid(w, h, c):
    return [[c] * w for _ in range(h)]

def read_bmp(path):
    d = open(path, "rb").read()
    off, = struct.unpack_from("<I", d, 10)
    w, h = struct.unpack_from("<ii", d, 18)
    bpp, = struct.unpack_from("<H", d, 28)
    assert bpp == 24
    stride = (w * 3 + 3) & ~3
    rows = []
    for y in range(abs(h)):
        base = off + y * stride
        rows.append([(d[base + x * 3 + 2], d[base + x * 3 + 1], d[base + x * 3]) for x in range(w)])
    return rows[::-1] if h > 0 else rows
