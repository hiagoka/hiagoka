#!/usr/bin/env python3
"""
render_hero_banner.py — hand-drawn (original, not official One Piece art)
pirate skull-and-crossbones emblem over a night-sea banner, with name and
title. Static — regenerate manually if you change your name/title.

Usage: python scripts/render_hero_banner.py
Output: assets/hero-banner.svg
"""
import os

WIDTH = 900
HEIGHT = 220

NAVY_DARK = "#04070d"
NAVY_MID = "#0a1220"
NAVY_WAVE = "#111d30"
GOLD = "#e6b93d"
GOLD_DARK = "#a97a24"
CREAM = "#fbfaf6"
INK = "#0a0a0a"

NAME = "HIAGO KALIL"
TITLE = "Front-end Developer"
TAGLINE = "navegando entre TypeScript, React e um mar de commits"

FONT = "'SFMono-Regular',Menlo,Consolas,'Liberation Mono',monospace"


STRAW = "#e2b658"
STRAW_DARK = "#b8892f"
BAND_RED = "#c62828"


def skull_emblem(cx, cy, scale=1.0):
    """
    Original skull-and-crossbones wearing a straw hat — an independent
    drawing evoking classic "straw hat pirate" iconography (a broad,
    public pirate trope), not a traced or closely-copied reproduction of
    any franchise's official logo/artwork.
    """
    s = scale
    parts = [f'<g transform="translate({cx},{cy}) scale({s})">']

    # crossbones (behind skull)
    for angle in (35, -35):
        parts.append(
            f'<g transform="rotate({angle})">'
            f'<rect x="-52" y="-6" width="104" height="12" rx="6" fill="{CREAM}" stroke="{INK}" stroke-width="2"/>'
            f'<circle cx="-52" cy="0" r="9" fill="{CREAM}" stroke="{INK}" stroke-width="2"/>'
            f'<circle cx="52" cy="0" r="9" fill="{CREAM}" stroke="{INK}" stroke-width="2"/>'
            f'</g>'
        )

    # skull
    parts.append(
        f'<circle cx="0" cy="0" r="40" fill="{CREAM}" stroke="{INK}" stroke-width="3"/>'
    )
    # jaw with a wide grin
    parts.append(
        f'<path d="M -22,22 Q 0,46 22,22 L 18,11 Q 0,22 -18,11 Z" '
        f'fill="{CREAM}" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>'
    )
    # teeth
    for tx in (-11, -3.7, 3.7, 11):
        parts.append(f'<line x1="{tx}" y1="19" x2="{tx}" y2="28" stroke="{INK}" stroke-width="2"/>')
    # round, friendly eye sockets
    parts.append(f'<circle cx="-14" cy="-4" r="9.5" fill="{INK}"/>')
    parts.append(f'<circle cx="14" cy="-4" r="9.5" fill="{INK}"/>')
    # nose
    parts.append(f'<path d="M 0,4 L -5,13 L 5,13 Z" fill="{INK}"/>')

    # straw hat: wide woven brim + rounded crown + red band
    parts.append(f'<ellipse cx="0" cy="-30" rx="58" ry="13" fill="{STRAW}" stroke="{INK}" stroke-width="2.5"/>')
    for i in range(-9, 10, 3):
        parts.append(f'<line x1="{i*6}" y1="-31" x2="{i*6+3}" y2="-29" stroke="{STRAW_DARK}" stroke-width="1.2"/>')
    parts.append(
        f'<path d="M -30,-32 Q -30,-62 0,-64 Q 30,-62 30,-32 Q 30,-24 0,-24 Q -30,-24 -30,-32 Z" '
        f'fill="{STRAW}" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round"/>'
    )
    parts.append(f'<rect x="-30" y="-34" width="60" height="9" fill="{BAND_RED}" stroke="{INK}" stroke-width="2"/>')

    parts.append('</g>')
    return "".join(parts)


def stars(n=26):
    # deterministic pseudo-random scatter (no random module, keeps output stable)
    pts = []
    seed = 17
    for i in range(n):
        seed = (seed * 1103515245 + 12345) & 0x7FFFFFFF
        x = seed % WIDTH
        seed = (seed * 1103515245 + 12345) & 0x7FFFFFFF
        y = seed % 70
        seed = (seed * 1103515245 + 12345) & 0x7FFFFFFF
        r = 0.6 + (seed % 100) / 100.0
        pts.append(f'<circle cx="{x}" cy="{y}" r="{r:.2f}" fill="{CREAM}" opacity="0.55"/>')
    return "".join(pts)


def build_svg():
    parts = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" '
        f'width="{WIDTH}" height="{HEIGHT}">'
    )
    parts.append(f'''
    <defs>
      <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="{NAVY_DARK}"/>
        <stop offset="1" stop-color="{NAVY_MID}"/>
      </linearGradient>
    </defs>
    ''')
    parts.append(f'<rect width="{WIDTH}" height="{HEIGHT}" rx="14" fill="url(#sky)"/>')
    parts.append(stars())

    # gentle waves near the bottom
    parts.append(
        f'<path d="M0,{HEIGHT-22} Q {WIDTH*0.125},{HEIGHT-34} {WIDTH*0.25},{HEIGHT-22} '
        f'T {WIDTH*0.5},{HEIGHT-22} T {WIDTH*0.75},{HEIGHT-22} T {WIDTH},{HEIGHT-22} '
        f'L {WIDTH},{HEIGHT} L 0,{HEIGHT} Z" fill="{NAVY_WAVE}" opacity="0.8"/>'
    )
    parts.append(
        f'<path d="M0,{HEIGHT-10} Q {WIDTH*0.16},{HEIGHT-20} {WIDTH*0.33},{HEIGHT-10} '
        f'T {WIDTH*0.66},{HEIGHT-10} T {WIDTH},{HEIGHT-10} L {WIDTH},{HEIGHT} L 0,{HEIGHT} Z" '
        f'fill="{NAVY_WAVE}" opacity="0.55"/>'
    )

    parts.append(
        f'<rect x="0.5" y="0.5" width="{WIDTH-1}" height="{HEIGHT-1}" rx="14" '
        f'fill="none" stroke="{GOLD_DARK}" stroke-width="1.5"/>'
    )

    parts.append(skull_emblem(WIDTH // 2, 66, scale=0.72))

    parts.append(
        f'<text x="{WIDTH//2}" y="150" text-anchor="middle" font-family="{FONT}" '
        f'font-size="34" font-weight="bold" letter-spacing="4" fill="{GOLD}">{NAME}</text>'
    )
    parts.append(
        f'<text x="{WIDTH//2}" y="176" text-anchor="middle" font-family="{FONT}" '
        f'font-size="15" fill="{CREAM}">{TITLE}</text>'
    )
    parts.append(
        f'<text x="{WIDTH//2}" y="198" text-anchor="middle" font-family="{FONT}" '
        f'font-size="11.5" fill="{GOLD_DARK}">{TAGLINE}</text>'
    )

    parts.append('</svg>')
    return "\n".join(parts)


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.dirname(here)
    out = os.path.join(root, "assets", "hero-banner.svg")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as f:
        f.write(build_svg())
    print(f"Saved {out}")


if __name__ == "__main__":
    main()
