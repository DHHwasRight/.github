# DHHwasRight logo, v3: a Ferris-shaped crab in vibe-coder shades, standing
# on a railway track at sunset. 64x64.
#
# Parts are drawn as shapes into a label grid, lit from the top left,
# reduced to a five-tone palette, then outlined. Output is SVG of 1x1 rects.
import math

N = 64

# ---- palette (validated, do not drift) -----------------------------------
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
STAR = "#e9d9ff"

# ---- shape helpers -------------------------------------------------------
LIGHT = (-0.55, -0.65, 0.53)
_l = math.sqrt(sum(c * c for c in LIGHT))
LIGHT = tuple(c / _l for c in LIGHT)

def lit(nx, ny):
    nz = math.sqrt(max(0.0, 1 - nx * nx - ny * ny))
    return nx * LIGHT[0] + ny * LIGHT[1] + nz * LIGHT[2]

def seg(px, py, ax, ay, bx, by):
    vx, vy = bx - ax, by - ay
    t = max(0.0, min(1.0, ((px - ax) * vx + (py - ay) * vy) / (vx * vx + vy * vy)))
    qx, qy = ax + t * vx, ay + t * vy
    return math.hypot(px - qx, py - qy), t, px - qx, py - qy

parts = []   # (z, fn(px, py) -> intensity | None)

def limb(z, pts, w0, w1, bias=0.0):
    segs = list(zip(pts, pts[1:]))
    n = len(segs)
    def f(px, py):
        best = None
        for i, ((ax, ay), (bx, by)) in enumerate(segs):
            d, t, ox, oy = seg(px, py, ax, ay, bx, by)
            r = (w0 + (w1 - w0) * ((i + t) / n)) / 2
            if d <= r:
                v = lit(0.9 * ox / (r + 1e-6), 0.9 * oy / (r + 1e-6)) + bias
                best = v if best is None else max(best, v)
        return best
    parts.append((z, f))

def claw(z, cx, cy, rx, ry, open_dir, gape=24, bias=0.08):
    """A pincer: a fat palm with a wedge cut toward `open_dir`."""
    dx0, dy0 = open_dir
    dl = math.hypot(dx0, dy0); dx0, dy0 = dx0 / dl, dy0 / dl
    cosg = math.cos(math.radians(gape))
    def f(px, py):
        ex, ey = (px - cx) / rx, (py - cy) / ry
        if ex * ex + ey * ey > 1:
            return None
        vx, vy = px - cx, py - cy
        d = math.hypot(vx, vy)
        # the wedge starts a little behind the centre, so the jaw reads open
        if d > 0.8 and (vx * dx0 + vy * dy0) / d > cosg:
            return None
        return lit(ex, ey) + bias
    parts.append((z, f))

# ---- the crab ------------------------------------------------------------
BX, BY, RX, RY = 32.0, 42.0, 20.0, 17.5    # dome centre and radii
SPIKES, SPIKE_LEN = 10, 5.2

def dome(px, py):
    dx, dy = px - BX, py - BY
    if dy > 0:
        # the underside is a shallow arc, lower in the middle
        lip = 3.2 * max(0.0, 1 - (dx / RX) ** 2)
        if abs(dx) <= RX and dy <= lip:
            return -0.2 if dy > lip - 2.2 else 0.15   # belly shadow band
        return None
    ang = math.atan2(-dy, dx)                        # 0 right, pi left
    # sawtooth along the top, fading out near the sides like Ferris
    phase = (ang / math.pi) * SPIKES
    tri = 1 - abs((phase % 1) * 2 - 1)
    edge_fade = min(1.0, math.sin(ang) * 2.2)
    rx = RX + SPIKE_LEN * tri * edge_fade
    ry = RY + SPIKE_LEN * tri * edge_fade
    if (dx / rx) ** 2 + (dy / ry) ** 2 > 1:
        return None
    return 0.55 * lit(dx / (RX + 2), dy / (RY + 2)) + 0.28
parts.append((4, dome))

# legs: thin, under the dome, splayed differently on each side
limb(1, [(15, 42), (9, 45), (6, 52), (7, 54)], 3.2, 1.8)
limb(1, [(20, 44), (16, 49), (15, 54)], 3.0, 1.8)
limb(1, [(48, 42), (54, 46), (57, 51), (58, 54)], 3.2, 1.8)
limb(1, [(44, 44), (47, 49), (48, 54)], 3.0, 1.8)

