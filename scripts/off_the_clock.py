"""Builds profile/off-the-clock.svg: the casual card's interests as a
night-mode board (black / cream / flyer red, Anton + Geist). Edit BOARD below.
Needs: fonttools, fonts in ./fonts (see .github/workflows/profile.yml)."""
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.varLib.instancer import instantiateVariableFont

BOARD = [
    ("Music", "Loud, then very quiet.",
     ["Deftones", "Nirvana", "Have a Nice Life", "Slowdive", "Type O Negative", "Radiohead", "shoegaze", "late-night drives"]),
    ("Making", "Websites that feel inhabited.",
     ["SvelteKit", "WebGL shaders", "NIL", "RouteSim", "homelab", "self-hosting", "small-business sites"]),
    ("Analog", "Anything with a dial.",
     ["35mm film", "disposables", "cassettes", "CRTs", "flyers on telephone poles"]),
    ("Watching", "2am TV energy.",
     ["Donnie Darko", "Serial Experiments Lain", "Adult Swim bumpers", "concert docs"]),
    ("Playing", "The server is always up.",
     ["Minecraft", "modded servers", "co-op anything", "old handhelds"]),
]

W, PAD, GAP = 880, 36, 10
BG, SURF, INK, DIM, FAINT, RED = "#070707", "#0e0e0e", "#ece7dd", "#8c877d", "#57534c", "#e01b2e"
LINE = "#1f1e1c"


def font(path, wght=None):
    f = TTFont(path)
    return instantiateVariableFont(f, {"wght": wght}) if wght and "fvar" in f else f


anton, sans, sans_b, mono = (font("fonts/Anton.ttf"), font("fonts/Geist.ttf", 420),
                             font("fonts/Geist.ttf", 560), font("fonts/GeistMono.ttf", 450))


def width(f, s, size):
    cmap, k = f.getBestCmap(), size / f["head"].unitsPerEm
    return sum(f["hmtx"][cmap[ord(c)]][0] for c in s if ord(c) in cmap) * k


def text(f, s, x, y, size, track=0.0):
    gs, cmap, k, out = f.getGlyphSet(), f.getBestCmap(), size / f["head"].unitsPerEm, []
    for ch in s:
        g = cmap.get(ord(ch))
        if g is None: continue
        pen = SVGPathPen(gs, ntos=lambda v: f"{v:.1f}".rstrip("0").rstrip("."))
        gs[g].draw(TransformPen(pen, (k, 0, 0, -k, x, y))); out.append(pen.getCommands())
        x += f["hmtx"][g][0] * k + track
    return "".join(out)


body, y = [], 118
# header
body.append(f'<path fill="{INK}" d="{text(anton, "OFF THE CLOCK", PAD, 78, 46, 1)}"/>')
tag = "FLORIDA · AFTER DARK"
body.append(f'<path fill="{RED}" d="{text(mono, tag, W - PAD - width(mono, tag, 13) - 1.2 * len(tag), 72, 13, 1.2)}"/>')
body.append(f'<rect x="{PAD}" y="96" width="{W - 2 * PAD}" height="1" fill="{LINE}"/>')

for i, (label, blurb, items) in enumerate(BOARD):
    y += 16
    idx = f"{i + 1:02d}"
    body.append(f'<path fill="{FAINT}" d="{text(mono, idx, PAD, y + 4, 12)}"/>')
    body.append(f'<path fill="{INK}" d="{text(sans_b, label, PAD + 30, y + 5, 17)}"/>')
    body.append(f'<path fill="{DIM}" d="{text(sans, blurb, PAD + 30 + width(sans_b, label, 17) + 12, y + 5, 14)}"/>')
    y += 22
    x = PAD + 30
    for j, item in enumerate(items):
        w = width(sans, item, 14) + 28
        if x + w > W - PAD:
            x, y = PAD + 30, y + 38
        hot = j == 0
        body.append(f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="30" rx="15" '
                    f'fill="{RED if hot else SURF}" stroke="{RED if hot else "#2a2826"}"/>')
        body.append(f'<path fill="{"#fff6f2" if hot else INK}" d="{text(sans, item, x + 14, y + 20, 14)}"/>')
        x += w + GAP
    y += 30 + 14
    if i < len(BOARD) - 1:
        body.append(f'<rect x="{PAD}" y="{y + 6}" width="{W - 2 * PAD}" height="1" fill="{LINE}"/>')
    y += 8

H = y + 26
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
       f'aria-label="Off the clock: music, making, analog, watching, playing">\n'
       f'<defs><radialGradient id="g" cx="{W - 60}" cy="-40" r="520" gradientUnits="userSpaceOnUse">'
       f'<stop offset="0" stop-color="{RED}" stop-opacity=".38"/><stop offset="1" stop-color="{RED}" stop-opacity="0"/></radialGradient>'
       f'<clipPath id="c"><rect width="{W}" height="{H}" rx="24"/></clipPath><pattern id="d" width="6" height="6" patternUnits="userSpaceOnUse"><rect width="2" height="2" fill="{RED}" opacity=".16"/></pattern></defs>\n'
       f'<rect width="{W}" height="{H}" rx="24" fill="{BG}"/>'
       f'<rect width="{W}" height="{H}" rx="24" fill="url(#g)"/>'
       f'<rect x="{W - 300}" width="300" height="110" fill="url(#d)" opacity=".9" clip-path="url(#c)"/>'
       f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="23.5" fill="none" stroke="#1c1b19"/>\n'
       + "\n".join(body) + "\n</svg>\n")
open("profile/off-the-clock.svg", "w", encoding="utf-8").write(svg)
print(f"off-the-clock.svg: {len(svg):,} bytes, {W}x{H}")
