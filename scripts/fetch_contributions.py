#!/usr/bin/env python3
"""
fetch_contributions.py — scrape the public contribution calendar HTML
fragment GitHub serves at /users/<username>/contributions (no token, no
GraphQL API needed) and write data/contributions.json with raw days plus
derived stats (current streak, longest streak, best day, monthly totals).

Usage: python scripts/fetch_contributions.py
Output: data/contributions.json
"""
import json
import os
import re
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

USERNAME = "hiagoka"


def fetch_html(username):
    url = f"https://github.com/users/{username}/contributions"
    headers = {"User-Agent": "Mozilla/5.0 (compatible; profile-art-bot/1.0)"}
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.text


def parse_count(tooltip_text):
    if not tooltip_text:
        return 0
    if tooltip_text.lower().startswith("no contributions"):
        return 0
    m = re.match(r"(\d+)\s+contribution", tooltip_text.strip())
    return int(m.group(1)) if m else 0


def parse_days(html):
    soup = BeautifulSoup(html, "html.parser")

    tooltip_by_id = {}
    for tip in soup.select("tool-tip"):
        for_id = tip.get("for")
        if for_id:
            tooltip_by_id[for_id] = tip.get_text(strip=True)

    days = []
    for td in soup.select("td.ContributionCalendar-day"):
        date = td.get("data-date")
        if not date:
            continue
        level = td.get("data-level")
        tip_text = tooltip_by_id.get(td.get("id"), "")
        days.append(
            {
                "date": date,
                "level": int(level) if level is not None else 0,
                "count": parse_count(tip_text),
            }
        )

    days.sort(key=lambda d: d["date"])
    return days


def compute_stats(days):
    total = sum(d["count"] for d in days)

    longest_streak = 0
    run = 0
    for d in days:
        if d["count"] > 0:
            run += 1
            longest_streak = max(longest_streak, run)
        else:
            run = 0

    current_streak = 0
    for d in reversed(days):
        if d["count"] > 0:
            current_streak += 1
        else:
            break

    best_day = max(days, key=lambda d: d["count"]) if days else None

    monthly = {}
    for d in days:
        ym = d["date"][:7]
        monthly[ym] = monthly.get(ym, 0) + d["count"]

    return {
        "total": total,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "best_day": best_day,
        "monthly": monthly,
    }


def main():
    print(f"Fetching contribution calendar for {USERNAME} ...")
    html = fetch_html(USERNAME)
    days = parse_days(html)
    if not days:
        raise SystemExit("No contribution cells found — GitHub markup may have changed.")

    stats = compute_stats(days)

    out = {
        "username": USERNAME,
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "days": days,
        "stats": stats,
    }

    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.dirname(here)
    out_path = os.path.join(root, "data", "contributions.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)

    print(f"Saved {out_path}: {len(days)} days, {stats['total']} contributions total")


if __name__ == "__main__":
    main()
