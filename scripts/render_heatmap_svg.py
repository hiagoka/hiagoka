#!/usr/bin/env python3
"""
render_heatmap_svg.py — draw data/contributions.json as the classic
53-week x 7-day calendar of rounded, colored boxes. Reveals once with a
diagonal, line-after-line slide-down (CSS keyframes, plays on load then
freezes — no looping), plus a Less->More legend and a stats footer.

Usage: python scripts/render_heatmap_svg.py
Output: contrib-heatmap.svg
"""
import json
import os
from datetime import datetime

PALETTE = [
    "#161b22", "#0e4429", "#006d32",
    "#26a641", "#39d353", "#69f0a0",
]
#          none -> brightest (level 5 is a neon top end)

# Days with an unusually high count get bumped past GitHub's own 0-4 scale
# to the custom neon top tier — a bit of extra pop for standout days.
HOT_DAY_THRESHOLD = 10

CELL = 11
GAP = 3
STEP = CELL + GAP
PAD_LEFT = 28
PAD_TOP = 34
PAD_RIGHT = 16
PAD_BOTTOM = 54

BG = "#0d1117"
BORDER = "#30363d"
LABEL_COLOR = "#8b949e"
TITLE_COLOR = "#e6edf3"
FONT = "'SFMono-Regular',Menlo,Consolas,'Liberation Mono',monospace"

STAGGER_STEP = 0.011
REVEAL_DUR = 0.4

MONTH_ABBR = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
DOW_LABELS = {1: "Seg", 3: "Qua", 5: "Sex"}  # 0=Sun..6=Sat


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def level_for(day):
    lvl = day.get("level", 0)
    if day.get("count", 0) >= HOT_DAY_THRESHOLD:
        lvl = 5
    return max(0, min(lvl, 5))


def build_svg(data):
    days = data["days"]
    stats = data["stats"]
    weeks = (len(days) + 6) // 7

    grid_w = weeks * STEP - GAP
    grid_h = 7 * STEP - GAP
    width = PAD_LEFT + grid_w + PAD_RIGHT
    height = PAD_TOP + grid_h + PAD_BOTTOM

    parts = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'width="{width}" height="{height}">'
    )
    parts.append(
        f'<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="10" '
        f'fill="{BG}" stroke="{BORDER}" stroke-width="1"/>'
    )
    parts.append(
        f'<style>'
        f'.cell{{opacity:0;transform:translateY(-6px);animation:reveal {REVEAL_DUR}s ease-out forwards;}}'
        f'@keyframes reveal{{to{{opacity:1;transform:translateY(0);}}}}'
        f'text{{font-family:{FONT};fill:{LABEL_COLOR};font-size:10px;}}'
        f'</style>'
    )

    # day-of-week labels
    for dow, label in DOW_LABELS.items():
        y = PAD_TOP + dow * STEP + CELL - 1
        parts.append(f'<text x="4" y="{y}">{esc(label)}</text>')

    # month labels (one per week column where the month changes)
    last_month = None
    for w in range(weeks):
        idx = w * 7
        if idx >= len(days):
            break
        try:
            dt = datetime.strptime(days[idx]["date"], "%Y-%m-%d")
        except ValueError:
            continue
        if dt.month != last_month:
            x = PAD_LEFT + w * STEP
            parts.append(f'<text x="{x}" y="{PAD_TOP - 10}">{MONTH_ABBR[dt.month - 1]}</text>')
            last_month = dt.month

    # cells, staggered diagonally (week + day-of-week)
    for i, day in enumerate(days):
        week = i // 7
        dow = i % 7
        x = PAD_LEFT + week * STEP
        y = PAD_TOP + dow * STEP
        color = PALETTE[level_for(day)]
        delay = round((week + dow) * STAGGER_STEP, 3)
        parts.append(
            f'<rect class="cell" x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" '
            f'fill="{color}" style="animation-delay:{delay}s">'
            f'<title>{esc(day["count"])} contribuições em {esc(day["date"])}</title>'
            f'</rect>'
        )

    # legend: Less [swatches] More, bottom-left
    legend_y = height - PAD_BOTTOM + 20
    lx = PAD_LEFT
    parts.append(f'<text x="{lx}" y="{legend_y + 8}">Menos</text>')
    lx += 42
    for lvl in range(6):
        parts.append(
            f'<rect x="{lx}" y="{legend_y}" width="{CELL}" height="{CELL}" rx="2" fill="{PALETTE[lvl]}"/>'
        )
        lx += STEP
    parts.append(f'<text x="{lx + 4}" y="{legend_y + 8}">Mais</text>')

    # stats footer
    total = stats.get("total", 0)
    streak = stats.get("current_streak", 0)
    longest = stats.get("longest_streak", 0)
    footer = f'{total} contribuições no último ano · streak atual: {streak}d · recorde: {longest}d'
    parts.append(
        f'<text x="{width - PAD_RIGHT}" y="{legend_y + 8}" text-anchor="end" '
        f'fill="{TITLE_COLOR}">{esc(footer)}</text>'
    )

    parts.append('</svg>')
    return "\n".join(parts)


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.dirname(here)
    data_path = os.path.join(root, "data", "contributions.json")
    out_path = os.path.join(root, "contrib-heatmap.svg")

    with open(data_path) as f:
        data = json.load(f)

    svg = build_svg(data)
    with open(out_path, "w") as f:
        f.write(svg)
    print(f"Saved {out_path}")


if __name__ == "__main__":
    main()
