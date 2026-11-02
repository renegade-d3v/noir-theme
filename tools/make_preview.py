#!/usr/bin/env python3
"""Renders preview.png of Noir (WPS + menu) using the theme's real fonts, icons and bitmaps.
Pure Python. Layout mirrors Noir.wps / Noir.sbs coordinates; sample metadata is fake."""
import os, struct, zlib, math, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_bitmaps import read_bmp  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
RB = os.path.join(HERE, "..", ".rockbox")
W, H = 320, 240

def hexc(s):
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))

# ---------- canvas ----------
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = [[bg] * w for _ in range(h)]

    def put(self, x, y, c, a=1.0, clip=None):
        if clip:
            cx, cy, cw, ch = clip
            if not (cx <= x < cx + cw and cy <= y < cy + ch):
                return
        if 0 <= x < self.w and 0 <= y < self.h:
            if a >= 1.0:
                self.px[y][x] = c
            elif a > 0:
                o = self.px[y][x]
                self.px[y][x] = tuple(round(o[i] + (c[i] - o[i]) * a) for i in range(3))

    def rect(self, x, y, w, h, c):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.put(xx, yy, c)

    def blit(self, img, x, y, key=None, clip=None):
        for yy, row in enumerate(img):
            for xx, c in enumerate(row):
                if c != key:
                    self.put(x + xx, y + yy, c, clip=clip)

# ---------- bmp / png io ----------
def write_png(path, px):
    h, w = len(px), len(px[0])
    raw = b"".join(b"\0" + bytes(v for c in row for v in c) for row in px)
    def chunk(t, data):
        return struct.pack(">I", len(data)) + t + data + struct.pack(">I", zlib.crc32(t + data) & 0xffffffff)
    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b"")
    open(path, "wb").write(png)

