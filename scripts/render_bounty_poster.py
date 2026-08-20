#!/usr/bin/env python3
"""
render_bounty_poster.py — a "wanted poster" styled stats card, built from
data/contributions.json (see fetch_contributions.py). Purely original
layout/art — no official One Piece assets.

Usage: python scripts/render_bounty_poster.py
Output: assets/bounty-poster.svg
"""
import json
import os

WIDTH = 380
HEIGHT = 460

PARCHMENT = "#f1e3bf"
PARCHMENT_EDGE = "#c9aa63"
INK = "#0a0a0a"
RED = "#c62828"
GOLD_DARK = "#a97a24"

FONT = "'SFMono-Regular',Menlo,Consolas,'Liberation Mono',monospace"

# Primary languages across public repos (by repo count) — update by hand if
# your stack shifts; GitHub doesn't expose this via a simple public scrape.
TOP_LANGUAGE = "TypeScript"

RANKS = [
    (0, "CAN'T EVEN SWIM YET"),
    (10, "SHIP'S CABIN HAND"),
    (50, "SUPERNOVA OF THE EAST BLUE"),
    (150, "ALMOST A YONKOU"),
    (500, "THE PIRATE KING!"),
]


def rank_for(total):
    label = RANKS[0][1]
    for threshold, name in RANKS:
        if total >= threshold:
            label = name
    return label


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def mini_skull(cx, cy, scale=1.0):
    s = scale
    parts = [f'<g transform="translate({cx},{cy}) scale({s})">']
    for angle in (35, -35):
        parts.append(
            f'<g transform="rotate({angle})">'
            f'<rect x="-30" y="-3.5" width="60" height="7" rx="3.5" fill="{INK}"/>'
            f'<circle cx="-30" cy="0" r="5" fill="{INK}"/>'
            f'<circle cx="30" cy="0" r="5" fill="{INK}"/>'
            f'</g>'
        )
    parts.append(f'<circle cx="0" cy="-2" r="20" fill="{PARCHMENT}" stroke="{INK}" stroke-width="2.5"/>')
    parts.append(
        f'<path d="M -11,11 Q 0,23 11,11 L 9,5 Q 0,11 -9,5 Z" '
        f'fill="{PARCHMENT}" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round"/>'
    )
    parts.append(f'<circle cx="-7" cy="-3" r="5" fill="{INK}"/>')
    parts.append(f'<circle cx="7" cy="-3" r="5" fill="{INK}"/>')
    parts.append(f'<path d="M 0,2 L -3,7 L 3,7 Z" fill="{INK}"/>')
    # small straw hat, matching the hero banner emblem
    parts.append(f'<ellipse cx="0" cy="-16" rx="30" ry="6.5" fill="#e2b658" stroke="{INK}" stroke-width="1.5"/>')
    parts.append(
        f'<path d="M -15,-17 Q -15,-32 0,-33 Q 15,-32 15,-17 Q 15,-12 0,-12 Q -15,-12 -15,-17 Z" '
        f'fill="#e2b658" stroke="{INK}" stroke-width="1.5" stroke-linejoin="round"/>'
    )
    parts.append(f'<rect x="-15" y="-18" width="30" height="4.5" fill="#c62828" stroke="{INK}" stroke-width="1"/>')
    parts.append('</g>')
    return "".join(parts)