# arms: right waves high, left rests out to the side
limb(2, [(15, 41), (8, 41), (5, 37)], 4.2, 3.4, bias=0.05)
claw(3, 6.0, 31.0, 5.2, 5.8, (-0.45, -1.0), gape=24)
limb(2, [(50, 38), (57, 32), (56, 22)], 4.2, 3.4, bias=0.05)
claw(3, 55.5, 16.0, 5.6, 6.4, (-0.35, -1.0))

# ---- rasterise the crab --------------------------------------------------
label = [[None] * N for _ in range(N)]
val = [[0.0] * N for _ in range(N)]
for z, f in sorted(parts, key=lambda p: p[0]):
    for y in range(N):
        for x in range(N):
            v = f(x + 0.5, y + 0.5)
            if v is not None:
                label[y][x] = z
                val[y][x] = v

def tone(v):
    return 0 if v < 0.05 else 1 if v < 0.32 else 2 if v < 0.58 else 3 if v < 0.80 else 4

crab = [[None] * N for _ in range(N)]
for y in range(N):
    for x in range(N):
        if label[y][x] is not None:
            crab[y][x] = SHELL[tone(val[y][x])]

def inside(x, y):
    return 0 <= x < N and 0 <= y < N

# inner line where a part sits in front of another
for y in range(N):
    for x in range(N):
        z = label[y][x]
        if z is None:
            continue
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if inside(nx, ny) and label[ny][nx] is not None and label[ny][nx] > z:
                crab[y][x] = INNER
                break

