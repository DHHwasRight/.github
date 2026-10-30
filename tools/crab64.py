# A 64x64 pixel-art crab in sunglasses on a railway track, at sunset.
#
# Parts are drawn as shapes into a label grid, lit from the top left,
# quantised to a five-tone palette, then outlined. The output is an SVG of
# 1x1 rects, so it scales without blur.
import math, sys

N = 64
CX = 32

# ---- palette -------------------------------------------------------------
SHELL = ["#5a1608", "#9b2c0c", "#d44516", "#f26b2e", "#ffb07a"]   # dark..light
OUTLINE = "#22090a"
INNER = "#4a1208"
GLASS = "#0b0a12"
LENS = ["#2a1450", "#5b2d8f", "#8a4cc4"]
GLINT = ["#ffffff", "#7fe9ff"]
SKY = ["#140c2b", "#1f1140", "#341556", "#55196a", "#7d2275", "#a8327a"]
SUN = ["#ffd35c", "#ffb04d", "#ff8a4a", "#ff5f5a", "#ff3f7a"]
RAIL = ["#5d6577", "#a6afc0", "#e4e9f2"]
TIE = ["#3b2416", "#6a4126"]
GROUND = "#120a1f"

# ---- geometry helpers ----------------------------------------------------
def in_ellipse(x, y, cx, cy, rx, ry):
    return ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1.0

def seg_dist(px, py, ax, ay, bx, by):
    vx, vy = bx - ax, by - ay
    t = max(0.0, min(1.0, ((px - ax) * vx + (py - ay) * vy) / (vx * vx + vy * vy)))
    qx, qy = ax + t * vx, ay + t * vy
    return math.hypot(px - qx, py - qy), t, (px - qx, py - qy)

LIGHT = (-0.55, -0.65, 0.53)
ln = math.sqrt(sum(c * c for c in LIGHT)); LIGHT = tuple(c / ln for c in LIGHT)

def shade_sphere(nx, ny):
    nz = math.sqrt(max(0.0, 1 - nx * nx - ny * ny))
    return nx * LIGHT[0] + ny * LIGHT[1] + nz * LIGHT[2]

# Each part: (z, contains(x,y) -> intensity or None)
parts = []

def ellipse(z, cx, cy, rx, ry, bias=0.0, cut=None):
    def f(x, y):
        px, py = x + 0.5, y + 0.5
        if not in_ellipse(px, py, cx, cy, rx, ry):
            return None
        if cut and cut(px, py):
            return None
        return shade_sphere((px - cx) / rx, (py - cy) / ry) + bias
    parts.append((z, f))

def limb(z, pts, w0, w1, bias=0.0):
    """A jointed limb: a polyline whose width tapers from w0 to w1."""
    segs = list(zip(pts, pts[1:]))
    n = len(segs)
    def f(x, y):
        px, py = x + 0.5, y + 0.5
        best = None
        for i, ((ax, ay), (bx, by)) in enumerate(segs):
            d, t, (ox, oy) = seg_dist(px, py, ax, ay, bx, by)
            w = w0 + (w1 - w0) * ((i + t) / n)
            if d <= w / 2:
                # normal across the limb, lit like a cylinder
                nx, ny = (ox / (w / 2 + 1e-6), oy / (w / 2 + 1e-6))
                v = shade_sphere(nx * 0.9, ny * 0.9) + bias
                if best is None or v > best:
                    best = v
        return best
    parts.append((z, f))

def both(fn, *a, **k):
    fn(*a, **k)
    # mirror: rebuild with mirrored x coordinates
    k2 = dict(k)
    if fn is limb:
        z, pts, *rest = a
        fn(z, [(N - px, py) for px, py in pts], *rest, **k2)
    else:
        z, cx, *rest = a
        if "cut" in k2 and k2["cut"]:
            c = k2["cut"]; k2["cut"] = lambda px, py, c=c: c(N - px, py)
        fn(z, N - cx, *rest, **k2)

# ---- the crab ------------------------------------------------------------
# legs, three a side, behind the body
both(limb, 1, [(17, 42), (9, 40), (4, 48), (3, 55)], 4.2, 2.2)
both(limb, 1, [(19, 46), (12, 48), (9, 54), (9, 57)], 4.0, 2.0)
both(limb, 1, [(23, 50), (18, 53), (16, 56), (17, 57)], 3.8, 2.0)

# claw arms: shoulder -> elbow -> wrist
both(limb, 2, [(18, 38), (10, 33), (10, 23)], 5.0, 4.0, bias=0.05)

# pincers: a fat palm with a wedge cut out of the top = open claw
def pincer_cut(px, py, cx=11.0, cy=14.5):
    # open jaw: a V-shaped notch opening upward and slightly outward
    dx, dy = px - cx, py - cy
    return dy < 1.0 and abs(dx + 0.4 * dy - 0.5) < (2.0 - dy) * 0.33
both(ellipse, 3, 11.0, 15.0, 6.2, 7.2, bias=0.08, cut=pincer_cut)

# body (carapace), in front of everything but the face details
ellipse(4, CX, 43, 21.5, 11.0, bias=0.02)
# rim spikes along the top edge of the shell
for sx in (17, 21, 43, 47):
    sy = 43 - 11.0 * math.sqrt(max(0, 1 - ((sx - CX) / 21.5) ** 2))
    ellipse(4, sx, sy + 0.8, 1.7, 2.0, bias=0.1)

# eye stalks

