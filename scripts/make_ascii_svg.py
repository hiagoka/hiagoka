#!/usr/bin/env python3
"""
make_ascii_svg.py — convert source-prepped.png into a self-typing,
monochrome ASCII-art SVG that animates once (SMIL) and freezes.

Usage: python scripts/make_ascii_svg.py
Output: avi-ascii.svg
"""
import os
from PIL import Image

COLS = 100
ROWS = 53
RAMP = " .`:-=+*cs#%@"   # bright (sparse) -> dark (dense)
#      ^ leading space clears the background to nothing

FONT_SIZE = 12
CHAR_W = round(FONT_SIZE * 0.6, 2)   # monospace advance width
CHAR_H = round(FONT_SIZE * 1.16, 2)  # line height

TEXT_COLOR = "#9fb0c0"     # single light-gray fill, no per-char rainbow
CURSOR_COLOR = "#e6edf3"   # brighter block that rides the wipe edge
BG_COLOR = "#0d1117"       # dark terminal card so it reads on any page theme

ROW_DUR = 0.55       # seconds for one row to fully wipe in
ROW_STAGGER = 0.028  # seconds between each row's start


def image_to_grid(path):
    im = Image.open(path).convert("L").resize((COLS, ROWS), Image.LANCZOS)
    rows = []
    px = im.load()
    for y in range(ROWS):
        line = []
        for x in range(COLS):
            b = px[x, y]  # 0 dark .. 255 bright
            idx = int(round((255 - b) / 255 * (len(RAMP) - 1)))
            line.append(RAMP[idx])
        rows.append("".join(line))
    return rows


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_svg(rows):
    width = COLS * CHAR_W
    height = ROWS * CHAR_H

    parts = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {width:.2f} {height:.2f}" width="{width:.2f}" height="{height:.2f}">'
    )
    parts.append(
        f'<rect x="0" y="0" width="{width:.2f}" height="{height:.2f}" fill="{BG_COLOR}"/>'
    )
    parts.append(
        f'<style>text{{font-family:"SFMono-Regular",Menlo,Consolas,'
        f'"Liberation Mono",monospace;font-size:{FONT_SIZE}px;fill:{TEXT_COLOR};'
        f'white-space:pre;}}</style>'
    )

    for i, row_text in enumerate(rows):
        row_top = i * CHAR_H
        text_y = row_top + CHAR_H * 0.85  # baseline sits near the bottom of the row
        begin = round(i * ROW_STAGGER, 3)
        row_w = width
        clip_id = f"clip-row-{i}"

        parts.append(f'<clipPath id="{clip_id}">')
        parts.append(
            f'<rect x="0" y="{row_top:.2f}" width="0" height="{CHAR_H:.2f}">'
            f'<animate attributeName="width" from="0" to="{row_w:.2f}" '
            f'dur="{ROW_DUR}s" begin="{begin}s" fill="freeze" '
            f'calcMode="spline" keySplines="0.25 0.1 0.25 1" keyTimes="0;1" values="0;{row_w:.2f}"/>'
            f'</rect>'
        )
        parts.append('</clipPath>')

        parts.append(f'<g clip-path="url(#{clip_id})">')
        parts.append(
            f'<text x="0" y="{text_y:.2f}" xml:space="preserve">{esc(row_text)}</text>'
        )
        parts.append('</g>')

        # small block cursor riding the wipe edge, disappears once the row is done
        parts.append(
            f'<rect x="0" y="{row_top:.2f}" width="{CHAR_W:.2f}" height="{CHAR_H:.2f}" '
            f'fill="{CURSOR_COLOR}" opacity="0">'
            f'<animate attributeName="opacity" values="0;1;1;0" '
            f'keyTimes="0;0.001;0.999;1" dur="{ROW_DUR}s" begin="{begin}s" fill="freeze"/>'
            f'<animate attributeName="x" from="0" to="{row_w - CHAR_W:.2f}" '
            f'dur="{ROW_DUR}s" begin="{begin}s" fill="freeze" '
            f'calcMode="spline" keySplines="0.25 0.1 0.25 1" keyTimes="0;1" values="0;{row_w - CHAR_W:.2f}"/>'
            f'</rect>'
        )

    parts.append('</svg>')
    return "\n".join(parts)


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.dirname(here)
    src = os.path.join(root, "source-prepped.png")
    out = os.path.join(root, "avi-ascii.svg")

    print(f"Reading {src} ...")
    rows = image_to_grid(src)
    print(f"Building {COLS}x{ROWS} ASCII grid -> SVG ...")
    svg = build_svg(rows)
    with open(out, "w") as f:
        f.write(svg)
    print(f"Saved {out}")


if __name__ == "__main__":
    main()