# fill holes the background cannot reach from the edge (gaps between limbs)
reach = [[False] * N for _ in range(N)]
stack = [(x, y) for x in range(N) for y in (0, N - 1)] + [(x, y) for y in range(N) for x in (0, N - 1)]
while stack:
    x, y = stack.pop()
    if not inside(x, y) or reach[y][x] or label[y][x] is not None:
        continue
    reach[y][x] = True
    stack += [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
for y in range(N):
    for x in range(N):
        if label[y][x] is None and not reach[y][x]:
            label[y][x] = 0
            crab[y][x] = INNER

# outer outline
ring = []
for y in range(N):
    for x in range(N):
        if label[y][x] is None and any(
            inside(x + dx, y + dy) and label[y + dy][x + dx] is not None
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
            ring.append((x, y))
for x, y in ring:
    crab[y][x] = OUTLINE

def put(x, y, c):
    if inside(x, y):
        crab[y][x] = c

# a sheen on the upper left of the shell, and a few pits on the right
for x, y in ((19, 29), (20, 28), (21, 27), (22, 26), (23, 26)):
    if crab[y][x] in SHELL[2:]:
        put(x, y, SHELL[4])
for x, y in ((42, 36), (46, 38), (40, 27), (47, 34)):
    if crab[y][x] in SHELL[1:]:
        put(x, y, SHELL[1])

# ---- shades, tilted one pixel (the right side sits higher) ---------------
def lens(cx, top):
    for x in range(cx - 5, cx + 6):
        for y in range(top, top + 5):
            r = y - top
            if r >= 3 and x in (cx - 5, cx + 5):
                continue
            if r == 4 and (x <= cx - 4 or x >= cx + 4):
                continue
            edge = r == 4 or x in (cx - 5, cx + 5) or (r == 3 and x in (cx - 4, cx + 4))
            put(x, y, GLASS if edge else LENS[0 if r >= 3 else 1 if r >= 1 else 2])
    put(cx - 3, top + 1, GLINT[0]); put(cx - 2, top + 1, GLINT[1]); put(cx - 3, top + 2, GLINT[1])

for x in range(19, 32):
    put(x, 31, GLASS)                       # left half of the bar
for x in range(32, 46):
    put(x, 30, GLASS)                       # right half, one pixel up
put(19, 32, GLASS); put(45, 31, GLASS)      # hinges
lens(25, 32)
lens(38, 31)
put(31, 32, GLASS); put(32, 31, GLASS)      # bridge

# mouth: Ferris's small open smile, off to the left a touch
for x, y, c in ((29, 39, OUTLINE), (30, 40, OUTLINE), (31, 40, OUTLINE), (32, 40, OUTLINE),
                (33, 39, OUTLINE), (30, 39, INNER), (31, 39, SHELL[0]), (32, 39, INNER)):
    put(x, y, c)

# ---- scene ---------------------------------------------------------------
HORIZON = 49

def scene():
    g = [[None] * N for _ in range(N)]
    for y in range(N):
        band = min(len(SKY) - 1, int(y / HORIZON * len(SKY)))
        for x in range(N):
            g[y][x] = SKY[band]
    for x, y in ((5, 4), (13, 13), (27, 3), (36, 9), (49, 5), (58, 12), (61, 3), (44, 16), (3, 23)):
        g[y][x] = STAR
    # sun, off to the left, striped toward the horizon
    scx, scy, r = 17, 27, 14
    for y in range(N):
        for x in range(N):
            if math.hypot(x + 0.5 - scx, y + 0.5 - scy) <= r and y < HORIZON:
                if y > scy and (y - scy) % 4 == 1 + (y - scy) // 8:
                    continue
                k = (y - (scy - r)) / (2 * r)
                g[y][x] = SUN[min(len(SUN) - 1, int(k * len(SUN)))]
    # a far hill on the right balances the sun
    for x in range(N):
        top = HORIZON - int(7 * max(0.0, 1 - ((x - 52) / 16) ** 2) + 2 * max(0.0, 1 - ((x - 38) / 7) ** 2))
        for y in range(top, HORIZON):
            g[y][x] = SKY[1] if y > top else SKY[2]
    # ground: gravel bed
    for y in range(HORIZON, N):
        for x in range(N):
            g[y][x] = GROUND
    for x, y in ((3, 51), (11, 63), (17, 50), (26, 62), (33, 51), (40, 63), (49, 50), (55, 62),
                 (62, 51), (8, 56), (21, 57), (52, 56), (60, 61), (30, 56), (44, 61)):
        g[y][x] = RAIL[0]
    return g

FAR_RAIL, NEAR_RAIL = 52, 57

def ties(g):
    # 3/4 view: each tie is a plank, narrow at the far rail, wide at the near
    for i in range(-1, 10):
        x0 = 2 + i * 9
        for y in range(FAR_RAIL - 2, NEAR_RAIL + 6):
            k = (y - (FAR_RAIL - 2)) / (NEAR_RAIL + 6 - (FAR_RAIL - 2))
            w = 4 + round(4 * k)
            sx = x0 - round(2 * k)                 # slight lean: vanishing to the right
            for x in range(sx, sx + w):
                if 0 <= x < N:
                    face = TIE[1] if x < sx + w - 1 else TIE[0]
                    if y == NEAR_RAIL + 5:
                        face = TIE[0]                # front edge of the plank
                    g[y][x] = face

def rail(g, y, thick):
    for x in range(N):
        g[y][x] = RAIL[2]
        g[y + 1][x] = RAIL[1]
        if thick:
            g[y + 2][x] = RAIL[0]
    for x in range(N):
        if g[y + (3 if thick else 2)][x] in TIE:
            g[y + (3 if thick else 2)][x] = TIE[0]   # rail shadow on the ties
    if thick:
        for i in range(-1, 10):
            bx = 2 + i * 9 - 2
            for x in (bx, bx + 6):
                if 0 <= x < N:
                    g[y + 2][x] = RAIL[1]            # tie plates and bolts

def compose(with_sky):
    g = scene() if with_sky else [[None] * N for _ in range(N)]
    ties(g)
    rail(g, FAR_RAIL, thick=False)
    for y in range(N):
        for x in range(N):
            if crab[y][x] is not None:
                g[y][x] = crab[y][x]
    rail(g, NEAR_RAIL, thick=True)                   # in front of the feet
    return g

def svg(grid):
    rects = []
    for y, row in enumerate(grid):
        x = 0
        while x < N:
            c = row[x]
            if c is None:
                x += 1
                continue
            run = 1
            while x + run < N and row[x + run] == c:
                run += 1
            rects.append(f'<rect x="{x}" y="{y}" width="{run}" height="1" fill="{c}"/>')
            x += run
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {N} {N}" width="512" '
            f'height="512" shape-rendering="crispEdges">{"".join(rects)}</svg>')

open("logo.svg", "w").write(svg(compose(True)))
open("logo-transparent.svg", "w").write(svg(compose(False)))
