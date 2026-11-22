#!/usr/bin/env python3
"""PURE HONEY - one picture that tastes of honey.

Deterministic, PIL-only, no network, no randomness. Renders a wooden
honey dipper pouring a single glossy S-shaped ribbon of golden honey
into a honey pool, on a warm dark background with a faint honeycomb.
Writes entry.png (1024x1024, < 1 MiB) next to this script, or to the
path given as argv[1].
"""
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFilter

W = H = 1024

GOLD = (247, 183, 51)
GOLD_DEEP = (201, 121, 10)
GOLD_DARK = (146, 86, 8)
GOLD_LIGHT = (255, 222, 140)
WOOD = (139, 92, 44)
WOOD_DARK = (88, 54, 22)
WOOD_LIGHT = (183, 128, 62)


def lerp(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def vertical_gradient(top, bottom):
    strip = Image.new("RGB", (1, H))
    sp = strip.load()
    for y in range(H):
        sp[0, y] = lerp(top, bottom, y / (H - 1))
    return strip.resize((W, H))


def radial_glow(cx, cy, radius, color, peak):
    """Soft round glow centred at (cx, cy), peak alpha at the centre."""
    size = 256
    mask = Image.new("L", (size, size), 0)
    mp = mask.load()
    for j in range(size):
        for i in range(size):
            dx = (i - size / 2) / (size / 2)
            dy = (j - size / 2) / (size / 2)
            d = math.sqrt(dx * dx + dy * dy)
            v = max(0.0, 1.0 - d)
            mp[i, j] = int(peak * v * v)
    glow = Image.new("RGBA", (size, size), color + (0,))
    glow.putalpha(mask)
    glow = glow.resize((radius * 2, radius * 2), Image.BICUBIC)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    layer.alpha_composite(glow, (cx - radius, cy - radius))
    return layer


def hexagon(cx, cy, r):
    pts = []
    for k in range(6):
        a = math.pi / 3 * k + math.pi / 6
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def draw_background(img):
    base = vertical_gradient((24, 13, 6), (60, 35, 14)).convert("RGBA")
    img.alpha_composite(base)
    img.alpha_composite(radial_glow(512, 480, 520, (122, 70, 18), 90))
    img.alpha_composite(radial_glow(512, 300, 300, (160, 100, 30), 60))


def draw_honeycomb(img):
    """Faint honeycomb clusters in the upper corners, barely there."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    r = 46
    step_x = int(r * 1.73)
    step_y = int(r * 1.5)
    for cluster_cx, cluster_cy, span in ((150, 130, 4), (880, 110, 4)):
        for row in range(span):
            for col in range(span):
                cx = cluster_cx + (col - span / 2) * step_x
                cy = cluster_cy + (row - span / 2) * step_y
                if row % 2:
                    cx += step_x / 2
                fade = 1.0 - (abs(cx - cluster_cx) + abs(cy - cluster_cy)) / 420.0
                if fade <= 0:
                    continue
                a = int(26 * fade)
                d.polygon(hexagon(cx, cy, r), fill=(255, 190, 80, max(0, a - 12)),
                          outline=(255, 205, 100, a))
    img.alpha_composite(layer)


def draw_pool(img):
    """The honey pool at the bottom: deep gold ellipse, glossy top."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    # Body of the pool: stacked ellipses, darker at the rim, lighter inside.
    d.ellipse((72, 768, 952, 992), fill=GOLD_DEEP + (255,))
    d.ellipse((102, 786, 922, 972), fill=(232, 158, 32) + (255,))
    d.ellipse((150, 806, 874, 952), fill=GOLD + (255,))
    # Bright sheen across the upper half of the pool.
    d.ellipse((190, 800, 834, 920), fill=(255, 214, 110) + (255,))
    # Dark lower crescent for depth.
    d.ellipse((150, 880, 874, 972), fill=(176, 104, 8) + (255,))
    d.ellipse((230, 896, 794, 962), fill=(196, 118, 10) + (255,))
    img.alpha_composite(layer.filter(ImageFilter.GaussianBlur(1.0)))
    # Crisp glossy arcs on the pool surface.
    top = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    td = ImageDraw.Draw(top)
    td.arc((170, 800, 854, 940), start=200, end=340, fill=(255, 232, 160, 200), width=7)
    td.arc((250, 830, 774, 950), start=205, end=335, fill=(255, 240, 190, 150), width=4)
    img.alpha_composite(top)


def ribbon_points(t):
    """One S-shaped pour: from the dipper tip down to the pool."""
    y = 330 + 480 * t
    x = 668 + 88 * math.sin(t * 3.4) - 62 * t
    return x, y


def draw_ribbon(img):
    """Glossy golden ribbon with a soft glow, dark edge and light core."""
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    body = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(body)
    n = 260
    for i in range(n + 1):
        t = i / n
        x, y = ribbon_points(t)
        w = 20 + 11 * math.sin(math.pi * t)
        gd.ellipse((x - w - 16, y - w - 16, x + w + 16, y + w + 16),
                   fill=(255, 180, 50, 110))
        bd.ellipse((x - w - 2, y - w - 2, x + w + 2, y + w + 2),
                   fill=GOLD_DARK + (255,))
        bd.ellipse((x - w, y - w, x + w, y + w), fill=GOLD + (255,))
        # Bright core, offset up-left so the ribbon reads as lit.
        hw = w * 0.52
        bd.ellipse((x - hw - 8, y - hw - 3, x + hw - 8, y + hw - 3),
                   fill=(255, 232, 150, 255))
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(14)))
    img.alpha_composite(body.filter(ImageFilter.GaussianBlur(0.7)))
    # Impact mound where the ribbon meets the pool.
    top = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    td = ImageDraw.Draw(top)
    ix, iy = ribbon_points(1.0)
    td.ellipse((ix - 66, iy - 26, ix + 66, iy + 34), fill=GOLD + (255,))
    td.ellipse((ix - 44, iy - 30, ix + 44, iy + 8), fill=GOLD_LIGHT + (255,))
    td.ellipse((ix - 20, iy - 26, ix + 20, iy - 6), fill=(255, 240, 190, 255))
    # Ripples around the impact.
    for k, (rx, ry, a) in enumerate(((110, 26, 150), (170, 40, 110), (235, 54, 70))):
        td.ellipse((ix - rx, iy - 14 - ry, ix + rx, iy - 14 + ry),
                   outline=(255, 226, 140, a), width=4)
    # A droplet that just left the ribbon, mid-air.
    td.ellipse((ix + 118, iy - 190, ix + 142, iy - 152), fill=GOLD + (255,))
    td.ellipse((ix + 124, iy - 186, ix + 136, iy - 168), fill=GOLD_LIGHT + (255,))
    img.alpha_composite(top)