# ---- rasterise -----------------------------------------------------------
label = [[None] * N for _ in range(N)]
inten = [[0.0] * N for _ in range(N)]
for z, f in sorted(parts, key=lambda p: p[0]):
    for y in range(N):
        for x in range(N):
            v = f(x, y)
            if v is not None:
                label[y][x] = z
                inten[y][x] = v

def tone(v):
    # thresholds tuned by eye
    if v < 0.05: return 0
    if v < 0.32: return 1
    if v < 0.58: return 2
    if v < 0.80: return 3
    return 4

px = [[None] * N for _ in range(N)]
for y in range(N):
    for x in range(N):
        if label[y][x] is not None:
            px[y][x] = SHELL[tone(inten[y][x])]

# inner lines: where a part sits in front of another, darken the back one
for y in range(N):
    for x in range(N):
        z = label[y][x]
        if z is None: continue
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < N and 0 <= ny < N and label[ny][nx] is not None and label[ny][nx] > z:
                px[y][x] = INNER
                break

# outer outline
outline = set()
for y in range(N):
    for x in range(N):
        if label[y][x] is None:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < N and 0 <= ny < N and label[ny][nx] is not None:
                    outline.add((x, y)); break
for x, y in outline:
    px[y][x] = OUTLINE

def put(x, y, c):
    if 0 <= x < N and 0 <= y < N: px[y][x] = c

# shell texture: a few pitted dots and a highlight sweep
for x, y in ((18, 44), (46, 44), (22, 49), (42, 49)):
    if px[y][x] in SHELL[2:]:
        put(x, y, SHELL[1])
        put(x - 1, y - 1, SHELL[4] if px[y - 1][x - 1] == SHELL[3] else px[y - 1][x - 1])

# mouth: a small smug smile
for x, y in ((29, 43), (30, 44), (31, 44), (32, 44), (33, 44), (34, 43)):
    put(x, y, INNER)

# ---- sunglasses ----------------------------------------------------------
# frame bar across both stalk tops, lenses below it
for x in range(19, 46):
    put(x, 34, GLASS)
for x in (19, 45):
    put(x, 35, GLASS)
for cx in (25, 39):
    for x in range(cx - 5, cx + 6):
        for y in range(35, 40):
            # trapezoid lens, wider at the top
            if y - 35 > 2 and (x == cx - 5 or x == cx + 5):
                continue
            if y == 39 and (x <= cx - 4 or x >= cx + 4):
                continue
            edge = (y == 39) or x in (cx - 5, cx + 5) or (y == 38 and x in (cx - 4, cx + 4))
            put(x, y, GLASS if edge else LENS[0 if y >= 38 else 1 if y >= 36 else 2])
    put(cx - 3, 36, GLINT[0]); put(cx - 2, 36, GLINT[1]); put(cx - 3, 37, GLINT[1])
for x in range(31, 34):
    put(x, 35, GLASS)          # bridge
# frame top catches the sky


crab = [row[:] for row in px]

# ---- background ----------------------------------------------------------
def background():
    bg = [[None] * N for _ in range(N)]
    horizon = 50
    for y in range(N):
        band = min(len(SKY) - 1, int(y / horizon * len(SKY)))
        for x in range(N):
            bg[y][x] = SKY[band]
    # stars
    for x, y in ((6, 5), (14, 11), (52, 7), (58, 15), (45, 3), (3, 18), (60, 26), (21, 4)):
        bg[y][x] = "#e9d9ff"
    # striped sun behind the crab
    scx, scy, r = 32, 27, 16
    for y in range(N):
        for x in range(N):
            d = math.hypot(x + 0.5 - scx, y + 0.5 - scy)
            if d <= r and y < horizon:
                k = (y - (scy - r)) / (2 * r)
                # stripes cut through the lower half, thicker toward the horizon
                if y > scy - 2 and (y - scy) % 5 in ((0,) if y < scy + 6 else (0, 1)):
                    continue
                bg[y][x] = SUN[min(len(SUN) - 1, int(k * len(SUN)))]
    # ground and track
    for y in range(horizon, N):
        for x in range(N):
            bg[y][x] = GROUND
    for x in range(N):
        if x % 7 in (1, 2, 3, 4):
            bg[60][x] = TIE[1]; bg[61][x] = TIE[0]
        bg[57][x] = RAIL[2]; bg[58][x] = RAIL[1]; bg[59][x] = RAIL[0]
    return bg

def compose(with_bg):
    out = background() if with_bg else [[None] * N for _ in range(N)]
    if not with_bg:
        # the track stays, so the transparent mark still says Rails
        b = background()
        for y in range(57, 62):
            for x in range(N):
                if b[y][x] in RAIL + TIE:
                    out[y][x] = b[y][x]
    for y in range(N):
        for x in range(N):
            if crab[y][x] is not None:
                out[y][x] = crab[y][x]
    return out

def svg(grid):
    rects = []
    for y, row in enumerate(grid):
        x = 0
        while x < N:
            c = row[x]
            if c is None:
                x += 1; continue
            run = 1
            while x + run < N and row[x + run] == c:
                run += 1
            rects.append(f'<rect x="{x}" y="{y}" width="{run}" height="1" fill="{c}"/>')
            x += run
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {N} {N}" width="512" '
            f'height="512" shape-rendering="crispEdges">{"".join(rects)}</svg>')

open("logo.svg", "w").write(svg(compose(True)))
open("logo-transparent.svg", "w").write(svg(compose(False)))