def build_svg(data):
    stats = data["stats"]
    total = stats.get("total", 0)
    streak = stats.get("current_streak", 0)
    longest = stats.get("longest_streak", 0)
    rank = rank_for(total)

    parts = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" '
        f'width="{WIDTH}" height="{HEIGHT}">'
    )
    parts.append(f'''
    <defs>
      <radialGradient id="vignette" cx="50%" cy="45%" r="75%">
        <stop offset="0.6" stop-color="{PARCHMENT}" stop-opacity="0"/>
        <stop offset="1" stop-color="#5c4522" stop-opacity="0.35"/>
      </radialGradient>
    </defs>
    ''')
    parts.append(f'<rect width="{WIDTH}" height="{HEIGHT}" rx="8" fill="{PARCHMENT}"/>')
    parts.append(f'<rect width="{WIDTH}" height="{HEIGHT}" rx="8" fill="url(#vignette)"/>')
    parts.append(
        f'<rect x="10" y="10" width="{WIDTH-20}" height="{HEIGHT-20}" fill="none" '
        f'stroke="{PARCHMENT_EDGE}" stroke-width="2"/>'
    )
    parts.append(
        f'<rect x="14" y="14" width="{WIDTH-28}" height="{HEIGHT-28}" fill="none" '
        f'stroke="{GOLD_DARK}" stroke-width="1"/>'
    )

    cx = WIDTH // 2
    parts.append(
        f'<text x="{cx}" y="52" text-anchor="middle" font-family="{FONT}" '
        f'font-size="30" font-weight="bold" letter-spacing="6" fill="{RED}">WANTED</text>'
    )
    parts.append(
        f'<line x1="34" y1="66" x2="{WIDTH-34}" y2="66" stroke="{INK}" stroke-width="1.5"/>'
    )

    parts.append(mini_skull(cx, 118, scale=1.05))

    parts.append(
        f'<text x="{cx}" y="178" text-anchor="middle" font-family="{FONT}" '
        f'font-size="10.5" letter-spacing="1" fill="{INK}">CONTRIBUTIONS CONFIRMED</text>'
    )

    # size the pill to fit the rank text (names vary a lot in length)
    rank_font_size = 15 if len(rank) <= 18 else 12.5
    pill_w = min(WIDTH - 40, max(180, len(rank) * (rank_font_size * 0.72) + 40))
    parts.append(
        f'<rect x="{cx-pill_w/2:.1f}" y="196" width="{pill_w:.1f}" height="34" rx="17" fill="{RED}"/>'
    )
    parts.append(
        f'<text x="{cx}" y="219" text-anchor="middle" font-family="{FONT}" '
        f'font-size="{rank_font_size}" font-weight="bold" letter-spacing="1.5" fill="{PARCHMENT}">{esc(rank)}</text>'
    )

    rows = [
        ("Contributions (1 year)", str(total)),
        ("Current streak", f"{streak} day" + ("s" if streak != 1 else "")),
        ("Longest streak", f"{longest} day" + ("s" if longest != 1 else "")),
        ("Main language", TOP_LANGUAGE),
    ]
    y = 260
    for label, value in rows:
        parts.append(
            f'<text x="34" y="{y}" font-family="{FONT}" font-size="13" fill="{GOLD_DARK}">{esc(label)}</text>'
        )
        parts.append(
            f'<text x="{WIDTH-34}" y="{y}" text-anchor="end" font-family="{FONT}" '
            f'font-size="13" font-weight="bold" fill="{INK}">{esc(value)}</text>'
        )
        y += 30

    parts.append(f'<line x1="34" y1="{y+2}" x2="{WIDTH-34}" y2="{y+2}" stroke="{GOLD_DARK}" stroke-width="1"/>')

    parts.append(
        f'<text x="{cx}" y="{HEIGHT-34}" text-anchor="middle" font-family="{FONT}" '
        f'font-size="10.5" fill="{INK}" opacity="0.75">Issued by: GitHub HQ · updated daily</text>'
    )
    parts.append(
        f'<text x="{cx}" y="{HEIGHT-18}" text-anchor="middle" font-family="{FONT}" '
        f'font-size="9.5" fill="{INK}" opacity="0.55">generated on {esc(data.get("generated_at","")[:10])}</text>'
    )

    parts.append('</svg>')
    return "\n".join(parts)


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.dirname(here)
    data_path = os.path.join(root, "data", "contributions.json")
    out_path = os.path.join(root, "assets", "bounty-poster.svg")

    with open(data_path) as f:
        data = json.load(f)

    svg = build_svg(data)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        f.write(svg)
    print(f"Saved {out_path}")


if __name__ == "__main__":
    main()
