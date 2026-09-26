"""Builds banner.svg (paper / graphite / clay, dithered dasdev mark).
Run by .github/workflows/profile.yml. Needs: pillow numpy fonttools, fonts in ./fonts."""
import base64, io, math
import numpy as np
from PIL import Image, ImageDraw
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.varLib.instancer import instantiateVariableFont

W, H, L = 1600, 420, 460
BG, INK, DIM, FAINT, CLAY = "#e2dbcc", "#141311", "#544f46", "#80796d", "#a84321"
PAL = np.array([(20, 19, 17), (118, 111, 99), (236, 231, 220)], dtype=np.uint8)
MARK = ("M578 905 893 485M642 1051 957 630", "M722 517A256 256 0 0 0 514 795M1021 740A256 256 0 0 1 812 1019")


def mark_mask(size):
    """The dasdev mark rasterised as an alpha mask, cropped to its ink."""
    sc = 4; h = size * sc; w = int(h * 628 / 728); k = h / 728
    im = Image.new("L", (w, h), 0); d = ImageDraw.Draw(im)
    X = lambda x: (x - 454) * k; Y = lambda y: (y - 404) * k
    def dot(p, r): d.ellipse([X(p[0]) - r, Y(p[1]) - r, X(p[0]) + r, Y(p[1]) + r], fill=255)
    for a, b in (((578, 905), (893, 485)), ((642, 1051), (957, 630))):
        d.line([(X(a[0]), Y(a[1])), (X(b[0]), Y(b[1]))], fill=255, width=int(104 * k)); dot(a, 52 * k); dot(b, 52 * k)
    cx, cy, r, sw = X(767.5), Y(767.5), 256 * k, 60 * k
    for p0, p1 in (((514, 795), (722, 517)), ((1021, 740), (812, 1019))):
        ang = lambda p: math.degrees(math.atan2(Y(p[1]) - cy, X(p[0]) - cx))
        d.arc([cx - r - sw / 2, cy - r - sw / 2, cx + r + sw / 2, cy + r + sw / 2], ang(p0), ang(p1), fill=255, width=int(sw))
        dot(p0, sw / 2); dot(p1, sw / 2)
    im = im.resize((w // sc, h // sc), Image.LANCZOS)
    return im.crop(im.getbbox())


def tile_png(n=106):
    """Bayer-dithered tile: light centre, dark edges, mark knocked out dead centre."""
    yy, xx = np.mgrid[0:n, 0:n] / (n - 1)
    lum = np.clip(1.05 - np.hypot(xx - 0.5, yy - 0.5) * 1.55, 0, 1)
    m = mark_mask(int(n * 0.62)); mk = Image.new("L", (n, n), 0)
    mk.paste(m, ((n - m.size[0]) // 2, (n - m.size[1]) // 2))
    lum *= 1 - np.asarray(mk) / 255 * 0.97
    B = np.array([[0,32,8,40,2,34,10,42],[48,16,56,24,50,18,58,26],[12,44,4,36,14,46,6,38],[60,28,52,20,62,30,54,22],
                  [3,35,11,43,1,33,9,41],[51,19,59,27,49,17,57,25],[15,47,7,39,13,45,5,37],[63,31,55,23,61,29,53,21]]) / 64
    th = B[np.arange(n)[:, None] % 8, np.arange(n)[None, :] % 8]
    v = lum * 2; lvl = np.clip(np.floor(v) + ((v - np.floor(v)) > th), 0, 2).astype(int)
    buf = io.BytesIO(); Image.fromarray(PAL[lvl]).quantize(colors=3).save(buf, "PNG", optimize=True)
    return base64.b64encode(buf.getvalue()).decode()


def font(path, wght=None):
    f = TTFont(path)
    return instantiateVariableFont(f, {"wght": wght}) if wght and "fvar" in f else f


def text(f, s, x, y, size):
    gs, cmap, k, out = f.getGlyphSet(), f.getBestCmap(), size / f["head"].unitsPerEm, []
    for ch in s:
        g = cmap.get(ord(ch))
        if g is None: continue
        pen = SVGPathPen(gs, ntos=lambda v: str(round(v)))
        gs[g].draw(TransformPen(pen, (k, 0, 0, -k, x, y))); out.append(pen.getCommands())
        x += f["hmtx"][g][0] * k
    return "".join(out)


serif = font("fonts/InstrumentSerif-Regular.ttf")
sans = lambda w: font("fonts/Geist.ttf", w)
mono = lambda w: font("fonts/GeistMono.ttf", w)
mark = lambda x, y, s, c: (f'<g transform="translate({x} {y}) scale({s / 728:.5f}) translate(-454 -404)" fill="none" '
                           f'stroke="{c}" stroke-linecap="round"><path d="{MARK[0]}" stroke-width="104"/>'
                           f'<path d="{MARK[1]}" stroke-width="60"/></g>')

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Arriq, web developer and design engineer, dasdev.net">
<defs>
<radialGradient id="w" cx="{W - 130}" cy="-30" r="760" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#cfa085" stop-opacity=".95"/><stop offset=".55" stop-color="#d9b9a3" stop-opacity=".45"/><stop offset="1" stop-color="{BG}" stop-opacity="0"/></radialGradient>
<filter id="s" x="-20%" y="-20%" width="140%" height="150%"><feGaussianBlur stdDeviation="16"/></filter>
<clipPath id="c"><rect x="70" y="50" width="320" height="320" rx="28"/></clipPath>
</defs>
<rect width="{W}" height="{H}" fill="{BG}"/><rect width="{W}" height="{H}" fill="url(#w)"/>
<rect x="80" y="78" width="300" height="300" rx="28" fill="#6f6556" opacity=".45" filter="url(#s)"/>
<image href="data:image/png;base64,{tile_png()}" x="70" y="50" width="320" height="320" clip-path="url(#c)" preserveAspectRatio="none" style="image-rendering:pixelated"/>
{mark(L, 62, 30, CLAY)}
<path fill="{CLAY}" d="{text(mono(500), "DASDEV.NET · GITHUB", L + 36, 83, 20)}"/>
<path fill="{INK}" d="{text(serif, "Arriq", L, 210, 136)}"/>
<path fill="#262420" d="{text(sans(420), "Web developer & design engineer.", L, 304, 34)}"/>
<path fill="{DIM}" d="{text(sans(400), "Full-stack builder — sites, local-first tools, AI agents, security tooling.", L, 341, 24)}"/>
<path fill="{FAINT}" d="{text(mono(400), "SvelteKit  /  TypeScript  /  Node  /  Linux  /  WebGL", L, 378, 17)}"/>
</svg>
'''
open("banner.svg", "w", encoding="utf-8").write(svg)
print(f"banner.svg: {len(svg):,} bytes")