def draw_dipper(img):
    """Wooden honey dipper, tilted, head down-right where the pour starts."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    # Handle axis: from head centre H up-left at 210 degrees.
    hx, hy = 585.0, 275.0
    ux, uy = math.cos(math.radians(210)), math.sin(math.radians(210))
    vx, vy = -uy, ux  # perpendicular, width direction
    ex, ey = hx + 385 * ux, hy + 385 * uy  # handle end
    hw = 17.0
    d.polygon([(hx + hw * vx, hy + hw * vy), (ex + hw * vx, ey + hw * vy),
               (ex - hw * vx, ey - hw * vy), (hx - hw * vx, hy - hw * vy)],
              fill=WOOD + (255,))
    d.polygon([(hx + hw * vx, hy + hw * vy), (ex + hw * vx, ey + hw * vy),
               (ex + (hw - 6) * vx, ey + (hw - 6) * vy),
               (hx + (hw - 6) * vx, hy + (hw - 6) * vy)],
              fill=WOOD_LIGHT + (255,))
    # Grooves along the handle.
    for s in (90, 170, 250, 330):
        gx, gy = hx + s * ux, hy + s * uy
        d.line([(gx - hw * vx, gy - hw * vy), (gx + hw * vx, gy + hw * vy)],
               fill=WOOD_DARK + (255,), width=4)
    # Head: grooved bulb past the handle, along the down-right direction.
    dx, dy = -ux, -uy
    cx, cy = hx + 62 * dx, hy + 62 * dy
    px, py = -dy, dx  # long axis of the bulb is along (dx, dy)
    # Bulb as a rotated ellipse (polygon), long axis along the pour.
    pts = []
    for k in range(48):
        a = 2 * math.pi * k / 48
        ox = 62 * math.cos(a)
        oy = 46 * math.sin(a)
        pts.append((cx + ox * dx + oy * px, cy + ox * dy + oy * py))
    d.polygon(pts, fill=WOOD + (255,))
    # Groove rings across the bulb, perpendicular to its long axis.
    for s in (-38, -14, 10, 34):
        gx, gy = cx + s * dx, cy + s * dy
        half = 46 * math.sqrt(max(0.0, 1 - (s / 62.0) ** 2))
        d.line([(gx - half * px, gy - half * py), (gx + half * px, gy + half * py)],
               fill=WOOD_DARK + (255,), width=6)
    # Warm highlight on the bulb's lit side.
    hpts = []
    for k in range(32):
        a = 2 * math.pi * k / 32
        ox = 40 * math.cos(a)
        oy = 30 * math.sin(a)
        hpts.append((cx - 12 + ox * dx + oy * px, cy - 14 + ox * dy + oy * py))
    d.polygon(hpts, fill=WOOD_LIGHT + (200,))
    # Honey coating the bottom of the head, dripping into the ribbon.
    d.ellipse((cx + 30, cy + 40, cx + 66, cy + 76), fill=GOLD + (255,))
    img.alpha_composite(layer)


def draw_vignette(img):
    mask = Image.new("L", (W, H), 0)
    md = ImageDraw.Draw(mask)
    for i in range(1, 41):
        inset = 512 - i * 13
        alpha = int(120 * (i / 40.0) ** 1.5)
        md.ellipse((-inset, -inset, W + inset, H + inset), fill=alpha)
    dark = Image.new("RGBA", (W, H), (8, 4, 1, 255))
    dark.putalpha(mask)
    img.alpha_composite(dark)


def build_image():
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw_background(img)
    draw_honeycomb(img)
    draw_pool(img)
    draw_ribbon(img)
    draw_dipper(img)
    draw_vignette(img)
    return img.convert("RGB")


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img = build_image()
    img.save(out, format="PNG", optimize=True)
    size = os.path.getsize(out)
    print(f"wrote {out} 1024x1024 PNG {size} bytes")
    assert size < 1048576, "entry.png exceeds 1 MiB"


if __name__ == "__main__":
    main()
