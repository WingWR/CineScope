from __future__ import annotations

import csv
import html
import math
from pathlib import Path
from statistics import median


ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_FILE = ROOT_DIR / "data" / "final" / "movies.csv"
GRAPH_DIR = ROOT_DIR / "visualization" / "graph"

FONT_FAMILY = "'Microsoft YaHei', 'SimHei', 'Noto Sans CJK SC', Arial, sans-serif"


def load_movies() -> list[dict[str, str]]:
    with DATA_FILE.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def as_float(row: dict[str, str], key: str) -> float | None:
    value = row.get(key, "")
    if value is None:
        return None
    value = str(value).strip()
    if not value:
        return None
    try:
        number = float(value)
    except ValueError:
        return None
    if not math.isfinite(number):
        return None
    return number


def as_year(row: dict[str, str], key: str = "movie_year") -> int | None:
    number = as_float(row, key)
    if number is None:
        return None
    year = int(number)
    if 1800 <= year <= 2100:
        return year
    return None


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def scale_linear(
    value: float,
    domain_min: float,
    domain_max: float,
    range_min: float,
    range_max: float,
) -> float:
    if domain_max == domain_min:
        return (range_min + range_max) / 2
    ratio = (value - domain_min) / (domain_max - domain_min)
    return range_min + ratio * (range_max - range_min)


def color_lerp(start: str, end: str, ratio: float) -> str:
    ratio = clamp(ratio)
    start = start.lstrip("#")
    end = end.lstrip("#")
    sr, sg, sb = (int(start[i : i + 2], 16) for i in (0, 2, 4))
    er, eg, eb = (int(end[i : i + 2], 16) for i in (0, 2, 4))
    r = round(sr + (er - sr) * ratio)
    g = round(sg + (eg - sg) * ratio)
    b = round(sb + (eb - sb) * ratio)
    return f"#{r:02x}{g:02x}{b:02x}"


def diverging_color(value: float) -> str:
    value = clamp((value + 1) / 2)
    if value < 0.5:
        return color_lerp("#4776b4", "#f7f7f7", value * 2)
    return color_lerp("#f7f7f7", "#c94c4c", (value - 0.5) * 2)


def format_money(value: float) -> str:
    abs_value = abs(value)
    if abs_value >= 1_000_000_000:
        return f"${value / 1_000_000_000:.1f}B"
    if abs_value >= 1_000_000:
        return f"${value / 1_000_000:.0f}M"
    if abs_value >= 1_000:
        return f"${value / 1_000:.0f}K"
    return f"${value:.0f}"


def format_money_millions(value: float) -> str:
    return f"${value / 1_000_000:.0f}M"


def nice_log_ticks(values: list[float]) -> list[float]:
    positive = [value for value in values if value > 0]
    if not positive:
        return []
    low = math.floor(math.log10(min(positive)))
    high = math.ceil(math.log10(max(positive)))
    ticks = [10**power for power in range(low, high + 1)]
    return [tick for tick in ticks if min(positive) <= tick <= max(positive)]


def nice_linear_ticks(max_value: float, count: int = 5) -> list[float]:
    if max_value <= 0:
        return [0]
    raw_step = max_value / max(1, count)
    magnitude = 10 ** math.floor(math.log10(raw_step))
    fraction = raw_step / magnitude
    if fraction <= 1:
        step = magnitude
    elif fraction <= 2:
        step = 2 * magnitude
    elif fraction <= 5:
        step = 5 * magnitude
    else:
        step = 10 * magnitude
    ticks = []
    current = 0.0
    while current <= max_value * 1.01:
        ticks.append(current)
        current += step
    return ticks


def shorten(text: str, limit: int = 22) -> str:
    if len(text) <= limit:
        return text
    return text[: limit - 1] + "..."


def median_or_none(values: list[float]) -> float | None:
    if not values:
        return None
    return float(median(values))


def write_svg(path: Path, width: int, height: int, elements: list[str]) -> None:
    GRAPH_DIR.mkdir(parents=True, exist_ok=True)
    style = f"""
    <style>
      text {{ font-family: {FONT_FAMILY}; fill: #243044; }}
      .title {{ font-size: 30px; font-weight: 700; }}
      .axis {{ stroke: #b8c2d0; stroke-width: 1; }}
      .grid {{ stroke: #e4e9f0; stroke-width: 1; }}
      .tick {{ font-size: 12px; fill: #687386; }}
      .label {{ font-size: 14px; fill: #3c4658; }}
      .note {{ font-size: 12px; fill: #7c8798; }}
    </style>
    """
    body = "\n".join(elements)
    svg = (
        f'<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img">\n'
        f"{style}\n{body}\n</svg>\n"
    )
    path.write_text(svg, encoding="utf-8")
