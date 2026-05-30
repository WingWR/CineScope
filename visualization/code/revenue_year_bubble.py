from __future__ import annotations

import math

from common_svg import (
    GRAPH_DIR,
    as_float,
    as_year,
    esc,
    format_money,
    load_movies,
    nice_log_ticks,
    scale_linear,
    write_svg,
)


OUTPUT = GRAPH_DIR / "revenue_year_bubble.svg"


def main() -> None:
    movies = []
    for row in load_movies():
        year = as_year(row)
        revenue = as_float(row, "revenue")
        if year is not None and revenue and revenue > 0:
            movies.append({"movie_year": year, "revenue": revenue})

    width, height = 1180, 780
    left, right, top, bottom = 95, 70, 95, 95
    plot_w = width - left - right
    plot_h = height - top - bottom

    years = [movie["movie_year"] for movie in movies]
    revenues = [movie["revenue"] for movie in movies]
    min_year, max_year = min(years), max(years)
    y_min = math.floor(math.log10(min(revenues)))
    y_max = math.ceil(math.log10(max(revenues)))

    def x_pos(year: int) -> float:
        return scale_linear(year, min_year, max_year, left, left + plot_w)

    def y_pos(revenue: float) -> float:
        return scale_linear(math.log10(revenue), y_min, y_max, top + plot_h, top)

    elements = [
        '<rect width="100%" height="100%" fill="#fbfcff"/>',
        '<text class="title" x="60" y="54">movie_year vs revenue</text>',
        f'<line class="axis" x1="{left}" y1="{top + plot_h}" x2="{left + plot_w}" y2="{top + plot_h}"/>',
        f'<line class="axis" x1="{left}" y1="{top}" x2="{left}" y2="{top + plot_h}"/>',
    ]

    decade_start = (min_year // 10) * 10
    for year in range(decade_start, max_year + 1, 10):
        if year < min_year:
            continue
        x = x_pos(year)
        elements.append(f'<line class="grid" x1="{x:.2f}" y1="{top}" x2="{x:.2f}" y2="{top + plot_h}"/>')
        elements.append(f'<text class="tick" text-anchor="middle" x="{x:.2f}" y="{top + plot_h + 25}">{year}</text>')

    for tick in nice_log_ticks(revenues):
        y = y_pos(tick)
        elements.append(f'<line class="grid" x1="{left}" y1="{y:.2f}" x2="{left + plot_w}" y2="{y:.2f}"/>')
        elements.append(f'<text class="tick" text-anchor="end" x="{left - 12}" y="{y + 4:.2f}">{esc(format_money(tick))}</text>')

    for movie in movies:
        elements.append(
            f'<circle cx="{x_pos(movie["movie_year"]):.2f}" cy="{y_pos(movie["revenue"]):.2f}" '
            f'r="2.2" fill="#4e79a7" fill-opacity="0.34" stroke="#ffffff" stroke-width="0.4"/>'
        )

    elements.extend(
        [
            f'<text class="label" text-anchor="middle" x="{left + plot_w / 2}" y="{height - 34}">movie_year</text>',
            f'<text class="label" transform="translate(34 {top + plot_h / 2}) rotate(-90)" text-anchor="middle">revenue, log scale</text>',
        ]
    )

    write_svg(OUTPUT, width, height, elements)
    print(f"Saved {OUTPUT}")


if __name__ == "__main__":
    main()
