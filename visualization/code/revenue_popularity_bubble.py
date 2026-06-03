from __future__ import annotations

import math

from common_svg import (
    GRAPH_DIR,
    as_float,
    esc,
    format_money,
    load_movies,
    nice_log_ticks,
    scale_linear,
    write_svg,
)


OUTPUT = GRAPH_DIR / "revenue_popularity_bubble.svg"


def main() -> None:
    movies = []
    for row in load_movies():
        popularity = as_float(row, "tmdb_popularity")
        revenue = as_float(row, "revenue")
        if popularity is not None and 0 <= popularity <= 20 and revenue and revenue > 0:
            movies.append({"tmdb_popularity": popularity, "revenue": revenue})

    width, height = 1180, 780
    left, right, top, bottom = 95, 70, 95, 95
    plot_w = width - left - right
    plot_h = height - top - bottom

    revenues = [movie["revenue"] for movie in movies]
    x_min = 0.0
    x_max = 20.0
    y_min = math.floor(math.log10(min(revenues)))
    y_max = math.ceil(math.log10(max(revenues)))

    def x_pos(popularity: float) -> float:
        return scale_linear(popularity, x_min, x_max, left, left + plot_w)

    def y_pos(revenue: float) -> float:
        return scale_linear(math.log10(revenue), y_min, y_max, top + plot_h, top)

    elements = [
        '<rect width="100%" height="100%" fill="#fbfcff"/>',
        '<text class="title" x="60" y="54">tmdb_popularity vs revenue</text>',
        f'<line class="axis" x1="{left}" y1="{top + plot_h}" x2="{left + plot_w}" y2="{top + plot_h}"/>',
        f'<line class="axis" x1="{left}" y1="{top}" x2="{left}" y2="{top + plot_h}"/>',
    ]

    x_ticks = _linear_ticks(x_max, count=10)
    for tick in x_ticks:
        x = x_pos(tick)
        elements.append(f'<line class="grid" x1="{x:.2f}" y1="{top}" x2="{x:.2f}" y2="{top + plot_h}"/>')
        elements.append(f'<text class="tick" text-anchor="middle" x="{x:.2f}" y="{top + plot_h + 25}">{tick:g}</text>')

    for tick in nice_log_ticks(revenues):
        y = y_pos(tick)
        elements.append(f'<line class="grid" x1="{left}" y1="{y:.2f}" x2="{left + plot_w}" y2="{y:.2f}"/>')
        elements.append(f'<text class="tick" text-anchor="end" x="{left - 12}" y="{y + 4:.2f}">{esc(format_money(tick))}</text>')

    for movie in movies:
        elements.append(
            f'<circle cx="{x_pos(movie["tmdb_popularity"]):.2f}" cy="{y_pos(movie["revenue"]):.2f}" '
            f'r="2.2" fill="#4e79a7" fill-opacity="0.34" stroke="#ffffff" stroke-width="0.4"/>'
        )

    elements.extend(
        [
            f'<text class="label" text-anchor="middle" x="{left + plot_w / 2}" y="{height - 34}">tmdb_popularity</text>',
            f'<text class="label" transform="translate(34 {top + plot_h / 2}) rotate(-90)" text-anchor="middle">revenue, log scale</text>',
        ]
    )

    write_svg(OUTPUT, width, height, elements)
    print(f"Saved {OUTPUT}")


def _linear_ticks(max_value: float, count: int = 6) -> list[float]:
    if max_value <= 0:
        return [0.0]
    step = max_value / count
    magnitude = 10 ** math.floor(math.log10(step))
    fraction = step / magnitude
    if fraction <= 1:
        nice_step = magnitude
    elif fraction <= 2:
        nice_step = 2 * magnitude
    elif fraction <= 5:
        nice_step = 5 * magnitude
    else:
        nice_step = 10 * magnitude
    ticks = []
    value = 0.0
    while value <= max_value * 1.001:
        ticks.append(value)
        value += nice_step
    return ticks


if __name__ == "__main__":
    main()