# ---------- rockbox .fnt (RB12, 4-bit AA from convttf) ----------
class Font:
    def __init__(self, path):
        d = open(path, "rb").read()
        assert d[:4] == b"RB12"
        (self.maxw, self.height, self.ascent, self.depth, self.first, self.default,
         self.size, nbits, noff, nwid) = struct.unpack_from("<HHHHIIIIII", d, 4)
        p = 36
        self.bits = d[p:p + nbits]
        p += nbits
        long_off = nbits >= 0xFFDB
        if long_off:
            p = (p + 3) & ~3
            self.offs = struct.unpack_from("<%dI" % noff, d, p); p += 4 * noff
        else:
            p = (p + 1) & ~1
            self.offs = struct.unpack_from("<%dH" % noff, d, p); p += 2 * noff
        self.widths = d[p:p + nwid]

    def idx(self, ch):
        i = ord(ch) - self.first
        return i if 0 <= i < self.size else self.default - self.first

    def width(self, s):
        return sum(self.widths[self.idx(ch)] for ch in s)

    def draw(self, cv, s, x, y, color, clip=None):
        for ch in s:
            i = self.idx(ch)
            w, off = self.widths[i], self.offs[i]
            for n in range(w * self.height):
                if self.depth:
                    b = self.bits[off + n // 2]
                    v = (b >> 4) if n & 1 else (b & 15)
                    a = (15 - v) / 15
                else:
                    raise NotImplementedError("1-bit fonts")
                if a:
                    cv.put(x + n % w, y + n // w, color, a, clip)
            x += w
        return x

# ---------- theme assets ----------
F_MONO = Font(os.path.join(RB, "fonts", "15-Noir-Mono.fnt"))
F_R20 = Font(os.path.join(RB, "fonts", "20-SF-Pro-Rounded-Semibold.fnt"))
F_R16 = Font(os.path.join(RB, "fonts", "16-SF-Pro-Rounded-Semibold.fnt"))
F_R14 = Font(os.path.join(RB, "fonts", "14-SF-Pro-Rounded-Semibold.fnt"))
WPSDIR = os.path.join(RB, "wps", "Noir")
def font_or(name, fallback):
    path = os.path.join(RB, "fonts", name)
    if not os.path.exists(path):
        print(f"warning: {name} not built yet, using {fallback} (run tools/make_fonts.sh)")
        path = os.path.join(RB, "fonts", fallback)
    return Font(path)
F_R22 = font_or("22-SF-Pro-Rounded-Semibold.fnt", "20-SF-Pro-Rounded-Semibold.fnt")
F_MONO14 = font_or("14-Noir-Mono.fnt", "15-Noir-Mono.fnt")
BATTERY = read_bmp(os.path.join(RB, "wps", "Noir", "battery.bmp"))
LOCK = read_bmp(os.path.join(RB, "wps", "Noir", "lock.bmp"))
PB_FILL = read_bmp(os.path.join(RB, "wps", "Noir", "pb_fill.bmp"))
PB_BACK = read_bmp(os.path.join(RB, "wps", "Noir", "pb_back.bmp"))
MAGENTA = (255, 0, 255)
ACCENT, FG, BG = hexc("FF6B4A"), hexc("D8D8D8"), hexc("1E1C1A")

def vp_text(cv, vp, font, color, left="", right="", line=0):
    x, y, w, h = vp
    ty = y + line * font.height
    clip = (x, y, w, h)
    rx = x + w - font.width(right)
    if right:
        font.draw(cv, right, rx, ty, color, clip)
    if left:
        lclip = (x, y, (rx - x - 6) if right else w, h)
        font.draw(cv, left, x, ty, color, lclip)

def fake_cover(size):
    img = []
    for y in range(size):
        row = []
        for x in range(size):
            t = (x + y) / (2 * size)
            base = tuple(round(0x2A + (c - 0x2A) * (1 - t) * 0.55) for c in ACCENT)
            d = math.hypot(x - size * 0.62, y - size * 0.40)
            if d < size * 0.22:
                base = tuple(min(255, round(c * 1.0 + 40)) for c in ACCENT)
            elif d < size * 0.235:
                base = (20, 20, 20)
            if y > size * 0.78:
                base = tuple(round(c * 0.35) for c in base)
            row.append(base)
        img.append(row)
    return img

# ---------- screens ----------
def statusbar_strip(cv):
    cv.rect(0, 0, W, 24, (0, 0, 0))

def statusbar(cv, pos=4, total=100, hold=True, battery=87, charging=False,
              clock="02.11.2026 14:05"):
    white = (255, 255, 255)
    statusbar_strip(cv)
    count = f"{pos}/{total}" if pos else ""  # hidden when nothing plays
    vp_text(cv, (8, 4, 96, 16), F_MONO, white, count)
    if hold:
        n = len(str(pos)) + len(str(total))
        cv.blit(LOCK, 19 + 8 * n, 6)
    x = 96 + (128 - F_MONO.width(clock)) // 2
    F_MONO.draw(cv, clock, x, 4, white)
    vp_text(cv, (224, 4, 56, 16), F_MONO, white, "", f"{battery}%")
    frame = min(battery * 11 // 100, 10) + (11 if charging else 0)
    cv.blit(BATTERY[frame * 13:(frame + 1) * 13], 284, 6)

def img(name):
    return read_bmp(os.path.join(WPSDIR, name))

def wps(lossless=True, volume_change=False):
    cv = Canvas(W, H, BG)
    statusbar(cv)
    cv.blit(fake_cover(136), 12, 30)
    cv.blit(img("art_frame.bmp"), 10, 28, key=MAGENTA)
    vp_text(cv, (160, 29, 148, 23), F_R22, hexc("39FF88"), "Без бою")
    vp_text(cv, (160, 52, 148, 17), F_R16, hexc("DCDCDC"), "Океан Ельзи")
    vp_text(cv, (160, 68, 148, 17), F_R16, hexc("9A9A9A"), "Модель • 2001")
    vp_text(cv, (160, 85, 148, 15), F_R14, hexc("6E6E6E"), "Rock")
    if lossless:
        cv.blit(img("lossless.bmp"), 160, 130)
        info = "FLAC 912kbps 44.1kHz"
    else:
        cv.blit(img("codec.bmp"), 160, 130)
        vp_text(cv, (191, 131, 117, 15), F_R14, hexc("FFFFFF"), "MP3")
        info = "320kbps 44.1kHz"
    vp_text(cv, (160, 151, 148, 15), F_MONO14, hexc("9A9A9A"), info)
    cv.blit(img("pb_back.bmp"), 12, 178)
    cv.blit([row[:int(296 * 0.42)] for row in img("pb_fill.bmp")], 12, 178)
    vp_text(cv, (12, 186, 96, 16), F_MONO, hexc("9A9A9A"), "1:43")
    vp_text(cv, (212, 186, 96, 16), F_MONO, hexc("9A9A9A"), "", "-2:21")
    if volume_change:
        cv.blit(img("spk_low.bmp"), 12, 212)
        cv.blit(img("spk_high.bmp"), 12 + 280, 212)
        cv.blit(img("vol_back.bmp"), 36, 216)
        cv.blit([row[:int(248 * 0.66)] for row in img("vol_fill.bmp")], 36, 216)
    else:
        cv.blit(img("volume.bmp")[36 * 14:36 * 15], 104, 200)
        cv.blit(img("repeat.bmp")[20:40], 152, 208)
        cv.blit(img("shuffle.bmp")[:20], 190, 208)
    return cv

GREEN = hexc("39FF88")

def menu(items, selected=0, playing=True, now="Океан Ельзи - Без бою", **sb):
    """Mirrors Noir.sbs: reFresh-style skinned list in SF Pro Rounded Semibold 20, rounded green bar,
    now-playing bar (30x30 art with 4px corners + scrolling artist - title) while music plays."""
    cv = Canvas(W, H, BG)
    statusbar(cv, **sb)
    lh = F_R20.height
    vh = 172 if playing else 208
    for i, text in enumerate(items):
        y = 32 + i * lh
        if y >= 32 + vh:
            break
        clip = (8, y, 304, min(lh, 32 + vh - y))
        if i == selected:
            cv.rect(8, y, 304, clip[3], GREEN)
        F_R20.draw(cv, "   " + text, 8, y, BG if i == selected else hexc("FFFFFF"), clip=clip)
        if i == selected:
            for name, x, cy in (("TL", 0, 0), ("BL", 0, 15)):
                cv.blit(img(f"corner{name}.bmp"), 8 + x, y + cy, key=MAGENTA)
        cap = img("menu_cap_sel.bmp" if i == selected else "menu_cap.bmp")
        cv.blit(cap[:clip[3]], 8 + 295, y)
    if playing:
        cv.blit(fake_cover(30), 12, 204)
        for name, x, y in (("TL", 0, 0), ("TR", 26, 0), ("BL", 0, 26), ("BR", 26, 26)):
            cv.blit(img(f"corner{name}_s.bmp"), 12 + x, 204 + y, key=MAGENTA)
        F_R16.draw(cv, now, 50, 211, hexc("FFFFFF"), clip=(50, 211, 259, 17))
    return cv

MAIN_MENU = ["Файлы", "База данных", "Сейчас играет", "Настройки",
             "Плейлисты", "Плагины", "Система"]
BROWSER = ["Океан Ельзи", "Бумбокс", "Daft Punk", "Kalush Orchestra", "The Hardkiss",
           "ДахаБраха", "Radiohead — OK Computer OKNOTOK 1997 2017", "Скрябін", "Тартак",
           "Portishead", "Sigur Rós"]

def statusbar_variants():
    """Zoomed status bar crops: hold+87%, charging, low battery."""
    out = []
    for kw in (dict(), dict(pos=128, total=2450, battery=54, charging=True),
               dict(pos=7, total=9, hold=False, battery=6)):
        cv = Canvas(W, H, BG)
        statusbar(cv, **kw)
        out.append([row for row in cv.px[:24]])
    return out

def compose(screens, scale=2, pad=32, gap=32):
    sw, sh = W * scale, H * scale
    tw = pad * 2 + len(screens) * sw + (len(screens) - 1) * gap
    th = pad * 2 + sh
    out = [[hexc("161616")] * tw for _ in range(th)]
    for k, cv in enumerate(screens):
        ox = pad + k * (sw + gap)
        for y in range(sh):
            src = cv.px[y // scale]
            row = out[pad + y]
            for x in range(sw):
                row[ox + x] = src[x // scale]
    return out

if __name__ == "__main__":
    dst = os.path.join(HERE, "..", "docs", "preview.png")
    write_png(dst, compose([wps(), wps(lossless=False), wps(volume_change=True)]))
    mp = os.path.join(HERE, "..", "docs", "preview-menu.png")
    write_png(mp, compose([menu(MAIN_MENU, 2, playing=False, pos=0, hold=False),
                           menu(BROWSER, 6, hold=False,
                                now="Radiohead - Paranoid Android (Remastered)")]))
    print("wrote", os.path.normpath(mp))
    sb = os.path.join(HERE, "..", "docs", "preview-statusbar.png")
    rows, scale = [], 3
    for strip in statusbar_variants():
        for row in strip:
            big = [c for c in row for _ in range(scale)]
            rows += [big] * scale
        rows += [[hexc("161616")] * (W * scale)] * 12
    write_png(sb, rows[:-12])
    print("wrote", os.path.normpath(sb))
    print("wrote", os.path.normpath(dst))
