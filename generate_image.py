#!/usr/bin/env python3
"""PURE HONEY — one picture of a single ingredient: golden honey.

Draws a wooden honey dipper pouring one glossy S-shaped ribbon of honey
into a pool of honey, on a dark warm background with a faint honeycomb.
Pure Pillow, no network, no randomness: two runs are byte-identical.

Run:  python3 generate_image.py   -> writes entry.png (1024x1024, <=1 MiB)
"""

import math
from PIL import Image, ImageDraw, ImageFilter

S = 2                      # supersample factor
W = H = 1024 * S           # working canvas
OUT = "entry.png"

# ---- palette ------------------------------------------------------------
BG_TOP = (44, 26, 12)
BG_BOT = (14, 8, 3)
GLOW = (150, 84, 24)
COMB = (122, 74, 26)
WOOD = (139, 90, 43)
WOOD_DARK = (96, 58, 24)
WOOD_LIGHT = (176, 122, 66)
HONEY_DARK = (146, 82, 4)
HONEY_MID = (216, 134, 6)
HONEY_LIGHT = (247, 183, 51)
HONEY_BRIGHT = (255, 201, 60)
HIGHLIGHT = (255, 236, 170)


def lerp(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def ribbon_polygon(path, width):
    """Thick smooth ribbon as one filled polygon (no segment seams)."""
    n = len(path)
    left, right = [], []
    for i, (x, y) in enumerate(path):
        x0, y0 = path[max(i - 1, 0)]
        x1, y1 = path[min(i + 1, n - 1)]
        dx, dy = x1 - x0, y1 - y0
        ln = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / ln * width / 2, dx / ln * width / 2
        left.append((x + nx, y + ny))
        right.append((x - nx, y - ny))
    return left + right[::-1]


def catmull_rom(points, samples=24):
    """Smooth curve through points (Catmull-Rom), returns list of (x, y)."""
    pts = [points[0]] + points + [points[-1]]
    out = []
    for i in range(len(pts) - 3):
        p0, p1, p2, p3 = pts[i], pts[i + 1], pts[i + 2], pts[i + 3]
        for j in range(samples):
            t = j / samples
            t2, t3 = t * t, t * t * t
            x = 0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * t
                       + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2
                       + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3)
            y = 0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * t
                       + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2
                       + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)
            out.append((x, y))
    out.append(points[-1])
    return out


def vertical_gradient(size, top, bottom):
    w, h = size
    img = Image.new("RGB", (1, h))
    px = img.load()
    for y in range(h):
        px[0, y] = lerp(top, bottom, y / (h - 1))
    return img.resize((w, h))


def radial_glow(size, center, radius, color, peak=110):
    layer = Image.new("L", size, 0)
    d = ImageDraw.Draw(layer)
    steps = 48
    for i in range(steps, 0, -1):
        r = radius * i / steps
        a = int(peak * (1 - i / steps) ** 2)
        d.ellipse([center[0] - r, center[1] - r,
                   center[0] + r, center[1] + r], fill=a)
    tint = Image.new("RGB", size, color)
    return Image.composite(tint, Image.new("RGB", size, (0, 0, 0)), layer)


def hexagon(draw, cx, cy, r, outline, width):
    pts = [(cx + r * math.cos(math.radians(30 + 60 * k)),
            cy + r * math.sin(math.radians(30 + 60 * k))) for k in range(6)]
    draw.line(pts + [pts[0]], fill=outline, width=width, joint="curve")


