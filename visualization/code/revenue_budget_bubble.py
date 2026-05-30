from __future__ import annotations

import math

from common_svg import (
    GRAPH_DIR,
    as_float,
    esc,
    format_money,
    load_movies,
    scale_linear,
    write_svg,
)


OUTPUT = GRAPH_DIR / "revenue_budget_bubble.svg"


def main() -> None:
    movies = []
    for row in load_movies():
        budget = as_float(row, "budget")
        revenue = as_float(row, "revenue")
        if budget and revenue and budget >= 100_000 and revenue >= 50_000:
            movies.append({"budget": budget, "revenue": revenue})

    width, height = 1180, 780
    left, right, top, bottom = 95, 70, 95, 95
    plot_w = width - left - right
    plot_h = height - top - bottom

    budgets = [movie["budget"] for movie in movies]
    revenues = [movie["revenue"] for movie in movies]
    x_min = 100_000.0
    x_max = max(budgets) * 1.02
    y_min = math.log10(50_000)
    y_max = math.ceil(math.log10(max(revenues)))

    def x_pos(budget: float) -> float:
        return scale_linear(budget, x_min, x_max, left, left + plot_w)

    def y_pos(revenue: float) -> float:
        return scale_linear(math.log10(revenue), y_min, y_max, top + plot_h, top)

    elements = [
        '<rect width="100%" height="100%" fill="#fbfcff"/>',
        '<text class="title" x="60" y="54">budget vs revenue</text>',
        f'<line class="axis" x1="{left}" y1="{top + plot_h}" x2="{left + plot_w}" y2="{top + plot_h}"/>',
        f'<line class="axis" x1="{left}" y1="{top}" x2="{left}" y2="{top + plot_h}"/>',
    ]

    for tick in _linear_money_ticks(x_min, x_max):
        x = x_pos(tick)
        elements.append(f'<line class="grid" x1="{x:.2f}" y1="{top}" x2="{x:.2f}" y2="{top + plot_h}"/>')
        elements.append(f'<text class="tick" text-anchor="middle" x="{x:.2f}" y="{top + plot_h + 25}">{esc(format_money(tick))}</text>')

    for tick in _revenue_ticks(max(revenues)):
        y = y_pos(tick)
        elements.append(f'<line class="grid" x1="{left}" y1="{y:.2f}" x2="{left + plot_w}" y2="{y:.2f}"/>')
        elements.append(f'<text class="tick" text-anchor="end" x="{left - 12}" y="{y + 4:.2f}">{esc(format_money(tick))}</text>')

    for movie in movies:
        elements.append(
            f'<circle cx="{x_pos(movie["budget"]):.2f}" cy="{y_pos(movie["revenue"]):.2f}" '
            f'r="2.2" fill="#4e79a7" fill-opacity="0.34" stroke="#ffffff" stroke-width="0.4"/>'
        )

    elements.extend(
        [
            f'<text class="label" text-anchor="middle" x="{left + plot_w / 2}" y="{height - 34}">budget</text>',
            f'<text class="label" transform="translate(34 {top + plot_h / 2}) rotate(-90)" text-anchor="middle">revenue, log scale</text>',
        ]
    )

    write_svg(OUTPUT, width, height, elements)
    print(f"Saved {OUTPUT}")


def _revenue_ticks(max_revenue: float) -> list[float]:
    ticks = [50_000.0]
    value = 100_000
    while value <= max_revenue:
        ticks.append(float(value))
        value *= 10
    return ticks


def _linear_money_ticks(min_value: float, max_value: float, count: int = 7) -> list[float]:
    raw_step = (max_value - min_value) / count
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

    ticks = [min_value]
    value = math.ceil(min_value / step) * step
    if value <= min_value:
        value += step
    while value < max_value:
        ticks.append(float(value))
        value += step
    return ticks


if __name__ == "__main__":
    main()
