#!/usr/bin/env python3
"""
make_info_card.py — hand-authored SVG that looks like `neofetch` output:
a title bar, then colored key/value rows (Now / Prev / Stack / Highlights).

Each line fades + slides in on a short stagger, then freezes (SMIL, plays
once — no looping). Set STATIC=1 to emit a frozen frame with no animation
(useful for local Quick Look previews on macOS, which doesn't run SMIL).

Usage: python scripts/make_info_card.py
Output: info-card.svg
"""
import os
import textwrap

WIDTH = 490
PAD_X = 22
PAD_TOP = 26

BG = "#0d1117"
BORDER = "#30363d"
HEADER_COLOR = "#e6edf3"
RULE_COLOR = "#30363d"
LABEL_W = 108

FONT = "'SFMono-Regular',Menlo,Consolas,'Liberation Mono',monospace"
FONT_SIZE = 13.5
LINE_H = 22
VALUE_WRAP = 40  # chars per value line before wrapping

USER_HOST = "hiago@github"

FIELDS = [
    ("Now", "Estudante de Ciência da Computação · Front-end Dev", "#7ee787"),
    ("Prev", "Rocketseat — trilha React Native", "#79c0ff"),
    ("Stack", "TypeScript · React · React Native · JS/HTML/CSS", "#d2a8ff"),
    ("Highlights", "Sistema web para a PMPB · ai-chat-mobile (React Native + OpenAI)", "#ffa657"),
]

SWATCHES = ["#f85149", "#ffa657", "#e3b341", "#7ee787", "#79c0ff", "#d2a8ff", "#ff9bce", "#e6edf3"]

STAGGER = 0.09
FADE_DUR = 0.45


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def wrap_value(text, width=VALUE_WRAP):
    return textwrap.wrap(text, width=width, break_long_words=False, break_on_hyphens=False) or [""]


def animated_group(inner_svg, index, static):
    """Wrap inner content so it fades in + slides up, staggered by index."""
    if static:
        return inner_svg
    begin = round(index * STAGGER, 3)
    return (
        f'<g opacity="0" transform="translate(0,8)">'
        f'<animate attributeName="opacity" from="0" to="1" dur="{FADE_DUR}s" '
        f'begin="{begin}s" fill="freeze"/>'
        f'<animateTransform attributeName="transform" type="translate" '
        f'from="0 8" to="0 0" dur="{FADE_DUR}s" begin="{begin}s" fill="freeze" '
        f'calcMode="spline" keySplines="0.25 0.1 0.25 1" keyTimes="0;1" values="0 8;0 0"/>'
        f'{inner_svg}'
        f'</g>'
    )


def build_svg(static=False):
    y = PAD_TOP
    body_parts = []
    idx = 0

    # title bar: three traffic-light dots + user@host
    dots = (
        f'<circle cx="{PAD_X + 5}" cy="{y - 5}" r="5" fill="#f85149"/>'
        f'<circle cx="{PAD_X + 22}" cy="{y - 5}" r="5" fill="#e3b341"/>'
        f'<circle cx="{PAD_X + 39}" cy="{y - 5}" r="5" fill="#3fb950"/>'
    )
    body_parts.append(animated_group(dots, idx, static))
    idx += 1

    y += 26
    header = (
        f'<text x="{PAD_X}" y="{y}" font-family="{FONT}" font-size="15" '
        f'font-weight="bold" fill="{HEADER_COLOR}">{esc(USER_HOST)}</text>'
    )
    body_parts.append(animated_group(header, idx, static))
    idx += 1

    y += 10
    rule = f'<line x1="{PAD_X}" y1="{y}" x2="{WIDTH - PAD_X}" y2="{y}" stroke="{RULE_COLOR}" stroke-width="1"/>'
    body_parts.append(animated_group(rule, idx, static))
    idx += 1

    y += LINE_H
    for label, value, color in FIELDS:
        lines = wrap_value(value)
        row_parts = []
        for li, line in enumerate(lines):
            ly = y + li * (LINE_H - 4)
            if li == 0:
                row_parts.append(
                    f'<text x="{PAD_X}" y="{ly}" font-family="{FONT}" font-size="{FONT_SIZE}" '
                    f'font-weight="bold" fill="{color}">{esc(label)}</text>'
                )
            row_parts.append(
                f'<text x="{PAD_X + LABEL_W}" y="{ly}" font-family="{FONT}" '
                f'font-size="{FONT_SIZE}" fill="#c9d1d9">{esc(line)}</text>'
            )
        body_parts.append(animated_group("".join(row_parts), idx, static))
        idx += 1
        y += (LINE_H - 4) * len(lines) + 8

    y += 6
    swatch_size = 16
    swatch_gap = 6
    swatches = []
    sx = PAD_X
    for c in SWATCHES:
        swatches.append(f'<rect x="{sx}" y="{y}" width="{swatch_size}" height="{swatch_size}" rx="3" fill="{c}"/>')
        sx += swatch_size + swatch_gap
    body_parts.append(animated_group("".join(swatches), idx, static))
    idx += 1

    y += swatch_size + PAD_TOP - 6
    height = y

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {height}" '
        f'width="{WIDTH}" height="{height}">',
        f'<rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{height - 1}" rx="10" '
        f'fill="{BG}" stroke="{BORDER}" stroke-width="1"/>',
    ]
    svg.extend(body_parts)
    svg.append('</svg>')
    return "\n".join(svg)


def main():
    static = os.environ.get("STATIC") == "1"
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.dirname(here)
    out = os.path.join(root, "info-card.svg")

    svg = build_svg(static=static)
    with open(out, "w") as f:
        f.write(svg)
    print(f"Saved {out} (static={static})")


if __name__ == "__main__":
    main()