def main():
    img = vertical_gradient((W, H), BG_TOP, BG_BOT)
    img.paste(radial_glow((W, H), (W // 2, int(H * 0.72)), int(W * 0.52),
                          GLOW, peak=96), (0, 0))

    # ---- faint honeycomb, top corners ------------------------------------
    comb = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cd = ImageDraw.Draw(comb)
    r = 150
    dx, dy = int(r * 1.5), int(r * 0.866)
    for gx in range(-1, 10):
        for gy in range(-1, 5):
            cx = gx * dx + (r * 0.75 if gy % 2 else 0)
            cy = gy * dy
            if cx < W * 0.42 and cy < H * 0.42:
                hexagon(cd, cx, cy, r, COMB + (46,), 5)
            if cx > W * 0.58 and cy < H * 0.42:
                hexagon(cd, cx, cy, r, COMB + (46,), 5)
    comb = comb.filter(ImageFilter.GaussianBlur(3))
    img = Image.alpha_composite(img.convert("RGBA"), comb).convert("RGB")

    d = ImageDraw.Draw(img, "RGBA")

    # ---- honey pool ------------------------------------------------------
    pool_cx, pool_cy = W // 2, int(H * 0.86)
    pool_rx, pool_ry = int(W * 0.40), int(H * 0.115)
    # soft shadow under the pool
    d.ellipse([pool_cx - pool_rx - 30, pool_cy - pool_ry + 46,
               pool_cx + pool_rx + 30, pool_cy + pool_ry + 90],
              fill=(0, 0, 0, 110))
    # pool body: stacked ellipses, dark rim -> bright centre
    for i in range(26, 0, -1):
        t = i / 26
        rx = pool_rx * (0.55 + 0.45 * t)
        ry = pool_ry * (0.55 + 0.45 * t)
        col = lerp(HONEY_BRIGHT, HONEY_DARK, t * 0.85)
        d.ellipse([pool_cx - rx, pool_cy - ry, pool_cx + rx, pool_cy + ry],
                  fill=col + (255,))
    # swirl arcs inside the pool
    for k, (rr, a0, a1, col, wdt) in enumerate([
            (0.62, 195, 345, HONEY_DARK, 10),
            (0.74, 15, 165, HONEY_MID, 8),
            (0.50, 20, 160, HONEY_LIGHT, 7),
            (0.84, 200, 330, HONEY_DARK, 7)]):
        d.arc([pool_cx - pool_rx * rr, pool_cy - pool_ry * rr,
               pool_cx + pool_rx * rr, pool_cy + pool_ry * rr],
              a0, a1, fill=col + (150,), width=wdt)
    # glossy speculars on the pool
    d.ellipse([pool_cx - 300, pool_cy - 118, pool_cx + 60, pool_cy - 34],
              fill=HIGHLIGHT + (90,))
    d.ellipse([pool_cx + 180, pool_cy + 30, pool_cx + 420, pool_cy + 96],
              fill=HIGHLIGHT + (60,))

    # ---- honey ribbon: one S-curve from dipper to pool -------------------
    ctrl = [(1330, 620), (1150, 830), (1380, 1080), (1150, 1330),
            (1024, 1560)]
    path = catmull_rom(ctrl, samples=30)
    # layered filled ribbons: dark edge, mid body, bright core
    for width, col in [(150, HONEY_DARK), (118, HONEY_MID),
                       (78, HONEY_LIGHT), (40, HONEY_BRIGHT)]:
        d.polygon(ribbon_polygon(path, width), fill=col + (255,))
    # specular thread, offset to the light side
    thread = [(x - 26, y - 6) for (x, y) in path]
    d.polygon(ribbon_polygon(thread, 16), fill=HIGHLIGHT + (215,))
    # thickening blob where the ribbon meets the pool
    d.ellipse([968, 1480, 1140, 1620], fill=HONEY_LIGHT + (255,))
    d.ellipse([990, 1500, 1110, 1590], fill=HONEY_BRIGHT + (255,))
    # small droplets kicked up at the impact point
    for (x, y, r) in [(900, 1450, 18), (1150, 1420, 14), (1024, 1380, 12)]:
        d.ellipse([x - r, y - r, x + r, y + r], fill=HONEY_BRIGHT + (255,))

    # ---- falling droplets (clear of the ribbon) ---------------------------
    for (x, y, r) in [(700, 900, 26), (1520, 980, 20)]:
        d.ellipse([x - r, y - r, x + r, y + int(r * 1.25)],
                  fill=HONEY_LIGHT + (255,))
        d.ellipse([x - r + 6, y - r + 5, x - r + 16, y - r + 15],
                  fill=HIGHLIGHT + (235,))

    # ---- wooden dipper, top right, tilted --------------------------------
    dip = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dd = ImageDraw.Draw(dip)
    # handle: long rounded bar from top-right corner down to the head
    hx0, hy0, hx1, hy1 = 1560, 60, 1440, 560
    dd.line([(hx0, hy0), (hx1, hy1)], fill=WOOD + (255,), width=92,
            joint="curve")
    dd.line([(hx0 - 16, hy0), (hx1 - 16, hy1)], fill=WOOD_LIGHT + (255,),
            width=26, joint="curve")
    # grooved head: stacked rounded discs around (1370, 640)
    cx, cy = 1370, 640
    for i, (oy, rw, rh) in enumerate([(-96, 150, 62), (-32, 168, 62),
                                      (32, 168, 62), (96, 150, 62)]):
        col = WOOD if i % 2 == 0 else WOOD_DARK
        dd.ellipse([cx - rw, cy + oy - rh, cx + rw, cy + oy + rh],
                   fill=col + (255,))
        dd.arc([cx - rw, cy + oy - rh, cx + rw, cy + oy + rh],
               200, 340, fill=WOOD_LIGHT + (200,), width=10)
    # honey coating the head, dripping from its tip
    dd.ellipse([cx - 150, cy + 60, cx + 150, cy + 190],
               fill=HONEY_MID + (255,))
    dd.ellipse([cx - 120, cy + 90, cx + 120, cy + 185],
               fill=HONEY_LIGHT + (255,))
    dd.ellipse([cx - 40, cy + 150, cx + 40, cy + 260],
               fill=HONEY_LIGHT + (255,))
    dip = dip.rotate(-24, center=(cx, cy), resample=Image.BICUBIC)
    img = Image.alpha_composite(img.convert("RGBA"), dip).convert("RGB")

    # ---- vignette ---------------------------------------------------------
    vig = Image.new("L", (W, H), 0)
    vd = ImageDraw.Draw(vig)
    vd.ellipse([-W * 0.18, -H * 0.18, W * 1.18, H * 1.18], fill=255)
    vig = vig.filter(ImageFilter.GaussianBlur(220))
    black = Image.new("RGB", (W, H), (0, 0, 0))
    img = Image.composite(img, black, vig)

    img = img.resize((1024, 1024), Image.LANCZOS)
    img.save(OUT, "PNG", optimize=True)
    print(f"wrote {OUT}: {img.size}")


if __name__ == "__main__":
    main()
